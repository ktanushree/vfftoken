#!/usr/bin/env python
"""
Prisma SDWAN script to generate VFF license
tkamath@paloaltonetworks.com
"""
import sys
import os
import argparse
import cloudgenix

SCRIPT_NAME = "Generate VFF License"
SCRIPT_VERSION = "v1.0"


# Import CloudGenix Python SDK
try:
    import cloudgenix
except ImportError as e:
    cloudgenix = None
    sys.stderr.write("ERROR: 'cloudgenix' python module required. (try 'pip install cloudgenix').\n {0}\n".format(e))
    sys.exit(1)

# Check for cloudgenix_settings.py config file in cwd.
sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import CLOUDGENIX_AUTH_TOKEN

except ImportError:
    # if cloudgenix_settings.py file does not exist,
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

try:
    # Also, separately try and import USERNAME/PASSWORD from the config file.
    from cloudgenix_settings import CLOUDGENIX_USER, CLOUDGENIX_PASSWORD

except ImportError:
    # will get caught below
    CLOUDGENIX_USER = None
    CLOUDGENIX_PASSWORD = None


# Handle differences between python 2 and 3. Code can use text_type and binary_type instead of str/bytes/unicode etc.
if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


def cleanexit(cgx_session):
    print("INFO: Logging Out")
    cgx_session.get.logout()
    sys.exit()


ionmodel_licensecount_dict = {}
ionmodel_licenseid_dict = {}
ionmodel_deployedcount_dict = {}
ionmodel_availablecount_dict = {}
def get_license_usage(cgx_session):
    #
    # Retrive VFF License count for each ION models
    #
    resp = cgx_session.get.vfflicenses()
    if resp.cgx_status:
        licenselist = resp.cgx_content.get("items", None)

        for license in licenselist:
            ionmodel_licensecount_dict[license["model"]] = license["allowed_ions"]
            ionmodel_licenseid_dict[license["model"]] = license["id"]

            #
            # Get usage information
            #
            resp = cgx_session.get.vfflicense_status(license["id"])
            if resp.cgx_status:
                deployed_count = resp.cgx_content.get("deployed_ions")
                ionmodel_deployedcount_dict[license["model"]] = deployed_count
                available_count = license["allowed_ions"] - deployed_count
                ionmodel_availablecount_dict[license["model"]] = available_count

            else:
                print("ERR: Could not retrieve VFF License Status for model {}".format(license["model"]))
                cloudgenix.jd_detailed(resp)

    else:
        print("ERR: Could not retrieve VFF Licenses")
        cloudgenix.jd_detailed(resp)


model_map = {
    "3102": "ion 3102v",
    "3104": "ion 3104v",
    "3108": "ion 3108v",
    "7108": "ion 7108v",
    "7116": "ion 7116v",
    "7132": "ion 7132v"
}


def go():
    """
    Stub script entry point. Authenticates CloudGenix SDK, and gathers options from command line to run do_site()
    :return: No return
    """

    #############################################################################
    # Begin Script, parse arguments.
    ############################################################################

    # Parse arguments
    parser = argparse.ArgumentParser(description="{0}.".format(SCRIPT_NAME))

    # Allow Controller modification and debug level sets.
    controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
    controller_group.add_argument("--controller", "-C",
                                  help="Controller URI, ex. "
                                       "C-Prod: https://api.elcapitan.cloudgenix.com",
                                  default=None)

    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email as User Name instead of prompting",
                             default=None)
    login_group.add_argument("--pass", "-P", help="Use this Password instead of prompting",
                             default=None)

    # Debug Settings
    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--sdkdebug", "-D", help="Enable SDK Debug output, levels 0-2", type=int,
                             default=0)

    # Config Settings
    config_group = parser.add_argument_group('Config', 'These options are to provide VFF license parameters')
    config_group.add_argument("--model_name", "-M", help="Choose the ION model for license generation. Allowed values: 3102, 3104, 3108, 7108, 7116, 7132", default="3102")
    config_group.add_argument("--type", "-T", help="Single or Multi use token. Allowed values: single or multi",
                              default="multi")

    ############################################################################
    # Parse arguments provided via CLI
    ############################################################################
    args = vars(parser.parse_args())
    sdk_debuglevel = args["sdkdebug"]
    model_name = args["model_name"]
    type = args["type"]

    if type not in ["single", "multi"]:
        print("ERR: Invalid type. Please choose: single or multi")
        sys.exit()

    if type == "single":
        multiuse = "false"
    else:
        multiuse = "true"

    if model_name not in ["3102", "3104", "3108", "7108", "7116", "7132"]:
        print("ERR: Invalid model_name. Please choose from: 3102, 3104, 3108, 7108, 7116, 7132")
        sys.exit()

    ION_MODEL = model_map[model_name]
    ############################################################################
    # Instantiate API & Login
    ############################################################################
    cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=False)
    cgx_session.set_debug(sdk_debuglevel)
    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, cgx_session.version, cgx_session.controller))

    # login logic. Use cmdline if set, use AUTH_TOKEN next, finally user/pass from config file, then prompt.
    # figure out user
    if args["email"]:
        user_email = args["email"]
    elif CLOUDGENIX_USER:
        user_email = CLOUDGENIX_USER
    else:
        user_email = None

    # figure out password
    if args["pass"]:
        user_password = args["pass"]
    elif CLOUDGENIX_PASSWORD:
        user_password = CLOUDGENIX_PASSWORD
    else:
        user_password = None

    # check for token
    if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["pass"]:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("AUTH_TOKEN login failure, please check token.")
            sys.exit()

    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None
    ############################################################################
    # Get current license usage
    ############################################################################
    get_license_usage(cgx_session)
    ############################################################################
    # Generate VFF License
    ############################################################################
    ION_KEY = None
    ION_SECRET = None
    available_count = ionmodel_availablecount_dict[ION_MODEL]
    if available_count > 0:
        license_id = ionmodel_licenseid_dict[ION_MODEL]
        data = {
            "is_multiuse": multiuse,
            "vfflicense_id": None,
            "ion_key": None,
            "valid_till_secs": 0,
            "is_revoked": False,
            "secret_key": None,
            "is_used": False,
            "is_expired": False
        }

        resp = cgx_session.post.tokens_vfflicenses(vfflicense_id=license_id, data=data)
        if resp.cgx_status:
            tokendata = resp.cgx_content
            ION_KEY = tokendata["ion_key"]
            ION_SECRET = tokendata["secret_key"]
            print("SUCCESS: {} use VFF token successfully created for {}".format(type, ION_MODEL))
            print("\n\nKey: {}\nSecret:{}\n\n".format(ION_KEY, ION_SECRET))

        else:
            print("ERR: Could not create VFF token")
            cloudgenix.jd_detailed(resp)

    else:
        print("WARN: No more licenses available for the model: {}".format(ION_MODEL))
        cleanexit(cgx_session)

    ############################################################################
    # Logout to clear session.
    ############################################################################
    cleanexit(cgx_session)


if __name__ == "__main__":
    go()
