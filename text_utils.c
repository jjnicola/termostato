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

int c2i (char *buffer)
{
    int val = 0;
    val = (buffer[4] - 48 ) * 100;
    val = val + (buffer[5] - 48 ) * 10;
    val = val + (buffer[6] - 48 );
    return val;
}

int check_cmd(char* buffer)
{
    int cmd_r;
    int i, j;
    for (j = 0; j < 3; j++)
    {
        cmd_r = -1;
        for (i = 0; i < 3; i++)
        {
            if (buffer[i] == cmd[j][i])
                cmd_r++;
        }
        if (cmd_r == 2)
            return j;
                      
    }
    
    /*if (buffer[0]  == 'T' && buffer[1] == 'M' && buffer[2] == 'P')
        cmd_r = 0;
    if (buffer[0]  == 'S' && buffer[1] == 'T' && buffer[2] == 'Y')
        cmd_r = 1;
    if (buffer[0]  == 'R' && buffer[1] == 'S' && buffer[2] == 'T')
        cmd_r = 2;
    */
    return -1;
}

