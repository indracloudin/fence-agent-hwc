#!/bin/bash

# Installation script for Huawei Cloud fence agent
# Run this script as root to install the fence agent

set -e  # Exit on any error

# Function to print colored output
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_info "Starting Huawei Cloud fence agent installation..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Check if Python is available
if ! command_exists python3 && ! command_exists python; then
    print_error "Python is not installed. Please install Python 2.7 or 3.x"
    exit 1
fi

# Determine which Python command to use
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
fi

print_info "Using $PYTHON_CMD for installation"

# Check if fence-agents directory exists, otherwise try common locations
FENCE_DIR=""
for dir in "/usr/sbin" "/sbin" "/usr/libexec/fence" "/usr/lib/fence" "/usr/share/fence"; do
    if [ -d "$dir" ]; then
        FENCE_DIR="$dir"
        break
    fi
done

if [ -z "$FENCE_DIR" ]; then
    print_warning "Could not find standard fence agents directory. Creating in /usr/sbin"
    FENCE_DIR="/usr/sbin"
    mkdir -p "$FENCE_DIR"
fi

print_info "Installing to $FENCE_DIR..."

# Copy the fence agent
AGENT_FILE="fence_huaweicloud.py"
AGENT_PATH="$FENCE_DIR/$AGENT_FILE"

# Check if file already exists
if [ -f "$AGENT_PATH" ]; then
    print_warning "File $AGENT_PATH already exists. Creating backup..."
    cp "$AGENT_PATH" "$AGENT_PATH.backup.$(date +%Y%m%d_%H%M%S)"
    print_info "Backup created: $AGENT_PATH.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy the agent file
cp "$AGENT_FILE" "$AGENT_PATH"
chmod +x "$AGENT_PATH"

# Also copy the fence-agents lib directory if it exists
if [ -d "fence-agents" ]; then
    LIB_DIR="/usr/share/fence-agents/lib"
    mkdir -p "$LIB_DIR"
    cp -r fence-agents/lib/* "$LIB_DIR/" 2>/dev/null || true
    print_info "Fence agents library copied to $LIB_DIR"
fi

# Test the installation
print_info "Testing the fence agent..."
if "$AGENT_PATH" -o metadata >/dev/null 2>&1; then
    print_success "Installation test successful!"
    print_success "Fence agent installed to: $AGENT_PATH"
else
    print_error "Installation test failed - fence agent not working properly"
    exit 1
fi

# Check if Python dependencies are available
print_info "Checking Python dependencies..."

# List of required packages
REQUIRED_PKGS=("huaweicloudsdkcore" "huaweicloudsdkecs")

MISSING_PKGS=()
for pkg in "${REQUIRED_PKGS[@]}"; do
    if ! $PYTHON_CMD -c "import $pkg" 2>/dev/null; then
        MISSING_PKGS+=("$pkg")
    fi
done

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    print_warning "Missing Python packages: ${MISSING_PKGS[*]}"

    if command_exists pip || command_exists pip3; then
        PIP_CMD="pip"
        if command_exists pip3; then
            PIP_CMD="pip3"
        fi

        print_info "Installing Huawei Cloud Python SDK dependencies..."
        if $PIP_CMD install "${REQUIRED_PKGS[@]}" 2>/dev/null; then
            print_success "Dependencies installed successfully"
        else
            print_error "Failed to install dependencies automatically"
            print_warning "Install manually with: $PIP_CMD install ${REQUIRED_PKGS[*]}"
        fi
    else
        print_error "pip is not available. Please install Python dependencies manually:"
        print_warning "$PYTHON_CMD -m ensurepip (if needed)"
        print_warning "pip install ${REQUIRED_PKGS[*]}"
    fi
else
    print_success "All required Python packages are already installed"
fi

# Check if Pacemaker is installed
if command_exists pcs; then
    print_info "Pacemaker tools detected. Fence agent is ready for use with Pacemaker."
else
    print_warning "Pacemaker tools (pcs) not detected. Install if you plan to use with Pacemaker/Corosync."
fi

# Create a sample config file if it doesn't exist
if [ ! -f "config.json" ]; then
    print_info "Creating sample config.json file..."
    cat > config.json << 'EOF'
{
  "region": "cn-north-1",
  "access_key": "your_access_key_here",
  "secret_key": "your_secret_key_here",
  "project_id": "your_project_id_here",
  "domain_id": "your_domain_id_here",
  "enterprise_project_id": "0"
}
EOF
    print_info "Sample config.json created. Update with your actual credentials."
fi

print_success ""
print_success "Installation complete!"
print_success ""

print_info "Configuration options:"
print_info "- Direct parameters: provide access_key, secret_key, region, project_id directly"
print_info "- Config file: create config.json with credentials and use --config-file parameter"
print_info ""

print_info "Basic usage examples:"
print_info "  Check status: $AGENT_PATH -a <ACCESS_KEY> -s <SECRET_KEY> -r <REGION> --project-id <PROJECT_ID> -n <INSTANCE_ID> -o status"
print_info "  Using config: $AGENT_PATH --config-file /path/to/config.json -n <INSTANCE_ID> -o status"
print_info ""

print_info "To configure in Pacemaker, use:"
print_info "pcs stonith create <resource_name> fence_huaweicloud \\"
print_info "    access_key=<ACCESS_KEY> \\"
print_info "    secret_key=<SECRET_KEY> \\"
print_info "    region=<REGION> \\"
print_info "    project_id=<PROJECT_ID> \\"
print_info "    ip=<INSTANCE_ID> \\"
print_info "    pcmk_host_list=<NODE_NAMES>"
print_info ""

print_info "Or using config file:"
print_info "pcs stonith create <resource_name> fence_huaweicloud \\"
print_info "    config_file=/path/to/config.json \\"
print_info "    ip=<INSTANCE_ID> \\"
print_info "    pcmk_host_list=<NODE_NAMES>"
print_info ""

print_info "For more information, run: $AGENT_PATH -o metadata"
print_info "Documentation: $AGENT_PATH -o help"