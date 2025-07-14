import platform
import subprocess
import re
import sys
import json
from typing import Dict, List, Optional


def get_macos_applications():
    """
    Get installed macOS applications using system_profiler.
    Returns a dictionary with application names and versions.
    """
    software_list = {}
    
    try:
        # Method 1: System applications via system_profiler
        print("Scanning macOS applications...")
        result = subprocess.run([
            'system_profiler', 'SPApplicationsDataType', '-xml'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Parse the XML output (simplified)
            lines = result.stdout.split('\n')
            current_app = None
            for i, line in enumerate(lines):
                if '<key>_name</key>' in line:
                    if i + 1 < len(lines):
                        name_match = re.search(r'<string>(.+)</string>', lines[i + 1])
                        if name_match:
                            current_app = name_match.group(1)
                elif '<key>version</key>' in line and current_app:
                    if i + 1 < len(lines):
                        version_match = re.search(r'<string>(.+)</string>', lines[i + 1])
                        if version_match:
                            software_list[current_app] = version_match.group(1)
                            current_app = None
    except Exception as e:
        print(f"macOS system_profiler failed: {e}")
    
    return software_list


def get_homebrew_packages():
    """
    Get installed Homebrew packages.
    Returns a dictionary with package names and versions.
    """
    homebrew_packages = {}
    
    try:
        print("Scanning Homebrew packages...")
        result = subprocess.run(['brew', 'list', '--versions'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1]
                        homebrew_packages[f"Homebrew: {name}"] = version
    except Exception:
        pass  # Homebrew might not be installed
    
    return homebrew_packages


def get_homebrew_cask_packages():
    """
    Get installed Homebrew Cask packages.
    Returns a dictionary with package names and versions.
    """
    cask_packages = {}
    
    try:
        print("Scanning Homebrew Cask packages...")
        result = subprocess.run(['brew', 'list', '--cask', '--versions'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1]
                        cask_packages[f"Homebrew Cask: {name}"] = version
                    elif len(parts) == 1:
                        # Some casks might not have version info
                        name = parts[0]
                        cask_packages[f"Homebrew Cask: {name}"] = "Unknown"
    except Exception:
        pass  # Homebrew Cask might not be installed
    
    return cask_packages


def get_macports_packages():
    """
    Get installed MacPorts packages.
    Returns a dictionary with package names and versions.
    """
    macports_packages = {}
    
    try:
        print("Scanning MacPorts packages...")
        result = subprocess.run(['port', 'installed'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    # MacPorts format: name @version+variants (active)
                    match = re.match(r'^(\S+)\s+@([^\s+]+)', line.strip())
                    if match:
                        name = match.group(1)
                        version = match.group(2)
                        macports_packages[f"MacPorts: {name}"] = version
    except Exception:
        pass  # MacPorts might not be installed
    
    return macports_packages


def get_app_store_apps():
    """
    Get installed Mac App Store applications.
    Returns a dictionary with app names and versions.
    """
    app_store_apps = {}
    
    try:
        print("Scanning Mac App Store apps...")
        # Use mas (Mac App Store command line interface) if available
        result = subprocess.run(['mas', 'list'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    # mas format: id name (version)
                    match = re.match(r'^(\d+)\s+(.+?)\s+\(([^)]+)\)$', line.strip())
                    if match:
                        app_id = match.group(1)
                        name = match.group(2)
                        version = match.group(3)
                        app_store_apps[f"App Store: {name}"] = version
    except Exception:
        pass  # mas might not be installed
    
    return app_store_apps


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
    Get all installed software on macOS.
    Returns a dictionary with software names and versions.
    """
    all_software = {}
    
    print("Detecting software on macOS...")
    
    # Get macOS applications
    all_software.update(get_macos_applications())
    
    # Get Homebrew packages
    all_software.update(get_homebrew_packages())
    
    # Get Homebrew Cask packages
    all_software.update(get_homebrew_cask_packages())
    
    # Get MacPorts packages
    all_software.update(get_macports_packages())
    
    # Get Mac App Store apps
    all_software.update(get_app_store_apps())
    
    # Add Python packages
    all_software.update(get_python_packages())
    
    return all_software


def display_software_info():
    """
    Display all installed software in a simple format.
    """
    print("=" * 60)
    print("MACOS SOFTWARE & VERSIONS")
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
    Get a summary of installed macOS software by category.
    Returns a dictionary with categorized software information.
    """
    software = get_installed_software()
    
    summary = {
        'total_count': len(software),
        'python_packages': len([k for k in software.keys() if k.startswith('Python:')]),
        'system_applications': len([k for k in software.keys() if not k.startswith(('Python:', 'Homebrew:', 'MacPorts:', 'App Store:'))]),
        'homebrew_packages': len([k for k in software.keys() if k.startswith('Homebrew:')]),
        'macports_packages': len([k for k in software.keys() if k.startswith('MacPorts:')]),
        'app_store_apps': len([k for k in software.keys() if k.startswith('App Store:')]),
        'software_list': software
    }
    
    return summary


if __name__ == "__main__":
    # Display software information when run directly
    display_software_info()
