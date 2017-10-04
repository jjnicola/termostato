/* 
 * File:   delay.c
 * Author: Juan Nicola
 * Comments: 
 * Revision history: 
 */
#include "delay.h"

void delay_ms (int i){
    while (i != 0){
        int a = 400;
        while (a != 0){
            asm ("NOP");
            a--;
        }
        i--;
    }
}
