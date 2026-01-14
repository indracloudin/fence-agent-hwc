# Huawei Cloud Fence Agent for Pacemaker/Corosync

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pacemaker Integration](#pacemaker-integration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)
- [Testing](#testing)
- [License](#license)

## Overview

The `fence_huaweicloud.py` fence agent enables Pacemaker/Corosync clusters to perform power fencing operations on Huawei Cloud ECS (Elastic Cloud Server) instances. This is essential for preventing split-brain scenarios in high availability clusters by allowing the cluster to remotely power off/on Huawei Cloud ECS instances as part of cluster failover operations.

## Features

- **Power Control**: Start, stop, reboot Huawei Cloud ECS instances
- **Enterprise Project ID Support**: Support for Huawei Cloud enterprise projects
- **Config File Support**: Store credentials securely in JSON configuration file
- **Pacemaker Integration**: Full compatibility with Pacemaker/Corosync clusters
- **Flexible Authentication**: Support for both direct parameters and config file credentials
- **Enhanced Error Handling**: Improved error messages and logging
- **Force Operations**: Support for hard stop/reboot operations

## Prerequisites

- Python 2.7 or Python 3.x
- Huawei Cloud account with appropriate permissions
- Huawei Cloud SDK for Python installed: `pip install huaweicloudsdkcore huaweicloudsdkecs`

## Installation

### Automatic Installation (Recommended)

Run the installation script with root privileges:

```bash
sudo ./install.sh
```

The installation script will:
- Copy the fence agent to the appropriate directory
- Create a backup if the file already exists
- Install required Python dependencies
- Test the installation
- Create a sample config.json file

### Manual Installation

1. Install Huawei Cloud Python SDK:

```bash
pip install huaweicloudsdkcore huaweicloudsdkecs
```

2. Install the fence agent:

```bash
# Common locations:
# RHEL/CentOS: /usr/sbin/
# SUSE: /usr/sbin/
# Ubuntu: /usr/sbin/

sudo cp fence_huaweicloud.py /usr/sbin/
sudo chmod +x /usr/sbin/fence_huaweicloud.py
```

## Configuration

### Huawei Cloud Requirements

1. Create an IAM user with ECS permissions
2. Obtain Access Key (AK) and Secret Key (SK)
3. Note your region (e.g., cn-north-1, cn-east-3)
4. Note your Project ID
5. (Optional) Note your Enterprise Project ID if using enterprise projects
6. (Optional) Create a config.json file with credentials for easier management

### Required Permissions

The Huawei Cloud user needs the following permissions:
- ECS FullAccess or specific ECS start/stop permissions
- If using filters, appropriate read permissions for ECS instances

### Configuration File (Recommended for Security)

You can create a config.json file to store your credentials securely:

```json
{
  "region": "cn-north-1",
  "access_key": "your_access_key_here",
  "secret_key": "your_secret_key_here",
  "project_id": "your_project_id_here",
  "domain_id": "your_domain_id_here",
  "enterprise_project_id": "0"
}
```

## Usage

### Command Line Testing

```bash
# Check status of an instance using direct parameters
fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> --project-id <PROJECT_ID> -n <INSTANCE_ID> -o status

# Check status using config file (more secure)
fence_huaweicloud.py --config-file /path/to/config.json -n <INSTANCE_ID> -o status

# Power off an instance
fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> --project-id <PROJECT_ID> -n <INSTANCE_ID> -o off

# Power on an instance using config file
fence_huaweicloud.py --config-file /path/to/config.json -n <INSTANCE_ID> -o on

# Reboot an instance
fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> --project-id <PROJECT_ID> -n <INSTANCE_ID> -o reboot

# List all instances with enterprise project ID
fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> --project-id <PROJECT_ID> --enterprise-project-id <ENTERPRISE_PROJECT_ID> -o list

# List instances using config file
fence_huaweicloud.py --config-file /path/to/config.json -o list

# Force reboot an instance
fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> --project-id <PROJECT_ID> -n <INSTANCE_ID> -o reboot --force

# View metadata and supported parameters
fence_huaweicloud.py -o metadata
```

### Parameters

- `-a, --access-key`: Huawei Cloud Access Key
- `-s, --secret-key`: Huawei Cloud Secret Key
- `-r, --region`: Huawei Cloud region (e.g., cn-north-1)
- `-n, --plug`: Instance ID to fence
- `-o, --action`: Action to perform (on, off, reboot, status, list, metadata)
- `--project-id`: Project ID (required if not using config file)
- `--domain-id`: Domain ID (optional)
- `--enterprise-project-id`: Enterprise Project ID (optional, default: 0)
- `--config-file`: Path to config file containing credentials (optional, default: config.json)
- `--filter`: Filter for list operations (optional)
- `--force`: Force operation (hard stop/reboot)

## Pacemaker Integration

### 1. Create the fence resource using direct parameters

```bash
pcs stonith create fence-huaweicloud fence_huaweicloud \
    pcmk_host_list="<node1>,<node2>" \
    access_key="<ACCESS_KEY>" \
    secret_key="<SECRET_KEY>" \
    region="<REGION>" \
    project_id="<PROJECT_ID>" \
    enterprise_project_id="<ENTERPRISE_PROJECT_ID>" \
    ip="<INSTANCE_ID_1>" \
    login="<INSTANCE_ID_1>" \
    identity_file="" \
    power_wait=5 \
    power_timeout=60 \
    shell_timeout=30 \
    verbose=True
```

### 2. Create the fence resource using config file (more secure)

```bash
pcs stonith create fence-huaweicloud fence_huaweicloud \
    pcmk_host_list="<node1>,<node2>" \
    config_file="/path/to/config.json" \
    ip="<INSTANCE_ID_1>" \
    login="<INSTANCE_ID_1>" \
    power_wait=5 \
    power_timeout=60 \
    shell_timeout=30 \
    verbose=True
```

### 3. For multiple nodes, use instance mapping

```bash
# Create separate fence resources for each node
pcs stonith create fence-huaweicloud-node1 fence_huaweicloud \
    pcmk_host_list="<NODE1_NAME>" \
    config_file="/path/to/config.json" \
    ip="<INSTANCE_ID_1>" \
    login="<INSTANCE_ID_1>"

pcs stonith create fence-huaweicloud-node2 fence_huaweicloud \
    pcmk_host_list="<NODE2_NAME>" \
    config_file="/path/to/config.json" \
    ip="<INSTANCE_ID_2>" \
    login="<INSTANCE_ID_2>"
```

## Security Considerations

- **Config File Approach**: Use config.json file to store credentials instead of passing them on the command line
- **File Permissions**: Ensure config.json has appropriate permissions (e.g., 600) to protect credentials
- **Dedicated IAM Users**: Use dedicated IAM users with minimal required permissions
- **Access Key Rotation**: Regularly rotate Access Keys
- **Network Security**: Use SSL/TLS for all communications

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Verify Access Key, Secret Key, and region are correct
2. **Permission Denied**: Ensure the IAM user has appropriate ECS permissions
3. **Instance Not Found**: Verify the instance ID is correct and in the specified region
4. **Missing Dependencies**: Ensure Huawei Cloud SDK packages are installed

### Enable Debugging

Add the `-D` option to write debug information to a file:

```bash
fence_huaweicloud.py -a <AK> -s <SK> -r <REGION> --project-id <PROJECT_ID> -n <INSTANCE_ID> -o status -D /tmp/fence_debug.log
```

### Check Installation

Verify the fence agent is working:

```bash
fence_huaweicloud.py -o metadata
```

## Advanced Features

### Enterprise Project ID Support
The fence agent supports Huawei Cloud enterprise projects, allowing you to manage resources across different enterprise projects.

### Config File Flexibility
- Command line parameters override config file values
- Config file supports all credential parameters
- Multiple config files can be used for different environments

### Force Operations
The fence agent supports both soft and hard power operations:
- Soft operations (default): Graceful shutdown/reboot
- Hard operations (with `--force`): Immediate power off/reboot

## Testing

The project includes comprehensive testing capabilities:

1. **Unit Testing**: Run the test suite to verify functionality:
```bash
python test_enhancements.py
```

2. **Installation Testing**: Use the provided test script:
```bash
./test_installation.sh
```

3. **Simple Testing**: Basic functionality test:
```bash
python simple_test.py
```

## Notes

- The fence agent uses Huawei Cloud's ECS API to control instances
- Operations may take several seconds to complete
- The agent supports both soft and hard power operations
- Instance status changes may have a delay in the Huawei Cloud console
- Using config files is recommended for production environments to avoid credential exposure

## License

This fence agent is provided as-is for use with Pacemaker/Corosync clusters.