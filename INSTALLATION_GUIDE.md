# NetPulse 2.0 - Complete Installation & Distribution Guide

## 🚀 **Installation & Distribution System**

NetPulse 2.0 now includes a comprehensive installation and auto-update system with multiple distribution methods.

## 📦 **Distribution Packages**

### 1. **Professional Installer** (Recommended)
- **File**: `NetPulse-Setup.exe` (Windows) or `NetPulse-Setup` (Linux/macOS)
- **Features**: 
  - Guided installation wizard
  - System integration (shortcuts, PATH)
  - Automatic dependency installation
  - Uninstaller creation
  - Auto-update configuration

### 2. **Portable Package**
- **File**: `NetPulse-2.0.0-portable.zip`
- **Features**:
  - No installation required
  - Run from any location
  - Perfect for USB drives
  - All features included

### 3. **Installer Package**
- **File**: `NetPulse-2.0.0-installer.zip`
- **Features**:
  - Complete installer with wizard
  - Source code included
  - Customizable installation
  - Developer-friendly

## 🔧 **Building Distribution Packages**

### **Windows**
```batch
# Run the build script
cd build_scripts
build.bat

# Or manually:
python build.py
python create_installer.py
```

### **Linux/macOS**
```bash
# Run the build script
cd build_scripts
./build.sh

# Or manually:
python3 build.py
python3 create_installer.py
```

### **Build Options**
```bash
# Build all packages
python build.py

# Skip executable creation
python build.py --no-exe

# Clean build directories only
python build.py --clean-only

# Specify source directory
python build.py --source-dir /path/to/source
```

## 📋 **Installation Methods**

### **Method 1: Professional Installer (Recommended)**

1. **Download**: Get `NetPulse-Setup.exe` from releases
2. **Run**: Double-click the installer
3. **Follow Wizard**: Complete the installation steps
4. **Launch**: Use desktop shortcut or Start Menu

**Installer Features:**
- ✅ Guided installation with progress tracking
- ✅ Automatic dependency installation
- ✅ System integration (shortcuts, PATH)
- ✅ Auto-update configuration
- ✅ Uninstaller creation
- ✅ Professional UI with dark theme

### **Method 2: Portable Installation**

1. **Download**: Get `NetPulse-2.0.0-portable.zip`
2. **Extract**: Unzip to desired location
3. **Run**: Execute `main.py` or `python main.py`
4. **Dependencies**: Install manually if needed

### **Method 3: Developer Installation**

1. **Clone Repository**: `git clone https://github.com/kyywes/NetPulse`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Run**: `python main.py`

## 🔄 **Auto-Update System**

### **Enhanced Auto-Update Features**

- **Automatic Checking**: Checks for updates on startup
- **Silent Updates**: Background downloading and installation
- **Backup & Restore**: Automatic backup before updates
- **Rollback Support**: Restore previous version if update fails
- **Progress Tracking**: Real-time update progress
- **Smart Scheduling**: Configurable update intervals

### **Auto-Update Configuration**

Location: `config/update.json`

```json
{
  "enabled": true,
  "check_on_startup": true,
  "auto_install": true,
  "backup_before_update": true,
  "max_backups": 3,
  "check_interval_hours": 24,
  "download_timeout": 300
}
```

### **Manual Update Check**

```bash
# Check for updates
python updater_enhanced.py check

# Silent check
python updater_enhanced.py silent
```

## 🎯 **Installation Wizard Features**

### **Step 1: Welcome Screen**
- Application overview
- System requirements
- Prerequisites check

### **Step 2: License Agreement**
- MIT License display
- Agreement acceptance

### **Step 3: Installation Location**
- Default path selection
- Custom path option
- Space requirement check

### **Step 4: Component Selection**
- Core application (required)
- Python dependencies
- Auto-update system
- PATH integration

### **Step 5: Shortcuts**
- Desktop shortcut option
- Start Menu entry
- Installation summary

### **Step 6: Installation Progress**
- Real-time progress tracking
- Detailed installation log
- Error handling

### **Step 7: Completion**
- Installation summary
- Launch option
- Finish setup

## 🛠️ **Build System Architecture**

### **Build Scripts**
- `build.py`: Main build script
- `create_installer.py`: Installer creation
- `build.bat`: Windows build script
- `build.sh`: Linux/macOS build script

### **Build Process**
1. **Clean**: Remove previous build files
2. **Prepare**: Copy source files and create build structure
3. **Package**: Create ZIP archives
4. **Executable**: Build standalone executable (optional)
5. **Installer**: Create installer package
6. **Documentation**: Generate release notes
7. **Verification**: Create checksums

### **Output Structure**
```
dist/
├── NetPulse-2.0.0-portable.zip
├── NetPulse-2.0.0-installer.zip
├── NetPulse-Setup.exe
├── NetPulse-2.0.0-ReleaseNotes.txt
└── checksums.txt
```

## ⚙️ **Configuration Management**

### **Installation Configuration**
- **Location**: `config/installation.json`
- **Contents**: Installation details, paths, options
- **Purpose**: Track installation state and preferences

### **Update Configuration**
- **Location**: `config/update.json`
- **Contents**: Auto-update settings and schedule
- **Purpose**: Control update behavior

### **Application Settings**
- **Location**: `config/settings.json`
- **Contents**: User preferences and application state
- **Purpose**: Persist user customizations

## 🔒 **Security Features**

### **Update Verification**
- **Checksums**: SHA-256 verification for all packages
- **Backup System**: Automatic backup before updates
- **Rollback**: Restore previous version if update fails
- **Safe Installation**: Temporary directories for safe updates

### **Installation Security**
- **Permission Checks**: Verify installation permissions
- **Clean Installation**: Remove temporary files after installation
- **Uninstall Support**: Clean removal of all components

## 🚀 **Publishing & Distribution**

### **Release Process**
1. **Version Update**: Update `version.txt`
2. **Build**: Run build scripts
3. **Test**: Verify all packages
4. **Upload**: Upload to GitHub Releases
5. **Announce**: Update documentation

### **GitHub Integration**
- **Auto-Update**: Checks GitHub releases for updates
- **Download**: Downloads from GitHub releases
- **Version Control**: Uses semantic versioning
- **Release Notes**: Automatically formatted

## 🎯 **Usage Examples**

### **End User Installation**
```bash
# Download and run installer
NetPulse-Setup.exe

# Follow installation wizard
# Launch NetPulse from desktop shortcut
```

### **Portable Usage**
```bash
# Extract portable package
unzip NetPulse-2.0.0-portable.zip

# Run directly
cd NetPulse
python main.py
```

### **Developer Setup**
```bash
# Clone repository
git clone https://github.com/kyywes/NetPulse

# Install dependencies
pip install -r requirements.txt

# Build packages
cd build_scripts
python build.py
```

## 📈 **Update Workflow**

### **Automatic Updates**
1. **Startup Check**: Check for updates on application start
2. **Background Download**: Download updates in background
3. **User Notification**: Notify user of available updates
4. **Automatic Installation**: Install updates with user consent
5. **Restart**: Restart application with new version

### **Manual Updates**
1. **Check**: Use "Check for Updates" menu option
2. **Download**: Download update packages
3. **Backup**: Create backup of current installation
4. **Install**: Apply update with progress tracking
5. **Verify**: Verify installation and cleanup

## 🔧 **Troubleshooting**

### **Installation Issues**
- **Permission Errors**: Run installer as administrator
- **Dependency Errors**: Install Python dependencies manually
- **Path Issues**: Check PATH environment variable
- **Antivirus**: Add NetPulse to antivirus exceptions

### **Update Issues**
- **Connection Errors**: Check internet connection
- **Download Failures**: Manually download and install
- **Backup Failures**: Ensure write permissions
- **Rollback**: Use backup restore feature

## 📊 **System Requirements**

### **Minimum Requirements**
- **OS**: Windows 10, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.7+ (for source installation)
- **Memory**: 100MB RAM
- **Storage**: 100MB free space
- **Network**: Internet connection for updates

### **Recommended Requirements**
- **OS**: Windows 11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.9+
- **Memory**: 200MB RAM
- **Storage**: 500MB free space
- **Network**: Broadband internet connection

---

**NetPulse 2.0** - *Professional Network Toolkit with Modern Installation & Auto-Update System*