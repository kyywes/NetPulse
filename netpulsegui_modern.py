import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional

from network_tools import NetworkTools
from netpulsetheme import apply_modern_theme, ModernTheme
from netpulse_automate import NetPulseAutomate
from config_manager import ConfigManager

class ModernNetPulseGUI:
    """Modern NetPulse GUI with tabbed interface and enhanced features"""
    
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.network_tools = NetworkTools()
        self.automate = None
        
        # Initialize automation if DB config exists
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_ini = os.path.join(base_dir, "inventory", "db_config.ini")
        if os.path.isfile(db_ini):
            try:
                self.automate = NetPulseAutomate(db_ini)
            except Exception as e:
                print(f"Warning: Could not initialize automation: {e}")
        
        # UI State
        self.current_thread = None
        self.current_task = None
        
        # Setup UI
        self._setup_main_window()
        self._create_menu()
        self._create_main_interface()
        
        # Load saved state
        self._load_window_state()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_main_window(self):
        """Setup main window properties"""
        apply_modern_theme(self.root)
        
        self.root.title("NetPulse - Modern Network Toolkit")
        self.root.geometry(self.config.get_setting('window_geometry', '1200x800'))
        self.root.minsize(800, 600)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap(os.path.join(os.path.dirname(__file__), 'icon.ico'))
        except:
            pass
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root, bg=ModernTheme.COLORS['bg_primary'], 
                         fg=ModernTheme.COLORS['text_primary'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.COLORS['bg_secondary'],
                           fg=ModernTheme.COLORS['text_primary'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Command", command=self._new_command, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Export History", command=self._export_history)
        file_menu.add_command(label="Export Favorites", command=self._export_favorites)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.COLORS['bg_secondary'],
                            fg=ModernTheme.COLORS['text_primary'])
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Network Interfaces", command=self._show_network_interfaces)
        tools_menu.add_command(label="Clear History", command=self._clear_history)
        tools_menu.add_command(label="Clear Output", command=self._clear_output)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.COLORS['bg_secondary'],
                           fg=ModernTheme.COLORS['text_primary'])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Shortcuts", command=self._show_shortcuts)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self._new_command())
        self.root.bind('<Control-Return>', lambda e: self._execute_command())
        self.root.bind('<Control-l>', lambda e: self._clear_output())
        self.root.bind('<F5>', lambda e: self._execute_command())
        self.root.bind('<Escape>', lambda e: self._stop_command())
    
    def _create_main_interface(self):
        """Create main tabbed interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self._create_basic_tools_tab()
        self._create_advanced_tools_tab()
        self._create_automation_tab()
        self._create_history_tab()
        self._create_favorites_tab()
        
        # Status bar
        self._create_status_bar()
    
    def _create_basic_tools_tab(self):
        """Create basic network tools tab"""
        # Basic Tools Tab
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Basic Tools")
        
        # Tool selection and parameters
        control_frame = ttk.Frame(basic_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Command selection
        ttk.Label(control_frame, text="Tool:", style="Subheading.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.basic_command_var = tk.StringVar(value="Ping")
        self.basic_command_combo = ttk.Combobox(
            control_frame,
            textvariable=self.basic_command_var,
            values=["Ping", "Traceroute", "Nslookup", "Subnet Info"],
            state="readonly",
            width=15
        )
        self.basic_command_combo.grid(row=0, column=1, padx=(0, 20))
        
        # Parameters
        ttk.Label(control_frame, text="Target:", style="Subheading.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 10))
        
        self.basic_param_var = tk.StringVar()
        self.basic_param_entry = ttk.Entry(control_frame, textvariable=self.basic_param_var, width=30)
        self.basic_param_entry.grid(row=0, column=3, padx=(0, 10))
        self.basic_param_entry.bind("<Return>", lambda e: self._execute_basic_command())
        
        # Quick targets dropdown
        self.recent_targets = ttk.Combobox(control_frame, values=self.config.get_recent_commands(), width=20)
        self.recent_targets.grid(row=0, column=4, padx=(0, 10))
        self.recent_targets.bind("<<ComboboxSelected>>", self._on_recent_selected)
        
        # Options frame
        options_frame = ttk.Frame(basic_frame)
        options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Ping options
        self.continuous_ping = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Continuous Ping", 
                       variable=self.continuous_ping).pack(side="left", padx=(0, 20))
        
        self.ping_count_var = tk.StringVar(value="4")
        ttk.Label(options_frame, text="Count:").pack(side="left", padx=(0, 5))
        ttk.Entry(options_frame, textvariable=self.ping_count_var, width=5).pack(side="left", padx=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(basic_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Execute", style="Accent.TButton",
                  command=self._execute_basic_command).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Stop", style="Danger.TButton",
                  command=self._stop_command).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Clear", command=self._clear_output).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Add to Favorites", style="Success.TButton",
                  command=self._add_to_favorites).pack(side="left", padx=(0, 10))
        
        # Output frame
        output_frame = ttk.Frame(basic_frame)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create output text with scrollbar
        self.basic_output_text = tk.Text(
            output_frame,
            wrap="word",
            bg=ModernTheme.COLORS['bg_secondary'],
            fg=ModernTheme.COLORS['text_primary'],
            insertbackground=ModernTheme.COLORS['text_primary'],
            font=ModernTheme.FONTS['mono'],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10
        )
        
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.basic_output_text.yview)
        self.basic_output_text.configure(yscrollcommand=scrollbar.set)
        
        self.basic_output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure text tags for colored output
        self.basic_output_text.tag_config("success", foreground=ModernTheme.COLORS['success'])
        self.basic_output_text.tag_config("error", foreground=ModernTheme.COLORS['error'])
        self.basic_output_text.tag_config("warning", foreground=ModernTheme.COLORS['warning'])
        self.basic_output_text.tag_config("info", foreground=ModernTheme.COLORS['accent_primary'])
        self.basic_output_text.tag_config("timestamp", foreground=ModernTheme.COLORS['text_muted'])
    
    def _create_advanced_tools_tab(self):
        """Create advanced network tools tab"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced Tools")
        
        # Tool selection
        control_frame = ttk.Frame(advanced_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(control_frame, text="Advanced Tool:", style="Subheading.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.advanced_command_var = tk.StringVar(value="Port Scan")
        self.advanced_command_combo = ttk.Combobox(
            control_frame,
            textvariable=self.advanced_command_var,
            values=["Port Scan", "Network Discovery", "Bandwidth Test", "Network Interfaces"],
            state="readonly",
            width=20
        )
        self.advanced_command_combo.grid(row=0, column=1, padx=(0, 20))
        self.advanced_command_combo.bind("<<ComboboxSelected>>", self._on_advanced_command_change)
        
        # Parameters frame
        self.advanced_params_frame = ttk.Frame(advanced_frame)
        self.advanced_params_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Default parameters for port scan
        self._setup_port_scan_params()
        
        # Buttons
        buttons_frame = ttk.Frame(advanced_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Execute", style="Accent.TButton",
                  command=self._execute_advanced_command).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Stop", style="Danger.TButton",
                  command=self._stop_command).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Clear", command=self._clear_advanced_output).pack(side="left", padx=(0, 10))
        
        # Output frame
        output_frame = ttk.Frame(advanced_frame)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create output text with scrollbar
        self.advanced_output_text = tk.Text(
            output_frame,
            wrap="word",
            bg=ModernTheme.COLORS['bg_secondary'],
            fg=ModernTheme.COLORS['text_primary'],
            insertbackground=ModernTheme.COLORS['text_primary'],
            font=ModernTheme.FONTS['mono'],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10
        )
        
        scrollbar_adv = ttk.Scrollbar(output_frame, orient="vertical", command=self.advanced_output_text.yview)
        self.advanced_output_text.configure(yscrollcommand=scrollbar_adv.set)
        
        self.advanced_output_text.pack(side="left", fill="both", expand=True)
        scrollbar_adv.pack(side="right", fill="y")
        
        # Configure text tags
        self.advanced_output_text.tag_config("success", foreground=ModernTheme.COLORS['success'])
        self.advanced_output_text.tag_config("error", foreground=ModernTheme.COLORS['error'])
        self.advanced_output_text.tag_config("warning", foreground=ModernTheme.COLORS['warning'])
        self.advanced_output_text.tag_config("info", foreground=ModernTheme.COLORS['accent_primary'])
        self.advanced_output_text.tag_config("timestamp", foreground=ModernTheme.COLORS['text_muted'])
    
    def _create_automation_tab(self):
        """Create device automation tab"""
        if not self.automate:
            # Create placeholder tab
            automation_frame = ttk.Frame(self.notebook)
            self.notebook.add(automation_frame, text="Automation")
            
            ttk.Label(automation_frame, text="Database configuration not found.\nAutomation features are disabled.",
                     style="Subheading.TLabel", justify="center").pack(expand=True)
            return
        
        automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(automation_frame, text="Automation")
        
        # Device selection
        control_frame = ttk.Frame(automation_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(control_frame, text="Device Marker:", style="Subheading.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.device_marker_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.device_marker_var, width=20).grid(row=0, column=1, padx=(0, 20))
        
        # Automation commands
        ttk.Label(control_frame, text="Command:", style="Subheading.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 10))
        
        self.automation_command_var = tk.StringVar(value="Connect Devices")
        automation_combo = ttk.Combobox(
            control_frame,
            textvariable=self.automation_command_var,
            values=["Connect Devices", "Backup Config", "PAI-PL Version", "Data Management", "MCU Control", "Advanced MCU Config"],
            state="readonly",
            width=20
        )
        automation_combo.grid(row=0, column=3, padx=(0, 20))
        automation_combo.bind("<<ComboboxSelected>>", self._on_automation_command_change)
        
        # Additional parameters frame
        self.automation_params_frame = ttk.Frame(automation_frame)
        self.automation_params_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Setup default parameters
        self._setup_automation_params()
        
        # Buttons
        buttons_frame = ttk.Frame(automation_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Execute", style="Accent.TButton",
                  command=self._execute_automation_command).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Clear", command=self._clear_automation_output).pack(side="left", padx=(0, 10))
        
        # Output
        output_frame = ttk.Frame(automation_frame)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.automation_output_text = tk.Text(
            output_frame,
            wrap="word",
            bg=ModernTheme.COLORS['bg_secondary'],
            fg=ModernTheme.COLORS['text_primary'],
            insertbackground=ModernTheme.COLORS['text_primary'],
            font=ModernTheme.FONTS['mono'],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10
        )
        
        scrollbar_auto = ttk.Scrollbar(output_frame, orient="vertical", command=self.automation_output_text.yview)
        self.automation_output_text.configure(yscrollcommand=scrollbar_auto.set)
        
        self.automation_output_text.pack(side="left", fill="both", expand=True)
        scrollbar_auto.pack(side="right", fill="y")
        
        # Configure text tags
        self.automation_output_text.tag_config("success", foreground=ModernTheme.COLORS['success'])
        self.automation_output_text.tag_config("error", foreground=ModernTheme.COLORS['error'])
        self.automation_output_text.tag_config("warning", foreground=ModernTheme.COLORS['warning'])
        self.automation_output_text.tag_config("info", foreground=ModernTheme.COLORS['accent_primary'])

    def _setup_automation_params(self):
        """Setup automation command parameters"""
        for widget in self.automation_params_frame.winfo_children():
            widget.destroy()
        
        command = self.automation_command_var.get()
        
        if command == "Data Management":
            ttk.Label(self.automation_params_frame, text="New Date (optional):").grid(row=0, column=0, sticky="w", padx=(0, 10))
            self.data_new_date_var = tk.StringVar()
            ttk.Entry(self.automation_params_frame, textvariable=self.data_new_date_var, width=20).grid(row=0, column=1, padx=(0, 10))
            ttk.Label(self.automation_params_frame, text="Format: YYYY-MM-DD HH:MM:SS", style="Muted.TLabel").grid(row=0, column=2, sticky="w")
            
        elif command == "MCU Control":
            ttk.Label(self.automation_params_frame, text="Action:").grid(row=0, column=0, sticky="w", padx=(0, 10))
            self.mcu_action_var = tk.StringVar(value="status")
            mcu_combo = ttk.Combobox(self.automation_params_frame, textvariable=self.mcu_action_var,
                                   values=["status", "enable", "disable", "config", "restart"], 
                                   state="readonly", width=15)
            mcu_combo.grid(row=0, column=1, padx=(0, 10))
            
            ttk.Label(self.automation_params_frame, text="Config File:").grid(row=0, column=2, sticky="w", padx=(0, 10))
            self.mcu_config_file_var = tk.StringVar(value="CONFIGURATION")
            ttk.Entry(self.automation_params_frame, textvariable=self.mcu_config_file_var, width=15).grid(row=0, column=3)
            
        elif command == "Advanced MCU Config":
            ttk.Label(self.automation_params_frame, text="Config Updates (JSON):").grid(row=0, column=0, sticky="w", padx=(0, 10))
            self.mcu_updates_var = tk.StringVar(value='{"MCU_ENABLE": "true"}')
            ttk.Entry(self.automation_params_frame, textvariable=self.mcu_updates_var, width=40).grid(row=0, column=1, columnspan=2, padx=(0, 10))
            
        elif command == "Backup Config":
            ttk.Label(self.automation_params_frame, text="Backup Type:").grid(row=0, column=0, sticky="w", padx=(0, 10))
            self.backup_type_var = tk.StringVar(value="running")
            backup_combo = ttk.Combobox(self.automation_params_frame, textvariable=self.backup_type_var,
                                      values=["running", "startup", "mcu", "full"], 
                                      state="readonly", width=15)
            backup_combo.grid(row=0, column=1)
    
    def _on_automation_command_change(self, event=None):
        """Handle automation command selection change"""
        self._setup_automation_params()
    
    def _create_history_tab(self):
        """Create command history tab"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="History")
        
        # Controls
        control_frame = ttk.Frame(history_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(control_frame, text="Refresh", command=self._refresh_history).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Clear History", style="Danger.TButton",
                  command=self._clear_history).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Export History", command=self._export_history).pack(side="left", padx=(0, 10))
        
        # History treeview
        tree_frame = ttk.Frame(history_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ("timestamp", "command", "parameters", "status", "duration")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        self.history_tree.heading("timestamp", text="Timestamp")
        self.history_tree.heading("command", text="Command")
        self.history_tree.heading("parameters", text="Parameters")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("duration", text="Duration (s)")
        
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("command", width=100)
        self.history_tree.column("parameters", width=200)
        self.history_tree.column("status", width=80)
        self.history_tree.column("duration", width=80)
        
        # Scrollbar for history tree
        history_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to execute command
        self.history_tree.bind("<Double-1>", self._on_history_double_click)
        
        # Load initial history
        self._refresh_history()
    
    def _create_favorites_tab(self):
        """Create favorites tab"""
        favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(favorites_frame, text="Favorites")
        
        # Controls
        control_frame = ttk.Frame(favorites_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(control_frame, text="Add Favorite", style="Success.TButton",
                  command=self._add_favorite_dialog).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Remove Selected", style="Danger.TButton",
                  command=self._remove_favorite).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Export Favorites", command=self._export_favorites).pack(side="left", padx=(0, 10))
        
        # Favorites treeview
        tree_frame = ttk.Frame(favorites_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ("name", "command", "parameters", "description")
        self.favorites_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        self.favorites_tree.heading("name", text="Name")
        self.favorites_tree.heading("command", text="Command")
        self.favorites_tree.heading("parameters", text="Parameters")
        self.favorites_tree.heading("description", text="Description")
        
        self.favorites_tree.column("name", width=120)
        self.favorites_tree.column("command", width=100)
        self.favorites_tree.column("parameters", width=150)
        self.favorites_tree.column("description", width=200)
        
        # Scrollbar for favorites tree
        favorites_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=favorites_scrollbar.set)
        
        self.favorites_tree.pack(side="left", fill="both", expand=True)
        favorites_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to execute command
        self.favorites_tree.bind("<Double-1>", self._on_favorites_double_click)
        
        # Load initial favorites
        self._refresh_favorites()
    
    def _create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side="left", padx=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Connection status
        self.connection_var = tk.StringVar(value="Ready")
        connection_label = ttk.Label(status_frame, textvariable=self.connection_var, style="Muted.TLabel")
        connection_label.pack(side="right")
    
    def _setup_port_scan_params(self):
        """Setup port scan parameters"""
        for widget in self.advanced_params_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.advanced_params_frame, text="Target:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.port_scan_target_var = tk.StringVar()
        ttk.Entry(self.advanced_params_frame, textvariable=self.port_scan_target_var, width=20).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(self.advanced_params_frame, text="Ports:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.port_scan_ports_var = tk.StringVar(value="1-1000")
        ttk.Entry(self.advanced_params_frame, textvariable=self.port_scan_ports_var, width=15).grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(self.advanced_params_frame, text="Timeout:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.port_scan_timeout_var = tk.StringVar(value="3")
        ttk.Entry(self.advanced_params_frame, textvariable=self.port_scan_timeout_var, width=5).grid(row=0, column=5)
    
    def _setup_network_discovery_params(self):
        """Setup network discovery parameters"""
        for widget in self.advanced_params_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.advanced_params_frame, text="Network (CIDR):").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.network_discovery_target_var = tk.StringVar(value="192.168.1.0/24")
        ttk.Entry(self.advanced_params_frame, textvariable=self.network_discovery_target_var, width=20).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(self.advanced_params_frame, text="Timeout:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.network_discovery_timeout_var = tk.StringVar(value="3")
        ttk.Entry(self.advanced_params_frame, textvariable=self.network_discovery_timeout_var, width=5).grid(row=0, column=3)
    
    def _setup_bandwidth_test_params(self):
        """Setup bandwidth test parameters"""
        for widget in self.advanced_params_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.advanced_params_frame, text="Target:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.bandwidth_test_target_var = tk.StringVar(value="8.8.8.8")
        ttk.Entry(self.advanced_params_frame, textvariable=self.bandwidth_test_target_var, width=20).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(self.advanced_params_frame, text="Duration (s):").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.bandwidth_test_duration_var = tk.StringVar(value="10")
        ttk.Entry(self.advanced_params_frame, textvariable=self.bandwidth_test_duration_var, width=5).grid(row=0, column=3)
    
    def _on_advanced_command_change(self, event=None):
        """Handle advanced command selection change"""
        command = self.advanced_command_var.get()
        if command == "Port Scan":
            self._setup_port_scan_params()
        elif command == "Network Discovery":
            self._setup_network_discovery_params()
        elif command == "Bandwidth Test":
            self._setup_bandwidth_test_params()
        else:
            # Clear params for other commands
            for widget in self.advanced_params_frame.winfo_children():
                widget.destroy()
    
    def _on_recent_selected(self, event=None):
        """Handle recent target selection"""
        selected = self.recent_targets.get()
        if selected:
            self.basic_param_var.set(selected)
    
    def _execute_basic_command(self):
        """Execute basic network command"""
        command = self.basic_command_var.get().lower()
        params = self.basic_param_var.get().strip()
        
        if not params:
            messagebox.showwarning("Warning", "Please enter a target parameter.")
            return
        
        self._clear_basic_output()
        self.status_var.set("Executing command...")
        self.progress.start(10)
        
        # Start command in thread
        self.current_thread = threading.Thread(target=self._run_basic_command, args=(command, params), daemon=True)
        self.current_thread.start()
    
    def _run_basic_command(self, command: str, params: str):
        """Run basic command in thread"""
        start_time = time.time()
        
        try:
            if command == "ping":
                continuous = self.continuous_ping.get()
                count = int(self.ping_count_var.get()) if not continuous else 4
                
                if continuous:
                    result = self.network_tools.ping(params, continuous=True, callback=self._live_output_basic)
                else:
                    result = self.network_tools.ping(params, count=count)
                    
            elif command == "traceroute":
                result = self.network_tools.traceroute(params)
            elif command == "nslookup":
                result = self.network_tools.nslookup(params)
            elif command == "subnet info":
                result = self.network_tools.calc_subnet_info(params)
            else:
                result = {"error": "Unknown command"}
            
            execution_time = time.time() - start_time
            
            # Update UI in main thread
            self.root.after(0, self._display_basic_result, result, execution_time)
            
            # Add to history
            self.config.add_to_history(command, params, execution_time, result.get('success', False), 
                                     self.network_tools.format_output(result))
            
        except Exception as e:
            error_result = {"error": str(e), "success": False}
            execution_time = time.time() - start_time
            self.root.after(0, self._display_basic_result, error_result, execution_time)
    
    def _display_basic_result(self, result: dict, execution_time: float):
        """Display basic command result"""
        self.progress.stop()
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.basic_output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Format and display result
        if result.get('success', True):
            formatted_output = self.network_tools.format_output(result)
            self._append_colored_text(self.basic_output_text, formatted_output)
            self.status_var.set(f"Command completed in {execution_time:.2f}s")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.basic_output_text.insert(tk.END, f"Error: {error_msg}\n", "error")
            self.status_var.set(f"Command failed after {execution_time:.2f}s")
        
        self.basic_output_text.see(tk.END)
        
        # Update recent targets
        self._update_recent_targets(self.basic_param_var.get())
    
    def _live_output_basic(self, line: str):
        """Handle live output for basic commands"""
        self.root.after(0, self._append_live_line, self.basic_output_text, line)
    
    def _append_live_line(self, text_widget, line: str):
        """Append live line to text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        text_widget.insert(tk.END, f"[{timestamp}] {line}\n")
        text_widget.see(tk.END)
    
    def _append_colored_text(self, text_widget, text: str):
        """Append colored text based on content"""
        lines = text.split('\n')
        for line in lines:
            lower_line = line.lower()
            if 'error' in lower_line or 'failed' in lower_line or 'timeout' in lower_line:
                tag = "error"
            elif 'success' in lower_line or 'reply' in lower_line or 'open' in lower_line:
                tag = "success"
            elif 'warning' in lower_line:
                tag = "warning"
            else:
                tag = "info"
            
            text_widget.insert(tk.END, line + '\n', tag)
    
    def _execute_advanced_command(self):
        """Execute advanced network command"""
        command = self.advanced_command_var.get()
        
        self._clear_advanced_output()
        self.status_var.set("Executing advanced command...")
        self.progress.start(10)
        
        # Start command in thread
        self.current_thread = threading.Thread(target=self._run_advanced_command, args=(command,), daemon=True)
        self.current_thread.start()
    
    def _run_advanced_command(self, command: str):
        """Run advanced command in thread"""
        start_time = time.time()
        
        try:
            if command == "Port Scan":
                target = self.port_scan_target_var.get().strip()
                ports = self.port_scan_ports_var.get().strip()
                timeout = int(self.port_scan_timeout_var.get())
                
                if not target:
                    raise ValueError("Target is required for port scan")
                
                result = self.network_tools.port_scan(target, ports, timeout, self._live_output_advanced)
                
            elif command == "Network Discovery":
                network = self.network_discovery_target_var.get().strip()
                timeout = int(self.network_discovery_timeout_var.get())
                
                if not network:
                    raise ValueError("Network is required for discovery")
                
                result = self.network_tools.network_discovery(network, timeout, self._live_output_advanced)
                
            elif command == "Bandwidth Test":
                target = self.bandwidth_test_target_var.get().strip()
                duration = int(self.bandwidth_test_duration_var.get())
                
                if not target:
                    raise ValueError("Target is required for bandwidth test")
                
                result = self.network_tools.bandwidth_test(target, duration, self._live_output_advanced)
                
            elif command == "Network Interfaces":
                result = self.network_tools.get_network_interfaces()
                
            else:
                result = {"error": "Unknown command"}
            
            execution_time = time.time() - start_time
            
            # Update UI in main thread
            self.root.after(0, self._display_advanced_result, result, execution_time)
            
        except Exception as e:
            error_result = {"error": str(e), "success": False}
            execution_time = time.time() - start_time
            self.root.after(0, self._display_advanced_result, error_result, execution_time)
    
    def _display_advanced_result(self, result: dict, execution_time: float):
        """Display advanced command result"""
        self.progress.stop()
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.advanced_output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Format and display result
        if result.get('success', True):
            formatted_output = self.network_tools.format_output(result)
            self._append_colored_text(self.advanced_output_text, formatted_output)
            self.status_var.set(f"Command completed in {execution_time:.2f}s")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.advanced_output_text.insert(tk.END, f"Error: {error_msg}\n", "error")
            self.status_var.set(f"Command failed after {execution_time:.2f}s")
        
        self.advanced_output_text.see(tk.END)
    
    def _live_output_advanced(self, line: str):
        """Handle live output for advanced commands"""
        self.root.after(0, self._append_live_line, self.advanced_output_text, line)
    
    def _execute_automation_command(self):
        """Execute automation command"""
        if not self.automate:
            messagebox.showerror("Error", "Automation is not available")
            return
        
        command = self.automation_command_var.get().lower()
        marker = self.device_marker_var.get().strip()
        
        if not marker:
            messagebox.showwarning("Warning", "Please enter a device marker.")
            return
        
        self._clear_automation_output()
        self.status_var.set("Executing automation command...")
        self.progress.start(10)
        
        # Start command in thread
        self.current_thread = threading.Thread(target=self._run_automation_command, args=(command, marker), daemon=True)
        self.current_thread.start()
    
    def _run_automation_command(self, command: str, marker: str):
        """Run automation command in thread"""
        start_time = time.time()
        
        try:
            if command == "connect devices":
                result = self.automate.connect_devices(marker)
            elif command == "backup config":
                backup_type = getattr(self, 'backup_type_var', tk.StringVar(value="running")).get()
                result = self.automate.backup_config(marker, backup_type)
            elif command == "pai-pl version":
                result = self.automate.show_pai_version(marker)
            elif command == "data management":
                new_date = getattr(self, 'data_new_date_var', tk.StringVar()).get().strip()
                new_date = new_date if new_date else None
                result = self.automate.data(marker, new_date)
            elif command == "mcu control":
                action = getattr(self, 'mcu_action_var', tk.StringVar(value="status")).get()
                config_file = getattr(self, 'mcu_config_file_var', tk.StringVar(value="CONFIGURATION")).get()
                result = self.automate.mcu(marker, action, config_file)
            elif command == "advanced mcu config":
                import json
                try:
                    updates_str = getattr(self, 'mcu_updates_var', tk.StringVar(value="{}")).get()
                    config_updates = json.loads(updates_str) if updates_str.strip() else None
                    result = self.automate.advanced_mcu_config(marker, config_updates)
                except json.JSONDecodeError:
                    result = {"error": "Invalid JSON format in config updates"}
            else:
                result = {"error": "Unknown automation command"}
            
            execution_time = time.time() - start_time
            
            # Update UI in main thread
            self.root.after(0, self._display_automation_result, result, execution_time)
            
        except Exception as e:
            error_result = {"error": str(e), "success": False}
            execution_time = time.time() - start_time
            self.root.after(0, self._display_automation_result, error_result, execution_time)
    
    def _display_automation_result(self, result: dict, execution_time: float):
        """Display automation command result"""
        self.progress.stop()
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.automation_output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Format and display result
        if result.get('success', True):
            formatted_output = self.network_tools.format_output(result)
            self._append_colored_text(self.automation_output_text, formatted_output)
            self.status_var.set(f"Command completed in {execution_time:.2f}s")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.automation_output_text.insert(tk.END, f"Error: {error_msg}\n", "error")
            self.status_var.set(f"Command failed after {execution_time:.2f}s")
        
        self.automation_output_text.see(tk.END)
    
    def _stop_command(self):
        """Stop current command execution"""
        self.network_tools.stop_all_scans()
        self.status_var.set("Command stopped")
        self.progress.stop()
    
    def _clear_output(self):
        """Clear basic output"""
        self._clear_basic_output()
    
    def _clear_basic_output(self):
        """Clear basic output"""
        self.basic_output_text.delete("1.0", tk.END)
    
    def _clear_advanced_output(self):
        """Clear advanced output"""
        self.advanced_output_text.delete("1.0", tk.END)
    
    def _clear_automation_output(self):
        """Clear automation output"""
        if hasattr(self, 'automation_output_text'):
            self.automation_output_text.delete("1.0", tk.END)
    
    def _new_command(self):
        """Create new command (clear inputs and focus)"""
        self.basic_param_var.set("")
        self.basic_param_entry.focus()
    
    def _add_to_favorites(self):
        """Add current command to favorites"""
        command = self.basic_command_var.get()
        params = self.basic_param_var.get().strip()
        
        if not params:
            messagebox.showwarning("Warning", "Please enter parameters before adding to favorites.")
            return
        
        # Show dialog to get name and description
        self._show_add_favorite_dialog(command, params)
    
    def _show_add_favorite_dialog(self, command: str, params: str):
        """Show dialog to add favorite"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Favorites")
        dialog.geometry("400x200")
        dialog.configure(bg=ModernTheme.COLORS['bg_primary'])
        dialog.grab_set()
        
        # Center dialog
        dialog.transient(self.root)
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Name
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        name_var = tk.StringVar(value=f"{command} {params}")
        ttk.Entry(dialog, textvariable=name_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        # Description
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=40).grid(row=1, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def save_favorite():
            name = name_var.get().strip()
            desc = desc_var.get().strip()
            
            if not name:
                messagebox.showwarning("Warning", "Please enter a name.")
                return
            
            self.config.add_favorite(name, command, params, desc)
            self._refresh_favorites()
            dialog.destroy()
            messagebox.showinfo("Success", "Favorite added successfully!")
        
        ttk.Button(button_frame, text="Save", style="Accent.TButton", command=save_favorite).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
    
    def _add_favorite_dialog(self):
        """Show dialog to add new favorite"""
        self._show_add_favorite_dialog("", "")
    
    def _remove_favorite(self):
        """Remove selected favorite"""
        selection = self.favorites_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a favorite to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this favorite?"):
            item = self.favorites_tree.item(selection[0])
            favorite_id = item['values'][0]  # Assuming ID is stored as first hidden value
            
            # Remove from database
            self.config.remove_favorite(favorite_id)
            self._refresh_favorites()
    
    def _refresh_history(self):
        """Refresh command history"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Load history from database
        history = self.config.get_history()
        
        for entry in history:
            timestamp = entry['timestamp']
            command = entry['command']
            parameters = entry['parameters']
            status = "Success" if entry['success'] else "Failed"
            duration = f"{entry['execution_time']:.2f}" if entry['execution_time'] else "N/A"
            
            self.history_tree.insert("", "end", values=(timestamp, command, parameters, status, duration))
    
    def _refresh_favorites(self):
        """Refresh favorites list"""
        # Clear existing items
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)
        
        # Load favorites from database
        favorites = self.config.get_favorites()
        
        for favorite in favorites:
            self.favorites_tree.insert("", "end", values=(favorite['name'], favorite['command'], favorite['parameters'], favorite['description']))
    
    def _clear_history(self):
        """Clear command history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all command history?"):
            self.config.clear_history()
            self._refresh_history()
            messagebox.showinfo("Success", "Command history cleared.")
    
    def _export_history(self):
        """Export command history"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            if file_path.endswith('.csv'):
                self._export_history_csv(file_path)
            else:
                if self.config.export_data(file_path, 'history'):
                    messagebox.showinfo("Success", f"History exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export history")
    
    def _export_favorites(self):
        """Export favorites"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            if file_path.endswith('.csv'):
                self._export_favorites_csv(file_path)
            else:
                if self.config.export_data(file_path, 'favorites'):
                    messagebox.showinfo("Success", f"Favorites exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export favorites")
    
    def _export_history_csv(self, file_path: str):
        """Export history to CSV"""
        try:
            history = self.config.get_history()
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'command', 'parameters', 'success', 'execution_time']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for entry in history:
                    writer.writerow({k: entry.get(k, '') for k in fieldnames})
            messagebox.showinfo("Success", f"History exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {str(e)}")
    
    def _export_favorites_csv(self, file_path: str):
        """Export favorites to CSV"""
        try:
            favorites = self.config.get_favorites()
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'command', 'parameters', 'description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for favorite in favorites:
                    writer.writerow({k: favorite.get(k, '') for k in fieldnames})
            messagebox.showinfo("Success", f"Favorites exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export favorites: {str(e)}")
    
    def _on_history_double_click(self, event):
        """Handle double-click on history item"""
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            command = item['values'][1]
            parameters = item['values'][2]
            
            # Set the command in basic tools
            self.basic_command_var.set(command.title())
            self.basic_param_var.set(parameters)
            
            # Switch to basic tools tab
            self.notebook.select(0)
    
    def _on_favorites_double_click(self, event):
        """Handle double-click on favorites item"""
        selection = self.favorites_tree.selection()
        if selection:
            item = self.favorites_tree.item(selection[0])
            command = item['values'][1]
            parameters = item['values'][2]
            
            # Set the command in basic tools
            self.basic_command_var.set(command.title())
            self.basic_param_var.set(parameters)
            
            # Switch to basic tools tab
            self.notebook.select(0)
    
    def _update_recent_targets(self, target: str):
        """Update recent targets list"""
        if target:
            recent = self.config.get_recent_commands(10)
            if target not in recent:
                recent.insert(0, target)
                recent = recent[:10]  # Keep only last 10
            
            self.recent_targets['values'] = recent
    
    def _show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        messagebox.showinfo("Settings", "Settings dialog coming soon!")
    
    def _show_network_interfaces(self):
        """Show network interfaces information"""
        result = self.network_tools.get_network_interfaces()
        
        # Create new window to display interfaces
        interfaces_window = tk.Toplevel(self.root)
        interfaces_window.title("Network Interfaces")
        interfaces_window.geometry("600x400")
        interfaces_window.configure(bg=ModernTheme.COLORS['bg_primary'])
        
        # Create text widget to display interfaces
        text_widget = tk.Text(
            interfaces_window,
            bg=ModernTheme.COLORS['bg_secondary'],
            fg=ModernTheme.COLORS['text_primary'],
            font=ModernTheme.FONTS['mono']
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display interfaces information
        if result.get('success'):
            formatted_output = self.network_tools.format_output(result)
            text_widget.insert(tk.END, formatted_output)
        else:
            text_widget.insert(tk.END, f"Error: {result.get('error', 'Unknown error')}")
        
        text_widget.config(state='disabled')
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """NetPulse - Modern Network Toolkit

Version: 1.4.1+

A comprehensive network diagnostic and automation tool with modern interface.

Features:
• Network diagnostics (Ping, Traceroute, Nslookup)
• Advanced tools (Port Scanner, Network Discovery, Bandwidth Test)
• Device automation and management
• Command history and favorites
• Export capabilities
• Modern dark theme interface

© 2024 NetPulse Development Team
"""
        messagebox.showinfo("About NetPulse", about_text)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """Keyboard Shortcuts:

Ctrl+N      New Command
Ctrl+Enter  Execute Command
F5          Execute Command
Ctrl+L      Clear Output
Escape      Stop Command

Tab Navigation:
• Basic Tools
• Advanced Tools
• Automation
• History
• Favorites
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def _load_window_state(self):
        """Load saved window state"""
        geometry = self.config.get_setting('window_geometry')
        if geometry:
            try:
                self.root.geometry(geometry)
            except:
                pass
    
    def _save_window_state(self):
        """Save current window state"""
        geometry = self.root.geometry()
        self.config.set_setting('window_geometry', geometry)
    
    def _on_closing(self):
        """Handle window closing"""
        self._save_window_state()
        self.network_tools.stop_all_scans()
        self.root.destroy()