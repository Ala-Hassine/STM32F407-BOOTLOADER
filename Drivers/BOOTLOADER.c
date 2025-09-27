#include "BOOTLOADER.h"

static uint32_t BOOT_CRC_VERIFY(uint8_t *pData, uint32_t DataLen, uint32_t HosrCRC);
static uint8_t 	HOST_BUFFER[HOST_MAX_SIZE];
static void 	  BOOT_SEND_ACK(uint8_t DataLen);
static void 	  BOOT_SEND_NACK();
static uint8_t 	PERFORM_FLASH_ERASE(uint32_t Sector_Address, uint8_t Sector_Number);
static uint32_t FLASH_GET_RDP(void);
static uint8_t 	BOOT_VALIDATE_MEMORY_ACCESS(uint32_t Address, uint8_t Length);

static void BOOT_GET_VERSION(uint8_t *Host_buffer);
static void BOOT_GET_HELP(uint8_t *Host_buffer);
static void BOOT_GET_CHIP_IDENTIFICATION_NUMBER(uint8_t *Host_buffer);
static void BOOT_FLASH_ERASE(uint8_t *Host_buffer);
static void BOOT_WRITE_MEMORY(uint8_t *Host_buffer);
static void BOOT_READ_MEMORY(uint8_t *Host_buffer);
static void BOOT_READ_PROTECTION_LEVEL(uint8_t *Host_buffer);
static void BOOT_WRITE_PROTECTION(uint8_t *Host_buffer);


BOOT_STATUS BOOT_FEATCH_HOST_COMMAND()
{
  BOOT_STATUS status 			= BOOT_NACK;
  uint8_t DataLen 				= 0;
  memset(HOST_BUFFER, 0, HOST_MAX_SIZE);
  HAL_StatusTypeDef HAL_status 	= HAL_ERROR;
  HAL_status = HAL_UART_Receive(&huart2, HOST_BUFFER, 1, HAL_MAX_DELAY);
  if (HAL_status != HAL_OK)
  {
    status = BOOT_NACK;
  }
  else
  {
    DataLen 	= HOST_BUFFER[0];
    HAL_status 	= HAL_UART_Receive(&huart2, &HOST_BUFFER[1], DataLen, HAL_MAX_DELAY);

      if (HAL_status != HAL_OK)
      {
        status = BOOT_NACK;
      }
      else
      {
        switch(HOST_BUFFER[1])
        {
          case BOOT_GET_VER_CMD: BOOT_GET_VERSION(HOST_BUFFER); break;
          case BOOT_GET_HELP_CMD: BOOT_GET_HELP(HOST_BUFFER); break;
          case BOOT_GET_CID_CMD: BOOT_GET_CHIP_IDENTIFICATION_NUMBER(HOST_BUFFER); break;
          case BOOT_GO_TO_ADDR_CMD: BOOT_PRINT_MESSAGE("Jump To Address"); break;
          case BOOT_GET_RDP_STATUS_CMD: BOOT_READ_PROTECTION_LEVEL(HOST_BUFFER); break;
          case BOOT_FLASH_ERASE_CMD: BOOT_FLASH_ERASE(HOST_BUFFER); break;
          case BOOT_MEM_WRITE_CMD: BOOT_WRITE_MEMORY(HOST_BUFFER); break;
          case BOOT_MEM_READ_CMD: BOOT_READ_MEMORY(HOST_BUFFER); break;
          case BOOT_ED_W_PROTECT_CMD: BOOT_WRITE_PROTECTION(HOST_BUFFER); break;
          default : status = BOOT_NACK;
        }
      }
  }
  return status;
}

void BOOT_PRINT_MESSAGE(char *format,...)
{
  char message[100] = {0};
  va_list args;
  va_start(args, format);
  vsprintf(message, format, args);
  HAL_UART_Transmit(&huart2, (uint8_t *)message, sizeof(message), HAL_MAX_DELAY);
  va_end(args);
}

static uint32_t BOOT_CRC_VERIFY(uint8_t *pData, uint32_t DataLen, uint32_t HosrCRC)
{
  uint8_t CRC_STATUS 	= CRC_VERIFING_FAILED;
  uint32_t MCU_CRC 		= 0;
  uint32_t DATA_BUFFER 	= 0;
  for (uint8_t count = 0; count < DataLen; count++)
  {
	DATA_BUFFER = (uint32_t)pData[count];
    MCU_CRC 	= HAL_CRC_Accumulate(&hcrc, &DATA_BUFFER,1);
  }
  __HAL_CRC_DR_RESET(&hcrc);
  if (HosrCRC == MCU_CRC)
  {
	  CRC_STATUS = CRC_VERIFING_PASS;
  }
  else
  {
	  CRC_STATUS = CRC_VERIFING_FAILED;
  }
   return CRC_STATUS;
}

static void BOOT_SEND_ACK(uint8_t DataLen)
{
  uint8_t ACK_value[2] 	= {0};
  ACK_value[0] 			= SEND_ACK;
  ACK_value[1] 			= DataLen;
  HAL_UART_Transmit(&huart2, (uint8_t *)ACK_value, 2, HAL_MAX_DELAY);
}

static void BOOT_SEND_NACK()
{
  uint8_t NACK_value = SEND_NACK;
  HAL_UART_Transmit(&huart2, &NACK_value, sizeof(NACK_value), HAL_MAX_DELAY);
}

static uint8_t PERFORM_FLASH_ERASE(uint32_t Sector_Address, uint8_t Sector_Number)
{
	FLASH_EraseInitTypeDef 	pEraseInit;
	HAL_StatusTypeDef 		HAL_STATUS 		= HAL_ERROR;
	uint32_t 				PAGE_ERROR		= 0;
	uint8_t 				PAGE_STATUS 	= INVALID_PAGE_NUMBER;
	if (Sector_Number > BOOT_FLASH_MAX_PAGE_NUMBER)
	{
		PAGE_STATUS = INVALID_PAGE_NUMBER;
	}
	else
	{
		PAGE_STATUS = VALID_PAGE_NUMBER;
		if (Sector_Number <= (BOOT_FLASH_MAX_PAGE_NUMBER - 1) || Sector_Address == BOOT_FLASH_MASS_ERASE)
		{
			pEraseInit.TypeErase 	= FLASH_TYPEERASE_SECTORS;
			pEraseInit.Banks 		= FLASH_BANK_1;
			pEraseInit.VoltageRange = FLASH_VOLTAGE_RANGE_3;
			if (Sector_Address == BOOT_FLASH_MASS_ERASE)
			{
				pEraseInit.Sector 		= FLASH_SECTOR_0;
				pEraseInit.NbSectors 	= 12;
			}
			else
			{
				pEraseInit.Sector 		= Sector_Address;
				pEraseInit.NbSectors 	= Sector_Number;
			}
			HAL_FLASH_Unlock();
			HAL_STATUS 	= HAL_FLASHEx_Erase(&pEraseInit, &PAGE_ERROR);
			HAL_FLASH_Lock();
			if (HAL_STATUS == HAL_OK && PAGE_ERROR == HAL_SUCCESSFUL_ERASE)
			{
				PAGE_STATUS = SUCCESSFUL_ERASE;
			}
			else
			{
				PAGE_STATUS = UNSUCCESSFUL_ERASE;
			}
		}
		else
		{
			PAGE_STATUS = INVALID_PAGE_NUMBER;
		}
	}
	return PAGE_STATUS;
}

static void BOOT_GET_VERSION(uint8_t *Host_buffer)
{
  uint8_t Version[4] =
  {
		BOOT_VENDOR_ID,
		BOOT_SW_MAJOR_VERSION,
		BOOT_SW_MINOR_VERSION,
		BOOT_SW_PATCH_VERSION
  };
  uint16_t HOST_PACKET_LEN 	= 0;
  uint32_t CRC_VALUE 		= 0;
  HOST_PACKET_LEN 			= Host_buffer[0] + 1;
  CRC_VALUE 				= *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
  if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
  {
	  BOOT_SEND_ACK(4);
	  HAL_UART_Transmit(&huart2, (uint8_t*)Version, 4, HAL_MAX_DELAY);
  }
  else
  {
	  BOOT_SEND_NACK();
  }
}

static void BOOT_GET_HELP(uint8_t *Host_buffer)
{
  uint8_t BOOT_ALL_CMD[9] =
  {
	BOOT_GET_VER_CMD,        // Command to get bootloader version information
	BOOT_GET_HELP_CMD,       // Command to get list of supported commands (this command)
	BOOT_GET_CID_CMD,        // Command to get chip identification data
	BOOT_GET_RDP_STATUS_CMD, // Command to read flash protection status
	BOOT_GO_TO_ADDR_CMD,     // Command to jump to a specified address in memory
	BOOT_FLASH_ERASE_CMD,    // Command to erase flash memory sectors
	BOOT_MEM_WRITE_CMD,      // Command to write data to memory
	BOOT_ED_W_PROTECT_CMD,   // Command to enable/disable write protection
	BOOT_MEM_READ_CMD        // Command to read data from memory
  };
  uint16_t HOST_PACKET_LEN 	= 0;
  uint32_t CRC_VALUE 		= 0;
  HOST_PACKET_LEN 			= Host_buffer[0] + 1;
  CRC_VALUE 				= *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
  if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
  {
	  BOOT_SEND_ACK(6);
	  HAL_UART_Transmit(&huart2, (uint8_t*)BOOT_ALL_CMD, 6, HAL_MAX_DELAY);
  }
  else
  {
	  BOOT_SEND_NACK();
  }
}

static void BOOT_GET_CHIP_IDENTIFICATION_NUMBER(uint8_t *Host_buffer)
{
  uint16_t CHIP_ID 			= 0;
  uint16_t HOST_PACKET_LEN 	= 0;
  uint32_t CRC_VALUE 		= 0;
  HOST_PACKET_LEN 			= Host_buffer[0] + 1;
  CRC_VALUE 				= *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
  if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
  {
	  CHIP_ID = (uint16_t)(DBGMCU->IDCODE & 0x00000FFF);
	  BOOT_SEND_ACK(2);
	  HAL_UART_Transmit(&huart2, (uint8_t*)&CHIP_ID, 2, HAL_MAX_DELAY);
  }
  else
  {
	  BOOT_SEND_NACK();
  }
}

static void BOOT_FLASH_ERASE(uint8_t *Host_buffer)
{
  uint8_t ERASE_STATUS 		= UNSUCCESSFUL_ERASE;
  uint16_t HOST_PACKET_LEN 	= 0;
  uint32_t CRC_VALUE 		= 0;
  HOST_PACKET_LEN 			= Host_buffer[0] + 1;
  CRC_VALUE 				= *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
  if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
  {
	  ERASE_STATUS = PERFORM_FLASH_ERASE(*((uint32_t*)&Host_buffer[2]),Host_buffer[6]);
	  BOOT_SEND_ACK(1);
	  HAL_UART_Transmit(&huart2, (uint8_t*)&ERASE_STATUS, 1, HAL_MAX_DELAY);
  }
  else
  {
	  BOOT_SEND_NACK();
  }
}

static void BOOT_WRITE_MEMORY(uint8_t *Host_buffer)
{
  HAL_StatusTypeDef FLASH_STATUS 		= HAL_OK;
  uint8_t 			WRITE_STATUS 		= FLASH_PAYLOAD_WRITE_FAILED;
  uint16_t 			HOST_PACKET_LEN 	= 0;
  uint32_t 			CRC_VALUE 			= 0;
  uint32_t 			BASE_MEMORY_ADDRESS	= 0;
  uint8_t 			PAYLOAD_LENGTH 		= 0;
  uint8_t 			*PAYLOAD_DATA 		= NULL;
  HOST_PACKET_LEN 						= Host_buffer[0] + 1;
  CRC_VALUE 							= *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
  if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
  {
	BASE_MEMORY_ADDRESS 	= (uint32_t)Host_buffer[5] << 24 | (uint32_t)Host_buffer[4] << 16 | (uint32_t)Host_buffer[3] << 8 | (uint32_t)Host_buffer[2];
	PAYLOAD_LENGTH 			= Host_buffer[6];
	PAYLOAD_DATA 			= &Host_buffer[7];
    if (BASE_MEMORY_ADDRESS >= 0x08000000 && BASE_MEMORY_ADDRESS <= 0x080FFFFF && (BASE_MEMORY_ADDRESS + PAYLOAD_LENGTH) <= 0x08100000)
    {
      HAL_FLASH_Unlock();
      uint32_t CURRENT_ADDRESS = BASE_MEMORY_ADDRESS;
      for (uint8_t i = 0; i < PAYLOAD_LENGTH; i++)
      {
    	FLASH_STATUS = HAL_FLASH_Program(FLASH_TYPEPROGRAM_BYTE, CURRENT_ADDRESS, PAYLOAD_DATA[i]);
        if (FLASH_STATUS != HAL_OK)
        {
          break;
        }
        CURRENT_ADDRESS++;
      }
      HAL_FLASH_Lock();
      if (FLASH_STATUS == HAL_OK)
      {
    	  WRITE_STATUS = FLASH_PAYLOAD_WRITE_PASSED;
      }
      else
      {
    	  WRITE_STATUS = FLASH_PAYLOAD_WRITE_FAILED;
      }
    }
    else
    {
    	WRITE_STATUS = FLASH_PAYLOAD_WRITE_FAILED;
    }
    BOOT_SEND_ACK(1);
    HAL_UART_Transmit(&huart2, (uint8_t*)&WRITE_STATUS, 1, HAL_MAX_DELAY);
  }
  else
  {
	  BOOT_SEND_NACK();
  }
}

static void BOOT_READ_PROTECTION_LEVEL(uint8_t *Host_buffer)
{
  uint8_t 	RDP_STATUS 		= 0xEE; 		// Default : Error Reading Protection Level
  uint16_t 	HOST_PACKET_LEN = 0;
  uint32_t 	CRC_VALUE 		= 0;
  HOST_PACKET_LEN 			= Host_buffer[0] + 1;
  CRC_VALUE 				= *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
  if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
  {
    uint32_t OPTION_BYTE_DATA = FLASH_GET_RDP();
    if (OPTION_BYTE_DATA == RDP_LEVEL_0)
    {
    	RDP_STATUS = 0xAA; // LEVEL 0 - No Protection
    }
    else if (OPTION_BYTE_DATA == RDP_LEVEL_1)
    {
    	RDP_STATUS = 0x55; // LEVEL 1 - Read Protection
    }
    else if (OPTION_BYTE_DATA == RDP_LEVEL_2)
    {
    	RDP_STATUS = 0xCC; // LEVEL 2 - Full Chip Protection
    }
    else
    {
    	RDP_STATUS = 0xEE; // Error Or Unknown Protection Level
    }
    BOOT_SEND_ACK(1);
    HAL_UART_Transmit(&huart2, (uint8_t*)&RDP_STATUS, 1, HAL_MAX_DELAY);
  }
  else
  {
	  BOOT_SEND_NACK();
  }
}

static uint32_t FLASH_GET_RDP(void)
{
  uint32_t RDP_LEVEL = 0xFF;
  FLASH_OBProgramInitTypeDef OB_CONFIG;
  HAL_FLASHEx_OBGetConfig(&OB_CONFIG);
  switch(OB_CONFIG.RDPLevel)
  {
    case OB_RDP_LEVEL_0: RDP_LEVEL = RDP_LEVEL_0; break;
    case OB_RDP_LEVEL_1: RDP_LEVEL = RDP_LEVEL_1; break;
    case OB_RDP_LEVEL_2: RDP_LEVEL = RDP_LEVEL_2; break;
    default: RDP_LEVEL = RDP_ERROR; break;
  }
  return RDP_LEVEL;
}

static void BOOT_READ_MEMORY(uint8_t *Host_buffer)
{
    uint8_t 	READ_STATUS 	= MEM_READ_FAILED;
    uint16_t 	HOST_PACKET_LEN = 0;
    uint32_t 	CRC_VALUE 		= 0;
    uint32_t 	MEMORY_ADDRESS 	= 0;
    uint8_t 	DATA_LENGTH 	= 0;
    uint8_t 	READ_DATA[256] 	= {0};
    HOST_PACKET_LEN 			= Host_buffer[0] + 1;
    CRC_VALUE 					= *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
    if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
    {
    	MEMORY_ADDRESS = (uint32_t)Host_buffer[5] << 24 | (uint32_t)Host_buffer[4] << 16 | (uint32_t)Host_buffer[3] << 8 | (uint32_t)Host_buffer[2];
    	DATA_LENGTH = Host_buffer[6];
        if (BOOT_VALIDATE_MEMORY_ACCESS(MEMORY_ADDRESS, DATA_LENGTH))
        {
        	READ_STATUS = MEM_READ_SUCCESS;
            for (uint8_t i = 0; i < DATA_LENGTH; i++)
            {
            	READ_DATA[i] = *(uint8_t*)(MEMORY_ADDRESS + i);
            }
            BOOT_SEND_ACK(DATA_LENGTH + 1);
            HAL_UART_Transmit(&huart2, &READ_STATUS, 1, HAL_MAX_DELAY);
            HAL_UART_Transmit(&huart2, READ_DATA, DATA_LENGTH, HAL_MAX_DELAY);
        }
        else
        {
        	READ_STATUS = MEM_READ_FAILED;
            BOOT_SEND_ACK(1);
            HAL_UART_Transmit(&huart2, &READ_STATUS, 1, HAL_MAX_DELAY);
        }
    }
    else
    {
    	BOOT_SEND_NACK();
    }
}

static uint8_t BOOT_VALIDATE_MEMORY_ACCESS(uint32_t Address, uint8_t Length)
{
    // Allow Reading From Flash Memory (0x08000000 - 0x080FFFFF)
    if (Address >= 0x08000000 && (Address + Length) <= 0x08100000) return 1;
    // Allow Reading From RAM (0x20000000 - 0x20020000)
    if (Address >= 0x20000000 && (Address + Length) <= 0x20020000) return 1;
    // Allow Reading From System Memory (Bootloader Area)
    if (Address >= 0x1FFF0000 && (Address + Length) <= 0x1FFF7A00) return 1;
    return 0;
}

static void BOOT_WRITE_PROTECTION(uint8_t *Host_buffer)
{
    uint8_t 	PROTECTION_STATUS 	= PROTECTION_FAILED;
    uint16_t 	HOST_PACKET_LEN 	= 0;
    uint32_t 	CRC_VALUE 			= 0;
    uint8_t 	PROTECTION_ACTION 	= 0;
    uint32_t 	SECTOR_BITMASK 		= 0;
    HOST_PACKET_LEN = Host_buffer[0] + 1;
    CRC_VALUE = *(uint32_t*)(Host_buffer + HOST_PACKET_LEN - 4);
    if (CRC_VERIFING_PASS == BOOT_CRC_VERIFY((uint8_t*)&Host_buffer[0], HOST_PACKET_LEN - 4, CRC_VALUE))
    {
    	PROTECTION_ACTION = Host_buffer[2];          // Extract protection action (enable/disable)
        // Extract sector bitmask (4 bytes, little endian)
    	SECTOR_BITMASK = (uint32_t)Host_buffer[6] << 24 | (uint32_t)Host_buffer[5] << 16 | (uint32_t)Host_buffer[4] << 8 | (uint32_t)Host_buffer[3];
        // Validate Sector BiTmask (Only Bits 0-11 Are Valid For STM32F407)
        if ((SECTOR_BITMASK & 0xFFFFF000) == 0)
        {
            HAL_FLASH_Unlock();
            HAL_FLASH_OB_Unlock();
            FLASH_OBProgramInitTypeDef OB_CONFIG;
            HAL_FLASHEx_OBGetConfig(&OB_CONFIG);
            if (PROTECTION_ACTION == WRITE_PROTECT_ENABLE)
            {
                // Enable Write Protection For Specified Sectors
            	OB_CONFIG.WRPState 	= OB_WRPSTATE_ENABLE;
            	OB_CONFIG.WRPSector 	= SECTOR_BITMASK;
            }
            else if (PROTECTION_ACTION == WRITE_PROTECT_DISABLE)
            {
                // Disable Write Protection For Specified Sectors
            	OB_CONFIG.WRPState 	= OB_WRPSTATE_DISABLE;
            	OB_CONFIG.WRPSector 	= SECTOR_BITMASK;
            }
            HAL_StatusTypeDef HAL_STATUS = HAL_FLASHEx_OBProgram(&OB_CONFIG);
            if (HAL_STATUS == HAL_OK)
            {
                HAL_FLASH_OB_Launch();
                PROTECTION_STATUS = PROTECTION_SUCCESS;
            }
            HAL_FLASH_OB_Lock();
            HAL_FLASH_Lock();
        }
        BOOT_SEND_ACK(1);
        HAL_UART_Transmit(&huart2, (uint8_t*)&PROTECTION_STATUS, 1, HAL_MAX_DELAY);
    }
    else
    {
    	BOOT_SEND_NACK();
    }
}
