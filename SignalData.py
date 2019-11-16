import json
import pandas as pd
from threading import Lock

from logging import getLogger
logger = getLogger("app").getChild("SiganalData")

DATA_BUF_SIZE = 1000   # set data buffer size

class SiganlData:
    def __init__(self):
        self.data = {}
        self.__lock = Lock()

    def clear(self):
        with self.__lock:
            self.data.clear()

    def _parse_json(self, jmsg):
        try:
            j = json.loads(jmsg)
        except:
            logger.debug(jmsg)
            return (-1)

        ts = float(j["t"])
        for sig in j["d"]:
            if sig not in self.data:
                with self.__lock:
                    self.data[sig] = {ts:float(j["d"][sig])}
            else:
                with self.__lock:
                    self.data[sig][ts] = float(j["d"][sig])
            
            with self.__lock:
                if len(self.data[sig]) > DATA_BUF_SIZE:
                    self.data[sig].pop(min(self.data[sig]))

        return 0

    def parse_json(self, jmsg):
        if self._parse_json(jmsg) != 0:
            msg = jmsg.decode(encoding='utf-8')
            msg = msg.split("}{")
            mcnt = len(msg)

            for index, _ in enumerate(msg):
                if index == 0:
                    msg[index] = msg[index] + "}"
                elif index == mcnt - 1:
                    msg[index] = "{" + msg[index]
                else:
                    msg[index] = "{" + msg[index] + "}"
                    
                if self._parse_json(msg[index]) != 0:
                    logger.warning(msg[index])

    def get_all_signal(self):
        return self.data

    def get_signal(self, sig_name):
        if sig_name not in self.data:
            return {}
        else:
            return self.data[sig_name]


""" test
if __name__ == "__main__":
    msgs = [
        {"t":"1001.0", "d":{"sig1":"0.1", "sig2":"1.01"}},
        {"t":"1002.0", "d":{"sig1":"0.2", "sig2":"1.02"}},
        {"t":"1003.0", "d":{"sig1":"0.3", "sig2":"1.03"}},
        {"t":"1004.0", "d":{"sig1":"0.4"}               },
        {"t":"1005.0", "d":{"sig1":"0.5"}               },
        {"t":"1006.0", "d":{"sig1":"0.6"}               },
        {"t":"1007.0", "d":{              "sig2":"1.07"}},
        {"t":"1008.0", "d":{              "sig2":"1.08"}},
        {"t":"1009.0", "d":{              "sig2":"1.09"}},
        {"t":"1005.0", "d":{              "sig2":"1.05"}},
        {"t":"1005.0", "d":{"sig1":"5.0"}               },
        {"t":"1010.0", "d":{}                           }
    ]

    dat = SiganlData()

    for index, m in enumerate(msgs):
        jmsg = json.dumps(m)
        dat.parse_json(jmsg.encode("utf-8"))

    d = dat.get_all_signal()
    print(type(d)); print(d)
    print(pd.DataFrame(d))
    #print(pd.DataFrame.from_dict(d, orient='index').T.sort_index().reset_index().rename(columns={'index':'ts'}).sort_values("ts"))

    d = dat.get_signal("sig1")
    print(type(d)); print(d)
    print(pd.Series(d))

    DATA_BUF_SIZE = 3
    dat.clear()

    for index, m in enumerate(msgs):
        jmsg = json.dumps(m).encode("utf-8")
        dat.parse_json(jmsg)

    d = dat.get_all_signal()
    print(type(d)); print(d)
    print(pd.DataFrame(d))
    #print(pd.DataFrame.from_dict(d, orient='index').T.sort_index().reset_index().rename(columns={'index':'ts'}).sort_values("ts"))

    d = dat.get_signal("sig1")
    print(type(d)); print(d)
    print(pd.Series(d))
"""
#"""