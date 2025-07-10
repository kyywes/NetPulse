"""
NetPulse GUI Components
Modern and legacy GUI interfaces
"""

# Optional imports - only expose what's available in this environment
__all__ = []

def _safe_import():
    """Safely import GUI components"""
    imports = {}
    
    try:
        from .application import NetPulseApplication
        imports['NetPulseApplication'] = NetPulseApplication
    except ImportError as e:
        print(f"Could not import NetPulseApplication (GUI requires tkinter): {e}")
    
    try:
        from .theme import ModernTheme, apply_modern_theme
        imports['ModernTheme'] = ModernTheme
        imports['apply_modern_theme'] = apply_modern_theme
    except ImportError as e:
        print(f"Could not import theme components: {e}")
    
    try:
        from .legacy import NetPulseGUI
        imports['NetPulseGUI'] = NetPulseGUI
    except ImportError as e:
        print(f"Could not import legacy GUI: {e}")
    
    return imports

# Import what's available
_available_imports = _safe_import()
locals().update(_available_imports)
__all__ = list(_available_imports.keys())