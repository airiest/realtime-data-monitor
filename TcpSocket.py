import sys
import socket
import threading
import SignalData as sd

from logging import getLogger
logger = getLogger("app").getChild("TcpSocket")

RECV_BUF_SIZE = 2048    # set socket buffer size

class TcpSocket(threading.Thread):

    def __init__(self, data, host, port):
        super().__init__()
        self.started = threading.Event()
        self.alive = True
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        socket.setdefaulttimeout(1)

        self.dat = data
        
        self.start()

    def __del__(self):
        self.kill()
 
    def begin(self):
        self.started.set()
    
    def end(self):
        self.started.clear()

    def kill(self):
        self.s.close()
        self.started.set()
        self.alive = False
        self.join()

    def run(self):
        self.started.wait()
        while self.alive:
            self.s.listen(1)
            logger.info('Waiting for connection')

            try:
                self.client, self.addr = self.s.accept()
            except:
                break

            logger.info('Established connection')
            self.client.settimeout(60)

            while self.alive:
                try:
                    msg = self.client.recv(RECV_BUF_SIZE)
                    if msg:
                        self.dat.parse_json(msg)
                    else:
                        break
                except socket.error:
                    logger.debug("socket error")
                    break
                except:
                    logger.debug(sys.exc_info())
                    break
            
            self.client.close()
            self.started.wait()
        


""" test
if __name__ == "__main__":
    import time
    import pandas as pd
    
    host = "localhost"
    port = 5000
    d = sd.SiganlData()

    try:
        s = TcpSocket(d, host, port)
        s.begin()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        s.end()
        s.kill()
        print(pd.DataFrame(d.get_all_signal()))
"""
#"""