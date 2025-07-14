import platform
import subprocess
import json
import re
import os
import sys
from typing import Dict, List, Optional


def get_windows_software():
    """
    Get installed software on Windows using multiple methods.
    Returns a dictionary with software names and versions.
    """
    software_list = {}
    
    try:
        # Method 1: Using wmic (Windows Management Instrumentation)
        print("Scanning Windows software via WMI...")
        result = subprocess.run([
            'wmic', 'product', 'get', 'name,version', '/format:csv'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip() and ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        name = parts[1].strip()
                        version = parts[2].strip()
                        if name and version:
                            software_list[name] = version
    except Exception as e:
        print(f"WMI method failed: {e}")
    
    # Method 2: Comprehensive registry scanning
    registry_paths = [
        "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
        "HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
        "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*"
    ]
    
    for registry_path in registry_paths:
        try:
            print(f"Scanning registry path: {registry_path.split('\\')[-2]}...")
            ps_script = f"""
            Get-ItemProperty '{registry_path}' | 
            Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | 
            Where-Object {{$_.DisplayName -ne $null -and $_.DisplayName -ne ""}} | 
            ConvertTo-Json
            """
            
            result = subprocess.run([
                'powershell', '-Command', ps_script
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                name = item.get('DisplayName')
                                version = item.get('DisplayVersion')
                                if name and isinstance(name, str):
                                    name = name.strip()
                                    if name and name not in software_list:
                                        version = version.strip() if version and isinstance(version, str) else 'Unknown'
                                        software_list[name] = version
                    elif isinstance(data, dict):
                        name = data.get('DisplayName')
                        version = data.get('DisplayVersion')
                        if name and isinstance(name, str):
                            name = name.strip()
                            if name and name not in software_list:
                                version = version.strip() if version and isinstance(version, str) else 'Unknown'
                                software_list[name] = version
                except (json.JSONDecodeError, AttributeError) as e:
                    print(f"JSON parsing failed for {registry_path}: {e}")
        except Exception as e:
            print(f"Registry scan failed for {registry_path}: {e}")
    
    try:
        # Method 3: Using Get-Package (PackageManagement) for more modern installs
        print("Scanning via PackageManagement...")
        ps_script = """
        Get-Package | 
        Select-Object Name, Version, Source | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            name = item.get('Name')
                            version = item.get('Version')
                            source = item.get('Source', '')
                            if name and isinstance(name, str):
                                name = name.strip()
                                display_name = f"{name} ({source})" if source else name
                                if display_name not in software_list:
                                    version = version.strip() if version and isinstance(version, str) else 'Unknown'
                                    software_list[display_name] = version
                elif isinstance(data, dict):
                    name = data.get('Name')
                    version = data.get('Version')
                    source = data.get('Source', '')
                    if name and isinstance(name, str):
                        name = name.strip()
                        display_name = f"{name} ({source})" if source else name
                        if display_name not in software_list:
                            version = version.strip() if version and isinstance(version, str) else 'Unknown'
                            software_list[display_name] = version
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"PackageManagement JSON parsing failed: {e}")
    except Exception as e:
        print(f"PackageManagement method failed: {e}")
    
    try:
        # Method 4: Windows Store apps (AppX packages)
        print("Scanning Windows Store apps...")
        ps_script = """
        Get-AppxPackage | 
        Where-Object {$_.Name -notlike "*Microsoft*" -and $_.Name -notlike "*Windows*"} |
        Select-Object Name, Version | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            name = item.get('Name')
                            version = item.get('Version')
                            if name and isinstance(name, str):
                                name = name.strip()
                                display_name = f"Store: {name}"
                                if display_name not in software_list:
                                    version = version.strip() if version and isinstance(version, str) else 'Unknown'
                                    software_list[display_name] = version
                elif isinstance(data, dict):
                    name = data.get('Name')
                    version = data.get('Version')
                    if name and isinstance(name, str):
                        name = name.strip()
                        display_name = f"Store: {name}"
                        if display_name not in software_list:
                            version = version.strip() if version and isinstance(version, str) else 'Unknown'
                            software_list[display_name] = version
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"AppX JSON parsing failed: {e}")
    except Exception as e:
        print(f"AppX method failed: {e}")
    
    return software_list


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
    Get all installed software on Windows.
    Returns a dictionary with software names and versions.
    """
    all_software = {}
    
    print("Detecting software on Windows...")
    
    # Get Windows-specific software
    all_software.update(get_windows_software())
    
    # Add Python packages
    all_software.update(get_python_packages())
    
    return all_software


def display_software_info():
    """
    Display all installed software in a simple format.
    """
    print("=" * 60)
    print("WINDOWS SOFTWARE & VERSIONS")
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
    Get a summary of installed Windows software by category.
    Returns a dictionary with categorized software information.
    """
    software = get_installed_software()
    
    summary = {
        'total_count': len(software),
        'python_packages': len([k for k in software.keys() if k.startswith('Python:')]),
        'system_software': len([k for k in software.keys() if not k.startswith('Python:')]),
        'store_apps': len([k for k in software.keys() if k.startswith('Store:')]),
        'software_list': software
    }
    
    return summary


if __name__ == "__main__":
    # Display software information when run directly
    display_software_info()
