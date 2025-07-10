"""
NetPulse Utility Components
Update management and utility functions
"""

# Optional imports - only expose what's available
__all__ = []

def _safe_import():
    """Safely import utility components"""
    imports = {}
    
    try:
        from .updater import UpdateManager
        imports['UpdateManager'] = UpdateManager
    except ImportError as e:
        print(f"Could not import UpdateManager: {e}")
    
    return imports

# Import what's available
_available_imports = _safe_import()
locals().update(_available_imports)
__all__ = list(_available_imports.keys())