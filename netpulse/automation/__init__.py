"""
NetPulse Automation Components
Device management and automation tools
"""

# Optional imports - only expose what's available
__all__ = []

def _safe_import():
    """Safely import automation components"""
    imports = {}
    
    try:
        from .device_manager import DeviceManager
        imports['DeviceManager'] = DeviceManager
    except ImportError as e:
        print(f"Could not import DeviceManager (automation requires ODBC and other dependencies): {e}")
    
    return imports

# Import what's available
_available_imports = _safe_import()
locals().update(_available_imports)
__all__ = list(_available_imports.keys())