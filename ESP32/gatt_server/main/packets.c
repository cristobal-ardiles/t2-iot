#include <math.h>
#include <stdlib.h>
#include "esp_system.h"
#include "esp_mac.h"
#include "esp_log.h"
#include <string.h>
#include "packets.h"

void header(char* dest, char protocol, char transport_layer, short data_length){
    char* ID = "D1";
    memcpy((void*) &(dest[0]), (void*) ID, 2);
	uint8_t* MAC_addrs = malloc(6);
	esp_efuse_mac_get_default(MAC_addrs);
	memcpy((void*) &(dest[2]), (void*) MAC_addrs, 6);
    dest[8]= transport_layer;
	dest[9]= protocol;
	memcpy((void*) &(dest[10]), (void*) &data_length, 2);
	free(MAC_addrs);
}