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

/** Being conservative, in case of failure the best cases is to low down
the temperature. Better cold, green apple, stop fermentation which can be restarted later
than fusels which is not possible to eliminate. Therefore the fridge is "normal ON" when there is
no signal from the controler, and must be explicitely OFF with a signal to leave the temp to reise up.*/
#define FRIDGE_OFF 1
#define FRIDGE_ON  0

int MAX, MIN;
int style_set;
int custom_temp;
int hyst = 2; //Hysteresis
__bit new_cmd = 0;
char buffercmd[8] = "CMD:VAL\0";
char cmdcount = 0;

void __interrupt () ISR(void)
{
  /* Debounce done by hardware*/
  if (INTF == ON)
    {
      delay_ms (100);
      if (RB0 == 1)
      {
        if (style_set < 6)
            style_set++;
        else
            style_set = 0;
      }
      INTF = OFF;
    }
  if (RCIF == ON)
    {
      char a;
      a = getch();
      if (new_cmd)
        return;
      if (a == '\r')
        return;
      if (a == '\n')
        return;
      if (a == '%')
        {
          new_cmd = 1;
          cmdcount = 0;
          return;
        }
      buffercmd[cmdcount] = a;
      cmdcount++;
      if (cmdcount > 6)
        cmdcount = 0;
      //RCIF is cleared by the hardware
    }
}

int main (int argc, char** argv)
{
  TRISA = 0x0d;  // AD input.
  TRISB = 0x07;  //three first pins as input in Port B.
  char buffer_temp[] = "00000\0";
  char log_data[] =  "000000S\0";
  float temp_read = 0;
  int counterloop = 0;
  unsigned char a;
  int fridge_state = 0;
  int fridge_change_state_wait_count = 0;

  lcd_init ();
  lcd_show_lines ("  Ammann", "Cerveceria");
  delay_ms (3000);
  style_set = ENGLISH;
  custom_temp = temp[style_set];

  /* Init serial port. */
  init_comms ();
  delay_ms (100);
  TRISCbits.TRISC5 = 0;  //Set port C as output port.

  /* Set interruptions */
  PEIE = ON;     // Enabel perisferic interruption.
  INTF = OFF;    // Clean interruption flag for RB0.
  INTE = ON;     // Enable interruption for RB0.
  INTEDG = ON;   // Set ascendent edge interruption on rb0.
  GIE = ON;      // Enable global interruption.

  /* Begin infinite loop. */
  while(1)
    {
      if (style_set != CUSTOM)
        custom_temp = temp[style_set];

      val2temp (custom_temp, buffer_temp);
      lcd_show_lines (style[style_set], buffer_temp);

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
      lcd_show_lines ("Temp. Actual", buffer_temp);

      /* Set the new style or custom temperature. */
      if (new_cmd == 1)
        {
          int selcmd;
          new_cmd = 0;
          cmdcount = 0;
          lcd_show_lines ("New setup", buffercmd);
          selcmd = cmdchk (buffercmd);
          if (selcmd == GTL)
            {
              val2temp ((int)temp_read, log_data);
              log_data[5] = 48 + RC5;
              comm_send_log (log_data);
            }
          else if (selcmd == STY)
            {
              style_set = cmd2int (buffercmd);
              lcd_show_lines ("New Style\0", style[style_set]);
            }
          else if (selcmd == RST)
            {
              MAX = 0;
              MIN = 0;
              style_set = ENGLISH;
              lcd_show_lines ("Reset\0", "...\0");
            }
          else if (selcmd == TMP )
            {
              custom_temp = cmd2int (buffercmd);
              style_set = CUSTOM;
              lcd_show_lines ("Configure\0", buffercmd);
            }
          else if (selcmd == GTS)
            {
              val2temp (custom_temp, log_data);
              log_data[5] = 48 + style_set;
              comm_send_log (log_data);
            }
        }

      /* Check if the rb0 interruption is disables and if it must be enabled again.*/
      if (INTE == OFF)
        {
          fridge_change_state_wait_count--;

          /* After five time, the rb0 interruption is enabled again.*/
          if (fridge_change_state_wait_count == 0)
            INTE = ON;
        }

      /* Compare temperatures and set the fridge on or off.
       * It takes in count the hysteresis to avoid start and stop
       * the fridge in short time periods.
       * When the fridge starts or stops, the motor consumes some power,
       * and a lack on the circuit design, or even some induction produces
       * the selected state to increase in one or 2 posistion (like somebody pressing
       * the style selector button).
       * To avoid this, the rb0 (style selector button) is disable.
       */
      if (fridge_state == FRIDGE_OFF)
        {
          if (temp_read > (custom_temp + hyst))
            {
              // Disable rb0 interruption
              INTE = OFF;

              RC5 = FRIDGE_ON;
              fridge_state = FRIDGE_ON;
              fridge_change_state_wait_count = 5;

            }
        }
      else
        {
          if (temp_read < (custom_temp - hyst))
            {
              // Disable rb0 interruption
              INTE = OFF;

              RC5 = FRIDGE_OFF;
              fridge_state = FRIDGE_OFF;
              fridge_change_state_wait_count = 5;
            }
        }
    } /* End infinit loop */

  return (EXIT_SUCCESS);
}
