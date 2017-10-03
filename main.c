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
#include "estilos.h"
#include "text_utils.h"
#include "adc.h"
#include "serial.h"

#define ON        1
#define OFF       0
#define APAGADA   1
#define ENCENDIDA 0

int MAX, MIN;
int estilo_actual;
int custom_temp;
bit new_cmd = 0;
unsigned char buffercmd[8] = "CMD:VAL\0";
unsigned char cmdcount = 0;

void show_lines(const char *linea1, const char *linea2)
{
  lcd_send(LCD_COMMANDMODE, LCD_CLEAR);
  lcd_send(LCD_COMMANDMODE, LCD_LINE1);
  lcd_message(linea1);
  lcd_send(LCD_COMMANDMODE, LCD_LINE2);
  delay_ms (100);
  lcd_message(linea2);
  delay_ms (500);
}

void interrupt ISR()
{
  /* Debounce done by hardware*/
  if (INTF == 1)
    {
      if (estilo_actual < 6)
        estilo_actual++;
      else
        estilo_actual = 0;
      INTF = 0;
    }
}

int main(int argc, char** argv)
{
  TRISA = 0x0d; // AD input
  TRISB = 0x07;  //three first pins as input in Port B
  TRISC = 0x00; //Puerto C como salida
  char buffer_temp[] = "00000\0";
  float temp_read = 0;
  int contaloop = 0;
  unsigned char a;

  const char *linea1 = "  Ammann";
  const char *linea2 = "Cerveceria";
  lcd_init();
  show_lines(linea1, linea2);
  delay_ms(3000);
  estilo_actual = ENGLISH;
  custom_temp = temp[estilo_actual];

  /* Inicializo el puerto serie. */
  PEIE = ON; // Habilito interrupcion para perisfericos.
  INTF = OFF; //flag de interrupcion en B0
  INTE = ON; // Habilito la interrupcion en el pin B0
  INTEDG = OFF; //Interrupcion rb0 en el flanco ascendente.
  GIE = ON;  //habilito las interrupciones globales.

  /* Comienza loop infinito. */
  while(1)
    {
      if (estilo_actual != CUSTOM)
        custom_temp = temp[estilo_actual];

      val2temp(custom_temp, buffer_temp);
      show_lines (estilo[estilo_actual], buffer_temp);

      /* Leo AD y lo muestro*/
      adc_init(FOSC_64,A1_R0,INT_OFF);
      delay_ms(10);
      temp_read = 0;
      contaloop = 50;
      while(contaloop != 0)
        {
          temp_read = temp_read + adc_read(CHAN0) ;
          contaloop--;
        }
      adc_close();
      temp_read = (temp_read/50) * 0.423;

      val2temp((int)temp_read, buffer_temp);
      show_lines ("Temp. Actual", buffer_temp);

      int hist = 5; //Histeresis
      if (RC5 == APAGADA) { // heladera apagada
        if (temp_read > (custom_temp + hist))
          RC5 = ENCENDIDA; //
      }else { // heladera encendida
        if (temp_read < (custom_temp - hist))
          RC5 = APAGADA;
      }
    } /* End loop infinito */

  return (EXIT_SUCCESS);
}
