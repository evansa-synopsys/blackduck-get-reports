# blackduck-get-reports
A program that will create and download Version Vulnerability Status or an SBOM report for a specified project version to a
specified path on the system. 

| Filename         | Purpose                                                                                                            |
|------------------|--------------------------------------------------------------------------------------------------------------------|
| requirements.txt | Python package dependencies                                                                                        |
| get_report.py    | Python script that initiates the report creation and attempts to download it when it is available from the server. |
| helper.py        | Helper class that enables parameters to be passed on the command line                                              |

## Requirements

- Black Duck Hub Server
    - Solution was tested using v2022.10.x and is compatible with versions back to 2022.4.x
- User API token for authentication
- Python3
- [*blackduck*](https://pypi.org/project/blackduck/) PyPi library and possibly other python packages as specified in *requirements.txt*

## Setup and Usage

1. Clone this repository

2. Install *blackduck* library and any other Python package dependencies

   ```
   pip3 install -r requirements.txt
   ```

3. Create .restconfig.json file with Black Duck Hub authentication credentials setting appropriate values
    1. Option to supply url, username and password on the command line instead of a restconfig.json file has been added.

       ```
       cat > .restconfig.json
       {
          "baseurl": "https://blackduck-server-host",
          "api_token": "<YOUR-USER-API-TOKEN>",
          "insecure": true,
          "debug": false,
          "refresh_token": false
       }
       <ctrl>-d
       ```
## Create and download a Version Vulnerability Report using get_report.py

```
usage: A program that will create and download Version Vulnerability Status Report for a specified project version to a 
specified path on the system.        
       [-h] -u SOURCE_HUB_URL -t SOURCE_API_TOKEN [-i] [-v] -p PROJECT -pv
       PROJECT_VERSION [-l LOCALE] [-rf {CSV,JSON,TEXT,YAML,RDF,TAGVALUE}]
       [-rt {VERSION_VULNERABILITY_STATUS,SBOM}]
       [-st {SPDX_22,CYCLONEDX_13,CYCLONEDX_14}] [-m MAX_RETRIES]
       [-w WAIT_TIME] [-o OUT_PUT_FILE_PATH] [-la]


optional arguments:
-h, --help            show this help message and exit

-u SOURCE_HUB_URL,    --source-hub-url SOURCE_HUB_URL Source Black Duck Hub URL

-t SOURCE_API_TOKEN,  --source-api-token SOURCE_API_TOKEN Source Black Duck Api token

-i, --insecure        Supress ssl warnings, default is false

-v, --verbose         Turn on request DEBUG logging

-p PROJECT,           --project PROJECT Specify a project

-pv PROJECT_VERSION,  --project-version PROJECT_VERSION Specify a project version

-l LOCALE,            --locale LOCALE Specify a report locale

-rf {JSON,YAML,RDF,TAGVALUE}, --report-format {JSON,YAML,RDF,TAGVALUE} Report Format

-rt {VERSION_VULNERABILITY_STATUS,SBOM}, --report-type {VERSION_VULNERABILITY_STATUS,SBOM} Report Type

-st {SPDX_22,CYCLONEDX_13,CYCLONEDX_14}, --sbom-type {SPDX_22,CYCLONEDX_13,CYCLONEDX_14} Sbom Type. 
Note: CYCLONEDX_* types are only compatible with report-format = JSON as of 2022.10.x.

-m MAX_RETRIES, --max-retries MAX_RETRIES Maximum number of retries before time out, default = 5.

-w WAIT_TIME, --wait-time WAIT_TIME Time to sleep between retries (seconds).

-o OUT_PUT_FILE_PATH, --out-put-file-path OUT_PUT_FILE_PATH Specify a filepath to write the downloaded zip, 
                        if a valid path is not provided, the report will be
                        downloaded to the project root
                        
-la, --list-all       List all project and version names for target BD and
                        exit. Default is false.

```

## Example Usage:
```
python3 get_sbom.py
-u
https://<bd_url>
-t
<your_api_token>
-p
<project_name>
-pv
<project_version>
-rt
VERSION_VULNERABILITY_STATUS
-rf
CSV
-i
-v
-o
/Users/username/<your_working_dir>/

```
## Example Jenkins Pipeline Snippet:
```
environment {
        PROJECT_NAME='simple-maven-project-with-tests-pipeline' 
        PROJECT_VERSION_NAME='2.3'
    }
    
stage('Generate Report') {
            steps {
                git branch: 'main', credentialsId: 'github with latest token', url: 'https://github.com/evansa-synopsys/blackduck-get-reports.git'
                sh "ls -lhrt"
                sh "pwd"
                sh "virtualenv venv --distribute"
                sh ". venv/bin/activate" 
                sh "python3 -m pip install blackduck"
                sh "python3 -m pip install -r requirements.txt"
                sh '''python3 get_report.py \\
                -u https://<bd_url> \\
                -t <Your token> \\
                -p ${PROJECT_NAME} \\
                -pv ${PROJECT_VERSION_NAME} \\
                -o /var/lib/jenkins/ \\
                -i -v -w 25'''
            }
        }

```

## Sample Console Output
```
MainThread:2022-12-13 22:49:22,342:INFO:Successfully downloaded /var/lib/jenkins/vulnerability-status-report-simple-maven-project-with-tests-pipeline-2.3_2022-12-13_224857.zip
```

## Basic Troubleshooting Steps
```
1. Enable DEBUG logging by adding -v when running the script
2. Analyze DEBUG logging statements to gain insight into any errors that arise. 
```