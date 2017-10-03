/*adc.c
Código:
void adc_init(unsigned char fosc, unsigned char pcfg, unsigned char config);
void adc_close(void);
unsigned int adc_read(unsigned char canal);
void adc_startread(unsigned char canal);
*/
#include "adc.h"
#include "delay.h"

void adc_init(unsigned char fosc, unsigned char pcfg, unsigned char config)
{
   ADCON0 = 0;
   ADCON0 = (fosc & 0x03) << 6;         // establecer frecuencia
   ADCON1 = (pcfg & 0x0F)   ;      // establecer entradas
   ADFM = 1;
   if (fosc & 0x04)
      ADCS2 = 1;
   if (config & INT_ON)                 // establecer interrupciones
   {
      ADIF = 0;
      ADIE = 1;
      PEIE = 1;

   }
   ADON = 1;                            // habilitar módulo ADC
}


void adc_close(void)                    // deshabilitar módulo ADC
{
   ADON = 0;
   ADIE = 0;
}


unsigned int adc_read(unsigned char canal)
{
   unsigned int valor;
   ADCON0 &= 0xC7;                     // borrar anteriores selecciones
   ADCON0 |= (canal & 0x07) << 3;      // establecer canal seleccionado
   delay_ms(10);
   GO = 1;                             // iniciar conversión
   while (GO);                         // esperar que termine
   valor = (ADRESH << 8) | ADRESL;       // leer valor
   return valor;
}


void adc_startread(unsigned char canal)
{
   ADCON0 &= 0xC7;                     // borrar anteriores selecciones

   ADCON0 |= (canal & 0x07) << 3;      // establecer canal seleccionado
   delay_ms(10);
   GO = 1;               // iniciar conversión
}

