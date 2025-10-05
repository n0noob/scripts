#!/usr/bin/env python3

import os
import sys
import logging
import shutil

SCRIPTS_TO_INSTALL = [
    "./run-after/run-after",
    "./utilities/mpv-delete",
    "./dotmgr/dotmgr"
]

INSTALL_DIR = '/usr/local/bin'

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("setup")

def is_python_script(file_path):
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

def ensure_executable(file_path):
    """Ensure the script is executable."""
    if not os.access(file_path, os.X_OK):
        os.chmod(file_path, 0o755)
        logger.info(f"Made {os.path.basename(file_path)} executable")

def needs_update(source_path, dest_path):
    """Check if source is newer than destination file."""
    if not os.path.exists(dest_path):
        return True
        
    try:
        source_mtime = os.path.getmtime(source_path)
        dest_mtime = os.path.getmtime(dest_path)
        return source_mtime > dest_mtime
    except OSError as e:
        logger.error(f"Error checking modification times: {str(e)}")
        return True

def install_script(source_path, dest_path):
    """Copy script and set permissions."""
    try:
        shutil.copy2(source_path, dest_path)
        ensure_executable(dest_path)
        return True
    except Exception as e:
        logger.error(f"Failed to install {os.path.basename(source_path)}: {str(e)}")
        return False

def main():
    # Root check
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Use sudo.")
        sys.exit(1)

    if not os.path.exists(INSTALL_DIR):
        logger.info(f"Default script installation directory does not exist: {INSTALL_DIR}")

    # Process specified scripts
    installed = []
    updated = []
    skipped = []
    for script in SCRIPTS_TO_INSTALL:
        script_path = os.path.abspath(script)
        filename = os.path.basename(script_path)
        
        if not os.path.isfile(script_path):
            logger.warning(f"Script not found: {script_path}")
            skipped.append(filename)
            continue
            
        if not is_python_script(script_path):
            skipped.append(filename)
            continue

        dest_path = os.path.join(INSTALL_DIR, filename)

        # Handle existing installations
        if os.path.exists(dest_path):
            if os.path.islink(dest_path):
                logger.info(f"Replacing symlink with file copy: {filename}")
                os.unlink(dest_path)
                
            if os.path.isfile(dest_path):
                if needs_update(script_path, dest_path):
                    if install_script(script_path, dest_path):
                        updated.append(filename)
                        logger.info(f"Updated: {filename}")
                    else:
                        skipped.append(filename)
                else:
                    skipped.append(filename)
                    logger.debug(f"Already up-to-date: {filename}")
            else:
                logger.warning(f"Skipping {filename}: Path exists but is not a file")
                skipped.append(filename)
        else:
            if install_script(script_path, dest_path):
                installed.append(filename)
                logger.info(f"Installed: {filename}")
            else:
                skipped.append(filename)

    # Summary
    logger.info("Installation Summary:")
    if installed:
        logger.debug("Installed items: " + ", ".join(installed))
    if updated:
        logger.debug("Updated items: " + ", ".join(updated))
    if skipped:
        logger.debug("Skipped items: " + ", ".join(skipped))

if __name__ == '__main__':
    main()