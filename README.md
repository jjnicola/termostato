# termostato
Beer fermentation temperature control

This a temperature control for beer fermentation. Since the yeast is an alive organism, it needs good condition to live. If I want a good beer, I have to provide it not only sugar but also a confortable enviroment. Therefore this temperature control allows me to 
set a target temperature on my fridge depending on the strain and on the beer style I want.

The microcontroler used in this project is a PIC 16F877A from ON-Semi. This initial step use a LM35 as temperature sensor. The LM35 output is amplified with a LM324 to gain precision when it is converted to a binary value, using the full range 10 bits of the internal ADC. The set temperature and the read temperature are shown in 16x2 LCD display. To set the target temperature, there is a button with a debounce circuit, to avoid debouncing by software.

This project will contains:

- The code to be burned into the PIC.
- The schematics
- list of components.
