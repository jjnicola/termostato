/* 
 * File:   text_utils.h
 * Author: Juan Jose Nicola
 * Comments:
 * Revision history: 
 */

// This is a guard condition so that contents of this file are not included
// more than once.  
#ifndef TEXT_UTILS_H
#define	TEXT_UTILS_H

#include <xc.h> // include processor files - each processor file is guarded.  
enum cmds {TMP = 0, STY, RST};
char cmd[3][4] = {"TMP\0", "STY\0", "RST\0"};

void val2temp (int, char *);
void cmdchk(char *);

#endif
