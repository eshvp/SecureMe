import platform
import sys
from typing import Dict


def get_platform_reader():
    """
    Import and return the appropriate platform-specific software reader.
    """
    system = platform.system().lower()
    
    if system == 'windows':
        try:
            from . import software_reader_windows
            return software_reader_windows
        except ImportError:
            import software_reader_windows
            return software_reader_windows
    elif system == 'linux':
        try:
            from . import software_reader_linux
            return software_reader_linux
        except ImportError:
            import software_reader_linux
            return software_reader_linux
    elif system == 'darwin':  # macOS
        try:
            from . import software_reader_macos
            return software_reader_macos
        except ImportError:
            import software_reader_macos
            return software_reader_macos
    else:
        raise OSError(f"Unsupported operating system: {system}")


def get_installed_software():
    """
    Get all installed software based on the operating system.
    Returns a dictionary with software names and versions.
    """
    reader = get_platform_reader()
    return reader.get_installed_software()


def display_software_info():
    """
    Display all installed software in a simple format.
    """
    reader = get_platform_reader()
    reader.display_software_info()


def get_software_summary():
    """
    Get a summary of installed software by category.
    Returns a dictionary with categorized software information.
    """
    reader = get_platform_reader()
    return reader.get_software_summary()


if __name__ == "__main__":
    # Display software information when run directly
    display_software_info()