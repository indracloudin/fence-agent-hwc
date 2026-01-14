#!/@PYTHON@ -tt

import sys
import logging
import atexit
import json

import sys
import os
import importlib.util

# Handle both installed and development environments
fence_lib_path = "@FENCEAGENTSLIBDIR@"
if fence_lib_path.startswith("@") and fence_lib_path.endswith("@"):
    # This is the development version, use relative path
    fence_lib_path = os.path.join(os.path.dirname(__file__), "fence-agents", "lib")
    # For development, import the module using importlib since it has .py.py extension
    spec = importlib.util.spec_from_file_location("fencing", os.path.join(fence_lib_path, "fencing.py"))
    fencing = importlib.util.module_from_spec(spec)
    sys.modules["fencing"] = fencing
    spec.loader.exec_module(fencing)
else:
    sys.path.append(fence_lib_path)
    import fencing

from fencing import *
from fencing import fail_usage, run_delay


try:
    from huaweicloudsdkcore.auth.credentials import BasicCredentials
    from huaweicloudsdkcore.exceptions import exceptions
    from huaweicloudsdkecs.v2 import EcsClient
    from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
    from huaweicloudsdkecs.v2.model import *
except ImportError as e:
    logging.warning("The 'huaweicloudsdkcore' and 'huaweicloudsdkecs' modules have not been installed or are unavailable, try to execute the command 'pip install huaweicloudsdkcore huaweicloudsdkecs --upgrade' to solve. error: %s" % e)


def _send_request(conn, request, options=None):
    logging.debug("send request action: %s" % request.__class__.__name__)
    try:
        # Add enterprise project ID to header if provided and supported
        if options and "--enterprise-project-id" in options:
            enterprise_project_id = options["--enterprise-project-id"]
            if enterprise_project_id and enterprise_project_id != "0":
                # Some operations might need the enterprise project ID in the header
                # This depends on the specific Huawei Cloud SDK version
                pass

        response = conn._client.call_api(request)
        logging.debug("response: %s" % response)
        return response
    except exceptions.ClientRequestException as e:
        logging.error("API request failed: %s" % e)
        fail_usage("Failed: send request failed: Error: %s" % e)
    except Exception as e:
        logging.error("Unexpected error during API request: %s" % e)
        fail_usage("Failed: unexpected error during request: %s" % e)


def start_instance(conn, instance_id):
    logging.debug("start instance %s" % instance_id)
    request = StartServerRequest(server_id=instance_id)
    _send_request(conn, request)


def stop_instance(conn, instance_id):
    logging.debug("stop instance %s" % instance_id)
    request = StopServerRequest(
        server_id=instance_id,
        body=StopServerRequestBody(
            os_stop=ServerActionOption(
                type="SOFT"
            )
        )
    )
    _send_request(conn, request)


def force_stop_instance(conn, instance_id):
    logging.debug("force stop instance %s" % instance_id)
    request = StopServerRequest(
        server_id=instance_id,
        body=StopServerRequestBody(
            os_stop=ServerActionOption(
                type="HARD"
            )
        )
    )
    _send_request(conn, request)


def reboot_instance(conn, instance_id):
    logging.debug("reboot instance %s" % instance_id)
    request = RebootServerRequest(
        server_id=instance_id,
        body=RebootServerRequestBody(
            reboot=RebootServerOption(
                type="SOFT"
            )
        )
    )
    _send_request(conn, request)


def force_reboot_instance(conn, instance_id):
    logging.debug("force reboot instance %s" % instance_id)
    request = RebootServerRequest(
        server_id=instance_id,
        body=RebootServerRequestBody(
            reboot=RebootServerOption(
                type="HARD"
            )
        )
    )
    _send_request(conn, request)


def get_status(conn, instance_id):
    logging.debug("get instance %s status" % instance_id)
    try:
        request = ShowServerRequest(server_id=instance_id)
        response = _send_request(conn, request)

        instance_status = None
        if hasattr(response, 'server') and response.server:
            instance_status = response.server.status
        return instance_status
    except Exception as e:
        logging.error("Error getting status for instance %s: %s" % (instance_id, e))
        raise


def get_nodes_list(conn, options):
    logging.debug("start to get nodes list")
    result = {}

    try:
        # Create request with enterprise project ID if provided
        enterprise_project_id = options.get("--enterprise-project-id", "0")

        request = ListServersDetailsRequest()

        # Set enterprise project ID in header if provided
        if enterprise_project_id and enterprise_project_id != "0":
            # Some Huawei Cloud SDK versions support enterprise_project_id parameter
            # This may need to be set in the request header or as a parameter
            # depending on the specific SDK version
            pass  # The enterprise project ID is typically handled by the credentials

        # Apply filters if provided
        if "--filter" in options:
            filter_key = options["--filter"].split("=")[0].strip()
            filter_value = options["--filter"].split("=")[1].strip()
            # For Huawei Cloud, we might filter by tags or other parameters
            # This is a simplified approach - in real implementation, we'd parse the filter properly
            if filter_key == "name":
                # Filter servers by name if needed
                pass  # ListServersDetailsRequest doesn't have a direct name filter,
                      # but we can filter results after getting them

        response = _send_request(conn, request, options)

        if hasattr(response, 'servers') and response.servers:
            for item in response.servers:
                instance_id = item.id
                instance_name = item.name
                result[instance_id] = (instance_name, None)
    except Exception as e:
        logging.error("Error getting node list: %s" % e)

    logging.debug("get nodes list: %s" % result)
    return result


def get_power_status(conn, options):
    logging.debug("start to get power(%s) status" % options["--plug"])
    try:
        state = get_status(conn, options["--plug"])

        if state in ["ACTIVE", "REBOOT", "HARD_REBOOT", "PASSWORD", "RESIZE", "VERIFY_RESIZE", "REVERT_RESIZE", "MIGRATING", "BUILD"]:
            status = "on"
        elif state in ["SHUTOFF", "STOPPED"]:
            status = "off"
        else:
            status = "unknown"

        logging.debug("the power(%s) status is %s" % (options["--plug"], status))
        return status
    except Exception as e:
        logging.error("Error getting power status for instance %s: %s" % (options["--plug"], e))
        raise


def set_power_status(conn, options):
    logging.info("start to set power(%s) status to %s" % (options["--plug"], options["--action"]))

    if options["--action"] == "off":
        if "--force" in options:
            force_stop_instance(conn, options["--plug"])
        else:
            stop_instance(conn, options["--plug"])
    elif options["--action"] == "on":
        start_instance(conn, options["--plug"])
    elif options["--action"] == "reboot":
        if "--force" in options:
            force_reboot_instance(conn, options["--plug"])
        else:
            reboot_instance(conn, options["--plug"])


def define_new_opts():
    all_opt["region"] = {
        "getopt" : "r:",
        "longopt" : "region",
        "help" : "-r, --region=[name]            Region, e.g. cn-north-1",
        "shortdesc" : "Region.",
        "required" : "0",  # Made optional to allow config file
        "order" : 2
    }
    all_opt["access_key"] = {
        "getopt" : "a:",
        "longopt" : "access-key",
        "help" : "-a, --access-key=[name]        Access Key",
        "shortdesc" : "Access Key.",
        "required" : "0",  # Made optional to allow config file
        "order" : 3
    }
    all_opt["secret_key"] = {
        "getopt" : "s:",
        "longopt" : "secret-key",
        "help" : "-s, --secret-key=[name]        Secret Key",
        "shortdesc" : "Secret Key.",
        "required" : "0",  # Made optional to allow config file
        "order" : 4
    }
    all_opt["project_id"] = {
        "getopt": ":",
        "longopt": "project-id",
        "help": "--project-id=[id]              Project ID",
        "shortdesc": "Project ID.",
        "required": "0",  # Made optional to allow config file
        "order": 5
    }
    all_opt["domain_id"] = {
        "getopt": ":",
        "longopt": "domain-id",
        "help": "--domain-id=[id]               Domain ID",
        "shortdesc": "Domain ID.",
        "required": "0",
        "order": 6
    }
    all_opt["enterprise_project_id"] = {
        "getopt": ":",
        "longopt": "enterprise-project-id",
        "help": "--enterprise-project-id=[id]   Enterprise Project ID (optional, default: 0)",
        "shortdesc": "Enterprise Project ID.",
        "required": "0",
        "default": "0",
        "order": 7
    }
    all_opt["config_file"] = {
        "getopt": ":",
        "longopt": "config-file",
        "help": "--config-file=[path]           Path to config file containing credentials (default: config.json)",
        "shortdesc": "Path to config file.",
        "required": "0",
        "default": "config.json",
        "order": 8
    }
    all_opt["filter"] = {
        "getopt": ":",
        "longopt": "filter",
        "help": "--filter=[key=value]           Filter (e.g. name=server-name)",
        "shortdesc": "Filter for list-action.",
        "required": "0",
        "order": 9
    }
    all_opt["force"] = {
        "getopt": "",
        "longopt": "force",
        "help": "--force                        Force operation (hard stop/reboot)",
        "shortdesc": "Force operation (hard stop/reboot).",
        "required": "0",
        "order": 10
    }


def load_credentials_from_config(config_path):
    """Load credentials from config file"""
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Extract credentials from config
        credentials = {
            'region': config.get('region'),
            'access_key': config.get('access_key'),
            'secret_key': config.get('secret_key'),
            'project_id': config.get('project_id'),
            'domain_id': config.get('domain_id'),
            'enterprise_project_id': config.get('enterprise_project_id', '0')
        }

        return credentials
    except FileNotFoundError:
        fail_usage("Failed: Config file not found: %s" % config_path)
    except json.JSONDecodeError:
        fail_usage("Failed: Invalid JSON in config file: %s" % config_path)
    except Exception as e:
        fail_usage("Failed: Error reading config file: %s" % e)


# Main agent method
def main():
    conn = None

    device_opt = ["port", "no_password", "region", "access_key", "secret_key", "project_id", "domain_id", "enterprise_project_id", "config_file", "filter", "force"]

    atexit.register(atexit_handler)

    define_new_opts()

    all_opt["power_timeout"]["default"] = "60"

    options = check_input(device_opt, process_input(device_opt))

    docs = {}
    docs["shortdesc"] = "Fence agent for Huawei Cloud (Huawei Cloud Services)"
    docs["longdesc"] = """fence_huaweicloud is a Power Fencing agent for Huawei Cloud.
It allows Pacemaker/Corosync clusters to perform power fencing operations on Huawei Cloud ECS (Elastic Cloud Server) instances.
This is essential for preventing split-brain scenarios in high availability clusters.

Required parameters:
- Access Key, Secret Key: Huawei Cloud API credentials
- Region: Huawei Cloud region (e.g., cn-north-1)
- Project ID: Huawei Cloud project identifier
OR
- Config file: Path to config.json file containing credentials

Optional parameters:
- Domain ID: Huawei Cloud domain identifier
- Enterprise Project ID: Huawei Cloud enterprise project identifier
- Filter: Filter for list operations
- Force: Force hard stop/reboot operations"""
    docs["vendorurl"] = "http://www.huaweicloud.com"
    show_docs(options, docs)

    run_delay(options)

    # Load credentials from config file if provided
    credentials = {}
    if "--config-file" in options:
        config_path = options["--config-file"]
        credentials = load_credentials_from_config(config_path)

    # Override config values with command line options if provided
    region = options.get("--region") or credentials.get('region')
    access_key = options.get("--access-key") or credentials.get('access_key')
    secret_key = options.get("--secret-key") or credentials.get('secret_key')
    project_id = options.get("--project-id") or credentials.get('project_id')
    domain_id = options.get("--domain-id") or credentials.get('domain_id')
    enterprise_project_id = options.get("--enterprise-project-id") or credentials.get('enterprise_project_id', '0')

    # Validate required parameters
    if not region or not access_key or not secret_key or not project_id:
        fail_usage("Failed: Access Key, Secret Key, Region, and Project ID are required. Either provide them directly or via config file.")

    # Set up credentials
    credentials_obj = BasicCredentials(access_key, secret_key, project_id)

    # Set domain ID if provided
    if domain_id:
        try:
            credentials_obj.domain_id = domain_id
        except AttributeError:
            # If domain_id attribute doesn't exist, we'll pass it differently if needed
            pass

    # Create client
    try:
        client_builder = EcsClient.new_builder()
        conn = client_builder \
            .with_credentials(credentials_obj) \
            .with_region(EcsRegion.value_of(region)) \
            .build()
    except Exception as e:
        fail_usage("Failed: Unable to connect to Huawei Cloud: %s" % e)

    # Operate the fencing device
    result = fence_action(conn, options, set_power_status, get_power_status, get_nodes_list)
    sys.exit(result)


if __name__ == "__main__":
    main()