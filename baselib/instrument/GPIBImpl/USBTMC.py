import usbtmc
import re
from baselib.loglib.log_lib import *

class TMCDevice(object):
    ADDR_RANGE = 31
    def __init__(self, device_name=None):
        # try to load GPIB module and devices
        # try:
        #     ShellCmd.shell_check_output("sudo gpib_config")
        # except (StandardError, Exception):
        #     pass
        # try to find GPIB address
        address = self.__find_tmc_address(device_name)
        # create GPIB
        self.device = usbtmc.Instrument(address)
        pass

    def __find_tmc_address(self, device_name=None):
        logdebug("looking for %s"%(device_name))
        device_list = usbtmc.list_devices()
        # print device_list
        for i in device_list:
            inst = usbtmc.Instrument(i)
            #print inst
            try:
                dev_name = inst.ask("*IDN?")
                logdebug("dev:%s"%dev_name)
                if device_name == None:
                    address = i
                    break

                if dev_name.find(device_name) != -1:
                    address = i
                    break
            except:
                logerror("ask err %s"%i)
                pass
        else:
            raise StandardError("can't find TMC device address")
        return address

    def write(self, data):
        return self.device.write(data)

    def ask(self, data):
        return self.device.ask(data)
