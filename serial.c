#include "serial.h"

void init_comms(void)
{
        SPBRG = DIVIDER;
        TXSTA = (SPEED|NINE_BITS|0x20);
        RCSTA = (NINE_BITS|0x90);
        TRISC7=INPUT;
        TRISC6=OUTPUT;

        
        SPBRG=DIVIDER;
        BRGH=1;     //data rate for sending (see 16F876 manual under 'USART')
        SYNC=0;     //asynchronous
        SPEN=1;     //enable serial port pins
        SREN=0;     // Single Receive Enable bit. No effect in Async mode
        TXIE=0;     //disable tx interrupts
        RCIE=1;     //disable rx interrupts
        TX9=0;      //8-bit transmission
        RX9=0;      //8-bit reception
        CREN=1;     //enable reception
        TXEN=0;     //reset transmitter
        TXEN=1;     //enable the transmitter
        
}

void putch(unsigned char byte)
{
        /* output one byte */
        while(!TRMT)    /* set whilst TX in progress */
                continue;
        TXREG = byte;
}

unsigned char
getch() {
        /* retrieve one byte */
        while(!RCIF)    /* set when register is not empty */
               continue;
        return RCREG;
}


unsigned char
getche(void)
{
        unsigned char c;
        putch(c = getch());
        return c;
}
