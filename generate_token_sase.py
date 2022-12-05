#!/usr/bin/env python
"""
Script to generate VFF Tokens using a Service Account
tkamath@paloaltonetworks.com
"""
import sys
import os
import argparse
import prisma_sase
import pandas as pd
import datetime

SCRIPT_NAME = "Generate VFF Tokens"
SCRIPT_VERSION = "v1.0"

# Import Prisma SASE Python SDK
try:
    import prisma_sase
except ImportError as e:
    prisma_sase = None
    sys.stderr.write("ERROR: 'prisma_sase' python module required.\n {0}\n".format(e))
    sys.exit(1)

# Check for cloudgenix_settings.py config file in cwd.
sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import PRISMASASE_CLIENT_ID, PRISMASASE_CLIENT_SECRET, PRISMASASE_CLIENT_TSG

except ImportError:
    PRISMASASE_CLIENT_ID = None
    PRISMASASE_CLIENT_SECRET = None
    PRISMASASE_CLIENT_TSG = None


# Handle differences between python 2 and 3. Code can use text_type and binary_type instead of str/bytes/unicode etc.
if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


ionmodel_licensecount_dict = {}
ionmodel_licenseid_dict = {}
ionmodel_deployedcount_dict = {}
ionmodel_availablecount_dict = {}

def get_license_usage(sdk):
    #
    # Retrive VFF License count for each ION models
    #
    resp = sdk.get.vfflicenses()
    if resp.cgx_status:
        licenselist = resp.cgx_content.get("items", None)

        for license in licenselist:
            ionmodel_licensecount_dict[license["model"]] = license["allowed_ions"]
            ionmodel_licenseid_dict[license["model"]] = license["id"]

            #
            # Get usage information
            #
            resp = sdk.get.vfflicense_status(license["id"])
            if resp.cgx_status:
                deployed_count = resp.cgx_content.get("deployed_ions")
                ionmodel_deployedcount_dict[license["model"]] = deployed_count
                available_count = license["allowed_ions"] - deployed_count
                ionmodel_availablecount_dict[license["model"]] = available_count

            else:
                print("ERR: Could not retrieve VFF License Status for model {}".format(license["model"]))
                prisma_sase.jd_detailed(resp)

    else:
        print("ERR: Could not retrieve VFF Licenses")
        prisma_sase.jd_detailed(resp)


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
    Stub script entry point. Authenticates Prisma SASE SDK, and gathers options from command line to run do_site()
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
                                       "C-Prod: https://api.sase.paloaltonetworks.cloudgenix.com",
                                  default=None)

    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--client_id", "-CI", help="Service Account Client ID",
                             default=None)
    login_group.add_argument("--client_secret", "-CS", help="Service Account Client Secret",
                             default=None)
    login_group.add_argument("--client_tsg", "-CT", help="Service Account TSG",
                             default=None)
    # Debug Settings
    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--sdkdebug", "-D", help="Enable SDK Debug output, levels 0-2", type=int,
                             default=0)

    # Config Settings
    config_group = parser.add_argument_group('Config', 'These options are to provide VFF license parameters')
    config_group.add_argument("--model_name", "-M",
                              help="Choose the ION model for license generation. Allowed values: 3102, 3104",
                              default="3102")
    config_group.add_argument("--use", "-U", help="Single or Multi use token. Allowed values: single or multi",
                              default="multi")
    config_group.add_argument("--num", "-N", help="Number of tokens",
                              default=1)
    config_group.add_argument("--tsg_id", "-T", help="Child TSG ID", default=None)
    config_group.add_argument("--filename", "-F", help="File name with TSG IDs", default=None)


    ############################################################################
    # Parse arguments provided via CLI
    ############################################################################
    args = vars(parser.parse_args())
    sdk_debuglevel = args["sdkdebug"]
    model_name = args["model_name"]
    use = args["use"]
    tsg_id = args["tsg_id"]
    filename = args["filename"]
    num = int(args["num"])

    if filename is None and tsg_id is None:
        print("ERR: Please provide child TSG ID via a CSV file or the CLI parameter tsg_id")
        sys.exit()

    singletenant = True
    if filename:
        if not os.path.isfile(filename):
            print("ERR: File {} does not exist. Please enter the accurate file".format(filename))
            sys.exit()
        else:
            singletenant = False

    if use not in ["single", "multi"]:
        print("ERR: Invalid use. Please choose: single or multi")
        sys.exit()

    if use == "single":
        multiuse = "false"
    else:
        multiuse = "true"

    if model_name not in ["3102", "3104"]:
        print("ERR: Invalid model_name. Please choose from: 3102, 3104")
        sys.exit()

    client_id = client_secret = client_tsg = None
    if((PRISMASASE_CLIENT_ID is None) and (PRISMASASE_CLIENT_SECRET is None) and (PRISMASASE_CLIENT_TSG is None)):
        if ((args["client_id"] is None) or (args["client_secret"] is None) or (args["client_tsg"] is None)):
            print("ERR: Please provide Service Account Details via cloudgenix_settings.py file or CLI arguments to proceed")
            sys.exit()

        else:
            client_id = args["client_id"]
            client_secret = args["client_secret"]
            client_tsg = args["client_tsg"]
    else:
        client_id = PRISMASASE_CLIENT_ID
        client_secret = PRISMASASE_CLIENT_SECRET
        client_tsg = PRISMASASE_CLIENT_TSG


    ION_MODEL = model_map[model_name]
    ############################################################################
    # Instantiate API & Login
    ############################################################################
    sase_session = prisma_sase.API(controller=args["controller"], ssl_verify=False)
    sase_session.set_debug(sdk_debuglevel)
    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, sase_session.version, sase_session.controller))

    #
    # Use Service Account Details to login to tenant
    #
    sase_session.interactive.login_secret(client_id=client_id, client_secret=client_secret, tsg_id=client_tsg)
    if sase_session.tenant_id is None:
        print("ERR: Service Account login failure. Please check client credentials")
        sys.exit()

    ############################################################################
    # Determine List of TSG IDs
    ############################################################################

    tenantlist = []
    if singletenant:
        tenantlist.append(tsg_id)
    else:
        tdata = pd.read_csv(filename)
        columns = list(tdata.columns)

        if "tsg_id" not in columns:
            print("ERR: Invalid CSV. Please provide a CSV file with the column header: tsg_is")
            sys.exit()

        tenantlist = tdata.tsg_id.unique()

    ############################################################################
    # Iterate through tenant list to get:
    # - License Types
    # - Create VFF
    ############################################################################
    vffdata = pd.DataFrame()
    for tenant in tenantlist:
        tokennum = num
        print(tenant)
        sdk = prisma_sase.API(controller=args["controller"], ssl_verify=False)
        sdk.interactive.login_secret(client_id=client_id, client_secret=client_secret, tsg_id=tenant)
        get_license_usage(sdk)
        ############################################################################
        # Generate VFF License
        ############################################################################
        ION_KEY = None
        ION_SECRET = None
        available_count = ionmodel_availablecount_dict[ION_MODEL]
        if available_count - num > 0:
            print("\tINFO: Licenses available to generate {} tokens for {}".format(num, ION_MODEL))
        else:
            print("\tERR: Not enough licenses available to generate {} tokens for {}. Skipping tenant: {}".format(num, ION_MODEL, tenant))
            continue

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

            while tokennum > 0:
                resp = sdk.post.tokens_vfflicenses(vfflicense_id=license_id, data=data)
                if resp.cgx_status:
                    tokendata = resp.cgx_content
                    ION_KEY = tokendata["ion_key"]
                    ION_SECRET = tokendata["secret_key"]
                    print("\tSUCCESS: {} use VFF token successfully created for {}".format(use, ION_MODEL))
                    print("\tKey: {}\n\tSecret:{}".format(ION_KEY, ION_SECRET))
                    vffdata = vffdata.append({"tenant_id": tenant,
                                              "model": ION_MODEL,
                                              "key": ION_KEY,
                                              "secret": ION_SECRET}, ignore_index=True)

                else:
                    print("ERR: Could not create VFF token")
                    prisma_sase.jd_detailed(resp)

                tokennum = tokennum-1

        else:
            print("WARN: No more licenses available for the model: {}".format(ION_MODEL))
            sys.exit()

    ############################################################################
    # Save VFF Key & Secret in CSV File
    ############################################################################
    curtime_str = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    vfffilename = "vffdata_{}.csv".format(curtime_str)
    print("INFO: Saving VFF Keys & Secret to file: {}".format(vfffilename))
    vffdata.to_csv(vfffilename, index=False)
    ############################################################################
    # Exit Script
    ############################################################################
    sys.exit()


if __name__ == "__main__":
    go()
