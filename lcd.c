
//Código:
//
// LCD.C
//
// Autor: Juan Nicola
//
//
// Rutinas para el manejo de un display Hitachi 44780 compatible.
//-------------------------------------------------------------------------------------------------
#include <xc.h>
#include "delay.h"
#include "lcd.h"

void lcd_send_quartet( char mode, char dato )
{
    LCD_RS = mode;
    PORTD = dato  | (PORTD & 0x0f) ;
    LCD_ENABLE = 1;
    delay_ms(1);
    LCD_ENABLE = 0;
}

void lcd_send( char mode, const char dato )
{
    char dat = dato;
    LCD_RS = mode;
    dat = dato & 0xf0;
    PORTD = dat | (PORTD & 0x0f) ;
    LCD_ENABLE = 1;
    delay_ms(1);
    LCD_ENABLE = 0;
    dat = ((dato<<4)& 0xf0);
    PORTD = dat | (PORTD & 0x0f) ;
    LCD_ENABLE = 1;
    delay_ms(1);
    LCD_ENABLE = 0;
    delay_ms(1);
}

void lcd_init (void)
{
  LCD_DATA_TRIS &= 0x00;
  LCD_DATA = 0x00;
  delay_ms(20);
  lcd_send_quartet(LCD_COMMANDMODE, LCD_RESET);
  delay_ms(10);
  lcd_send_quartet(LCD_COMMANDMODE, LCD_RESET);
  delay_ms(10);
  lcd_send_quartet(LCD_COMMANDMODE, LCD_RESET);
  delay_ms(10);
  lcd_send_quartet(LCD_COMMANDMODE, LCD_D4_BIT_CONF);
  delay_ms(10);
  lcd_send(LCD_COMMANDMODE, LCD_D4_BIT);
  delay_ms(10);
  lcd_send(LCD_COMMANDMODE, LCD_CLEAR);
  delay_ms(10);
  lcd_send(LCD_COMMANDMODE, LCD_CURSOR_OFF);
  delay_ms(10);
  lcd_send(LCD_COMMANDMODE, LCD_NORMAL);
  delay_ms(10);
  lcd_send(LCD_COMMANDMODE, LCD_DIS_ON);
  delay_ms(10);
}

void lcd_message (const char * mess )
{
  while ( *mess )
  {
    lcd_send(LCD_CHARMODE, *mess ) ;
    mess++ ;
  }
}