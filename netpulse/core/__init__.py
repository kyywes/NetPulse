"""
NetPulse Core Components
Network tools, configuration management, and utilities
"""

# Optional imports - only expose what's available
__all__ = []

def _safe_import():
    """Safely import core components"""
    imports = {}
    
    try:
        from .network_tools import NetworkTools
        imports['NetworkTools'] = NetworkTools
    except ImportError as e:
        print(f"Could not import NetworkTools: {e}")
    
    try:
        from .config_manager import ConfigManager
        imports['ConfigManager'] = ConfigManager
    except ImportError as e:
        print(f"Could not import ConfigManager: {e}")
    
    try:
        from .credential_manager import CredentialManager
        imports['CredentialManager'] = CredentialManager
    except ImportError as e:
        print(f"Could not import CredentialManager: {e}")
    
    return imports

# Import what's available
_available_imports = _safe_import()
locals().update(_available_imports)
__all__ = list(_available_imports.keys())