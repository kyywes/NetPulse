import tkinter as tk
from tkinter import ttk

def apply_github_dark_theme(root: tk.Tk):
    style = ttk.Style(root)
    style.theme_use('clam')

    # palette GitHub Dark
    bg_main      = '#0D1117'  # sfondo primario
    bg_highlight = '#161B22'  # header, selezioni
    fg_default   = '#C9D1D9'  # testo normale
    fg_success   = '#2EA043'  # verde add
    fg_error     = '#F85149'  # rosso remove
    fg_warning   = '#D29922'  # giallo warning
    fg_cmd       = '#58A6FF'  # blu accent

    # finestra
    root.configure(bg=bg_main)
    # generico
    style.configure('.',
        background=bg_main,
        foreground=fg_default,
        fieldbackground=bg_main
    )
    # Label / Button / Entry / Combobox / Checkbutton
    style.configure('TLabel',   background=bg_main, foreground=fg_default)
    style.configure('TButton',  background=bg_highlight, foreground=fg_default)
    style.configure('TEntry',   fieldbackground=bg_main, foreground=fg_default)
    style.configure('TCombobox',fieldbackground=bg_main, foreground=fg_default)
    style.configure('TCheckbutton', background=bg_main, foreground=fg_default)

    style.map('TButton',
        background=[('active', bg_highlight)],
        foreground=[('active', fg_default)]
    )

    # Treeview (rows + header)
    style.configure('Treeview',
        background=bg_main,
        foreground=fg_default,
        fieldbackground=bg_main,
        rowheight=22,
        font=('Consolas', 10)
    )
    style.map('Treeview',
        background=[('selected', bg_highlight)],
        foreground=[('selected', fg_default)]
    )
    style.configure('Treeview.Heading',
        background=bg_highlight,
        foreground=fg_default,
        relief='flat'
    )
    style.map('Treeview.Heading',
        background=[('active', bg_highlight)]
    )

    # Progressbar
    style.configure('Green.Horizontal.TProgressbar',
        troughcolor=bg_main,
        background=fg_success,
        thickness=12
    )

    return {
        'bg_main': bg_main,
        'fg_default': fg_default,
        'fg_success': fg_success,
        'fg_error': fg_error,
        'fg_warning': fg_warning,
        'fg_cmd': fg_cmd
    }
