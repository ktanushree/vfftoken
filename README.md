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
There are 2 scripts in this repo.
generate_token.py can be used to generate tokens using login credentials or an AUTH Token. To retrieve tokens using a service account, use the script generate_token_sase.py

#### CloudGenix
1. Generate Single Use token
```
./generate_token.py -M 3104 -T single 
```
2. Generate Multiple Use token 
``` 
./generate_token.py -M 3104 -T multi 
```

#### PRISMA SASE 
1. Generate one single use token for a single child tenant
```
./generate_token_sase.py -CI "client_id" -CS "client_secret" -CT "master_tsg_id" -M 3102 -T "child_tsg_id" -N 1 -U single
```
2. Generate 10 single use token for a single child tenant
```
./generate_token_sase.py -CI "client_id" -CS "client_secret" -CT "master_tsg_id" -M 3102 -T "child_tsg_id" -N 10 -U single
```
3. Generate 1 multi use token for a single child tenant
```
./generate_token_sase.py -CI "client_id" -CS "client_secret" -CT "master_tsg_id" -M 3102 -T "child_tsg_id" -N 1 -U multi
```
4. Generate 10 multi use token for a single child tenant
```
./generate_token_sase.py -CI "client_id" -CS "client_secret" -CT "master_tsg_id" -M 3102 -T "child_tsg_id" -N 10 -U multi
```
5. Generate 1 multi use token for each child tenants via a CSV file
```
./generate_token_sase.py -CI "client_id" -CS "client_secret" -CT "master_tsg_id" -M 3102 -F tsg_ids.csv -N 1 -U multi
```

### Help Text:
#### CloudGenix
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

#### Prisma SASE
```angular2
(base) Tanushree:scripts tkamath$ ./generate_token_sase.py -h
usage: generate_token_sase.py [-h] [--controller CONTROLLER] [--client_id CLIENT_ID] [--client_secret CLIENT_SECRET] [--client_tsg CLIENT_TSG] [--sdkdebug SDKDEBUG]
                              [--model_name MODEL_NAME] [--use USE] [--num NUM] [--tsg_id TSG_ID] [--filename FILENAME]

Generate VFF Tokens.

optional arguments:
  -h, --help            show this help message and exit

API:
  These options change how this program connects to the API.

  --controller CONTROLLER, -C CONTROLLER
                        Controller URI, ex. C-Prod: https://api.sase.paloaltonetworks.cloudgenix.com

Login:
  These options allow skipping of interactive login

  --client_id CLIENT_ID, -CI CLIENT_ID
                        Service Account Client ID
  --client_secret CLIENT_SECRET, -CS CLIENT_SECRET
                        Service Account Client Secret
  --client_tsg CLIENT_TSG, -CT CLIENT_TSG
                        Service Account TSG

Debug:
  These options enable debugging output

  --sdkdebug SDKDEBUG, -D SDKDEBUG
                        Enable SDK Debug output, levels 0-2

Config:
  These options are to provide VFF license parameters

  --model_name MODEL_NAME, -M MODEL_NAME
                        Choose the ION model for license generation. Allowed values: 3102, 3104
  --use USE, -U USE     Single or Multi use token. Allowed values: single or multi
  --num NUM, -N NUM     Number of tokens
  --tsg_id TSG_ID, -T TSG_ID
                        Child TSG ID
  --filename FILENAME, -F FILENAME
                        File name with TSG IDs
(base) Tanushree:scripts tkamath$ 
```

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * For more information on Prisma SDWAN Python SDK, go to https://developers.cloudgenix.com
 

