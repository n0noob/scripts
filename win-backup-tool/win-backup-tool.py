import logging
import shutil
import sys
import subprocess
import ctypes
import os
import platform
import argparse
from datetime import datetime
from pathlib import Path
import winreg
import msvcrt

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger('BackupTool')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Windows Backup Tool')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate backup without actual file operations')
    return parser.parse_args()

def is_admin():
    """Check if running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    """Reload with admin privileges"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def get_windows_version():
    """Get Windows version in 24H2 format"""
    build_to_version = {
        '22000': '21H2',
        '22621': '22H2',
        '22631': '23H2',
        '26100': '24H2'
    }
    build_number = platform.version().split('.')[-1]
    return build_to_version.get(build_number, f"build{build_number}")

def is_junction(path: Path) -> bool:
    """Check if a path is a junction point"""
    try:
        return bool(os.stat(path).st_file_attributes & os.FILE_ATTRIBUTE_REPARSE_POINT)
    except (FileNotFoundError, AttributeError):
        return False

def copy_directory(src: Path, dst: Path) -> None:
    """Custom directory copier that skips junctions and shortcuts"""
    logger.info(f"Copying directory: {src}")
    if not dst.exists():
        dst.mkdir(parents=True, exist_ok=True)
    
    for item in src.iterdir():
        dest_item = dst / item.name
        if item.is_dir():
            if is_junction(item):
                logger.warning(f"Skipping junction point: {item}")
                continue
            logger.info(f"Copying subdirectory: {item}")
            copy_directory(item, dest_item)
        else:
            # Skip shortcut files
            if item.suffix.lower() == '.lnk':
                logger.info(f"Skipping shortcut file: {item}")
                continue
            logger.info(f"Copying file: {item}")
            shutil.copy2(item, dest_item)

def generate_tree(directory: Path, depth: int = 1, prefix: str = '') -> str:
    """Generate a tree structure string for the given directory"""
    if depth < 0 or not directory.is_dir():
        return ''
    
    tree = []
    try:
        entries = sorted(directory.iterdir(), key=lambda e: e.name)
    except PermissionError:
        return " [Permission Denied]"
    
    for index, entry in enumerate(entries):
        if index >= 5:
            tree.append(f"{prefix}└── ...")
            break
            
        connector = '├── ' if index < len(entries) - 1 else '└── '
        if entry.is_dir():
            tree.append(f"{prefix}{connector}{entry.name}/")
            if depth > 0:
                tree.append(generate_tree(entry, depth-1, prefix + ('│   ' if index < len(entries)-1 else '    ')))
        else:
            tree.append(f"{prefix}{connector}{entry.name}")
    
    return '\n'.join(tree)

def get_backup_dir(args) -> Path:
    """Get backup directory from user with formatted name"""
    default_base = Path("D:/WindowsBackup")
    user_input = input(f"\nEnter backup base directory [{default_base}]: ").strip()
    base_dir = Path(user_input) if user_input else default_base

    # Create formatted directory name
    computer_name = os.environ['COMPUTERNAME']
    win_version = get_windows_version()
    timestamp = datetime.now().strftime("[%Y-%m-%d-%H-%M-%S]")
    dir_name = f"{computer_name}-win{win_version}-backup-{timestamp}"
    
    backup_dir = base_dir / dir_name
    
    if not args.dry_run:
        try:
            backup_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            logger.error("Backup directory already exists!")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to create backup directory: {str(e)}")
            sys.exit(1)
    else:
        logger.info(f"Would create directory: {backup_dir}")
    
    return backup_dir

def select_profiles() -> list[Path]:
    """Show available user profiles and return selected ones"""
    users_dir = Path("C:/Users")
    profiles = [p for p in users_dir.iterdir() if p.is_dir() and p.name not in ['Public', 'Default']]
    
    print("\nAvailable user profiles:")
    for i, profile in enumerate(profiles, 1):
        print(f"  {i}. {profile.name}")
    
    selections = input("\nEnter profile numbers to back up (space-separated) or 'all': ").strip()
    if selections.lower() == 'all':
        return profiles
    
    selected = []
    for num in selections.split():
        try:
            index = int(num.strip()) - 1
            if 0 <= index < len(profiles):
                selected.append(profiles[index])
        except ValueError:
            continue
    return selected

def backup_core_directories(user_home: Path, backup_dir: Path, args) -> dict:
    """Backup mandatory directories for a user"""
    core_dirs = ['Documents', 'Desktop', 'Downloads', 'Pictures', 'Videos']
    logger.info(f"\nBacking up core directories for {user_home.name}...")
    summary = {'total': 0, 'skipped': 0, 'failed': 0}
    
    for dir_name in core_dirs:
        source = user_home / dir_name
        dest = backup_dir / dir_name
        
        if not source.exists():
            logger.warning(f"Skipping non-existent: {dir_name}")
            summary['skipped'] += 1
            continue
            
        try:
            if args.dry_run:
                logger.info(f"[DRY RUN] Would copy: {dir_name}")
                summary['total'] += 1
            else:
                if not dest.exists():
                    copy_directory(source, dest)
                    logger.info(f"Backed up: {dir_name}")
                    summary['total'] += 1
                else:
                    logger.warning(f"Skipping existing: {dir_name}")
                    summary['skipped'] += 1
        except Exception as e:
            logger.error(f"Failed to backup {dir_name}: {str(e)}")
            summary['failed'] += 1
    
    return summary

def process_user_directory(user_home: Path, backup_dir: Path, args) -> dict:
    """Process additional directories for a user with interactive prompts"""
    logger.info(f"\nProcessing additional directories for {user_home.name}:")
    core_dirs = ['Documents', 'Desktop', 'Downloads', 'Pictures', 'Videos']
    summary = {'total': 0, 'skipped': 0, 'failed': 0}
    
    for child in user_home.iterdir():
        if child.is_dir() and child.name not in core_dirs:
            print(f"\nDirectory: {child.name}")
            print(generate_tree(child, depth=1))
            
            choice = input(f"Back up '{child.name}'? [y/N]: ").lower().strip()
            if choice == 'y':
                dest = backup_dir / child.name
                try:
                    if args.dry_run:
                        logger.info(f"[DRY RUN] Would copy: {child.name}")
                        summary['total'] += 1
                    else:
                        copy_directory(child, dest)
                        logger.info(f"Backed up: {child.name}")
                        summary['total'] += 1
                except Exception as e:
                    logger.error(f"Failed to backup {child.name}: {str(e)}")
                    summary['failed'] += 1
            else:
                summary['skipped'] += 1
    
    return summary

def save_software_list(backup_dir: Path, args) -> None:
    """Save software list to text file (names only)"""
    logger.info("\nCollecting installed software...")
    software_list = []
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for hive, path in registry_paths:
        try:
            with winreg.OpenKey(hive, path) as key:
                index = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, index)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                software_list.append(winreg.QueryValueEx(subkey, "DisplayName")[0])
                            except OSError:
                                pass
                        index += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue

    # Sort software list alphabetically
    software_list = sorted(software_list, key=lambda x: x.lower())

    output_file = backup_dir / 'installed-softwares.txt'
    if args.dry_run:
        logger.info(f"[DRY RUN] Would save {len(software_list)} software entries to {output_file.name}")
    else:
        try:
            with output_file.open('w', encoding='utf-8') as f:
                for name in software_list:
                    f.write(f"{name}\n")
            logger.info(f"Saved software list to: {output_file.name}")
        except Exception as e:
            logger.error(f"Failed to save software list: {str(e)}")

def check_chocolatey(backup_dir: Path, args) -> None:
    """Check for Chocolatey and save installed packages (names only)"""
    try:
        result = subprocess.run(['choco', '--version'], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        output_file = backup_dir / 'choco-installed-softwares.txt'
        
        if args.dry_run:
            logger.info(f"[DRY RUN] Would save Chocolatey package list to {output_file.name}")
            return
            
        logger.info("\nChocolatey detected, saving package list...")
        result = subprocess.run(['choco', 'list', '--local-only', '--limit-output'],
                              capture_output=True,
                              text=True,
                              check=True)
        
        # Extract and sort package names
        packages = sorted(
            [line.split('|')[0] for line in result.stdout.splitlines()],
            key=lambda x: x.lower()
        )
        
        with output_file.open('w', encoding='utf-8') as f:
            f.write('\n'.join(packages))
            
        logger.info(f"Saved Chocolatey packages to: {output_file.name}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Chocolatey not found, skipping package list")

def main():
    args = parse_arguments()
    
    # Elevate privileges if not admin
    if not is_admin():
        print("Admin privileges required - requesting elevation...")
        elevate()

    try:
        backup_dir = get_backup_dir(args)
        selected_profiles = select_profiles()
        total_summary = {
            'directories': 0,
            'software_entries': 0,
            'choco_packages': 0,
            'users': len(selected_profiles)
        }
        
        if not selected_profiles:
            logger.error("No profiles selected!")
            sys.exit(1)
            
        for profile in selected_profiles:
            user_backup_dir = backup_dir / profile.name
            if not args.dry_run:
                user_backup_dir.mkdir(exist_ok=True)
            
            logger.info(f"\n{'=' * 50}")
            logger.info(f"Processing profile: {profile.name}")
            logger.info(f"{'=' * 50}")
            
            core_summary = backup_core_directories(profile, user_backup_dir, args)
            additional_summary = process_user_directory(profile, user_backup_dir, args)
            
            total_summary['directories'] += core_summary['total'] + additional_summary['total']
            
            # Add pause after each user
            if not args.dry_run:
                print(f"\nUser '{profile.name}' backup completed.", end=' ')
            else:
                print(f"\nUser '{profile.name}' dry-run completed.", end=' ')
            input("Press Enter to continue...")
        
        save_software_list(backup_dir, args)
        check_chocolatey(backup_dir, args)
        
        # Dry-run summary
        if args.dry_run:
            print("\n=== DRY RUN SUMMARY ===")
            print(f"Would create backup structure in: {backup_dir}")
            print(f"Would process {total_summary['users']} user profiles")
            print(f"Would copy {total_summary['directories']} directories")
            print("Software lists would be generated")
            print("Chocolatey packages would be listed if installed")
        else:
            logger.info("\nBackup completed successfully!")
            print(f"\nBackup directory: {backup_dir}")

        # Final pause
        print("\nBackup process complete. Press Enter to exit...")
        input()
        
    except Exception as e:
        logger.critical(f"\nBackup failed: {str(e)}")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()