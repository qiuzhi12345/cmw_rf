# make sure visa32.dll exist in C:\Windows\System32
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('ISO-8859-1')
import visa
from baselib.loglib.log_lib import *

class GPIBDevice(object):

    def __init__(self, device_name=None, num_of_machine=1):
        visa_version = visa.__version__
        logdebug("visa_version:%s"%visa_version)
        logdebug(device_name)
        device_list=[]
        if float(visa_version[2:4]) > 5:
            # 1.6+ version visa
            rm = visa.ResourceManager()
            if device_name is None:
                # get the first GPIB device if not specify device name
                res_list = rm.list_resources()
                for res_name in res_list:
                    if res_name.find("GPIB") != -1 or res_name.find("TCPIP0") != -1 or res_name.find("USB") != -1:
                        logdebug(res_name)
                        device_name = res_name
                        break
                self.device = rm.open_resource(device_name)
            else:
                res_list = rm.list_resources()
                logdebug(res_list)
                for res_name in res_list:
                    if res_name.find("GPIB") != -1 or res_name.find("TCPIP0") != -1 or res_name.find("USB") != -1:
                        logdebug(res_name)
                        # self.device = rm.open_resource(res_name)
                        # dev_name = self.device.ask("*IDN?")
                        # logdebug(dev_name)
                        # if dev_name.find(device_name) != -1:
                        #     break
                        try:
                            self.device = rm.open_resource(res_name)
                            dev_name = self.device.ask("*IDN?")
                            logdebug(dev_name)
                            if dev_name.find(device_name) != -1:
                                device_list.append(self.device)
                                break

                        except:
                            logerror('{} disconnect to instrument'.format(res_name))
                            return


        else:
            # 1.5- version visa
            # get the first GPIB device if not specify device name
            res_list = visa.get_instruments_list()
            for res_name in res_list:
                if res_name.find("GPIB") != -1 or res_name.find("TCPIP0") != -1 or res_name.find("USB") != -1:
                    logdebug(res_name)
                    self.device = visa.instrument(res_name)
                    try:
                        dev_name = self.device.ask("*IDN?")
                        logdebug(dev_name)
                        if dev_name.find(device_name) != -1:
                            device_list.append(self.device)
                    except:
                        logerror('{} disconnect to instrument'.format(res_name))
                        return
        # if device_list == []:
        #     raise StandardError("can't find GPIB device address")
        # self.device.timeout=5000
        # self.device = device_list[num_of_machine-1]
        # logdebug('you are using {}'.format(self.device.ask("*IDN?")))
        # pass

    def write(self, data):
        logdebug(data)
        return self.device.write(data)

    def ask(self, data):
        logdebug(data)
        # res = self.device.ask(data)
        res = self.device.query(data)
        return res
