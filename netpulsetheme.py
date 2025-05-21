from tkinter import ttk

def apply_dark_theme(root):
    root.configure(bg="#1e1e1e")
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background="#1e1e1e", foreground="#dcdcdc",
                    fieldbackground="#2a2a2a", bordercolor="#3c3c3c",
                    lightcolor="#3c3c3c", darkcolor="#1e1e1e",
                    troughcolor="#2a2a2a", relief="flat", borderwidth=0)

    style.configure("TButton", background="#2d2d2d", foreground="#dcdcdc",
                    padding=6, relief="flat")
    style.map("TButton",
              background=[("active", "#3e3e3e")],
              foreground=[("disabled", "#7f7f7f")])

    style.configure("TLabel", background="#1e1e1e", foreground="#dcdcdc", padding=5)
    style.configure("TEntry", fieldbackground="#2a2a2a", foreground="#ffffff")
    style.configure("TCombobox", fieldbackground="#2a2a2a", foreground="#ffffff")
    style.configure("TCheckbutton", background="#1e1e1e", foreground="#dcdcdc")
    style.configure("TFrame", background="#1e1e1e")
    style.configure("Horizontal.TProgressbar", background="#4CAF50",
                    troughcolor="#303030", bordercolor="#1e1e1e",
                    lightcolor="#4CAF50", darkcolor="#4CAF50")
