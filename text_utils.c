/* 
 * File:   text_utils.c
 * Author: Juan Nicola
 * Comments: 
 * Revision history: 
 */
#include "text_utils.h"

/** Brief Convert an integer into a string with Temperature Format. 
 * e.g. 127 will be 12.7C
 */
void val2temp(int read_value, char *temp_msg)
{   
    temp_msg[0] = read_value/100 + 48;
    temp_msg[1] = (read_value % 100 ) / 10 + 48;
    temp_msg[2] = '.';
    temp_msg[3] = read_value % 10 + 48;
    temp_msg[4] = 'C';
}
