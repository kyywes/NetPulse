"""
NetPulse 2.0 - Modern Network Toolkit
A comprehensive network diagnostic and automation tool with modern interface.
"""

__version__ = "2.0.0"
__author__ = "NetPulse Development Team"
__license__ = "MIT"

# Core imports for easy access
from .core.network_tools import NetworkTools
from .core.config_manager import ConfigManager
from .automation.device_manager import DeviceManager
from .gui.application import NetPulseApplication

__all__ = [
    'NetworkTools',
    'ConfigManager', 
    'DeviceManager',
    'NetPulseApplication'
]