#ifndef BOOTLOADER_H_
#define BOOTLOADER_H_

#include "string.h"
#include "stdarg.h"
#include "stdio.h"
#include "usart.h"
#include "crc.h"


#define BOOT_GET_VER_CMD   			0x10
#define BOOT_GET_HELP_CMD   		0x11
#define BOOT_GET_CID_CMD   			0x12
#define BOOT_GET_RDP_STATUS_CMD     0x13
#define BOOT_GO_TO_ADDR_CMD   		0x14
#define BOOT_FLASH_ERASE_CMD   		0x15
#define BOOT_MEM_WRITE_CMD   		0x16
#define BOOT_ED_W_PROTECT_CMD       0x17
#define BOOT_MEM_READ_CMD           0x18
#define HOST_MAX_SIZE           	200
#define CRC_VERIFING_FAILED     	0x00
#define CRC_VERIFING_PASS       	0x01
#define SEND_NACK               	0xAB
#define SEND_ACK                	0xCD
#define BOOT_VENDOR_ID   			100
#define BOOT_SW_MAJOR_VERSION   	1
#define BOOT_SW_MINOR_VERSION   	1
#define BOOT_SW_PATCH_VERSION   	0
#define BOOT_FLASH_MAX_PAGE_NUMBER  12
#define BOOT_FLASH_MASS_ERASE    	0xFF
#define INVALID_PAGE_NUMBER   		0x00
#define VALID_PAGE_NUMBER   		0x01
#define UNSUCCESSFUL_ERASE    		0x02
#define SUCCESSFUL_ERASE   			0x03
#define HAL_SUCCESSFUL_ERASE   		0xFFFFFFFFU
#define ADDRESS_IS_INVALID   		0x00
#define ADDRESS_IS_VALID	   		0x01
#define FLASH_PAYLOAD_WRITE_FAILED   0x00
#define FLASH_PAYLOAD_WRITE_PASSED   0x01
#define RDP_LEVEL_0                 0xAA
#define RDP_LEVEL_1                 0x55
#define RDP_LEVEL_2                 0xCC
#define RDP_ERROR                   0xEE
#define MEM_READ_SUCCESS            0x01
#define MEM_READ_FAILED             0x00
#define WRITE_PROTECT_ENABLE        0x01
#define WRITE_PROTECT_DISABLE       0x00
#define PROTECTION_SUCCESS          0x01
#define PROTECTION_FAILED           0x00

typedef enum
{
  BOOT_NACK = 0,
  BOOT_ACK
} BOOT_STATUS;

BOOT_STATUS BOOT_FEATCH_HOST_COMMAND();
void BOOT_PRINT_MESSAGE(char *format,...);

#endif
