# NetPulse 2.0 - Advanced Automation Commands Guide

## 🔧 **Enhanced Automation Commands**

NetPulse 2.0 now includes powerful automation commands for advanced device management and configuration.

### 📊 **Data Management Command**

**Purpose**: Manage system date and navigation on CPU B devices

**Syntax**: 
- Basic: `marker`
- With date: `marker|YYYY-MM-DD HH:MM:SS`

**Examples**:
```
PL001                    # Check current date and navigation
PL001|2024-12-15 10:30:00   # Set new date and time
```

**Features**:
- Navigation: `cd .. && ls` for directory listing
- Current date: `date` command output
- Date setting: `date -s "new_date"` with validation
- Targets CPU B devices specifically
- Error handling for invalid date formats

### 🔌 **MCU Control Command**

**Purpose**: Comprehensive MCU (Microcontroller Unit) management

**Actions Available**:
- `status` - Get MCU status and configuration
- `enable` - Enable MCU in configuration
- `disable` - Disable MCU in configuration  
- `config` - View MCU configuration
- `restart` - Restart MCU services

**Syntax**: 
- Basic: `marker`
- With action: `marker|action`
- With config file: `marker|action|config_file`

**Examples**:
```
PL001                           # Get MCU status
PL001|enable                    # Enable MCU
PL001|disable                   # Disable MCU
PL001|config                    # View configuration
PL001|restart                   # Restart MCU services
PL001|status|CUSTOM_CONFIG      # Check status with custom config file
```

**Features**:
- Automatic backup before changes
- Configuration validation
- Service restart with multiple methods
- Comprehensive status reporting
- Timestamp tracking

### ⚙️ **Advanced MCU Configuration**

**Purpose**: Advanced MCU configuration management with JSON updates

**Syntax**: `marker|{"key": "value", "key2": "value2"}`

**Examples**:
```
PL001|{"MCU_ENABLE": "true"}
PL001|{"MCU_ENABLE": "true", "MCU_TIMEOUT": "30"}
PL001|{"MCU_DEBUG": "false", "MCU_LOG_LEVEL": "INFO"}
```

**Features**:
- JSON-based configuration updates
- Automatic backup before changes
- Configuration diff reporting
- Bulk configuration changes
- Verification of applied changes

### 💾 **Enhanced Backup Configuration**

**Purpose**: Comprehensive configuration backup with multiple types

**Backup Types**:
- `running` - Running configuration
- `startup` - Startup configuration
- `mcu` - MCU configuration files
- `full` - Complete system backup

**Syntax**: 
- Basic: `marker`
- With type: `marker|backup_type`

**Examples**:
```
PL001                    # Default running config backup
PL001|running           # Running configuration
PL001|startup           # Startup configuration
PL001|mcu              # MCU configuration
PL001|full             # Full system backup
```

**Features**:
- Timestamped backups
- Multiple configuration types
- Compressed archives
- System file inclusion
- Verification and logging

## 🎯 **Command Parameters Guide**

### **Parameter Formats**

**Single Parameter**: `marker`
- Example: `PL001`

**Multiple Parameters**: `marker|param1|param2`
- Example: `PL001|enable|CONFIGURATION`

**JSON Parameters**: `marker|{"key": "value"}`
- Example: `PL001|{"MCU_ENABLE": "true"}`

### **Device Targeting**

**Data Management**: Targets `CPU B` devices
**MCU Commands**: Targets `CPU B`, `MCU`, or `Controller` devices
**General Commands**: All devices for the marker

## 🔐 **Security Features**

### **Automatic Backups**
- All configuration changes create timestamped backups
- Backup verification before proceeding
- Rollback capability

### **Validation**
- Parameter validation before execution
- Date format validation
- JSON syntax validation
- SSH connection verification

### **Error Handling**
- Comprehensive error reporting
- Graceful failure handling
- Connection timeout management
- Command result validation

## 📋 **Usage Examples**

### **Complete MCU Management Workflow**

```bash
# 1. Check MCU status
Command: MCU Control
Parameter: PL001

# 2. View current configuration
Command: MCU Control  
Parameter: PL001|config

# 3. Enable MCU with backup
Command: MCU Control
Parameter: PL001|enable

# 4. Apply advanced configuration
Command: Advanced MCU Config
Parameter: PL001|{"MCU_TIMEOUT": "60", "MCU_DEBUG": "true"}

# 5. Restart MCU services
Command: MCU Control
Parameter: PL001|restart

# 6. Verify status
Command: MCU Control
Parameter: PL001|status
```

### **Date Management Example**

```bash
# 1. Check current date and navigation
Command: Data Management
Parameter: PL001

# 2. Set new date and time
Command: Data Management
Parameter: PL001|2024-12-15 14:30:00

# 3. Verify date change
Command: Data Management
Parameter: PL001
```

### **Backup Strategy Example**

```bash
# 1. Create full system backup
Command: Backup Config
Parameter: PL001|full

# 2. Backup only MCU configuration
Command: Backup Config
Parameter: PL001|mcu

# 3. Daily running config backup
Command: Backup Config
Parameter: PL001|running
```

## 🛠️ **Advanced Features**

### **SSH Command Execution**
- Secure SSH connections with timeout handling
- Command output parsing and formatting
- Error detection and reporting
- Connection management

### **Configuration Management**
- File-based configuration editing
- Backup and restore capabilities
- Version tracking
- Change verification

### **Service Management**
- Multiple restart methods
- Service status monitoring
- Process management
- Health checking

## 🔍 **Troubleshooting**

### **Common Issues**

**SSH Connection Failures**:
- Verify device IP addresses
- Check network connectivity
- Confirm SSH credentials
- Validate firewall settings

**Configuration Errors**:
- Check file permissions
- Verify configuration syntax
- Review backup files
- Validate parameter formats

**MCU Issues**:
- Check service status
- Review system logs
- Verify configuration files
- Test connectivity

### **Error Messages**

**"No CPU B for PL marker"**: No CPU B devices found for the marker
**"SSH Error"**: Connection or authentication issues
**"Invalid date format"**: Date parameter format incorrect
**"Unknown action"**: Invalid MCU action specified
**"Invalid JSON format"**: JSON syntax error in parameters

## 📈 **Performance Considerations**

### **Command Execution**
- Commands run in separate threads
- Timeout handling for long operations
- Progress reporting for complex tasks
- Resource management

### **Network Efficiency**
- Connection pooling where possible
- Optimized command batching
- Bandwidth-aware operations
- Error recovery mechanisms

---

**NetPulse 2.0** - *Advanced Network Automation Made Simple*