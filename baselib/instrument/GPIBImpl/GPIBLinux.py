import Gpib
from baselib.loglib.log_lib import *

class GPIBDevice(object):
    ADDR_RANGE = 31
    def __init__(self, device_name=None,num_of_machine=0):
        # try to load GPIB module and devices
        # try:
        #     ShellCmd.shell_check_output("sudo gpib_config")
        # except (StandardError, Exception):
        #     pass
        # try to find GPIB address
        self.address = self.__find_gpib_address(device_name)
        self.device_dict = dict()
        # create GPIB
        for i,addr in enumerate(self.address):
            self.device_dict.update({i: addr})
        #self.address = self.__find_gpib_address_all(device_name)
        loginfo("gpib_dict: %s"%(self.device_dict))
        self.device = Gpib.Gpib(0,self.device_dict[num_of_machine])
        pass

    #def machine_to_use(self, num_of_machine=0):
    #    self.device = Gpib.Gpib(0,self.device_dict[num_of_machine])

    def __find_gpib_address(self, device_name=None):
        logdebug("looking for %s"%(device_name))
        address = []
        flag_dupDev = 0
        flg=0
        for i in range(self.ADDR_RANGE):
            inst = Gpib.Gpib(0, i)
            try:
                inst.write("*IDN?")
                dev_name = inst.read(100)
                logdebug("dev:%s"%dev_name)
                if dev_name.find(device_name) != -1:
                    if i in address:
                        logerror('Duplicated Device GPIB Address! Use Device Menu to change')
                        return None
                    else:
                        address.append(i)
                        logdebug('Found Device GPIB %d'%i)
            except (StandardError, Gpib.gpib.GpibError):
                if i == self.ADDR_RANGE-1 and address != []: break
                else:                                        pass
        else: raise StandardError("can't find GPIB device address")
        return address

    def write(self, data):
        return self.device.write(data)

    def ask(self, data):
        self.device.write(data)
        return self.device.read(8192)

