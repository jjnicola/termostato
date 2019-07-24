/* 
 * File:   serial.c
 * Author: Juan Nicola
 * Comments: 
 * Revision history: 
 */

#include "serial.h"

void init_comms(void)
{
        SPBRG = DIVIDER;
        TXSTA = (SPEED|NINE_BITS|0x20);
        RCSTA = (NINE_BITS|0x90);
        TRISC7 = INPUT; //RX
        TRISC6 = OUTPUT; //TX

        
        SPBRG=DIVIDER;
        BRGH=1;     //data rate for sending (see 16F876 manual under 'USART')
        SYNC=0;     //asynchronous
        SPEN=1;     //enable serial port pins
        SREN=0;     // Single Receive Enable bit. No effect in Async mode
        TXIE=0;     //disable tx interrupts
        RCIE=1;     //enable rx interrupts
        TX9=0;      //8-bit transmission
        RX9=0;      //8-bit reception
        CREN=1;     //enable reception
        TXEN=0;     //reset transmitter
        TXEN=1;     //enable the transmitter
        
}

void putch(char byte)
{
        /* output one byte */
        while(!TRMT)    /* set whilst TX in progress */
                continue;
        TXREG = byte;
}

char getch() {
        /* retrieve one byte */
        while(!RCIF)    /* set when register is not empty */
               continue;
        return RCREG;
}

/**  @Brief Send a 8 chars length string through the serial port. 
     19.1C1S -> 19.1 Cent. degrees and 1S is device status ON.
 */

void comm_send_log (char *log_data)
{
  while (*log_data)
    {
      putch (*log_data);
      log_data++;
    }
}
