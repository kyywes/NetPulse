#!/usr/bin/env python3
"""
NetPulse 2.0 - Modern Network Toolkit
Main application entry point
"""

import os
import sys
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Application version
__version__ = "2.0.0"

# Check if GUI is available
try:
    import tkinter as tk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    print("⚠️  GUI not available - NetPulse will run in headless mode")

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_for_updates():
    """Check for application updates"""
    try:
        from netpulse.utils.updater import UpdateManager
        
        app_dir = os.path.dirname(os.path.abspath(__file__))
        updater = UpdateManager(app_dir)
        
        if updater.should_check_for_updates():
            print("Checking for updates...")
            updater.check_for_updates(show_ui=False)
            
    except Exception as e:
        print(f"Update check failed: {e}")

def show_splash():
    """Show application splash screen"""
    try:
        splash = tk.Tk()
        splash.overrideredirect(True)
        
        # Center splash screen
        w, h = 400, 250
        sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
        splash.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        splash.configure(bg="#0D1117")
        
        # Splash content
        tk.Label(splash, text="NetPulse 2.0", font=("Segoe UI", 28, "bold"),
                fg="#3B82F6", bg="#0D1117").pack(pady=(50,10))
        tk.Label(splash, text="Modern Network Toolkit", font=("Segoe UI", 12),
                fg="#F9FAFB", bg="#0D1117").pack()
        tk.Label(splash, text="Loading...", font=("Segoe UI", 10),
                fg="#9CA3AF", bg="#0D1117").pack(pady=(20,0))
        
        # Progress bar
        canvas = tk.Canvas(splash, width=200, height=6,
                          bg="#161B22", highlightthickness=0)
        bar = canvas.create_rectangle(0, 0, 0, 6, fill="#3B82F6")
        canvas.pack(pady=20)
        
        # Animate progress bar
        for i in range(0, 201, 8):
            splash.after(i*2, lambda x=i: canvas.coords(bar, 0, 0, x, 6))
        
        splash.after(1000, splash.destroy)
        splash.mainloop()
        
    except Exception as e:
        print(f"Could not show splash screen: {e}")

def launch_application():
    """Launch the main NetPulse application"""
    try:
        # Try modern GUI first
        from netpulse.gui.application import NetPulseApplication
        
        root = tk.Tk()
        app = NetPulseApplication(root)
        print("NetPulse 2.0 - Modern interface loaded")
        root.mainloop()
        
    except Exception as e:
        print(f"Modern GUI failed to load: {e}")
        
        # Fallback to legacy GUI
        try:
            from netpulse.gui.legacy import NetPulseGUI
            
            root = tk.Tk() 
            app = NetPulseGUI(root)
            print("NetPulse 2.0 - Legacy interface loaded (fallback)")
            root.mainloop()
            
        except Exception as e2:
            print(f"Both GUIs failed to load: {e2}")
            print("Please check your Python tkinter installation")
            sys.exit(1)

def main():
    """Main application function"""
    print(f"Starting NetPulse {__version__}...")
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check for updates
    check_for_updates()
    
    # Show splash screen
    show_splash()
    
    # Launch main application
    launch_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)