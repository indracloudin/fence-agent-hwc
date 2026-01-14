#!/bin/bash

# Test script for Huawei Cloud fence agent
# This script tests the basic functionality of the fence agent

echo "Testing Huawei Cloud fence agent..."

# Check if the fence agent file exists
if [ ! -f "fence_huaweicloud.py" ]; then
    echo "Error: fence_huaweicloud.py not found!"
    exit 1
fi

echo "fence_huaweicloud.py exists."

# Make the fence agent executable
chmod +x fence_huaweicloud.py

# Test the help function to verify the agent is syntactically correct
echo "Testing help function..."
python fence_huaweicloud.py -h

if [ $? -eq 0 ]; then
    echo "Help function works correctly."
else
    echo "Error: Help function failed."
    exit 1
fi

# Test the metadata function
echo "Testing metadata function..."
python fence_huaweicloud.py -o metadata

if [ $? -eq 0 ]; then
    echo "Metadata function works correctly."
else
    echo "Error: Metadata function failed."
    exit 1
fi

echo "Basic tests passed. The fence agent appears to be syntactically correct."
echo ""
echo "To use the fence agent with Huawei Cloud, you will need:"
echo "- Access Key and Secret Key"
echo "- Region (e.g., cn-north-1)"
echo "- Project ID (if using project-based authentication)"
echo "- Instance ID for the target ECS instance"
echo ""
echo "Example usage:"
echo "python fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> -n <INSTANCE_ID> -o status"
echo "python fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> -n <INSTANCE_ID> -o off"
echo "python fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> -n <INSTANCE_ID> -o on"
echo "python fence_huaweicloud.py -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> -n <INSTANCE_ID> -o reboot"