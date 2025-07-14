import platform
import os
import subprocess
import sys


def get_os_info():
    """
    Get basic operating system information.
    Returns a dictionary with OS details.
    """
    try:
        os_info = {
            'OS Name': platform.system(),
            'OS Version': platform.version(),
            'OS Release': platform.release(),
            'Architecture': platform.machine(),
            'Platform': platform.platform(),
            'Processor': platform.processor()
        }
        return os_info
    except Exception as e:
        return {'Error': f'Failed to get OS info: {str(e)}'}


def get_kernel_info():
    """
    Get kernel-specific information based on the operating system.
    Returns a dictionary with kernel details.
    """
    try:
        system = platform.system().lower()
        kernel_info = {}
        
        if system == 'windows':
            # Windows kernel information
            kernel_info['Kernel Type'] = 'Windows NT'
            kernel_info['Build Number'] = platform.win32_ver()[1]
            kernel_info['Service Pack'] = platform.win32_ver()[2]
            
        elif system == 'linux':
            # Linux kernel information
            kernel_info['Kernel Version'] = platform.release()
            try:
                # Try to get more detailed kernel info
                with open('/proc/version', 'r') as f:
                    kernel_info['Kernel Details'] = f.read().strip()
            except:
                pass
                
        elif system == 'darwin':  # macOS
            kernel_info['Kernel Type'] = 'Darwin'
            kernel_info['Kernel Version'] = platform.release()
            
        else:
            kernel_info['Kernel Type'] = 'Unknown'
            kernel_info['Kernel Version'] = platform.release()
            
        return kernel_info
    except Exception as e:
        return {'Error': f'Failed to get kernel info: {str(e)}'}


def get_system_details():
    """
    Get additional system details.
    Returns a dictionary with system information.
    """
    try:
        details = {
            'Python Version': sys.version.split()[0],
            'Node Name': platform.node(),
            'Boot Time': 'N/A'  # Would require additional libraries for accurate boot time
        }
        
        # Try to get uptime on different systems
        system = platform.system().lower()
        if system == 'windows':
            try:
                result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'System Boot Time' in line:
                            details['Boot Time'] = line.split(':', 1)[1].strip()
                            break
            except:
                pass
        
        return details
    except Exception as e:
        return {'Error': f'Failed to get system details: {str(e)}'}


def display_os_kernel_info():
    """
    Display all OS and kernel information in a simple format.
    """
    print("=" * 50)
    print("OS & KERNEL INFORMATION")
    print("=" * 50)
    
    # OS Information
    print("\n📟 Operating System:")
    print("-" * 20)
    os_info = get_os_info()
    for key, value in os_info.items():
        print(f"{key}: {value}")
    
    # Kernel Information
    print("\n🔧 Kernel Information:")
    print("-" * 20)
    kernel_info = get_kernel_info()
    for key, value in kernel_info.items():
        print(f"{key}: {value}")
    
    # System Details
    print("\n💻 System Details:")
    print("-" * 20)
    system_details = get_system_details()
    for key, value in system_details.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 50)


def get_all_info():
    """
    Get all OS and kernel information as a combined dictionary.
    Returns a dictionary with all system information.
    """
    all_info = {
        'os_info': get_os_info(),
        'kernel_info': get_kernel_info(),
        'system_details': get_system_details()
    }
    return all_info


if __name__ == "__main__":
    # Display information when run directly
    display_os_kernel_info()