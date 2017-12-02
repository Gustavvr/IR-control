#!/usr/bin/env python

import serial
import io
import argparse
import sys


class Projector(object):
    """Class to encapsulate the projector.
    """

    def __init__(self, serial_port="/dev/ttyUSB0",
                 baudrate=19200, timeout=0.5):
        """Set up serial connection to projector."""

        self._serial_port = serial_port
        self._baudrate = baudrate
        self._timeout = timeout

        self.port = serial.Serial(self._serial_port, self._baudrate,
                                   timeout=self._timeout)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.port,self.port),
                       newline='\n')
# https://www.infocus.com/resources/documents/Reference-Documents/InFocus-IN5310HD-RS232-Commands.pdf
    def __del__(self):
        self.port.close()

    def power_state(self):
        self.sio.write(unicode('(PWR?)'))
        self.sio.flush()
        state = self.sio.readline()
        state = state[11]
        return int(state)
        
    def power_on(self):
        self.sio.write(unicode('(PWR1)'))
        self.sio.flush()
        ret = self.sio.readline()

    def power_off(self):
        self.sio.write(unicode('(PWR0)'))
        self.sio.flush()
        ret = self.sio.readline()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default="/dev/ttyUSB0", help="Defaults to /dev/ttyUSB0")
    parser.add_argument("-b", "--baudrate", type=int, default=19200, help="Defaults to 19200")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet")
    parser.add_argument("-t", "--timeout", type=int, default=0.5, help="Defaults to 0.5")
    parser.add_argument("state", choices=["on", "off"])
    args = parser.parse_args()

    projector = Projector(args.port, args.baudrate, args.timeout)

    if args.state == "on":
      projector.power_on()
    if args.state == "off":
      projector.power_off()
    state = projector.power_state()
    if state == 1:
      if not args.quiet:
        print "on"
      sys.exit(1)
    elif state == 0:
     if not args.quiet:
        print "off"
     sys.exit(0)
    else:
      if not args.quiet:
        print "error"
      sys.exit(2)



if __name__ == '__main__':
    DEBUG = True
    main()      
