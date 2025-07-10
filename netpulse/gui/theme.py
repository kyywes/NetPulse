from tkinter import ttk
import tkinter as tk

class ModernTheme:
    # Modern color palette
    COLORS = {
        'bg_primary': '#0D1117',      # Dark background
        'bg_secondary': '#161B22',    # Secondary background  
        'bg_tertiary': '#21262D',     # Tertiary background
        'bg_accent': '#1F2937',       # Accent background
        'accent_primary': '#3B82F6',  # Blue accent
        'accent_secondary': '#10B981', # Green accent
        'accent_danger': '#EF4444',   # Red accent
        'accent_warning': '#F59E0B',  # Yellow accent
        'text_primary': '#F9FAFB',    # Primary text
        'text_secondary': '#9CA3AF',  # Secondary text
        'text_muted': '#6B7280',      # Muted text
        'border': '#374151',          # Border color
        'border_focus': '#3B82F6',    # Focused border
        'hover': '#374151',           # Hover state
        'success': '#10B981',         # Success color
        'error': '#EF4444',           # Error color
        'warning': '#F59E0B',         # Warning color
    }
    
    # Typography
    FONTS = {
        'default': ('Segoe UI', 10),
        'heading': ('Segoe UI', 14, 'bold'),
        'subheading': ('Segoe UI', 12, 'bold'),
        'mono': ('Consolas', 10),
        'mono_large': ('Consolas', 12),
        'small': ('Segoe UI', 9),
    }

def apply_modern_theme(root):
    """Apply modern dark theme with enhanced styling"""
    root.configure(bg=ModernTheme.COLORS['bg_primary'])
    
    style = ttk.Style(root)
    style.theme_use("clam")
    
    # Configure base styles
    style.configure(".", 
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   fieldbackground=ModernTheme.COLORS['bg_secondary'],
                   bordercolor=ModernTheme.COLORS['border'],
                   lightcolor=ModernTheme.COLORS['border'],
                   darkcolor=ModernTheme.COLORS['bg_primary'],
                   troughcolor=ModernTheme.COLORS['bg_secondary'],
                   relief="flat",
                   borderwidth=1,
                   font=ModernTheme.FONTS['default'])
    
    # Modern button styling
    style.configure("TButton",
                   background=ModernTheme.COLORS['bg_tertiary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   padding=(12, 8),
                   relief="flat",
                   borderwidth=1,
                   font=ModernTheme.FONTS['default'])
    
    style.map("TButton",
              background=[("active", ModernTheme.COLORS['hover']),
                         ("pressed", ModernTheme.COLORS['bg_accent'])],
              bordercolor=[("focus", ModernTheme.COLORS['border_focus'])])
    
    # Accent button styles
    style.configure("Accent.TButton",
                   background=ModernTheme.COLORS['accent_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   padding=(12, 8),
                   relief="flat",
                   borderwidth=0,
                   font=ModernTheme.FONTS['default'])
    
    style.map("Accent.TButton",
              background=[("active", "#2563EB"),
                         ("pressed", "#1D4ED8")])
    
    # Success button
    style.configure("Success.TButton",
                   background=ModernTheme.COLORS['accent_secondary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   padding=(12, 8),
                   relief="flat",
                   borderwidth=0)
    
    # Danger button
    style.configure("Danger.TButton",
                   background=ModernTheme.COLORS['accent_danger'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   padding=(12, 8),
                   relief="flat",
                   borderwidth=0)
    
    # Label styles
    style.configure("TLabel",
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   padding=5,
                   font=ModernTheme.FONTS['default'])
    
    style.configure("Heading.TLabel",
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   font=ModernTheme.FONTS['heading'])
    
    style.configure("Subheading.TLabel",
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   font=ModernTheme.FONTS['subheading'])
    
    style.configure("Muted.TLabel",
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_muted'],
                   font=ModernTheme.FONTS['small'])
    
    # Entry and Combobox styles
    style.configure("TEntry",
                   fieldbackground=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   bordercolor=ModernTheme.COLORS['border'],
                   lightcolor=ModernTheme.COLORS['border'],
                   darkcolor=ModernTheme.COLORS['border'],
                   insertcolor=ModernTheme.COLORS['text_primary'],
                   padding=8,
                   font=ModernTheme.FONTS['default'])
    
    style.map("TEntry",
              bordercolor=[("focus", ModernTheme.COLORS['border_focus'])])
    
    style.configure("TCombobox",
                   fieldbackground=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   bordercolor=ModernTheme.COLORS['border'],
                   lightcolor=ModernTheme.COLORS['border'],
                   darkcolor=ModernTheme.COLORS['border'],
                   arrowcolor=ModernTheme.COLORS['text_secondary'],
                   padding=8,
                   font=ModernTheme.FONTS['default'])
    
    # Checkbutton and Radiobutton
    style.configure("TCheckbutton",
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   focuscolor=ModernTheme.COLORS['border_focus'],
                   font=ModernTheme.FONTS['default'])
    
    # Frame styles
    style.configure("TFrame",
                   background=ModernTheme.COLORS['bg_primary'],
                   relief="flat",
                   borderwidth=0)
    
    style.configure("Card.TFrame",
                   background=ModernTheme.COLORS['bg_secondary'],
                   relief="flat",
                   borderwidth=1)
    
    # Notebook (tabs) styling
    style.configure("TNotebook",
                   background=ModernTheme.COLORS['bg_primary'],
                   borderwidth=0,
                   tabposition="n")
    
    style.configure("TNotebook.Tab",
                   background=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['text_secondary'],
                   padding=[12, 8],
                   font=ModernTheme.FONTS['default'])
    
    style.map("TNotebook.Tab",
              background=[("selected", ModernTheme.COLORS['bg_primary']),
                         ("active", ModernTheme.COLORS['hover'])],
              foreground=[("selected", ModernTheme.COLORS['text_primary']),
                         ("active", ModernTheme.COLORS['text_primary'])])
    
    # Progressbar
    style.configure("TProgressbar",
                   background=ModernTheme.COLORS['accent_primary'],
                   troughcolor=ModernTheme.COLORS['bg_secondary'],
                   bordercolor=ModernTheme.COLORS['border'],
                   lightcolor=ModernTheme.COLORS['accent_primary'],
                   darkcolor=ModernTheme.COLORS['accent_primary'],
                   borderwidth=0,
                   relief="flat")
    
    # Treeview (for tables)
    style.configure("Treeview",
                   background=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   fieldbackground=ModernTheme.COLORS['bg_secondary'],
                   bordercolor=ModernTheme.COLORS['border'],
                   font=ModernTheme.FONTS['default'])
    
    style.configure("Treeview.Heading",
                   background=ModernTheme.COLORS['bg_tertiary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   font=ModernTheme.FONTS['subheading'])
    
    # Scrollbar
    style.configure("TScrollbar",
                   background=ModernTheme.COLORS['bg_secondary'],
                   troughcolor=ModernTheme.COLORS['bg_primary'],
                   bordercolor=ModernTheme.COLORS['border'],
                   arrowcolor=ModernTheme.COLORS['text_secondary'],
                   darkcolor=ModernTheme.COLORS['bg_secondary'],
                   lightcolor=ModernTheme.COLORS['bg_secondary'])

def apply_dark_theme(root):
    """Legacy function for backward compatibility"""
    apply_modern_theme(root)