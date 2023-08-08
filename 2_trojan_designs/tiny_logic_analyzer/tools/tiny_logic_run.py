#!/usr/bin/env python3
"""Usage: python3 tiny_logic_run.py [-c <clockrate>] [-n] <output.bin>

Options: -c <clockrate>   uses given clockrate as a samplerate in pulseview.
                          By default, an imaginary samplerate of 1000000 Hz is
                          used.
         -n               Does not quit openocd after the script.

This uses the configured JTAG configuration of (modified!!!) openocd and saves
exactly one dump of the tiny logic analyzer's output and opens it via
pulseview."""
import getopt
import os
import socket
import sys
import time

#OPENOCD_COMMAND = "./openocd -f /usr/share/openocd/scripts/interface/usb-jtag.cfg -f /usr/share/openocd/scripts/cpld/xilinx-xc6s.cfg"
OPENOCD_COMMAND = "./openocd -f board/digilent_nexys_video.cfg"
#PULSEVIEW_COMMAND = "pulseview -I binary:numchannels=64:samplerate={} -i {}"
PULSEVIEW_COMMAND = "python ramb36_parser.py {} | less"

def exit():
    sys.exit(1)

def usage():
    print(__doc__)

class OpenOCD():
    COMMAND_TOKEN = b'\x1a'

    def __init__(self, ip="127.0.0.1", port=6666):
        self.ip = ip
        self.port = port
        self.buffer_size = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        try:
            self.sock.connect((self.ip, self.port))
        except socket.error:
            return False
        return True

    def disconnect(self):
        try:
            self.send("exit")
        finally:
            self.sock.close()

    def send(self, cmd, noreply=False):
        print("openocd send: {}".format(cmd))
        data = bytearray(cmd.encode("utf-8")) + OpenOCD.COMMAND_TOKEN
        self.sock.send(data)
        if noreply:
            return None
        return self._recv()

    def _recv(self):
        data = bytes()
        while True:
            chunk = self.sock.recv(self.buffer_size)
            data += chunk
            if OpenOCD.COMMAND_TOKEN in chunk:
                break

        print("openocd received: {}".format(data))

        data = data[:data.index(OpenOCD.COMMAND_TOKEN)].decode("utf-8")

        return data


def main():
    clockrate = 1000000
    noquit = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:n", ["help", "clockrate", "noquit"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--clockrate"):
            clockrate = int(arg)
        elif opt in ("-n", "--noquit"):
            noquit = True
    if len(args) < 1:
        usage()
        exit()

    filename = args[0]

    ocd = OpenOCD()
    if not ocd.connect():
        # spawns an openocd server on tcp port 6666
        os.system(OPENOCD_COMMAND + " & disown")
        time.sleep(1)

        if not ocd.connect():
            print("error: no connection could be established")
            exit()

    ocd.send("runtest 100000")
    time.sleep(0.1)
    ocd.send("virtex2 tinyla_run 0")
    ocd.send("runtest 100000")
    time.sleep(0.1)
    ocd.send("virtex2 tinyla_dump 0 {}".format(filename))

    if not noquit:
        ocd.send("shutdown", noreply=True)

    ocd.disconnect()

    os.system(PULSEVIEW_COMMAND.format(filename)) # clockrate, 


if __name__ == "__main__":
    main()