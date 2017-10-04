/* 
 * File:   main.c
 * Author: Juan Jose Nicola
 *
 * Created on July 8, 2017, 6:30 PM
 */
#define _XTAL_FREQ 16000000

#pragma config FOSC = HS        // Oscillator Selection bits (HS oscillator)
#pragma config WDTE = OFF       // Watchdog Timer Enable bit (WDT disabled)
#pragma config PWRTE = OFF      // Power-up Timer Enable bit (PWRT disabled)
#pragma config BOREN = ON       // Brown-out Reset Enable bit (BOR enabled)
#pragma config LVP = OFF        // Low-Voltage (Single-Supply) In-Circuit Serial Programming Enable bit (RB3/PGM pin has PGM function; low-voltage programming enabled)
#pragma config CPD = OFF        // Data EEPROM Memory Code Protection bit (Data EEPROM code protection off)
#pragma config WRT = OFF        // Flash Program Memory Write Enable bits (Write protection off; all program memory may be written to by EECON control)
#pragma config CP = OFF         // Flash Program Memory Code Protection bit (Code protection off)
#pragma config DEBUG = OFF

#include <stdio.h>
#include <stdlib.h>
#include <xc.h>
#include "delay.h"
#include "lcd.h"
#include "styles.h"
#include "text_utils.h"
#include "adc.h"
#include "serial.h"

#define ON         1
#define OFF        0
#define FRIDGE_OFF 1
#define FRIDGE_ON  0

int MAX, MIN;
int style_set;
int custom_temp;
bit new_cmd = 0;
unsigned char buffercmd[8] = "CMD:VAL\0";
unsigned char cmdcount = 0;

void show_lines (const char *linea1, const char *linea2)
{
  lcd_send (LCD_COMMANDMODE, LCD_CLEAR);
  lcd_send (LCD_COMMANDMODE, LCD_LINE1);
  lcd_message (linea1);
  lcd_send (LCD_COMMANDMODE, LCD_LINE2);
  delay_ms (100);
  lcd_message (linea2);
  delay_ms (500);
}

void interrupt ISR()
{
  /* Debounce done by hardware*/
  if (INTF == 1)
    {
      if (style_set < 6)
        style_set++;
      else
        style_set = 0;
      INTF = 0;
    }
}

int main (int argc, char** argv)
{
  TRISA = 0x0d;  // AD input.
  TRISB = 0x07;  //three first pins as input in Port B.
  TRISC = 0x00;  //Set port C as output port.
  char buffer_temp[] = "00000\0";
  float temp_read = 0;
  int counterloop = 0;
  unsigned char a;

  const char *linea1 = "  Ammann";
  const char *linea2 = "Cerveceria";
  lcd_init ();
  show_lines (linea1, linea2);
  delay_ms (3000);
  style_set = ENGLISH;
  custom_temp = temp[style_set];

  /* Set interruptions */
  PEIE = ON;     // Enabel perisferic interruption.
  INTF = OFF;    //Clean interruption flag for RB0.
  INTE = ON;     // Enable interruption for RB0.
  INTEDG = OFF;  //Set ascendent edge interruption on rb0.
  GIE = ON;      //Enable global interruption.

  /* Begin infinite loop. */
  while(1)
    {
      if (style_set != CUSTOM)
        custom_temp = temp[style_set];

      val2temp (custom_temp, buffer_temp);
      show_lines (style[style_set], buffer_temp);

      /* Read ADC and show the temperature*/
      adc_init (FOSC_64,A1_R0,INT_OFF);
      delay_ms (10);
      temp_read = 0;
      counterloop = 50;
      while (counterloop != 0)
        {
          temp_read = temp_read + adc_read (CHAN0) ;
          counterloop--;
        }
      adc_close();
      temp_read = (temp_read/50) * 0.423;

      val2temp ((int)temp_read, buffer_temp);
      show_lines ("Temp. Actual", buffer_temp);

      int hyst = 5; //Hysteresis
      if (RC5 == FRIDGE_OFF)
        {
          if (temp_read > (custom_temp + hyst))
            RC5 = FRIDGE_ON; 
        }
      else
        { 
          if (temp_read < (custom_temp - hyst))
            RC5 = FRIDGE_OFF;
        }
    } /* End loop infinito */

  return (EXIT_SUCCESS);
}
