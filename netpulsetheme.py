import tkinter as tk
from tkinter import ttk

def apply_dark_theme(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    background = '#1e1e1e'
    foreground = '#ffffff'
    field_bg = '#2a2a2a'
    accent = '#3c3f41'

    root.configure(bg=background)
    style.configure('.', background=background, foreground=foreground, fieldbackground=field_bg)
    style.configure('TLabel', background=background, foreground=foreground)
    style.configure('TButton', background=accent, foreground=foreground, padding=6, relief='flat')
    style.map('TButton',
              background=[('active', '#3e3e3e')],
              foreground=[('disabled', '#7f7f7f')])
    style.configure('TEntry', fieldbackground=field_bg, foreground=foreground)
    style.configure('TCombobox', fieldbackground=field_bg, foreground=foreground)
    style.configure('TFrame', background=background)
    style.configure('TCheckbutton', background=background, foreground=foreground)
    style.configure('Horizontal.TProgressbar', background='#4CAF50', troughcolor='#303030')
