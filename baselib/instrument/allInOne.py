#-------------------------------------------------------------------------
# Name:        epsdm.py
# Purpose:     Multimeter | DC Power Supply (U3606B)
# Created:     09/26/2019
# Author:      Z
# Copyright:   (c) Test 2019
#-------------------------------------------------------------------------
import time
from baselib.loglib.log_lib import *
import platform


class allInOne(object):
    ''' script for Multimeter DC Supply all in one GPIB control
    '''

    def __init__(self, device_name="U3606B"):
        if platform.platform().find("Linux") != -1:
            from GPIBImpl import GPIBLinux
            self.device = GPIBLinux.GPIBDevice(device_name)
        else:
            from GPIBImpl import GPIBWindows
            self.device = GPIBWindows.GPIBDevice(device_name)
        pass
        self.para_list = ['AUTO', 'MAX', 'MIN', 'DEF']
        self.num_list = [float, int]

    def _isbusy(self, timeout=100):
        '''checks if equip ready for use'''
        for i in range(0, timeout):
            if self.device.ask('*OPC?').find("1") != -1:
                return False
            time.sleep(1)
            logwarn('U3606B operations are not complete\nWait another second')
        return True

    def _wait(self):
        self.device.write('*WAI')
        while self._isbusy() == True:
            logdebug('U36068B is still operating...')
        return True

    def _clean(self, timeout=10):
        self.device.write('*CLS')
        if False == self._isbusy(timeout):
            self.op_stat = 'OPEN'
            logdebug('U3606B Error Queue clears')
            return True
        else:
            logdebug('U3606B clean timeout %4.9f sec!' % timeout)
            self.op_stat = 'ERROR'
            return False

    def _reset(self, timeout=10):
        self.device.write('*RST')
        if False == self._isbusy(timeout):
            self.op_stat = 'OPEN'
            logdebug('U3606B Resets to factory default state')
            return True
        else:
            logdebug('U3606B reset timeout %4.9f sec!' % timeout)
            self.op_stat = 'ERROR'
            return False

    def conf_meas(self, func='VOLT', rng='AUTO', f_type='DC'):
        '''configures equip measurement parameters

        - :param func: 
            - VOLT: voltage mode
            - CURR: current mode
        - :param rng:
            - AUTO, MAX, MIN, DEF
            - numeric values are also supported
        '''
        if func in ['VOLT', 'CURR']:
            if rng in self.para_list or type(rng) in self.num_list:
                self.device.write('CONF:%s:%s %s' % (func, f_type, rng))
                logdebug('U3606B MEAS CONF to: %s %s RNG: %r' %(f_type, func, rng))
            else:
                logerror('Command Error!\nRange parameter type not supported')
        else:
            logerror('Command Error!\nOnly "VOLT & CURR" are currently supported')

    def sour_out(self, stat='OFF'):
        if stat in [0, 1, 'OFF', 'ON']:
            self.device.write('OUTP:STAT %s' % stat)
            stat_info = stat
            if   stat == 1:   stat_info = 'ON'
            elif stat == 0: stat_info = 'OFF'
            logdebug('U3606B OUTPUT: %s' % stat_info)
        else:
            logerror('Command Error!\nOnly "0,1,ON,OFF" allowed')

    def _sour_vol_rng(self, rng='AUTO'):
        if rng in ['30V', '8V', '1V '] + self.para_list:
            # DEF is default value, which is 30V
            # otuput is open for configuration only in standby mode
            self.sour_out('OFF')
            self.device.write('SOUR:VOLT:RANG %s' % rng)
            logdebug('U3606B VOLTAGE RANG sets to: %s' % rng)
        else:
            logerror('Command Error!\nOnly "30V,8V,1V,AUTO,MAX,MIN,DEF" allowed')

    def _sour_cur_rng(self, rng='AUTO'):
        if rng in ['3A', '1A', '100mA '] + self.para_list:
            # DEF is default value, which is 1A
            # otuput is open for configuration only in standby mode
            self.sour_out('OFF')
            self.device.write('SOUR:VOLT:RANG %s' % rng)
            logdebug('U3606B VOLTAGE RANG sets to: %s' % rng)
        else:
            logerror('Command Error!\nOnly "3A,1A,100mA,AUTO,MAX,MIN,DEF" allowed')

    def _sour_ivlim(self,func='VOLT',iv_lim=3):
        '''setup current/voltage limit range based on output function selected
        '''
        lim_item = 'CURR' if func == 'VOLT' else 'VOLT' 
        unit = 'A' if func == 'VOLT' else 'V' 
        self.device.write('SOUR:%s:LIM %r'%(lim_item,iv_lim))
        lim_r = float(self.device.ask('SOUR:%s:LIM?'%lim_item))
        logdebug('U3606B CURRENT LIMIT sets to: %.2f%s' % (lim_r,unit))

    def meas(self, func='VOLT', rng='AUTO', res='MIN', f_type='DC'):
        '''measures current or voltage, frequency & resistannce can be supported, not yet
        '''
        if func in ['VOLT', 'CURR']:
            unit = 'V' if func == 'VOLT' else 'A'
            if (rng in self.para_list or type(rng) in self.num_list) and (res in self.para_list[1:] or type(res) in self.num_list):
                val = float(self.device.ask('MEAS:%s:%s? %s, %s' %
                                            (func, f_type, rng, res)))
                logdebug('U3606B Measures %s %s: %4.8f%s' %
                         (f_type, func, val, unit))
                return val
            else:
                logerror('Command Error!\nRange parameter type not supported')
        else:
            logerror('Command Error!\nOnly "VOLT & CURR" are currently supported')

    def sour(self, func='VOLT', lvl=0, rng_auto=True, out='ON', iv_lim=3):
        '''constat voltage or current output

        - :param func: VOLT & CURR
        - :param lvl:
        - :param iv_lim: setup current/voltage limit
        - :param rng_auto:
            - manually setup function range if has concern for required total power, see device screen for specs
        '''
        if func in ['VOLT', 'CURR']:
            unit = 'V' if func == 'VOLT' else 'A'
            if type(lvl) in self.num_list:
                if not rng_auto:
                    # use below commands will turn off power ouput first in
                    # order to configure range
                    if func == 'VOLT' and lvl <= 1:
                        self._sour_vol_rng(rng='1V')
                    elif func == 'VOLT' and lvl <= 8:
                        self._sour_vol_rng(rng='8V')
                    elif func == 'VOLT' and lvl <= 30:
                        self._sour_vol_rng(rng='30V')
                    elif func == 'CURR' and lvl <= 0.1:
                        self._sour_vol_rng(rng='100mA')
                    elif func == 'CURR' and lvl <= 1:
                        self._sour_vol_rng(rng='1A')
                    elif func == 'CURR' and lvl <= 3:
                        self._sour_vol_rng(rng='3A')
                self.device.write('%s %r' % (func, lvl))
                val_ask = self.device.ask('%s?' % func)
                logdebug('U3606B OUTPUT %s level sets to %r' % (func, val_ask))
                # self._sour_ivlim(func=func,iv_lim=iv_lim)
                self.sour_out(out)
            else:
                logerror('Command Error!\nRange parameter type not supported')
        else:
            logerror('Command Error!\nOnly "VOLT & CURR" are currently supported')
