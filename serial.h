/* 
 * File:   serial.h
 * Author: Juan Nicola
 * Comments: 
 * Revision history: 
 */


#ifndef _SERIAL_H_
#define _SERIAL_H_

#include <xc.h>

#define BAUD 9600
#define NINE 0     /* Use 9bit communication? FALSE=8bit */
#define OUTPUT 1
#define INPUT 1
#define DIVIDER 103 /* From a datasheets table. Xtal:16Mhz Baud:9600*/
#define HIGH_SPEED 1

#if NINE == 1
#define NINE_BITS 0x40
#else
#define NINE_BITS 0
#endif

#if HIGH_SPEED == 1
#define SPEED 0x4
#else
#define SPEED 0
#endif


void init_comms(void);
void putch(unsigned char);
unsigned char getch(void);
unsigned char getche(void);


#endif
