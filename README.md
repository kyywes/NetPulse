# NetPulse 2.0 - Modern Network Toolkit

🚀 **A comprehensive network diagnostic and automation tool with modern interface**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/kyywes/NetPulse)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-yellow.svg)](https://python.org)

## ✨ **Features**

### 🎨 **Modern Interface**
- **Tabbed Layout**: Organized tools in logical tabs
- **Professional Dark Theme**: Modern, eye-friendly design
- **Real-time Updates**: Live command output and progress tracking
- **Responsive Design**: Adapts to different screen sizes

### 🔧 **Network Tools**
- **Basic Tools**: Ping, Traceroute, DNS Lookup, Subnet Calculator
- **Advanced Tools**: Port Scanner, Network Discovery, Bandwidth Testing
- **Network Interfaces**: Detailed system network information
- **Multi-threading**: Concurrent operations for faster scanning

### 🤖 **Device Automation**
- **Data Management**: System date and navigation control
- **MCU Control**: Microcontroller management with 5 action types
- **Advanced Configuration**: JSON-based bulk configuration updates
- **Enhanced Backup**: Multiple backup types with compression

### 📊 **Data Management**
- **Command History**: Automatic logging with SQLite database
- **Favorites System**: Save frequently used commands
- **Export Capabilities**: JSON and CSV export options
- **Configuration Management**: Centralized settings with persistence

### 🔄 **Auto-Update System**
- **GitHub Integration**: Automatic update checking
- **Safe Updates**: Backup and rollback capabilities
- **Professional Installer**: Guided installation wizard
- **Cross-Platform**: Windows, Linux, macOS support

## 🏗️ **Project Structure**

```
NetPulse/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── version.txt               # Version information
├── LICENSE                   # MIT License
│
├── netpulse/                 # Main package
│   ├── __init__.py
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── network_tools.py  # Network utilities
│   │   └── config_manager.py # Configuration management
│   ├── gui/                  # User interface
│   │   ├── __init__.py
│   │   ├── application.py    # Modern GUI application
│   │   ├── theme.py         # Theme system
│   │   └── legacy.py        # Legacy GUI (fallback)
│   ├── automation/           # Device automation
│   │   ├── __init__.py
│   │   └── device_manager.py # Device management and automation
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── updater.py       # Auto-update system
│
├── scripts/                  # Build and utility scripts
│   ├── build_scripts/       # Build system
│   │   ├── build.py         # Main build script
│   │   ├── create_installer.py
│   │   ├── build.bat        # Windows build
│   │   └── build.sh         # Linux/macOS build
│   ├── installer/           # Installation wizard
│   │   └── setup_wizard.py  # Professional installer
│   └── netpulse.py         # Legacy core (deprecated)
│
├── tests/                   # Tests and demos
│   ├── test_installation.py # Installation system test
│   ├── test_automation.py   # Automation features test
│   ├── demo_installation.py # Installation demo
│   └── demo_automation.py   # Automation demo
│
├── docs/                    # Documentation
│   ├── README_MODERN.md     # Modern features guide
│   ├── INSTALLATION_GUIDE.md # Complete installation guide
│   └── AUTOMATION_COMMANDS.md # Automation commands reference
│
├── inventory/               # Device inventory (optional)
│   └── db_config.ini       # Database configuration
│
├── config/                  # Runtime configuration
└── data/                   # Application data
    └── netpulse.db         # SQLite database
```

## 🚀 **Quick Start**

### **Installation**

#### **Option 1: Professional Installer (Recommended)**
1. Download `NetPulse-Setup.exe` from releases
2. Run installer and follow the wizard
3. Launch from desktop shortcut

#### **Option 2: From Source**
```bash
# Clone repository
git clone https://github.com/kyywes/NetPulse
cd NetPulse

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

#### **Option 3: Portable**
1. Download `NetPulse-2.0.0-portable.zip`
2. Extract and run `main.py`

### **First Run**
1. The application will check for updates automatically
2. Configure your network settings if needed
3. Start using the network tools from the tabbed interface

## 🎯 **Usage Guide**

### **Basic Network Tools**
- **Ping**: Test connectivity with real-time monitoring
- **Traceroute**: Trace network paths with detailed analysis
- **DNS Lookup**: Resolve domains with multiple record types
- **Subnet Calculator**: Advanced subnet calculations

### **Advanced Network Tools**
- **Port Scanner**: Multi-threaded TCP port scanning
- **Network Discovery**: Find live hosts on network segments
- **Bandwidth Test**: Network performance analysis
- **Network Interfaces**: System interface information

### **Device Automation**
- **Data Management**: `PL001` or `PL001|2024-12-15 10:30:00`
- **MCU Control**: `PL001|enable` or `PL001|restart`
- **Advanced Config**: `PL001|{"MCU_ENABLE": "true"}`
- **Backup**: `PL001|full` or `PL001|mcu`

### **Command History & Favorites**
- All commands are automatically logged
- Double-click history entries to re-execute
- Save frequently used commands as favorites
- Export data in JSON or CSV format

## ⚙️ **Configuration**

### **Application Settings**
- **Location**: `config/settings.json`
- **Auto-save**: Window size, preferences, recent commands
- **Themes**: Dark theme with customizable colors

### **Update Settings**
- **Location**: `config/update.json`
- **Auto-update**: Configurable check intervals
- **Backup**: Automatic backup before updates

### **Database**
- **Location**: `data/netpulse.db`
- **Contents**: Command history, favorites, device profiles
- **Export**: Built-in export capabilities

## 🔧 **Development**

### **Building from Source**
```bash
# Build all packages
cd scripts/build_scripts
python build.py

# Create installer
python create_installer.py

# Run tests
cd ../../tests
python test_installation.py
python test_automation.py
```

### **Package Structure**
- **netpulse.core**: Network tools and configuration
- **netpulse.gui**: User interface components
- **netpulse.automation**: Device management
- **netpulse.utils**: Utilities and updater

### **Adding New Features**
1. Create new modules in appropriate packages
2. Update `__init__.py` files for imports
3. Add GUI components if needed
4. Update documentation

## 🔐 **Security Features**

### **Auto-Update Security**
- SHA-256 checksum verification
- Automatic backup before updates
- Rollback capability
- Secure temporary directories

### **Device Automation Security**
- SSH key management
- Automatic configuration backups
- Command validation
- Error recovery

### **Data Protection**
- SQLite database encryption (optional)
- Configuration file protection
- Secure credential storage
- Audit logging

## 📚 **Documentation**

- **[Installation Guide](docs/INSTALLATION_GUIDE.md)**: Complete installation instructions
- **[Automation Commands](docs/AUTOMATION_COMMANDS.md)**: Device automation reference
- **[Modern Features](docs/README_MODERN.md)**: New features in 2.0

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- Python community for excellent libraries
- Users who provided feedback and suggestions
- Contributors to the open-source ecosystem

## 📞 **Support**

- **GitHub Issues**: [Report bugs and request features](https://github.com/kyywes/NetPulse/issues)
- **Documentation**: Check the `docs/` directory
- **Email**: Contact the development team

---

**NetPulse 2.0** - *Making network diagnostics modern, efficient, and user-friendly*

![NetPulse Interface](https://via.placeholder.com/800x500/0D1117/3B82F6?text=NetPulse+2.0+Modern+Interface)