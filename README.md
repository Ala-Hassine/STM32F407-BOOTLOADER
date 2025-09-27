# STM32F407 Custom Bootloader Host Application

A Python-based host application for communicating with a custom bootloader on STM32F407 microcontrollers via serial interface.

## 📋 Supported Commands

| Command Code | Command Name | Constant | Status | Description |
|-------------|--------------|----------|---------|-------------|
| **1** | Get Version | `BOOT_GET_VER_CMD` | ✅ Implemented | Read bootloader version and vendor ID from MCU |
| **2** | Get Help | `BOOT_GET_HELP_CMD` | ✅ Implemented | Get list of commands supported by the bootloader |
| **3** | Get Chip ID | `BOOT_GET_CID_CMD` | ✅ Implemented | Read MCU chip identification number |
| **4** | Read Protection Level | `BOOT_GET_RDP_STATUS_CMD` | ✅ Implemented | Read flash read protection level (Level 0, 1, or 2) |
| **5** | Go to Address | `BOOT_GO_TO_ADDR_CMD` | ✅ Implemented | Jump bootloader to specified address in memory |
| **6** | Flash Erase | `BOOT_FLASH_ERASE_CMD` | ✅ Implemented | Mass erase or sector erase of user flash memory |
| **7** | Memory Write | `BOOT_MEM_WRITE_CMD` | ✅ Implemented | Write data from binary file to MCU memories |
| **8** | Memory Read | `BOOT_MEM_READ_CMD` | ✅ Implemented | Read data from MCU memories |
| **9** | Write Protection | `BOOT_ED_W_PROTECT_CMD` | ✅ Implemented | Enable/disable write protection for flash sectors |
| **10** | Read Sector Status | `BOOT_READ_SECTOR_STATUS_CMD` | ❌ Not Implemented | Read sector protection status |
| **11** | OTP Read | `BOOT_OTP_READ_CMD` | ❌ Not Implemented | Read One-Time Programmable memory |
| **12** | Change ROP Level | `BOOT_CHANGE_ROP_Level_CMD` | ✅ Implemented | Change read protection level of user flash |

## 🚀 Command Details

### ✅ **1. Get Version** (`BOOT_GET_VER_CMD`)
- **Command Code**: `1`
- **Function**: Retrieves bootloader vendor ID and version information
- **Response**: Vendor ID, Major.Minor.Patch version

### ✅ **2. Get Help** (`BOOT_GET_HELP_CMD`)
- **Command Code**: `2`
- **Function**: Returns list of supported commands by the bootloader
- **Response**: Hexadecimal codes of supported commands

### ✅ **3. Get Chip ID** (`BOOT_GET_CID_CMD`)
- **Command Code**: `3`
- **Function**: Reads the unique chip identification number
- **Response**: 32-bit Chip ID number

### ✅ **4. Read Protection Level** (`BOOT_GET_RDP_STATUS_CMD`)
- **Command Code**: `4`
- **Function**: Checks current flash read protection level
- **Response**: 
  - `0xAA` = LEVEL 0 (No protection)
  - `0x55` = LEVEL 1 (Read protection)
  - `0xCC` = LEVEL 2 (No debug access)

### ✅ **5. Go to Address** (`BOOT_GO_TO_ADDR_CMD`)
- **Command Code**: `5`
- **Function**: Jumps execution to specified memory address
- **Input**: Hexadecimal memory address
- **Response**: Address validity status

### ✅ **6. Flash Erase** (`BOOT_FLASH_ERASE_CMD`)
- **Command Code**: `6`
- **Function**: Erases flash memory sectors or mass erase
- **Options**:
  - `0xFF`: Mass erase (complete flash)
  - `0-11`: Sector erase (specific sectors)
- **Sector Map**:
  ```
  Sector 00: 0x08000000-0x08003FFF
  Sector 01: 0x08004000-0x08007FFF
  ... up to Sector 11
  ```

### ✅ **7. Memory Write** (`BOOT_MEM_WRITE_CMD`)
- **Command Code**: `7`
- **Function**: Writes binary file to flash memory
- **File**: `AlaHassine.bin` (hardcoded filename)
- **Features**: 
  - Automatic chunking (128 bytes per packet)
  - CRC32 verification
  - Progress tracking

### ✅ **8. Memory Read** (`BOOT_MEM_READ_CMD`)
- **Command Code**: `8`
- **Function**: Reads data from specified memory address
- **Input**: Memory address and byte count (1-255)
- **Output**: Hexadecimal and ASCII formatted memory dump

### ✅ **9. Write Protection** (`BOOT_ED_W_PROTECT_CMD`)
- **Command Code**: `9`
- **Function**: Enables/disables write protection for flash sectors
- **Actions**:
  - `0`: Disable write protection
  - `1`: Enable write protection
- **Sector Selection**: Bitmask (0x001 for sector 0, 0xFFF for all sectors)

### ❌ **10. Read Sector Status** (`BOOT_READ_SECTOR_STATUS_CMD`)
- **Command Code**: `10`
- **Status**: ⚠️ **Not Implemented**
- **Planned Function**: Read protection status of individual sectors

### ❌ **11. OTP Read** (`BOOT_OTP_READ_CMD`)
- **Command Code**: `11`
- **Status**: ⚠️ **Not Implemented**
- **Planned Function**: Read One-Time Programmable memory areas

### ✅ **12. Change ROP Level** (`BOOT_CHANGE_ROP_Level_CMD`)
- **Command Code**: `12`
- **Function**: Changes read protection level
- **Supported Levels**:
  - `0`: Level 0 (No protection)
  - `1`: Level 1 (Read protection)
  - `2`: Level 2 (Not supported)

## 🔧 Technical Features

- **Serial Communication**: 115200 baud, 8N1
- **CRC32 Verification**: All commands include CRC32 checks
- **Platform Support**: Windows COM ports
- **Verbose Mode**: Detailed operation logging
- **Error Handling**: Comprehensive status reporting

## 📁 File Structure

```
Host.py                 # Main bootloader host application
AlaHassine.bin          # Binary file for flashing (required for command 7)
```

## 🚀 Usage

1. Connect STM32F407 via serial port
2. Run `python Host.py`
3. Enter COM port name (e.g., COM1)
4. Select command from menu
5. Follow prompts for command-specific inputs

## ⚠️ Notes

- Command 10 and 11 are listed in menu but not implemented
- Binary filename is hardcoded as `AlaHassine.bin`
- Ensure proper flash sector alignment when using erase/write commands
- Changing ROP level to 2 is irreversible and not supported
