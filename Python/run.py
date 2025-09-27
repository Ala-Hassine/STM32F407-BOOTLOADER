import struct
import os
import glob
from time import sleep
import sys
import serial

''' Bootloader Commands '''
BOOT_GET_VER_CMD              = 0x10
BOOT_GET_HELP_CMD             = 0x11
BOOT_GET_CID_CMD              = 0x12
BOOT_GET_RDP_STATUS_CMD       = 0x13
BOOT_GO_TO_ADDR_CMD           = 0x14
BOOT_FLASH_ERASE_CMD          = 0x15
BOOT_MEM_WRITE_CMD            = 0x16
BOOT_ED_W_PROTECT_CMD         = 0x17
BOOT_MEM_READ_CMD             = 0x18
BOOT_READ_SECTOR_STATUS_CMD   = 0x19
BOOT_OTP_READ_CMD             = 0x20
BOOT_CHANGE_ROP_Level_CMD     = 0x21
INVALID_SECTOR_NUMBER         = 0x00
VALID_SECTOR_NUMBER           = 0x01
UNSUCCESSFUL_ERASE            = 0x02
SUCCESSFUL_ERASE              = 0x03
FLASH_PAYLOAD_WRITE_FAILED    = 0x00
FLASH_PAYLOAD_WRITE_PASSED    = 0x01
verbose_mode                  = 1
Memory_Write_Active           = 0

def Check_Serial_Ports():
    Serial_Ports = []
    if sys.platform.startswith('win'):
        Ports = ['COM%s' % (i + 1) for i in range(256)]
    else:
        raise EnvironmentError("Error ... Unsupported Platform\n")
    for Serial_Port in Ports:
        try:
            test = serial.Serial(Serial_Port)
            test.close()
            Serial_Ports.append(Serial_Port)
        except (OSError, serial.SerialException):
            pass
    return Serial_Ports

def Serial_Port_Configuration(Port_Number):
    global Serial_Port_Obj
    try:
        Serial_Port_Obj = serial.Serial(Port_Number, 115200, timeout = 2)
    except:
        print("Error ... That Was Not A Valid Port\n")
        Port_Number = Check_Serial_Ports()
        if(not Port_Number):
            print("Error ... No Ports Detected\n")
        else:
            print("Here Are Some Available Ports On Your PC ... Try Again")
            print("\n", Port_Number)
        return -1
    if Serial_Port_Obj.is_open:
        print("Port Open Success\n")
    else:
        print("Port Open Failed\n")

def Write_Data_To_Serial_Port(Value, Length):
    _data = struct.pack('>B', Value)
    if(verbose_mode):
        Value = bytearray(_data)
        print("   " + "0x{:02x}".format(Value[0]), end = ' ')
        if(Memory_Write_Active and (not verbose_mode)):
            print("#", end = ' ')
        Serial_Port_Obj.write(_data)

def Read_Serial_Port(Data_Len):
    Serial_Value = Serial_Port_Obj.read(Data_Len)
    Serial_Value_len = len(Serial_Value)
    while Serial_Value_len <= 0:
        Serial_Value = Serial_Port_Obj.read(Data_Len)
        Serial_Value_len = len(Serial_Value)
        print("Waiting Replay From The Bootloader")
    return Serial_Value

def Read_Data_From_Serial_Port(Command_Code, Memory_Address=None):
    Length_To_Follow = 0
    BL_ACK = Read_Serial_Port(2)
    if(len(BL_ACK)):
        BL_ACK_Array = bytearray(BL_ACK)
        if(BL_ACK_Array[0] == 0xCD):
            print ("Received Acknowledgement From Bootloader\n")
            Length_To_Follow = BL_ACK_Array[1]
            print("Preparing To Receive (", int(Length_To_Follow), ") Bytes From The Bootloader\n")
            if(Command_Code == BOOT_GET_VER_CMD):
                Process_BOOT_GET_VER_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_GET_HELP_CMD):
                Process_BOOT_GET_HELP_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_GET_CID_CMD):
                Process_BOOT_GET_CID_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_GET_RDP_STATUS_CMD):
                Process_BOOT_GET_RDP_STATUS_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_GO_TO_ADDR_CMD):
                Process_BOOT_GO_TO_ADDR_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_FLASH_ERASE_CMD):
                Process_BOOT_FLASH_ERASE_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_MEM_WRITE_CMD):
                Process_BOOT_MEM_WRITE_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_CHANGE_ROP_Level_CMD):
                Process_BOOT_CHANGE_ROP_Level_CMD(Length_To_Follow)
            elif (Command_Code == BOOT_MEM_READ_CMD):
                Process_BOOT_MEM_READ_CMD(Length_To_Follow, Memory_Address)
            elif (Command_Code == BOOT_ED_W_PROTECT_CMD):
                Process_BOOT_ED_W_PROTECT_CMD(Length_To_Follow)
        else:
            print ("Received Not-Acknowledgement From Bootloader\n")
            sys.exit()
        
def Process_BOOT_GET_VER_CMD(Data_Len):
    Serial_Data = Read_Serial_Port(Data_Len)
    _value_     = bytearray(Serial_Data)
    print("Bootloader Vendor ID : ", _value_[0])
    print("Bootloader Version   : ", _value_[1], ".", _value_[2], ".", _value_[3])

def Process_BOOT_GET_HELP_CMD(Data_Len):
    Serial_Data = Read_Serial_Port(Data_Len)
    _value_     = bytearray(Serial_Data)
    print("Supported Commands : ", end = ' ')
    for command in _value_:
        print(hex(command), end = ' ')

def Process_BOOT_GET_CID_CMD(Data_Len):
    Serial_Data = Read_Serial_Port(Data_Len)
    CID         = (Serial_Data[1] << 8) | Serial_Data[0]
    print("Chip Identification Number : ", hex(CID))

def Process_BOOT_GET_RDP_STATUS_CMD(Data_Len):
    Serial_Data = Read_Serial_Port(Data_Len)
    _value_ = bytearray(Serial_Data)
    if(_value_[0] == 0xEE):
        print("Error While Reading FLASH Protection Level\n")
    elif(_value_[0] == 0xAA):
        print("FLASH Protection : LEVEL 0\n")
    elif(_value_[0] == 0x55):
        print("FLASH Protection : LEVEL 1\n")
    elif(_value_[0] == 0xCC):
        print("FLASH Protection : LEVEL 2\n")

def Process_BOOT_GO_TO_ADDR_CMD(Data_Len):
    Serial_Data = Read_Serial_Port(Data_Len)
    _value_     = bytearray(Serial_Data)
    if(_value_[0] == 1):
        print("Address Status Is Valid\n")
    else:
        print("Address Status Is InValid\n")

def Process_BOOT_FLASH_ERASE_CMD(Data_Len):
    BL_Erase_Status = 0
    Serial_Data = Read_Serial_Port(Data_Len)
    if(len(Serial_Data)):
        BL_Erase_Status = bytearray(Serial_Data)
        if(BL_Erase_Status[0] == INVALID_SECTOR_NUMBER):
            print("Erase Status -> Invalid Sector Number\n")
        elif (BL_Erase_Status[0] == UNSUCCESSFUL_ERASE):
            print("Erase Status -> Unsuccessfule Erase\n")
        elif (BL_Erase_Status[0] == SUCCESSFUL_ERASE):
            print("Erase Status -> Successfule Erase\n")
        else:
            print("Erase Status ---> Unknown Error\n")
    else:
        print("Timeout ... Bootloader Is Not Responding\n")

def Process_BOOT_MEM_WRITE_CMD(Data_Len):
    global Memory_Write_All
    BL_Write_Status = 0
    Serial_Data     = Read_Serial_Port(Data_Len)
    BL_Write_Status = bytearray(Serial_Data)
    if(BL_Write_Status[0] == FLASH_PAYLOAD_WRITE_FAILED):
        print("Write Status ---> Write Failed Or Invalid Address\n")
    elif (BL_Write_Status[0] == FLASH_PAYLOAD_WRITE_PASSED):
        print("Write Status ---> Write Successfully\n")
        Memory_Write_All = Memory_Write_All and FLASH_PAYLOAD_WRITE_PASSED
    else:
        print("Timeout ... Bootloader Is Not Responding")
        
def Process_BOOT_MEM_READ_CMD(Data_Len, Memory_Address=None):
    Serial_Data = Read_Serial_Port(Data_Len)
    if(len(Serial_Data)):
        Read_Status = Serial_Data[0] # First byte is status (0x00 = failed, 0x01 = success)
        if(Read_Status == 0x01):  # Memory read successful
            Read_Data = Serial_Data[1:]  # The remaining bytes are the actual data read from memory
            print("Memory Read Successfully\n")
            print(f"Read {len(Read_Data)} Bytes From Memory : ")
            # Use the actual address provided by the user
            if Memory_Address is None:
                Memory_Address = 0x08008000  # Default fallback
            base_address = Memory_Address
            # Display in hexadecimal format (32-bit aligned)
            print("\n   Address    | 0        | 4        | 8        | C        | ASCII")
            print("   " + "-" * 70)
            for i in range(0, len(Read_Data), 16):
                if i + 16 <= len(Read_Data):
                    addr_str = f"0x{base_address + i:08X}"  # Format address using the actual base address
                    # Format 32-bit words
                    word0 = f"{Read_Data[i+3]:02X}{Read_Data[i+2]:02X}{Read_Data[i+1]:02X}{Read_Data[i]:02X}"
                    word1 = f"{Read_Data[i+7]:02X}{Read_Data[i+6]:02X}{Read_Data[i+5]:02X}{Read_Data[i+4]:02X}"
                    word2 = f"{Read_Data[i+11]:02X}{Read_Data[i+10]:02X}{Read_Data[i+9]:02X}{Read_Data[i+8]:02X}"
                    word3 = f"{Read_Data[i+15]:02X}{Read_Data[i+14]:02X}{Read_Data[i+13]:02X}{Read_Data[i+12]:02X}"
                    # Format ASCII
                    ascii_str = ""
                    for j in range(16):
                        byte_val = Read_Data[i + j]
                        if 32 <= byte_val <= 126:  # Printable ASCII
                            ascii_str += chr(byte_val)
                        else:
                            ascii_str += '.'
                    print(f"   {addr_str} | {word0} | {word1} | {word2} | {word3} | {ascii_str}")
            # Also show raw bytes for verification
            print("Raw Bytes (Little Endian) : ")
            print("HEX : ", end='')
            for i, byte in enumerate(Read_Data):
                if i > 0 and i % 4 == 0:  # Space every 4 bytes
                    print(" ", end='')
                if i > 0 and i % 16 == 0:  # New line every 16 bytes
                    print("\n        ", end='')
                print(f"{byte:02x}", end='')
            print()
        else:  # Memory read failed
            print("Memory Read Failed ... Invalid Address Or Access Denied")
    else:
        print("Timeout ... Bootloader Is Not Responding")

def Process_BOOT_CHANGE_ROP_Level_CMD(Data_Len):
    BL_CHANGE_ROP_Level_Status  = 0
    Serial_Data                 = Read_Serial_Port(Data_Len)
    if(len(Serial_Data)):
        BL_CHANGE_ROP_Level_Status = bytearray(Serial_Data)
        if(BL_CHANGE_ROP_Level_Status[0] == 0x01):
            print("ROP Level Changed\n")
        elif (BL_CHANGE_ROP_Level_Status[0] == 0x00):
            print("ROP Level Not Changed\n")
        else:
            print("ROP Level ---> Unknown Error\n")

def Process_BOOT_ED_W_PROTECT_CMD(Data_Len):
    Serial_Data = Read_Serial_Port(Data_Len)
    if(len(Serial_Data)):
        Protection_Status = bytearray(Serial_Data)[0]
        if(Protection_Status == 0x01):
            print("Write Protection Operation Successfully\n")
        else:
            print("Write Protection Operation Failed\n")
    else:
        print("Timeout ... Bootloader Is Not Responding\n")

def Calculate_CRC32(Buffer, Buffer_Length):
    CRC_Value = 0xFFFFFFFF
    for DataElem in Buffer[0:Buffer_Length]:
        CRC_Value = CRC_Value ^ DataElem
        for DataElemBitLen in range(32):
            if(CRC_Value & 0x80000000):
                CRC_Value = (CRC_Value << 1) ^ 0x04C11DB7
            else:
                CRC_Value = (CRC_Value << 1)
    return CRC_Value
    
def Word_Value_To_Byte_Value(Word_Value, Byte_Index, Byte_Lower_First):
    Byte_Value = (Word_Value >> (8 * (Byte_Index - 1)) & 0x000000FF)
    return Byte_Value

def CalulateBinFileLength():
    BinFileLength = os.path.getsize("AlaHassine.bin")
    return BinFileLength

def OpenBinFile():
    global BinFile
    BinFile = open('AlaHassine.bin', 'rb')

def Decode_BOOT_Command(Command):
    BL_Host_Buffer  = []
    BL_Return_Value = 0
    ''' Clear The Bootloader Host Buffer '''
    for counter in range(255):
        BL_Host_Buffer.append(0)
    if(Command == 1):
        print("Request The Bootloader Version\n")
        BOOT_GET_VER_CMD_Len = 6
        BL_Host_Buffer[0]    = BOOT_GET_VER_CMD_Len - 1
        BL_Host_Buffer[1]    = BOOT_GET_VER_CMD
        CRC32_Value          = Calculate_CRC32(BL_Host_Buffer, BOOT_GET_VER_CMD_Len - 4)
        CRC32_Value          = CRC32_Value & 0xFFFFFFFF
        print("Host CRC = ", hex(CRC32_Value))
        BL_Host_Buffer[2]    = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[3]    = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[4]    = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[5]    = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
        for Data in BL_Host_Buffer[1 : BOOT_GET_VER_CMD_Len]:
            Write_Data_To_Serial_Port(Data, BOOT_GET_VER_CMD_Len - 1)
        Read_Data_From_Serial_Port(BOOT_GET_VER_CMD)
    elif (Command == 2):
        print("Read The Commands Supported By The Bootloader\n")
        BOOT_GET_HELP_CMD_Len = 6
        BL_Host_Buffer[0]     = BOOT_GET_HELP_CMD_Len - 1
        BL_Host_Buffer[1]     = BOOT_GET_HELP_CMD
        CRC32_Value           = Calculate_CRC32(BL_Host_Buffer, BOOT_GET_HELP_CMD_Len - 4)
        CRC32_Value           = CRC32_Value & 0xFFFFFFFF
        BL_Host_Buffer[2]     = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[3]     = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[4]     = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[5]     = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
        for Data in BL_Host_Buffer[1 : BOOT_GET_HELP_CMD_Len]:
            Write_Data_To_Serial_Port(Data, BOOT_GET_HELP_CMD_Len - 1)
        Read_Data_From_Serial_Port(BOOT_GET_HELP_CMD)
    elif (Command == 3):
        print("Read The MCU Chip Identification Number\n")
        BOOT_GET_CID_CMD_Len  = 6
        BL_Host_Buffer[0]     = BOOT_GET_CID_CMD_Len - 1
        BL_Host_Buffer[1]     = BOOT_GET_CID_CMD
        CRC32_Value           = Calculate_CRC32(BL_Host_Buffer, BOOT_GET_CID_CMD_Len - 4)
        CRC32_Value           = CRC32_Value & 0xFFFFFFFF
        BL_Host_Buffer[2]     = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[3]     = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[4]     = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[5]     = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
        for Data in BL_Host_Buffer[1 : BOOT_GET_CID_CMD_Len]:
            Write_Data_To_Serial_Port(Data, BOOT_GET_CID_CMD_Len - 1)
        Read_Data_From_Serial_Port(BOOT_GET_CID_CMD)
    elif (Command == 4):
        print("Read The FLASH Read Protection Level\n")
        BOOT_GET_RDP_STATUS_CMD_Len  = 6
        BL_Host_Buffer[0]            = BOOT_GET_RDP_STATUS_CMD_Len - 1
        BL_Host_Buffer[1]            = BOOT_GET_RDP_STATUS_CMD
        CRC32_Value                  = Calculate_CRC32(BL_Host_Buffer, BOOT_GET_RDP_STATUS_CMD_Len - 4)
        CRC32_Value                  = CRC32_Value & 0xFFFFFFFF
        BL_Host_Buffer[2]            = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[3]            = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[4]            = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[5]            = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
        for Data in BL_Host_Buffer[1 : BOOT_GET_RDP_STATUS_CMD_Len]:
            Write_Data_To_Serial_Port(Data, BOOT_GET_RDP_STATUS_CMD_Len - 1)
        Read_Data_From_Serial_Port(BOOT_GET_RDP_STATUS_CMD)
    elif (Command == 5):
        print("Jump Bootloader To Specified Address Command\n")
        BOOT_GO_TO_ADDR_CMD_Len  = 10
        BOOT_Jump_Address        = input("Please Enter The Address In HEX : ")
        BOOT_Jump_Address        = int(BOOT_Jump_Address, 16)
        BL_Host_Buffer[0]        = BOOT_GO_TO_ADDR_CMD_Len - 1
        BL_Host_Buffer[1]        = BOOT_GO_TO_ADDR_CMD
        BL_Host_Buffer[2]        = Word_Value_To_Byte_Value(BOOT_Jump_Address, 1, 1)
        BL_Host_Buffer[3]        = Word_Value_To_Byte_Value(BOOT_Jump_Address, 2, 1)
        BL_Host_Buffer[4]        = Word_Value_To_Byte_Value(BOOT_Jump_Address, 3, 1)
        BL_Host_Buffer[5]        = Word_Value_To_Byte_Value(BOOT_Jump_Address, 4, 1)
        CRC32_Value              = Calculate_CRC32(BL_Host_Buffer, BOOT_GO_TO_ADDR_CMD_Len - 4)
        CRC32_Value              = CRC32_Value & 0xFFFFFFFF
        BL_Host_Buffer[6]        = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[7]        = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[8]        = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[9]        = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
        for Data in BL_Host_Buffer[1 : BOOT_GO_TO_ADDR_CMD_Len]:
            Write_Data_To_Serial_Port(Data, BOOT_GO_TO_ADDR_CMD_Len - 1)
        Read_Data_From_Serial_Port(BOOT_GO_TO_ADDR_CMD)
    elif (Command == 6):
        print("Mass Erase Or Sector Erase Of The User Flash Command\n")
        print("Enter 0xFF For Mass Erase Or Sector Number (0-11) For Sector Erase\n")
        print("========= STM32F407 Sector Map =========")
        print("*** Sector 00: 0x08000000-0x08003FFF ***")
        print("*** Sector 01: 0x08004000-0x08007FFF ***") 
        print("*** Sector 02: 0x08008000-0x0800BFFF ***")
        print("*** Sector 03: 0x0800C000-0x0800FFFF ***")
        print("*** Sector 04: 0x08010000-0x0801FFFF ***")
        print("*** Sector 05: 0x08020000-0x0803FFFF ***")
        print("*** Sector 06: 0x08040000-0x0805FFFF ***")
        print("*** Sector 07: 0x08060000-0x0807FFFF ***")
        print("*** Sector 08: 0x08080000-0x0809FFFF ***")
        print("*** Sector 09: 0x080A0000-0x080BFFFF ***")
        print("*** Sector 10: 0x080C0000-0x080DFFFF ***")
        print("*** Sector 11: 0x080E0000-0x080FFFFF ***")
        Sector_input = input("Please Enter Sector Number (0-11) Or 0xFF For Mass Erase : ")
        # Convert input to integer
        if Sector_input.startswith('0x'):
            SectorNumber = int(Sector_input, 16)
        else:
            SectorNumber = int(Sector_input)
        if SectorNumber != 0xFF:
            NumberOfSectors_input = input("Please Enter Number Of Sectors To Erase (12 Max) : ")
            if NumberOfSectors_input.startswith('0x'):
                NumberOfSectors   = int(NumberOfSectors_input, 16)
            else:
                NumberOfSectors   = int(NumberOfSectors_input)
        else:
            NumberOfSectors       = 0  # Mass erase
        # Packet structure: [Length][CMD][Sector(4 bytes)][NumSectors][CRC(4 bytes)]
        BOOT_FLASH_ERASE_CMD_Len  = 11  # Total packet length
        BL_Host_Buffer            = [0] * 255  # Clear buffer
        # Fill packet data
        BL_Host_Buffer[0]         = BOOT_FLASH_ERASE_CMD_Len - 1  # Packet length minus length byte
        BL_Host_Buffer[1]         = BOOT_FLASH_ERASE_CMD
        # Sector number as 4-byte value (LITTLE ENDIAN - Important)
        BL_Host_Buffer[2]         = (SectorNumber >> 0) & 0xFF   # LSB
        BL_Host_Buffer[3]         = (SectorNumber >> 8) & 0xFF
        BL_Host_Buffer[4]         = (SectorNumber >> 16) & 0xFF
        BL_Host_Buffer[5]         = (SectorNumber >> 24) & 0xFF  # MSB
        BL_Host_Buffer[6]         = NumberOfSectors & 0xFF       # Number of sectors
        # Calculate CRC on first 7 bytes (positions 0-6)
        CRC32_Value               = Calculate_CRC32(BL_Host_Buffer, 7)
        CRC32_Value               = CRC32_Value & 0xFFFFFFFF
        # Add 4-byte CRC (LITTLE ENDIAN)
        BL_Host_Buffer[7]         = (CRC32_Value >> 0) & 0xFF   # CRC LSB
        BL_Host_Buffer[8]         = (CRC32_Value >> 8) & 0xFF
        BL_Host_Buffer[9]         = (CRC32_Value >> 16) & 0xFF
        BL_Host_Buffer[10]        = (CRC32_Value >> 24) & 0xFF # CRC MSB
        print(f"Sending {BOOT_FLASH_ERASE_CMD_Len} bytes : ")
        print("Bytes : ", end='')
        # Send the complete packet
        for i in range(BOOT_FLASH_ERASE_CMD_Len):
            Write_Data_To_Serial_Port(BL_Host_Buffer[i], 1)
        print()  # New line after printing all bytes
        # Wait a bit before reading response
        sleep(0.1)
        # Read response from bootloader
        Read_Data_From_Serial_Port(BOOT_FLASH_ERASE_CMD)
    elif (Command == 7):
        print("Write Data Into Different Memories Of The MCU Command\n")
        global Memory_Write_Is_Active
        global Memory_Write_All
        File_Total_Len          = 0
        BinFileRemainingBytes   = 0
        BinFileSentBytes        = 0
        BaseMemoryAddress       = 0
        BinFileReadLength       = 0
        Memory_Write_All        = 1
        File_Total_Len          = CalulateBinFileLength()   # Get the total length of the binary file
        print("Preparing Writing A Binary File With Length (", File_Total_Len, ") Bytes\n")
        OpenBinFile()
        BinFileRemainingBytes   = File_Total_Len - BinFileSentBytes
        BaseMemoryAddress       = input("Enter The Start Address : ")
        BaseMemoryAddress       = int(BaseMemoryAddress, 16)
        while(BinFileRemainingBytes):
            Memory_Write_Is_Active  = 1
            if(BinFileRemainingBytes >= 128):
                BinFileReadLength   = 128
            else:
                BinFileReadLength   = BinFileRemainingBytes
            for BinFileByte in range(BinFileReadLength):
                BinFileByteValue    = BinFile.read(1)
                BinFileByteValue    = bytearray(BinFileByteValue)
                BL_Host_Buffer[7 + BinFileByte] = int(BinFileByteValue[0])
            BL_Host_Buffer[1]       = BOOT_MEM_WRITE_CMD
            BL_Host_Buffer[2]       = Word_Value_To_Byte_Value(BaseMemoryAddress, 1, 1)
            BL_Host_Buffer[3]       = Word_Value_To_Byte_Value(BaseMemoryAddress, 2, 1)
            BL_Host_Buffer[4]       = Word_Value_To_Byte_Value(BaseMemoryAddress, 3, 1)
            BL_Host_Buffer[5]       = Word_Value_To_Byte_Value(BaseMemoryAddress, 4, 1)
            BL_Host_Buffer[6]       = BinFileReadLength
            BOOT_MEM_WRITE_CMD_Len   = (BinFileReadLength + 11)
            BL_Host_Buffer[0]       = BOOT_MEM_WRITE_CMD_Len - 1
            CRC32_Value             = Calculate_CRC32(BL_Host_Buffer, BOOT_MEM_WRITE_CMD_Len - 4)
            CRC32_Value             = CRC32_Value & 0xFFFFFFFF
            BL_Host_Buffer[7  + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
            BL_Host_Buffer[8  + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
            BL_Host_Buffer[9  + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
            BL_Host_Buffer[10 + BinFileReadLength] = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
            BaseMemoryAddress       = BaseMemoryAddress + BinFileReadLength
            Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
            for Data in BL_Host_Buffer[1 : BOOT_MEM_WRITE_CMD_Len]:
                Write_Data_To_Serial_Port(Data, BOOT_MEM_WRITE_CMD_Len - 1)
            BinFileSentBytes = BinFileSentBytes + BinFileReadLength
            BinFileRemainingBytes = File_Total_Len - BinFileSentBytes
            print("Bytes Sent To The Bootloader : {0}".format(BinFileSentBytes))
            BL_Return_Value = Read_Data_From_Serial_Port(BOOT_MEM_WRITE_CMD)
            sleep(0.1)
        Memory_Write_Is_Active = 0
        if(Memory_Write_All == 1):
            print("Payload Written Successfully\n")
    elif (Command == 8):
        print("Read Data From Different Memories Of The MCU Command")
        BOOT_MEM_READ_CMD_Len   = 11
        Memory_Address          = input("Please Enter The Memory Address In Hex : ")
        Memory_Address          = int(Memory_Address, 16)
        Data_Length             = input("Please Enter The Number Of Bytes To Read (1 - 255) : ")
        Data_Length             = int(Data_Length)
        BL_Host_Buffer[0]       = BOOT_MEM_READ_CMD_Len - 1
        BL_Host_Buffer[1]       = BOOT_MEM_READ_CMD
        BL_Host_Buffer[2]       = Word_Value_To_Byte_Value(Memory_Address, 1, 1) 
        BL_Host_Buffer[3]       = Word_Value_To_Byte_Value(Memory_Address, 2, 1) 
        BL_Host_Buffer[4]       = Word_Value_To_Byte_Value(Memory_Address, 3, 1) 
        BL_Host_Buffer[5]       = Word_Value_To_Byte_Value(Memory_Address, 4, 1)
        BL_Host_Buffer[6]       = Data_Length
        CRC32_Value             = Calculate_CRC32(BL_Host_Buffer, BOOT_MEM_READ_CMD_Len - 4)
        CRC32_Value             = CRC32_Value & 0xFFFFFFFF
        BL_Host_Buffer[7]       = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[8]       = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[9]       = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[10]      = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
        for Data in BL_Host_Buffer[1 : BOOT_MEM_READ_CMD_Len]:
            Write_Data_To_Serial_Port(Data, BOOT_MEM_READ_CMD_Len - 1)
        Read_Data_From_Serial_Port(BOOT_MEM_READ_CMD, Memory_Address)
    elif (Command == 9):
        print("Enable/Disable Write Protection For Flash Sectors\n")
        print("Protection Action : ")
        print("0 ===> Disable Write Protection")
        print("1 ===> Enable Write Protection")
        Protection_Action           = input("Enter Protection Action (0 Or 1) : ")
        Protection_Action           = int(Protection_Action)      
        print("\nSector Bitmask Guide : ")
        print("Set Bit 0 For Sector 0, Bit 1 For Sector 1, Etc.")
        print("Example: 0x003 For Sectors 0 and 1 (Binary : 0000 0000 0011)")
        print("Example: 0xFFF For all Sectors 0-11")
        Sector_Bitmask              = input("Enter Sector Bitmask In HEX (Example : 0x003) : ")
        Sector_Bitmask              = int(Sector_Bitmask, 16)
        # Packet structure: [Length][CMD][Action][SectorBitmask(4 bytes)][CRC(4 bytes)]
        BOOT_ED_W_PROTECT_CMD_Len    = 11
        BL_Host_Buffer[0]           = BOOT_ED_W_PROTECT_CMD_Len - 1
        BL_Host_Buffer[1]           = BOOT_ED_W_PROTECT_CMD
        BL_Host_Buffer[2]           = Protection_Action
        BL_Host_Buffer[3]           = Word_Value_To_Byte_Value(Sector_Bitmask, 1, 1)  # LSB
        BL_Host_Buffer[4]           = Word_Value_To_Byte_Value(Sector_Bitmask, 2, 1)
        BL_Host_Buffer[5]           = Word_Value_To_Byte_Value(Sector_Bitmask, 3, 1)
        BL_Host_Buffer[6]           = Word_Value_To_Byte_Value(Sector_Bitmask, 4, 1)  # MSB
        CRC32_Value                 = Calculate_CRC32(BL_Host_Buffer, BOOT_ED_W_PROTECT_CMD_Len - 4)
        CRC32_Value                 = CRC32_Value & 0xFFFFFFFF
        BL_Host_Buffer[7]           = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
        BL_Host_Buffer[8]           = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
        BL_Host_Buffer[9]           = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
        BL_Host_Buffer[10]          = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
        Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
        for Data in BL_Host_Buffer[1 : BOOT_ED_W_PROTECT_CMD_Len]:
            Write_Data_To_Serial_Port(Data, BOOT_ED_W_PROTECT_CMD_Len - 1)
        Read_Data_From_Serial_Port(BOOT_ED_W_PROTECT_CMD)
    elif (Command == 10):
        pass
    elif (Command == 11):
        pass
    elif (Command == 12):
        print("Change Read Protection Level Of The User Flash Command\n")
        Protection_level = input("Please Enter One Of These Protection Levels : (0 or 1 or 2) : ")
        Protection_level = int(Protection_level, 8)
        if(Protection_level == 2):
            print("\nProtection Level (2) Not Supported")
        elif(Protection_level == 0 or Protection_level == 1):
            print("\nChanging The Protection Level To Be : ", Protection_level)
            BOOT_CHANGE_ROP_Level_CMD_Len   = 7
            BL_Host_Buffer[0]               = BOOT_CHANGE_ROP_Level_CMD_Len - 1
            BL_Host_Buffer[1]               = BOOT_CHANGE_ROP_Level_CMD
            BL_Host_Buffer[2]               = Protection_level
            CRC32_Value                     = Calculate_CRC32(BL_Host_Buffer, BOOT_CHANGE_ROP_Level_CMD_Len - 4)
            CRC32_Value                     = CRC32_Value & 0xFFFFFFFF
            BL_Host_Buffer[3]               = Word_Value_To_Byte_Value(CRC32_Value, 1, 1)
            BL_Host_Buffer[4]               = Word_Value_To_Byte_Value(CRC32_Value, 2, 1)
            BL_Host_Buffer[5]               = Word_Value_To_Byte_Value(CRC32_Value, 3, 1)
            BL_Host_Buffer[6]               = Word_Value_To_Byte_Value(CRC32_Value, 4, 1)
            Write_Data_To_Serial_Port(BL_Host_Buffer[0], 1)
            for Data in BL_Host_Buffer[1 : BOOT_CHANGE_ROP_Level_CMD_Len]:
                Write_Data_To_Serial_Port(Data, BOOT_CHANGE_ROP_Level_CMD_Len - 1)
            Read_Data_From_Serial_Port(BOOT_CHANGE_ROP_Level_CMD)
        else:
            print("\nProtection Level (", Protection_level, ") Not Supported")
            
SerialPortName = input("Enter The Port Name Of Your Device (Ex: COM1) : ")
Serial_Port_Configuration(SerialPortName)
        
while True:
    print("\nSTM32F407 Custom BootLoader")
    print("===========================================")
    print("Which Command You Need To Send To The BootLoader :")
    print("   BOOT_GET_VER_CMD              --> 1")
    print("   BOOT_GET_HELP_CMD             --> 2")
    print("   BOOT_GET_CID_CMD              --> 3")
    print("   BOOT_GET_RDP_STATUS_CMD       --> 4")
    print("   BOOT_GO_TO_ADDR_CMD           --> 5")
    print("   BOOT_FLASH_ERASE_CMD          --> 6")
    print("   BOOT_MEM_WRITE_CMD            --> 7")
    print("   BOOT_MEM_READ_CMD             --> 8")
    print("   BOOT_ED_W_PROTECT_CMD         --> 9")
    print("   BOOT_READ_SECTOR_STATUS_CMD   --> 10")
    print("   BOOT_OTP_READ_CMD             --> 11")
    print("   BOOT_CHANGE_ROP_Level_CMD     --> 12")
    print("==========================================")
    BOOT_Command = input("\nEnter The Command Code : ")
    if(not BOOT_Command.isdigit()):
        print("Error ... Please Enter A Valid Command ...\n")
    else:
        Decode_BOOT_Command(int(BOOT_Command))
    input("\nPlease Press Any Key To Continue ...")
    Serial_Port_Obj.reset_input_buffer()
