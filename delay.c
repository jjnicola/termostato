#include "delay.h"

void delay_us(char i){
    while (i!=0){
        int a=4;
        while(a!=0){
            asm("NOP");
            a--;
        }
        i--;
    }
}

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