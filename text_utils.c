#include "text_utils.h"

/* Convierte un entero a un string con formato de temperatura.
 * por ejemplo el 127 entero, se representa como 12.7C  
 */
void val2temp(int valor, char *temp_msg)
{   
    temp_msg[0] = valor/100 + 48;
    temp_msg[1] = (valor % 100 ) / 10 + 48;
    temp_msg[2] = '.';
    temp_msg[3] = valor % 10 + 48;
    temp_msg[4] = 'C';
}