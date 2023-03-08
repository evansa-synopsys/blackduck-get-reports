import argparse
import logging
import os.path
import sys
import time

from helper import MyHub

parser = argparse.ArgumentParser("A program that will create and download Version Vulnerability Status Report for a specified project "
                                 "version to a specified path on the system.")

parser.add_argument('-u', '--source-hub-url', required=True, help="Source Black Duck Hub URL")
parser.add_argument("-t", "--source-api-token", required=True, help="Source Black Duck Api token")
parser.add_argument("-i", "--insecure", action="store_true", help="Supress ssl warnings, default is false")
parser.add_argument("-v", "--verbose", action="store_true", help='Turn on request DEBUG logging')
parser.add_argument("-p", "--project", required=True, help="Specify a project")
parser.add_argument("-pv", "--project-version", required=True, help="Specify a project version")
parser.add_argument("-l", "--locale", default="en_US", help="Specify a report locale")
parser.add_argument("-rf", "--report-format", default="CSV", choices=["CSV", "JSON", "TEXT", "YAML", "RDF", "TAGVALUE"],
                    help="Report Format.")
parser.add_argument("-rt", "--report-type", default="VERSION_VULNERABILITY_STATUS",
                    choices=["VERSION_VULNERABILITY_STATUS", "SBOM"],help="Report Type")
parser.add_argument("-st", "--sbom-type", default="SPDX_22", choices=["SPDX_22", "CYCLONEDX_13", "CYCLONEDX_14"],
                    help="Sbom Type. Note: CYCLONEDX_* types are only compatible with report-format = JSON as of "
                         "2022.10.x.")
parser.add_argument("-m", "--max-retries", default=5, help="Maximum number of retries before time out, default = 5")
parser.add_argument("-w", "--wait-time", type=int, default=25, help="Time to sleep between retries (seconds).")
parser.add_argument("-o", "--out-put-file-path", help="Specify a filepath to write the downloaded zip, "
                                                      "if a valid path is not provided, the report will "
                                                      "be downloaded to the project root")

args = parser.parse_args()
logging.basicConfig(format='%(threadName)s:%(asctime)s:%(levelname)s:%(message)s', stream=sys.stderr,
                    level=logging.INFO)
if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("blackduck").setLevel(logging.DEBUG)

output_path = args.out_put_file_path
working_dir = ""
try:
    if os.path.exists(output_path):
        working_dir = os.path.abspath(output_path)
        logging.info(f"Will save report in {working_dir}")
    else:
        raise FileNotFoundError
except TypeError:
    logging.info(f"Output path not provided, will save report to the project root")
    pass
except FileNotFoundError:
    logging.info(f"Output path not valid, will save report to the project root")
    pass

source_hub = MyHub(args.source_hub_url, args.source_api_token, args.insecure)
project_info = source_hub.get_project_version_by_name(args.project, args.project_version)


def create_report():
    if args.report_type == "VERSION_VULNERABILITY_STATUS":
        version_id = source_hub.get_link(project_info, 'versionReport').split('/')[-2]
        endpoint = f"{source_hub.get_apibase()}/versions/{version_id}/vulnerability-status-reports"
        data = {
            "reportFormat": args.report_format,
            "projects": [],
            "locale": args.locale
        }
    elif args.report_type == "SBOM":
        endpoint = f"{project_info.get('_meta').get('href')}/sbom-reports"
        data = {
            "reportFormat": args.report_format,
            "reportType": args.report_type,
            "sbomType": args.sbom_type
        }
    response = source_hub.execute_post(endpoint, data)
    if response.status_code == 201:
        return response
    elif response.status_code == 412:
        logging.info(f"CYCLONEDX_* types are only compatible with report-format = JSON as of 2022.10.x. "
                     f"response code {response.status_code}")
        return response
    else:
        logging.debug(f"Error generating the report, response was {response.status_code} {response.text}")
        return response


def download_report(url):
    response_obj = source_hub.execute_get(url).json()

    if response_obj.get('status') == "IN_PROGRESS":
        logging.info(f"Report is not ready to download, status = {response_obj.get('status')}, waiting {args.wait_time}"
                     f" seconds to try again")
        return
    elif response_obj.get('status') == "FAILED":
        logging.info(f"Report creation failed on the server, please check that "
                     f"sbom-type and report format are compatible, exiting.")
        exit()

    download_url = source_hub.get_link(response_obj, 'download')
    file_download_response = source_hub.execute_get(download_url)
    download_filename = os.path.join(working_dir, response_obj.get('fileName')) if working_dir else response_obj.get(
        'fileName')
    with open(download_filename, "wb") as f:
        f.write(file_download_response.content)
        logging.info(f"Successfully downloaded {download_filename}")

    return file_download_response.status_code


report_url = create_report().links.get('self').get('url')
retries = args.max_retries
while retries:
    time.sleep(args.wait_time)
    if download_report(report_url) in [200, 201]:
        break
    else:
        retries -= 1
        continue
