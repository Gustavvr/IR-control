#!/usr/bin/env python

'''
   Python port of irsend.c
   
   ver. 0.10150102

'''
import socket
import time
import sys
import os.path


#LIRCD = "/var/run/lirc/lircd"

class IRSend(object):

    def __init__(self, device):
        
        if os.path.isfile(device):
        #if address==None: 
            # connect to unix socket
            # yeah no checking in here LIRC dosn't work well on Mac so I don't expect this to really be used.
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            print "Connect to unix socket: %s" % device
            self.sock.connect(device)
            self.sfile = self.sock.makefile()
        else:
            print "IP conncection"
            HOST, PORT = device.rsplit(':')
            print "HOST:%s PORT:%s" % (HOST, PORT) 
            self.sock = None
            for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
                af, socktype, proto, _, sa = res
                try:
                    self.sock = socket.socket(af, socktype, proto)
                except socket.error as msg:
                        self.sock = None
                        print 'Could not create to socket error:' + HOST + ":" +PORT
                        continue
                try:
                    self.sock.connect(sa)
                except socket.error as msg:
                    self.sock.close()
                    self.sock = None
                    print 'Could not connect to remote host error:' + HOST + ":" +PORT
                    continue
                break
            if self.sock is None:
                print 'could not open socket'
                raise
                #sys.exit(1)
            else:
                self.sfile = self.sock.makefile()

    def send_packet(self, packet):
        self.packet = packet
        self.sfile.write(packet)
        self.sfile.flush()      
        return self.read_response()


    def read_response(self):
        resp = []
        while True:
            line = self.sfile.readline().strip()
            resp.append(line)
            if line=="END":
                if "SUCCESS" in resp:
                    return resp
                else:
                    return False
        
    def send(self, codes):
        if not hasattr(self,'sfile'):
            print "no sfile"
        #return 3
        ''' send the specified codes
            codes: list of tuples of (directive, remote, code) or
                   (directive, remote, code, count)
        '''
        packet = ""
        for code in codes:
            directive = code[0]
            remote = code[1]
            if directive=="SEND_ONCE":
                acode = code[2]
#                if len(code)==4:
#                    count = code[3]
#                else:
#                    count = 1
                #packet = "%s %s %s %s\n" % (directive, remote, acode, struct.pack("=I",int(count)))
                packet = "%s %s %s\n" % (directive, remote, acode)
#                if not self.send_packet(packet):
#                    print "Error sending packet: %s" % packet
                return self.send_packet(packet)
            elif directive=="SLEEP":
                print "Sleep %s" % code[1]
                time.sleep(code[1])
            elif directive=="LIST":
                acode = code[2]
#               if len(code)==4:
#                    count = code[3]
#                else:
#                    count = 1 
                packet = "%s %s %s\n" % (directive, remote, acode)
                return self.send_packet(packet)
                # if not self.send_packet(packet):
                #    print "Error sending packet: %s" % packet


if __name__ == "__main__":
    
    from optparse import OptionParser

    parser = OptionParser(usage="""%prog [address or socket] -h|--help -a|-all""",
        description=__doc__)
    parser.add_option('-a', '--all', action="store_true", dest="showAll", help="List all buttons on all remotes", default=False)
    #parser.add_option('-s', '--send_once', action="store_true", dest="sendOnce", help="Send one command ", default=False)
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error("incorrect number of arguments.\nNeed at least a TCP/IP or unix socket (e.g  192.168.0.1:8765)")


    sender = IRSend(args[0])
    
    remotes = sender.send([("LIST", "", "")])
    if remotes:
        print "\n--REMOTES--"
        for remote in (remotes[5:-1]):
            print remote + ":",
            if options.showAll:
                buttons = sender.send([("LIST", remote, "")])
                for button in (buttons[5:-1]):
                    print button.rsplit(' ')[1] + ",",
                print
            else:        
                print
        
    else:
        print "No Remotes found.  check LIRC config on remote device"
    sys.exit(1)
    
         

\
