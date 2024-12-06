#File for GPIB VISA control of CMW
# -*- coding: utf-8 -*-
import time
import re
import platform
from baselib.loglib.log_lib import *
from functools import wraps

class MXG(object):

	def isbusy(self, timeout=10):
		for i in range(0, timeout):
			if -1 != self.device.ask('*OPC?').find('1'):
				return False
			time.sleep(1)
		return True

	def wait(self):
		self.device.write('*WAI')
		while self.isbusy() == True:
			logdebug('tester is still busy...')

		return True

	def clean(self, timeout=10):
		self.device.write('*CLS')
		if False == self.isbusy(timeout):
			self.op_stat = 'OPEN'
			logdebug('tester status clean ok!')
			return True
		else:
			logerror('tester clean timeout %d sec!' % timeout)
			self.op_stat = 'ERROR'
			return False

	def reset(self, timeout=10):
		self.device.write('*RST')
		if False == self.isbusy(timeout):
			self.op_stat = 'OPEN'
			logdebug('tester reset ok!')
			return True
		else:
			logerror('tester reset timeout %d sec!' % timeout)
			self.op_stat = 'ERROR'
			return False

	def str_check(self, i):
		w_str = 'OFF' if i == 0 else 'ON'
		return w_str

	def log(level='debug'):
		def logging_decorator(func):
			@wraps(func)
			def wrapper(*args,**kwargs):
				if level == 'debug':
					logdebug('**** {} ****		{}'.format(func.__name__,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())))
				if level == 'info':
					loginfo('**** {}  ****		{}'.format(func.__name__, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
				return func(*args,**kwargs)
			return wrapper
		return logging_decorator


	def __init__(self, device_name="N5182B", num_of_machine=0):
		if platform.platform().find("Linux") != -1:
			from GPIBImpl import GPIBLinux
			self.device = GPIBLinux.GPIBDevice(device_name,num_of_machine)
		else:
			from GPIBImpl import GPIBWindows
			self.device = GPIBWindows.GPIBDevice(device_name=device_name, num_of_machine=num_of_machine)
			res = self.get_mem_catalog()
			if len(res) < 60:
				self.load_all_waveform()
				time.sleep(5)
		pass

	@log()
	def set_cfreq(self, freq=2402):
		self.device.write(':SOURce:FREQuency:FIXed {:.2f} MHz'.format(freq))
		self.wait()

	@log()
	def get_cfreq(self):
		self.device.ask(':SOURce:FREQuency:FIXed?')

	@log()
	def set_power(self, level=-40):
		self.device.write(':SOURce:POWer {:+.1f}'.format(level))
		self.wait()

	@log()
	def get_power(self):
		self.device.ask(':SOURce:POWer?')

	@log()
	def para_set(self, freq=2402, power=-40):
		self.set_cfreq(freq=freq)
		self.set_power(level=power)

	@log()
	def output_state(self, rf=1, mod=1):
		self.device.write(':OUTPut:STATe %d' % rf)
		self.wait()
		self.device.write(':OUTPut:MODulation:STATe %d' % mod)
		self.wait()

	@log()
	def arb_state(self, state=1):
		self.device.write(':SOURce:RADio:ARB:STATe %d' % state)
		self.wait()

	@log()
	def arb_waveform(self, rate='1M_DH1'):
		self.arbfile_dic = {'1M_DH1':'BR_1M_DB61_00001111.WFM',
							'DH1_PN15': 'BR_1M_AF_DH1_PN15.WFM',
							'2M_DH1': 'EDR_2M_DB61_00001111.WFM',
							'2_DH1_PN15': 'EDR_2M_AF_DH1_PN15.WFM',
							'3M_DH1': 'EDR_3M_DB61_00001111.WFM',
							'3_DH1_PN15': 'EDR_3M_AF_DH1_PN15.WFM',
							'LE_1M_PN15': 'LE_1M_PN15_INTERFERENCE.WFM',
							'LE_500K_PN15': 'LE_500K_PN15_INTERFERENCE.WFM',
							'LE_125K_PN15': 'LE_125K_PN15_INTERFERENCE.WFM',
							'LE_1M': 'LE_1M_PN9.WFM',
							'LE_2M': 'LE_2M_PN9.WFM',
							'LE_2M_PN15': 'LE_2M_PN15_INTERFERENCE.WFM'}
		arb_file = self.arbfile_dic[rate]
		self.device.write(':RAD:ARB:WAV "WFM1:{}"'.format(arb_file))
		self.wait()


	@log()
	def load_all_waveform(self):
		self.device.write(':MMEMory:LOAD:WFM:ALL')
		self.wait()


	@log()
	def del_all_waveform(self):
		self.device.write(':MMEMory:DELete:WFM')
		self.wait()


	@log()
	def get_mem_catalog(self):
		res = self.device.ask(':MMEMory:CATalog? "/USER/BBG1/WAVEFORM"')
		res = res.split(",")
		return res

	@log()
	def trigger_type(self, type='SINGle'):
		'''
		type:	CONTinuous|SINGle
		'''
		self.device.write(':SOURce:RADio:ARB:TRIGger:TYPE {}'.format(type))
		self.wait()
		if type == 'SINGle' or type == 'SING':
			self.device.write(':RADio:ARB:RETRigger IMMediate')
			self.device.write(':SOURce:RADio:ARB:TRIGger:SOURce BUS')

	@log()
	def trigger_single_repeat(self, count=1000):
		'''
		count:	1 to 65535
		'''
		self.device.write(':SOURce:RADio:ARB:TRIGger:TYPE:SINGle:REPeat {}'.format(count))
		self.wait()

	@log()
	def trigger_source(self, type='BUS'):
		'''
		type:	KEY|EXT|BUS
		'''
		self.device.write(':SOURce:RADio:ARB:TRIGger:SOURce {}'.format(type))
		self.wait()


	@log()
	def trigger_on(self):
		'''
		viable when trigger_source is BUS
		'''
		self.device.write('*TRG')

	@log()
	def trriger_para_set(self, type='SINGle', count=1500):
		self.trigger_type(type=type)
		self.trigger_single_repeat(count=count)