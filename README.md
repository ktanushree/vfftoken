# VFF Token Management
Prisma SDWAN Script to generate VFF Token for a given VFF model

#### Synopsis
This script is used to generate a VFF token for a given ION model. It checks for available licenses before generating a token. By default, it generates a token for ION 3102v. 


#### Requirements
* Active Prisma SDWAN Account
* Python >=3.6
* Python modules:
    * CloudGenix Python SDK >= 6.0.1b1 - <https://github.com/CloudGenix/sdk-python>

#### License
MIT

#### Installation:
 - **Github:** Download files to a local directory, manually run `generate_token.py`. 

### Usage:
1. Generate Single Use token
```
./generate_token.py -M 3104 -T single 
```
2. Generate Multiple Use token 
``` 
./generate_token.py -M 3104 -T multi 
```

Help Text:
```angular2
TanushreeMacBookPro:vfflicencemanagement tanushreekamath$ ./generate_token.py -h
usage: generate_token.py [-h] [--controller CONTROLLER] [--email EMAIL] [--pass PASS] [--sdkdebug SDKDEBUG] [--model_name MODEL_NAME] [--type TYPE]

Generate VFF License.

optional arguments:
  -h, --help            show this help message and exit

API:
  These options change how this program connects to the API.

  --controller CONTROLLER, -C CONTROLLER
                        Controller URI, ex. C-Prod: https://api.elcapitan.cloudgenix.com

Login:
  These options allow skipping of interactive login

  --email EMAIL, -E EMAIL
                        Use this email as User Name instead of prompting
  --pass PASS, -P PASS  Use this Password instead of prompting

Debug:
  These options enable debugging output

  --sdkdebug SDKDEBUG, -D SDKDEBUG
                        Enable SDK Debug output, levels 0-2

Config:
  These options are to provide VFF license parameters

  --model_name MODEL_NAME, -M MODEL_NAME
                        Choose the ION model for license generation. Allowed values: 3102, 3104, 3108, 7108, 7116, 7132
  --type TYPE, -T TYPE  Single or Multi use token. Allowed values: single or multi
TanushreeMacBookPro:vfflicencemanagement tanushreekamath$

```

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * For more information on Prisma SDWAN Python SDK, go to https://developers.cloudgenix.com
 

