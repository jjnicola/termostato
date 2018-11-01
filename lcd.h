#ifndef LCD_H
#define LCD_H
/*-------------------------------------------------------------------------------------------------
  LCD Library (44780 compatible).
  No usa el pin R/W, ya que normalmente se lo conecta a la masa del circuito.

  Fecha de creación: 8/04/2009
  Autor: Felixls
  Web: http://sergiols.blogspot.com
  Changelog:
  Fecha   Versión     Observaciones
  8/4/09  1.00        Versión inicial
  Frecuencia de reloj: 4MHZ
  Compilador: SDCC 2.9.1
  -------------------------------------------------------------------------------------------------*/
/*  PORTD:4  ----->  LCD bit 4           */
/*  PORTD:5  ----->  LCD bit 5           */
/*  PORTD:6  ----->  LCD bit 6           */
/*  PORTD:7  ----->  LCD bit 7           */
/*  PORTD:1  ----->  LCD RS              */
/*  PORTD:2  ----->  LCD E               */


#define LCD_DATA                 PORTD // Data Port
#define LCD_DATA_TRIS            TRISD // Data Port Control
#define LCD_RS                   RD1   // Mode
#define LCD_ENABLE               RD2   // Data Send enable/disable
#define LCD_CLEAR                0x01 // Clear Display
#define LCD_HOME                 0x02 // Cursor to Home
#define LCD_NORMAL               0x06 // Cursor in incremental mode
#define LCD_REV                  0x04 // Normal-reverse
#define LCD_SCROLL               0x07 // Use scroll
#define LCD_SCROLL_REV           0x05 // Reverse
#define LCD_D8_BIT               0x38 // 8 bit 2 lines ( 5x7 font )
#define LCD_D4_BIT_CONF          0x20 // 4 bit
#define LCD_D4_BIT               0x28 // 4 bit 2 lines ( 5x7 font )
#define LCD_RESET                0x30 // Reset
#define LCD_DIS_ON               0x0C // Display on mode 2 lines
#define LCD_DIS_OFF              0x08 // Display off
#define LCD_LINE1                0x80 // Line 1 position 1
#define LCD_LINE2                0xC0 // Line 2 position 1
#define LCD_CURSOR_ON            0x0E // Cursor on
#define LCD_CURSOR_OFF           0x0C // Cursor off
#define LCD_BLINK_ON             0x0F // Cursor blink
#define LCD_CURSOR_DER           0x14 // Move cursor right
#define LCD_CURSOR_IZQ           0x10 // Mover cursor link
#define LCD_DISPLAY__DER         0x1C // Scroll display right
#define LCD_DISPLAY__IZQ         0x18 // Scroll display link
#define LCD_CHARMODE             0x01
#define LCD_COMMANDMODE          0x00

//#include "delay.h"

void lcd_init (void);
void lcd_send( char mode, char dato );
void lcd_message (const char * mess );
void lcd_send_quartet( char mode, char dato );
void lcd_send( char mode, char dato );
void lcd_init (void);
void lcd_message ( const char * mess );
char lcd_hexa(char a);
void lcd_showint(unsigned int value);
void lcd_showintright(unsigned int value, int index);
void lcd_sendentero(char mode, long int datoentero);
void lcd_show_lines (const char *line1, const char *line2);
#endif
