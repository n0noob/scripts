#!/usr/bin/env python3

import os
import sys
import logging

SCRIPTS_TO_INSTALL = [
    "./run-after/run-after",
    "./utilities/mpv-delete"
]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("setup")

def is_python_script(file_path, logger):
    """Check if a file is a Python script using shebang line."""
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            if not first_line.startswith('#!'):
                logger.warning(f"Skipping {file_path}: Missing shebang")
                return False
            if 'python' not in first_line:
                logger.warning(f"Skipping {file_path}: Not a Python shebang")
                return False
            return True
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return False

def ensure_executable(file_path, logger):
    """Ensure the script is executable."""
    if not os.access(file_path, os.X_OK):
        os.chmod(file_path, 0o755)
        logger.info(f"Made {os.path.basename(file_path)} executable")

def main():
    target_dir = '/usr/local/bin'

    # Root check
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Use sudo.")
        logger.info("Try: sudo python3 install-scripts.py")
        sys.exit(1)

    # Ensure target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        logger.info(f"Created target directory: {target_dir}")

    # Process specified scripts
    installed = []
    skipped = []
    for script in SCRIPTS_TO_INSTALL:
        script_path = os.path.abspath(script)
        filename = os.path.basename(script_path)
        
        if not os.path.isfile(script_path):
            logger.warning(f"Script not found: {script_path}")
            skipped.append(filename)
            continue
            
        if not is_python_script(script_path, logger):
            skipped.append(filename)
            continue

        ensure_executable(script_path, logger)

        dest_path = os.path.join(target_dir, filename)
        source_abspath = os.path.abspath(script_path)

        # Handle existing files
        if os.path.exists(dest_path):
            if os.path.islink(dest_path):
                if os.path.realpath(dest_path) == source_abspath:
                    logger.debug(f"Already exists: {filename}")
                    skipped.append(filename)
                else:
                    logger.info(f"Updating symlink: {filename}")
                    os.unlink(dest_path)
                    os.symlink(source_abspath, dest_path)
                    installed.append(filename)
            else:
                logger.warning(f"Skipping {filename}: Existing regular file")
                skipped.append(filename)
        else:
            logger.info(f"Installing: {filename}")
            os.symlink(source_abspath, dest_path)
            installed.append(filename)

    # Summary
    logger.info("\nInstallation Summary:")
    logger.info(f"Successfully installed/updated: {len(installed)}")
    logger.info(f"Skipped: {len(skipped)}")
    
    if installed:
        logger.debug("Installed items: " + ", ".join(installed))
    if skipped:
        logger.debug("Skipped items: " + ", ".join(skipped))

if __name__ == '__main__':
    main()