"""
NetPulse 2.0 - Modern Network Toolkit
A comprehensive network diagnostic and automation tool with modern interface.
"""

__version__ = "2.0.0"
__author__ = "NetPulse Development Team"
__license__ = "MIT"

# Core imports for easy access (with error handling)
def _safe_import():
    """Safely import core components"""
    imports = {}
    
    try:
        from .core.network_tools import NetworkTools
        imports['NetworkTools'] = NetworkTools
    except ImportError as e:
        print(f"Could not import NetworkTools: {e}")
    
    try:
        from .core.config_manager import ConfigManager
        imports['ConfigManager'] = ConfigManager
    except ImportError as e:
        print(f"Could not import ConfigManager: {e}")
    
    try:
        from .automation.device_manager import DeviceManager
        imports['DeviceManager'] = DeviceManager
    except ImportError as e:
        print(f"Could not import DeviceManager (automation requires ODBC): {e}")
    
    try:
        from .gui.application import NetPulseApplication
        imports['NetPulseApplication'] = NetPulseApplication
    except ImportError as e:
        print(f"Could not import NetPulseApplication (GUI requires tkinter): {e}")
    
    return imports

# Import what's available
_available_imports = _safe_import()
locals().update(_available_imports)

__all__ = list(_available_imports.keys())