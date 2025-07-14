import platform
import subprocess
import json
import re
import os
import sys
from typing import Dict, List, Optional


def get_windows_firmware():
    """
    Get firmware information on Windows systems.
    Returns a dictionary with firmware details.
    """
    firmware_info = {}
    
    try:
        # Method 1: BIOS/UEFI Information via WMI
        print("Scanning BIOS/UEFI firmware...")
        ps_script = """
        Get-WmiObject -Class Win32_BIOS | 
        Select-Object Manufacturer, Name, Version, ReleaseDate, SerialNumber | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    firmware_info['BIOS/UEFI'] = {
                        'Manufacturer': data.get('Manufacturer', 'Unknown'),
                        'Name': data.get('Name', 'Unknown'),
                        'Version': data.get('Version', 'Unknown'),
                        'Release Date': data.get('ReleaseDate', 'Unknown'),
                        'Serial Number': data.get('SerialNumber', 'Unknown')
                    }
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"BIOS JSON parsing failed: {e}")
    except Exception as e:
        print(f"BIOS scan failed: {e}")
    
    try:
        # Method 2: Motherboard Firmware
        print("Scanning motherboard firmware...")
        ps_script = """
        Get-WmiObject -Class Win32_BaseBoard | 
        Select-Object Manufacturer, Product, Version, SerialNumber | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    firmware_info['Motherboard'] = {
                        'Manufacturer': data.get('Manufacturer', 'Unknown'),
                        'Product': data.get('Product', 'Unknown'),
                        'Version': data.get('Version', 'Unknown'),
                        'Serial Number': data.get('SerialNumber', 'Unknown')
                    }
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Motherboard JSON parsing failed: {e}")
    except Exception as e:
        print(f"Motherboard scan failed: {e}")
    
    try:
        # Method 3: Network Adapter Firmware
        print("Scanning network adapter firmware...")
        ps_script = """
        Get-WmiObject -Class Win32_NetworkAdapter | 
        Where-Object {$_.PhysicalAdapter -eq $true -and $_.AdapterType -ne $null} |
        Select-Object Name, Manufacturer, Description, DriverVersion | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                network_adapters = {}
                if isinstance(data, list):
                    for i, adapter in enumerate(data):
                        if isinstance(adapter, dict):
                            adapter_name = adapter.get('Name', f'Network Adapter {i+1}')
                            network_adapters[adapter_name] = {
                                'Manufacturer': adapter.get('Manufacturer', 'Unknown'),
                                'Description': adapter.get('Description', 'Unknown'),
                                'Driver Version': adapter.get('DriverVersion', 'Unknown')
                            }
                elif isinstance(data, dict):
                    adapter_name = data.get('Name', 'Network Adapter')
                    network_adapters[adapter_name] = {
                        'Manufacturer': data.get('Manufacturer', 'Unknown'),
                        'Description': data.get('Description', 'Unknown'),
                        'Driver Version': data.get('DriverVersion', 'Unknown')
                    }
                
                if network_adapters:
                    firmware_info['Network Adapters'] = network_adapters
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Network adapter JSON parsing failed: {e}")
    except Exception as e:
        print(f"Network adapter scan failed: {e}")
    
    try:
        # Method 4: Storage Device Firmware
        print("Scanning storage device firmware...")
        ps_script = """
        Get-WmiObject -Class Win32_DiskDrive | 
        Select-Object Model, Manufacturer, FirmwareRevision, SerialNumber, InterfaceType | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                storage_devices = {}
                if isinstance(data, list):
                    for i, device in enumerate(data):
                        if isinstance(device, dict):
                            device_name = device.get('Model', f'Storage Device {i+1}')
                            storage_devices[device_name] = {
                                'Manufacturer': device.get('Manufacturer', 'Unknown'),
                                'Firmware Revision': device.get('FirmwareRevision', 'Unknown'),
                                'Serial Number': device.get('SerialNumber', 'Unknown'),
                                'Interface Type': device.get('InterfaceType', 'Unknown')
                            }
                elif isinstance(data, dict):
                    device_name = data.get('Model', 'Storage Device')
                    storage_devices[device_name] = {
                        'Manufacturer': data.get('Manufacturer', 'Unknown'),
                        'Firmware Revision': data.get('FirmwareRevision', 'Unknown'),
                        'Serial Number': data.get('SerialNumber', 'Unknown'),
                        'Interface Type': data.get('InterfaceType', 'Unknown')
                    }
                
                if storage_devices:
                    firmware_info['Storage Devices'] = storage_devices
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Storage device JSON parsing failed: {e}")
    except Exception as e:
        print(f"Storage device scan failed: {e}")
    
    try:
        # Method 5: Graphics Card Firmware/Driver
        print("Scanning graphics card firmware...")
        ps_script = """
        Get-WmiObject -Class Win32_VideoController | 
        Select-Object Name, DriverVersion, DriverDate, VideoProcessor | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                graphics_cards = {}
                if isinstance(data, list):
                    for i, card in enumerate(data):
                        if isinstance(card, dict):
                            card_name = card.get('Name', f'Graphics Card {i+1}')
                            graphics_cards[card_name] = {
                                'Driver Version': card.get('DriverVersion', 'Unknown'),
                                'Driver Date': card.get('DriverDate', 'Unknown'),
                                'Video Processor': card.get('VideoProcessor', 'Unknown')
                            }
                elif isinstance(data, dict):
                    card_name = data.get('Name', 'Graphics Card')
                    graphics_cards[card_name] = {
                        'Driver Version': data.get('DriverVersion', 'Unknown'),
                        'Driver Date': data.get('DriverDate', 'Unknown'),
                        'Video Processor': data.get('VideoProcessor', 'Unknown')
                    }
                
                if graphics_cards:
                    firmware_info['Graphics Cards'] = graphics_cards
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Graphics card JSON parsing failed: {e}")
    except Exception as e:
        print(f"Graphics card scan failed: {e}")
    
    return firmware_info


def get_linux_firmware():
    """
    Get firmware information on Linux systems.
    Returns a dictionary with firmware details.
    """
    firmware_info = {}
    
    try:
        # Method 1: DMI/SMBIOS Information (BIOS/UEFI)
        print("Scanning BIOS/UEFI firmware...")
        result = subprocess.run(['dmidecode', '-t', 'bios'], capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            bios_info = {}
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Vendor:' in line:
                    bios_info['Manufacturer'] = line.split(':', 1)[1].strip()
                elif 'Version:' in line:
                    bios_info['Version'] = line.split(':', 1)[1].strip()
                elif 'Release Date:' in line:
                    bios_info['Release Date'] = line.split(':', 1)[1].strip()
            
            if bios_info:
                firmware_info['BIOS/UEFI'] = bios_info
    except Exception as e:
        print(f"Linux BIOS scan failed: {e}")
    
    try:
        # Method 2: Network interface firmware
        print("Scanning network interface firmware...")
        result = subprocess.run(['lspci', '-v'], capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            network_devices = {}
            current_device = None
            for line in result.stdout.split('\n'):
                if 'Ethernet controller' in line or 'Network controller' in line:
                    current_device = line.split(': ', 1)[1] if ': ' in line else line
                    network_devices[current_device] = {}
                elif current_device and 'Kernel driver in use:' in line:
                    network_devices[current_device]['Driver'] = line.split(':', 1)[1].strip()
            
            if network_devices:
                firmware_info['Network Devices'] = network_devices
    except Exception as e:
        print(f"Linux network scan failed: {e}")
    
    try:
        # Method 3: Storage device firmware
        print("Scanning storage device firmware...")
        result = subprocess.run(['lsblk', '-o', 'NAME,MODEL,SERIAL,REV'], capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            storage_devices = {}
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 2 and not parts[0].startswith('├') and not parts[0].startswith('└'):
                    device_name = parts[1] if len(parts) > 1 and parts[1] != '' else parts[0]
                    device_info = {}
                    if len(parts) > 2:
                        device_info['Serial'] = parts[2]
                    if len(parts) > 3:
                        device_info['Firmware Revision'] = parts[3]
                    
                    if device_info:
                        storage_devices[device_name] = device_info
            
            if storage_devices:
                firmware_info['Storage Devices'] = storage_devices
    except Exception as e:
        print(f"Linux storage scan failed: {e}")
    
    return firmware_info


def get_macos_firmware():
    """
    Get firmware information on macOS systems.
    Returns a dictionary with firmware details.
    """
    firmware_info = {}
    
    try:
        # Method 1: System firmware information
        print("Scanning macOS system firmware...")
        result = subprocess.run(['system_profiler', 'SPHardwareDataType', '-json'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                hardware_info = data.get('SPHardwareDataType', [])
                if hardware_info and len(hardware_info) > 0:
                    hw = hardware_info[0]
                    firmware_info['System Firmware'] = {
                        'Boot ROM Version': hw.get('boot_rom_version', 'Unknown'),
                        'SMC Version': hw.get('SMC_version_system', 'Unknown'),
                        'Serial Number': hw.get('serial_number', 'Unknown')
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"macOS hardware JSON parsing failed: {e}")
    except Exception as e:
        print(f"macOS system firmware scan failed: {e}")
    
    try:
        # Method 2: Storage firmware
        print("Scanning macOS storage firmware...")
        result = subprocess.run(['system_profiler', 'SPStorageDataType', '-json'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                storage_info = data.get('SPStorageDataType', [])
                storage_devices = {}
                
                for device in storage_info:
                    device_name = device.get('_name', 'Unknown Storage')
                    storage_devices[device_name] = {
                        'Physical Drive': device.get('com.apple.diskUtility.partitionMapType', 'Unknown'),
                        'Media Name': device.get('device_model', 'Unknown'),
                        'Revision': device.get('device_revision', 'Unknown')
                    }
                
                if storage_devices:
                    firmware_info['Storage Devices'] = storage_devices
            except (json.JSONDecodeError, KeyError) as e:
                print(f"macOS storage JSON parsing failed: {e}")
    except Exception as e:
        print(f"macOS storage scan failed: {e}")
    
    return firmware_info


def get_firmware_info():
    """
    Get firmware information based on the operating system.
    Returns a dictionary with firmware details.
    """
    system = platform.system().lower()
    
    print(f"Detecting firmware on {system}...")
    
    if system == 'windows':
        return get_windows_firmware()
    elif system == 'linux':
        return get_linux_firmware()
    elif system == 'darwin':  # macOS
        return get_macos_firmware()
    else:
        return {'error': f'Unsupported operating system: {system}'}


def display_firmware_info():
    """
    Display all firmware information in a simple format.
    """
    print("=" * 60)
    print("FIRMWARE & HARDWARE-LEVEL SOFTWARE")
    print("=" * 60)
    
    firmware = get_firmware_info()
    
    if not firmware or 'error' in firmware:
        print("No firmware information could be retrieved.")
        if 'error' in firmware:
            print(f"Error: {firmware['error']}")
        return
    
    total_components = sum(len(v) if isinstance(v, dict) else 1 for v in firmware.values())
    print(f"\n🔧 Found {total_components} firmware components:\n")
    print("-" * 60)
    
    for category, info in firmware.items():
        print(f"\n📋 {category}:")
        print("-" * 40)
        
        if isinstance(info, dict):
            if any(isinstance(v, dict) for v in info.values()):
                # Multiple devices in category
                for device_name, device_info in info.items():
                    if isinstance(device_info, dict):
                        print(f"  🔹 {device_name}:")
                        for key, value in device_info.items():
                            print(f"    {key}: {value}")
                        print()
                    else:
                        print(f"  🔹 {device_name}: {device_info}")
            else:
                # Single device info
                for key, value in info.items():
                    print(f"  {key}: {value}")
        else:
            print(f"  {info}")
    
    print("\n" + "=" * 60)


def get_firmware_summary():
    """
    Get a summary of firmware information.
    Returns a dictionary with categorized firmware information.
    """
    firmware = get_firmware_info()
    
    if 'error' in firmware:
        return firmware
    
    total_components = sum(len(v) if isinstance(v, dict) else 1 for v in firmware.values())
    
    summary = {
        'total_components': total_components,
        'categories': list(firmware.keys()),
        'firmware_details': firmware
    }
    
    return summary


if __name__ == "__main__":
    # Display firmware information when run directly
    display_firmware_info()