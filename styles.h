/* 
 * File:   estilos.h
 * Author: Juan Nicola
 * Comments: 
 * Revision history: 
 */

// This is a guard condition so that contents of this file are not included
// more than once.  
#ifndef XC_HEADER_TEMPLATE_H
#define	XC_HEADER_TEMPLATE_H

#include <xc.h> // include processor files - each processor file is guarded.  

#ifdef	__cplusplus
extern "C" {
#endif /* __cplusplus */

    // TODO If C++ is being used, regular C code needs function names to have C 
    // linkage so the functions can be used by the c code. 

#ifdef	__cplusplus
}
#endif /* __cplusplus */

#endif	/* XC_HEADER_TEMPLATE_H */

#ifndef STYLES_H_INCLUDED
#define STYLES_H_INCLUDED

enum styles {
    MADURACION = 0,
    LAGER,
    KOLSCH,
    SCOTTISH,
    ENGLISH,
    WEIZEN,
    BELGA,
    CUSTOM       
    };
    
char style[8][12] = {"Maduracion\0", "Lager\0",
                "Kolsch\0", "Scottish\0",
                "British Ale\0", "Weizen\0",
                "Belga\0", "Custom\0"};
                
/* Define the temperature in Centigrades degrees. */                
int temp [8] = {0, 100, 150, 160, 180, 190, 200, 0};
#endif
