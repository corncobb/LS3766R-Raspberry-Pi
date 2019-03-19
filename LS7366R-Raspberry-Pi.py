#!/usr/bin/python3

#NOTE: All credit goes to Federico Bolanos. His original repo is here: https://github.com/fbolanos/LS7366R/blob/master/LS7366R.py
#I, Cameron Cobb, have updated this library to make it work for my needs
#and to make it usable for Python 3.

#Make sure you watch the video and check schematic for proper wiring.

#Python library to interface with the chip LS7366R for the Raspberry Pi
#Written by Federico Bolanos
#Last Edit: March 17th 2019 - Cameron Cobb
#Reason: Updated for Python 3.0 and above.

#Make sure you do a "pip install spidev"

# Usage: import LS7366R then create an object by calling enc = LS7366R(CSX, CLK, BTMD)
# CSX is either CE0 or CE1, CLK is the speed, BTMD is the bytemode 1-4 the resolution of your counter.
# example: lever.Encoder(0, 1000000, 4)
# These are the values I normally use.

import spidev 
from time import sleep

class LS7366R():

    #-------------------------------------------
    # Constants

    #   Commands
    CLEAR_COUNTER = 0x20
    CLEAR_STATUS = 0x30
    READ_COUNTER = 0x60
    READ_STATUS = 0x70
    WRITE_MODE0 = 0x88
    WRITE_MODE1 = 0x90

    #   Modes

    #May need to be change "QUADRATURE_COUNT_MODE" line depending on the quadrature count mode... look at datasheet.
    #These values are in HEX (base 16) whereas the data sheet displays them in binary.
    #Datasheet can be found here: https://www.lsicsi.com/pdfs/Data_Sheets/LS7366R.pdf

    #0x00: non-quadrature count mode. (A = clock, B = direction).
    #0x01: x1 quadrature count mode (one count per quadrature cycle).
    #0x02: x2 quadrature count mode (two counts per quadrature cycle).
    #0x03: x4 quadrature count mode (four counts per quadrature cycle).

    QUADRATURE_COUNT_MODE = 0x00


    FOURBYTE_COUNTER = 0x00
    THREEBYTE_COUNTER = 0x01
    TWOBYTE_COUNTER = 0x02
    ONEBYTE_COUNTER = 0x03

    BYTE_MODE = [ONEBYTE_COUNTER, TWOBYTE_COUNTER, THREEBYTE_COUNTER, FOURBYTE_COUNTER]

    #   Values
    max_val = 4294967295
    
    # Global Variables

    counterSize = 4 #Default 4
    
    #----------------------------------------------
    # Constructor

    def __init__(self, CSX, CLK, BTMD):
        self.counterSize = BTMD #Sets the byte mode that will be used


        self.spi = spidev.SpiDev() #Initialize object
        self.spi.open(0, CSX) #Which CS line will be used
        self.spi.max_speed_hz = CLK #Speed of clk (modifies speed transaction) 

        #Init the Encoder
        print('Clearing Encoder CS%s\'s Count...\t' % (str(CSX)), self.clearCounter())
        print('Clearing Encoder CS%s\'s Status..\t' % (str(CSX)), self.clearStatus())

        self.spi.xfer2([self.WRITE_MODE0, self.QUADRATURE_COUNT_MODE])
        
        sleep(.1) #Rest
        
        self.spi.xfer2([self.WRITE_MODE1, self.BYTE_MODE[self.counterSize-1]])

    def close(self):
        print('\nThanks for using me! :)')
        self.spi.close()

    def clearCounter(self):
        self.spi.xfer2([self.CLEAR_COUNTER])

        return '[DONE]'

    def clearStatus(self):
        self.spi.xfer2([self.CLEAR_STATUS])

        return '[DONE]'

    def readCounter(self):
        readTransaction = [self.READ_COUNTER]

        for i in range(self.counterSize):
            readTransaction.append(0)
            
        data = self.spi.xfer2(readTransaction)

        EncoderCount = 0
        for i in range(self.counterSize):
            EncoderCount = (EncoderCount << 8) + data[i+1]

        if data[1] != 255:    
            return EncoderCount
        else:
            return (EncoderCount - (self.max_val+1))  
        
    def readStatus(self):
        data = self.spi.xfer2([self.READ_STATUS, 0xFF])
        
        return data[1]


if __name__ == "__main__":
    from time import sleep
    
    encoder = LS7366R(0, 1000000, 4)
    try:
        while True:
            print("Encoder count: ", encoder.readCounter(), " Press CTRL-C to terminate test program.")
            sleep(0.5)
    except KeyboardInterrupt:
        encoder.close()
        print("All done, bye bois.")
