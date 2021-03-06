/* 
 * File:   text_utils.c
 * Author: Juan Nicola
 * Comments: 
 * Revision history: 
 */

#include <stdlib.h>
#include <string.h>
#include "text_utils.h"
#include "styles.h"
#include "lcd.h"


/** Brief Convert an integer into a string with Temperature Format. 
 * e.g. 127 will be 12.7C
 */
void val2temp(int read_value, char *temp_msg)
{   
    if (read_value == 0)
    {
        temp_msg[0] = '0';
        temp_msg[1] = '0';
        temp_msg[2] = '.';
        temp_msg[3] = '0';
        temp_msg[4] = 'C';
    }
    temp_msg[0] = read_value/100 + 48;
    temp_msg[1] = (read_value % 100 ) / 10 + 48;
    temp_msg[2] = '.';
    temp_msg[3] = read_value % 10 + 48;
    temp_msg[4] = 'C';
}

/** Brief Receive a string containing 3 numbers and converts
 *  it to integer. It could be a temperature or style.
 */
int cmd2int (char *buffer)
{
    int val = 0;
    val = (buffer[4] - 48 ) * 100;
    val = val + (buffer[5] - 48 ) * 10;
    val = val + (buffer[6] - 48 );
    return val;
}

void cmdcpy (char *dst, char *src, int n)
{
  while (n--)
    *dst++ = *src++;
}
/** Brief Parse a received command. 
 *  Return the cmd integer or -1 in case of unvalid cmd.
 */
int cmdchk(char *buffercmd)
{
  char txtcmd[4] = "aaa\0";
  int selcmd;

  /* Copy the command part of the string received. */
  cmdcpy (txtcmd, buffercmd, 3);
  for (selcmd = 0; selcmd < cmdnum; selcmd++)
    if (!strcmp (txtcmd, cmd[selcmd]))
      {
        return selcmd;
      }
  return -1;
}
