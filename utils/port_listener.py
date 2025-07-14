import platform
import subprocess
import socket
import json
import re
import sys
from typing import Dict, List, Optional, Tuple


def get_windows_ports():
    """
    Get open ports and listening services on Windows.
    Returns a dictionary with port information.
    """
    port_info = {}
    
    try:
        # Method 1: Using netstat for detailed port information
        print("Scanning open ports via netstat...")
        result = subprocess.run([
            'netstat', '-ano'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            listening_ports = {}
            lines = result.stdout.strip().split('\n')
            
            for line in lines[4:]:  # Skip header lines
                if 'LISTENING' in line or 'ESTABLISHED' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        protocol = parts[0]
                        local_address = parts[1]
                        state = parts[3]
                        pid = parts[4] if parts[4] != '0' else 'Unknown'
                        
                        # Extract port from address
                        if ':' in local_address:
                            ip, port = local_address.rsplit(':', 1)
                            try:
                                port_num = int(port)
                                key = f"{protocol}:{port_num}"
                                
                                if key not in listening_ports:
                                    listening_ports[key] = {
                                        'Protocol': protocol,
                                        'Port': port_num,
                                        'Local Address': ip,
                                        'State': state,
                                        'PID': pid,
                                        'Process': 'Unknown'
                                    }
                            except ValueError:
                                continue
            
            if listening_ports:
                port_info['Listening Ports'] = listening_ports
    except Exception as e:
        print(f"Netstat scan failed: {e}")
    
    try:
        # Method 2: Get process information for PIDs
        print("Mapping processes to ports...")
        if 'Listening Ports' in port_info:
            for port_key, port_data in port_info['Listening Ports'].items():
                pid = port_data.get('PID')
                if pid and pid != 'Unknown' and pid != '0':
                    try:
                        # Get process name using tasklist
                        result = subprocess.run([
                            'tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'
                        ], capture_output=True, text=True, timeout=10)
                        
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:  # Skip header
                                # Parse CSV format
                                process_line = lines[1].replace('"', '').split(',')
                                if len(process_line) > 0:
                                    port_data['Process'] = process_line[0]
                    except Exception:
                        pass
    except Exception as e:
        print(f"Process mapping failed: {e}")
    
    try:
        # Method 3: Using PowerShell for more detailed service information
        print("Scanning services via PowerShell...")
        ps_script = """
        Get-NetTCPConnection | Where-Object {$_.State -eq "Listen"} | 
        Select-Object LocalAddress, LocalPort, OwningProcess | 
        ConvertTo-Json
        """
        
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                tcp_listeners = {}
                
                if isinstance(data, list):
                    for conn in data:
                        if isinstance(conn, dict):
                            port = conn.get('LocalPort')
                            address = conn.get('LocalAddress', '0.0.0.0')
                            pid = conn.get('OwningProcess')
                            
                            if port:
                                key = f"TCP:{port}"
                                tcp_listeners[key] = {
                                    'Protocol': 'TCP',
                                    'Port': port,
                                    'Local Address': address,
                                    'State': 'LISTENING',
                                    'PID': pid,
                                    'Process': 'Unknown'
                                }
                elif isinstance(data, dict):
                    port = data.get('LocalPort')
                    address = data.get('LocalAddress', '0.0.0.0')
                    pid = data.get('OwningProcess')
                    
                    if port:
                        key = f"TCP:{port}"
                        tcp_listeners[key] = {
                            'Protocol': 'TCP',
                            'Port': port,
                            'Local Address': address,
                            'State': 'LISTENING',
                            'PID': pid,
                            'Process': 'Unknown'
                        }
                
                if tcp_listeners:
                    port_info['TCP Listeners'] = tcp_listeners
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"PowerShell TCP parsing failed: {e}")
    except Exception as e:
        print(f"PowerShell TCP scan failed: {e}")
    
    return port_info


def get_linux_ports():
    """
    Get open ports and listening services on Linux.
    Returns a dictionary with port information.
    """
    port_info = {}
    
    try:
        # Method 1: Using netstat
        print("Scanning open ports via netstat...")
        result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            listening_ports = {}
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if 'LISTEN' in line or 'udp' in line.lower():
                    parts = line.split()
                    if len(parts) >= 6:
                        protocol = parts[0]
                        local_address = parts[3]
                        process_info = parts[6] if len(parts) > 6 else 'Unknown'
                        
                        # Extract port from address
                        if ':' in local_address:
                            ip, port = local_address.rsplit(':', 1)
                            try:
                                port_num = int(port)
                                key = f"{protocol}:{port_num}"
                                
                                # Extract PID and process name
                                pid = 'Unknown'
                                process = 'Unknown'
                                if '/' in process_info:
                                    pid_part, process = process_info.split('/', 1)
                                    pid = pid_part
                                
                                listening_ports[key] = {
                                    'Protocol': protocol,
                                    'Port': port_num,
                                    'Local Address': ip,
                                    'State': 'LISTENING',
                                    'PID': pid,
                                    'Process': process
                                }
                            except ValueError:
                                continue
            
            if listening_ports:
                port_info['Listening Ports'] = listening_ports
    except Exception as e:
        print(f"Linux netstat scan failed: {e}")
    
    try:
        # Method 2: Using ss (socket statistics) - more modern
        print("Scanning ports via ss command...")
        result = subprocess.run(['ss', '-tulpn'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            ss_ports = {}
            lines = result.stdout.strip().split('\n')
            
            for line in lines[1:]:  # Skip header
                if 'LISTEN' in line or 'UNCONN' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        protocol = parts[0]
                        local_address = parts[4]
                        process_info = parts[6] if len(parts) > 6 else 'Unknown'
                        
                        # Extract port from address
                        if ':' in local_address:
                            ip, port = local_address.rsplit(':', 1)
                            try:
                                port_num = int(port)
                                key = f"{protocol}:{port_num}"
                                
                                # Extract process info
                                pid = 'Unknown'
                                process = 'Unknown'
                                if 'pid=' in process_info:
                                    pid_match = re.search(r'pid=(\d+)', process_info)
                                    if pid_match:
                                        pid = pid_match.group(1)
                                
                                if '(' in process_info and ')' in process_info:
                                    process_match = re.search(r'\("([^"]+)"', process_info)
                                    if process_match:
                                        process = process_match.group(1)
                                
                                ss_ports[key] = {
                                    'Protocol': protocol,
                                    'Port': port_num,
                                    'Local Address': ip,
                                    'State': 'LISTENING',
                                    'PID': pid,
                                    'Process': process
                                }
                            except ValueError:
                                continue
            
            if ss_ports:
                port_info['SS Listeners'] = ss_ports
    except Exception as e:
        print(f"Linux ss scan failed: {e}")
    
    return port_info


def get_macos_ports():
    """
    Get open ports and listening services on macOS.
    Returns a dictionary with port information.
    """
    port_info = {}
    
    try:
        # Method 1: Using netstat
        print("Scanning open ports via netstat...")
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            listening_ports = {}
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        protocol = parts[0]
                        local_address = parts[3]
                        
                        # Extract port from address
                        if '.' in local_address:
                            parts_addr = local_address.rsplit('.', 1)
                            if len(parts_addr) == 2:
                                ip, port = parts_addr
                                try:
                                    port_num = int(port)
                                    key = f"{protocol}:{port_num}"
                                    
                                    listening_ports[key] = {
                                        'Protocol': protocol,
                                        'Port': port_num,
                                        'Local Address': ip,
                                        'State': 'LISTENING',
                                        'PID': 'Unknown',
                                        'Process': 'Unknown'
                                    }
                                except ValueError:
                                    continue
            
            if listening_ports:
                port_info['Listening Ports'] = listening_ports
    except Exception as e:
        print(f"macOS netstat scan failed: {e}")
    
    try:
        # Method 2: Using lsof for process information
        print("Scanning ports via lsof...")
        result = subprocess.run(['lsof', '-i', '-P', '-n'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lsof_ports = {}
            lines = result.stdout.strip().split('\n')
            
            for line in lines[1:]:  # Skip header
                if 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 9:
                        process = parts[0]
                        pid = parts[1]
                        protocol_port = parts[8]
                        
                        if ':' in protocol_port and '->' not in protocol_port:
                            try:
                                address, port = protocol_port.rsplit(':', 1)
                                port_num = int(port)
                                protocol = 'TCP'  # lsof typically shows TCP for listening
                                
                                key = f"{protocol}:{port_num}"
                                lsof_ports[key] = {
                                    'Protocol': protocol,
                                    'Port': port_num,
                                    'Local Address': address if address != '*' else '0.0.0.0',
                                    'State': 'LISTENING',
                                    'PID': pid,
                                    'Process': process
                                }
                            except ValueError:
                                continue
            
            if lsof_ports:
                port_info['LSOF Listeners'] = lsof_ports
    except Exception as e:
        print(f"macOS lsof scan failed: {e}")
    
    return port_info


def get_common_port_services():
    """
    Get common port-to-service mappings for security analysis.
    Returns a dictionary of well-known ports and their typical services.
    """
    common_ports = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        993: 'IMAPS',
        995: 'POP3S',
        1433: 'MSSQL',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        5900: 'VNC',
        6379: 'Redis',
        8080: 'HTTP-Alt',
        8443: 'HTTPS-Alt',
        27017: 'MongoDB'
    }
    return common_ports


def get_listening_ports():
    """
    Get all listening ports and services based on the operating system.
    Returns a dictionary with port information.
    """
    system = platform.system().lower()
    
    print(f"Detecting listening ports on {system}...")
    
    if system == 'windows':
        return get_windows_ports()
    elif system == 'linux':
        return get_linux_ports()
    elif system == 'darwin':  # macOS
        return get_macos_ports()
    else:
        return {'error': f'Unsupported operating system: {system}'}


def display_port_info():
    """
    Display all listening ports and services in a simple format.
    """
    print("=" * 70)
    print("OPEN PORTS & LISTENING SERVICES")
    print("=" * 70)
    
    ports = get_listening_ports()
    common_services = get_common_port_services()
    
    if not ports or 'error' in ports:
        print("No port information could be retrieved.")
        if 'error' in ports:
            print(f"Error: {ports['error']}")
        return
    
    total_ports = 0
    for category, port_list in ports.items():
        if isinstance(port_list, dict):
            total_ports += len(port_list)
    
    print(f"\n🔌 Found {total_ports} listening ports/services:\n")
    print("-" * 70)
    
    for category, port_list in ports.items():
        print(f"\n📋 {category}:")
        print("-" * 50)
        
        if isinstance(port_list, dict):
            # Sort ports by port number
            sorted_ports = sorted(port_list.items(), key=lambda x: x[1].get('Port', 0))
            
            for port_key, port_info in sorted_ports:
                port_num = port_info.get('Port', 'Unknown')
                protocol = port_info.get('Protocol', 'Unknown')
                process = port_info.get('Process', 'Unknown')
                pid = port_info.get('PID', 'Unknown')
                address = port_info.get('Local Address', 'Unknown')
                
                # Check if it's a well-known service
                service_name = common_services.get(port_num, 'Unknown Service')
                risk_indicator = "⚠️" if port_num in [21, 23, 1433, 3389, 5900] else "🔓"
                
                print(f"  {risk_indicator} Port {port_num}/{protocol} ({service_name})")
                print(f"    📍 Address: {address}")
                print(f"    🔧 Process: {process} (PID: {pid})")
                print()
    
    # Security warnings
    print("\n🛡️ Security Notes:")
    print("-" * 30)
    risky_ports = [21, 23, 1433, 3389, 5900]
    found_risky = []
    
    for category, port_list in ports.items():
        if isinstance(port_list, dict):
            for port_info in port_list.values():
                port_num = port_info.get('Port')
                if port_num in risky_ports:
                    found_risky.append(port_num)
    
    if found_risky:
        print("⚠️  Warning: Found potentially risky open ports:")
        for port in set(found_risky):
            service = common_services.get(port, 'Unknown')
            print(f"   - Port {port} ({service}) - Consider securing or disabling")
    else:
        print("✅ No obviously risky ports detected")
    
    print("\n" + "=" * 70)


def get_port_summary():
    """
    Get a summary of listening ports and services.
    Returns a dictionary with categorized port information.
    """
    ports = get_listening_ports()
    
    if 'error' in ports:
        return ports
    
    total_ports = sum(len(v) if isinstance(v, dict) else 0 for v in ports.values())
    
    # Count by protocol
    tcp_count = 0
    udp_count = 0
    
    for category, port_list in ports.items():
        if isinstance(port_list, dict):
            for port_info in port_list.values():
                protocol = port_info.get('Protocol', '').upper()
                if 'TCP' in protocol:
                    tcp_count += 1
                elif 'UDP' in protocol:
                    udp_count += 1
    
    summary = {
        'total_ports': total_ports,
        'tcp_ports': tcp_count,
        'udp_ports': udp_count,
        'categories': list(ports.keys()),
        'port_details': ports
    }
    
    return summary


if __name__ == "__main__":
    # Display port information when run directly
    display_port_info()