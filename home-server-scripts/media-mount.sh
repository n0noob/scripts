#!/bin/bash

# Configuration Variables
#######################################################################
# Manual setup required
#######################################################################
#
# Create this directory manually and make default user own it:
# sudo mkdir /media && sudo chown $USER /media
#
readonly MOUNT_ROOT_PATH="/media/"
#######################################################################
readonly OMEGA_LOCATION="/run/media/anoop/OMEGA"

# Map of source directories to mount locations
declare -A MOUNT_MAP=(
    ["${OMEGA_LOCATION}/Movies/Hollywood"]="hollywood-movies"
    ["${OMEGA_LOCATION}/Movies/Bollywood"]="bollywood-movies"
)

######################################### Utility functions #########################################
# Check if directory does not exist and create it if required
check_and_create_dir() {
    local dir="$1"
    # Check if dir is a device file
    if [[ -b "$dir" || -c "$dir" ]]; then
        echo "$dir is a device file or character device, not a directory."
        return 0
    fi
    if [[ ! -d "$dir" ]]; then
        echo "Creating directory $dir..."
        mkdir -p "$dir"
    fi
}

# Check if podman is installed
check_podman() {
    if ! command -v podman &> /dev/null; then
        echo "Podman is not installed. Please install Podman to use this script."
        exit 1
    fi
}

# Check if mount given mount point is already mounted, mount if not
check_and_mount() {
    local target="$1"
    local mount_point="$2"
    check_and_create_dir "$mount_point"
    if mountpoint -q "$mount_point"; then
        echo "$mount_point is already mounted."
        return 1
    fi
    # Check if target doesn't exist
    if [[ ! -d "$target" ]]; then
        echo "Target directory $target does not exist or not available."
        return 1
    fi
    
    echo "Mounting $target to $mount_point..."
    sudo mount --bind -o ro "$target" "$mount_point"
}

# Check and unmount a directory
check_and_unmount() {
    local mount_point="$1"
    if mountpoint -q "$mount_point"; then
        echo "Unmounting $mount_point..."
        sudo umount "$mount_point"
    else
        echo "$mount_point is not mounted. Skipping..."
    fi
}

# Temporary
mount_internal_partitions() {
    echo "No internal partitions to mount"
}
######################################### End of utility functions #########################################

############################################## Main functions ##############################################
# Initialize required directories and mounts
initialize_system() {
    # Check if MOUNT_ROOT_PATH is accessible
    if [ ! -d "${MOUNT_ROOT_PATH}" ] || [ ! -r "${MOUNT_ROOT_PATH}" ]; then
        echo "Configured MOUNT_ROOT_PATH:${MOUNT_ROOT_PATH} either doesn't exist or is not readable"
        echo "Please create it manually using: sudo mkdir /media && sudo chown <user> /media"
        exit 1
    fi
    check_podman
    echo "Checking and creating required directories..."
}

# Mount directories based on the map
mount_directories() {
    echo "Mounting directories..."
    for SOURCE in "${!MOUNT_MAP[@]}"; do
        DESTINATION="${MOUNT_ROOT_PATH}${MOUNT_MAP[$SOURCE]}"
        check_and_mount "$SOURCE" "$DESTINATION"
    done
}

# Unmount directories based on the map
unmount_directories() {
    echo "Unmounting directories..."
    for SOURCE in "${!MOUNT_MAP[@]}"; do
        DESTINATION="${MOUNT_ROOT_PATH}${MOUNT_MAP[$SOURCE]}"
        check_and_unmount "$DESTINATION"
    done
}

mount() {
    initialize_system
    mount_internal_partitions
    mount_directories
}

unmount() {
    initialize_system
    unmount_directories
}

# Display usage information
show_help() {
    cat <<EOF
Usage: $0 {mount|unmount|help}

Commands:
  mount         Only mount directories without starting Jellyfin
  unmount       Only unmount directories without stopping Jellyfin
  help          Show this help message

EOF
}

# Main command dispatcher
main() {
    case "$1" in
        mount)
            mount
            ;;
        unmount)
            unmount
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo "Error: Unknown command '$1'"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with arguments
main "$@"
