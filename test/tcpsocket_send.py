import sys
import signal
import json
import socket
import time
from datetime import datetime
import math

def make_connection(host, port):
    global connect
    while True:
        try:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            soc.connect((host, port))
            print("socket connect to : " + host)
            connect = True
            return soc
        except socket.error:
            print('failed to connect, try reconnect')
            try:
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                sys.exit(1)


long_msg = {"t":"0.0", "d": {"sig1":"0.0", "sig2":"0.0", "sig3":"0.0", "sig4":"0.0", "sig5":"0.0","sig6":"0.0", "sig7":"0.0", "sig8":"0.0", "sig9":"0.0", "sig10":"0.0"}}
alt_msg  = {"t":"0.0", "d": {"sig2":"0.0"}}

def woker(arg1, args2):
    global connect

    if connect != True:
        return

    try:

        tim = datetime.now().timestamp()
        sig = 1.0 * math.sin(2.0 * math.pi * 1.0 * tim)

        #""" # long message
        long_msg["t"] = "{0:.6f}".format(tim)
        for index, sname in enumerate(long_msg["d"]):
            long_msg["d"][sname] = "{0:.9f}".format(sig + index)
        msg = long_msg
        """ # alternate message
        alt_msg["t"] = "{0:.6f}".format(tim)
        alt_msg["d"] = {"sig1" if "sig2" in alt_msg["d"] else "sig2" : "{0:.9f}".format(sig)}
        msg = alt_msg
        #"""

        jmsg = json.dumps(msg)
        s.send(jmsg.encode("utf-8"))
        print(jmsg)

    except socket.error:
        print('connection lost, try reconnect')
        connect = False

    except (KeyboardInterrupt, SystemExit):
        sys.exit()


if __name__ == "__main__":
    host = 'localhost'
    port = 5000
    connect = False

    s = make_connection(host, port)

    signal.signal(signal.SIGALRM, woker)
    signal.setitimer(signal.ITIMER_REAL, 0.01, 0.01)

    while True:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        if connect != True:
            s = make_connection(host, port)

    
