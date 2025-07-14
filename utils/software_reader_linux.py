import platform
import subprocess
import re
import sys
from typing import Dict, List, Optional


def get_linux_software():
    """
    Get installed software on Linux using package managers.
    Returns a dictionary with software names and versions.
    """
    software_list = {}
    
    # Try different package managers
    package_managers = [
        ('dpkg', ['dpkg', '-l']),  # Debian/Ubuntu
        ('rpm', ['rpm', '-qa']),   # RedHat/CentOS/Fedora
        ('pacman', ['pacman', '-Q']),  # Arch Linux
        ('apk', ['apk', 'list', '--installed']),  # Alpine Linux
        ('zypper', ['zypper', 'se', '--installed-only']),  # openSUSE
        ('portage', ['qlist', '-I']),  # Gentoo
    ]
    
    for pm_name, command in package_managers:
        try:
            print(f"Trying {pm_name} package manager...")
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                if pm_name == 'dpkg':
                    for line in lines:
                        if line.startswith('ii'):
                            parts = line.split()
                            if len(parts) >= 3:
                                name = parts[1]
                                version = parts[2]
                                software_list[name] = version
                
                elif pm_name == 'rpm':
                    for line in lines:
                        if '-' in line:
                            # RPM format: name-version-release.arch
                            match = re.match(r'^(.+)-([^-]+)-([^-]+)\.(.+)$', line.strip())
                            if match:
                                name = match.group(1)
                                version = f"{match.group(2)}-{match.group(3)}"
                                software_list[name] = version
                
                elif pm_name == 'pacman':
                    for line in lines:
                        if ' ' in line:
                            parts = line.split(' ', 1)
                            if len(parts) == 2:
                                name = parts[0]
                                version = parts[1]
                                software_list[name] = version
                
                elif pm_name == 'apk':
                    for line in lines:
                        if line and not line.startswith('WARNING'):
                            parts = line.split(' ')
                            if len(parts) >= 1:
                                pkg_info = parts[0]
                                if '-' in pkg_info:
                                    name_version = pkg_info.split('-')
                                    name = '-'.join(name_version[:-2])
                                    version = '-'.join(name_version[-2:])
                                    if name:
                                        software_list[name] = version
                
                elif pm_name == 'zypper':
                    for line in lines:
                        if '|' in line and not line.startswith('S'):
                            parts = [p.strip() for p in line.split('|')]
                            if len(parts) >= 3:
                                name = parts[1]
                                version = parts[2]
                                if name and version:
                                    software_list[name] = version
                
                elif pm_name == 'portage':
                    for line in lines:
                        if '/' in line:
                            # Gentoo format: category/package-version
                            match = re.match(r'^(.+)/(.+)-([^-]+)$', line.strip())
                            if match:
                                category = match.group(1)
                                name = match.group(2)
                                version = match.group(3)
                                software_list[f"{category}/{name}"] = version
                
                break  # If one package manager works, don't try others
                
        except Exception as e:
            print(f"{pm_name} failed: {e}")
            continue
    
    return software_list


def get_snap_packages():
    """
    Get installed Snap packages.
    Returns a dictionary with package names and versions.
    """
    snap_packages = {}
    
    try:
        print("Scanning Snap packages...")
        result = subprocess.run(['snap', 'list'], capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1]
                        snap_packages[f"Snap: {name}"] = version
    except Exception:
        pass  # Snap might not be installed
    
    return snap_packages


def get_flatpak_packages():
    """
    Get installed Flatpak packages.
    Returns a dictionary with package names and versions.
    """
    flatpak_packages = {}
    
    try:
        print("Scanning Flatpak packages...")
        result = subprocess.run(['flatpak', 'list', '--app', '--columns=name,version'], capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        version = parts[1].strip()
                        if name and version:
                            flatpak_packages[f"Flatpak: {name}"] = version
    except Exception:
        pass  # Flatpak might not be installed
    
    return flatpak_packages


def get_python_packages():
    """
    Get installed Python packages and their versions.
    Returns a dictionary with package names and versions.
    """
    python_packages = {}
    
    try:
        print("Scanning Python packages...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[2:]:  # Skip header lines
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1]
                        python_packages[f"Python: {name}"] = version
    except Exception as e:
        print(f"Python packages scan failed: {e}")
    
    return python_packages


def get_installed_software():
    """
    Get all installed software on Linux.
    Returns a dictionary with software names and versions.
    """
    all_software = {}
    
    print("Detecting software on Linux...")
    
    # Get Linux package manager software
    all_software.update(get_linux_software())
    
    # Get Snap packages
    all_software.update(get_snap_packages())
    
    # Get Flatpak packages
    all_software.update(get_flatpak_packages())
    
    # Add Python packages
    all_software.update(get_python_packages())
    
    return all_software


def display_software_info():
    """
    Display all installed software in a simple format.
    """
    print("=" * 60)
    print("LINUX SOFTWARE & VERSIONS")
    print("=" * 60)
    
    software = get_installed_software()
    
    if not software:
        print("No software information could be retrieved.")
        return
    
    print(f"\n📦 Found {len(software)} software packages:\n")
    print("-" * 60)
    
    # Sort software alphabetically
    for name in sorted(software.keys()):
        version = software[name]
        # Truncate long names for better display
        display_name = name[:45] + "..." if len(name) > 45 else name
        print(f"{display_name:<48} | {version}")
    
    print("-" * 60)
    print(f"Total software packages: {len(software)}")
    print("=" * 60)


def get_software_summary():
    """
    Get a summary of installed Linux software by category.
    Returns a dictionary with categorized software information.
    """
    software = get_installed_software()
    
    summary = {
        'total_count': len(software),
        'python_packages': len([k for k in software.keys() if k.startswith('Python:')]),
        'system_packages': len([k for k in software.keys() if not k.startswith(('Python:', 'Snap:', 'Flatpak:'))]),
        'snap_packages': len([k for k in software.keys() if k.startswith('Snap:')]),
        'flatpak_packages': len([k for k in software.keys() if k.startswith('Flatpak:')]),
        'software_list': software
    }
    
    return summary


if __name__ == "__main__":
    # Display software information when run directly
    display_software_info()
