#File for GPIB VISA control of CMW
# -*- coding: utf-8 -*-
import time
import re
import platform
from baselib.loglib.log_lib import *
from functools import wraps

prim_addr = -1
op_statlst = ['OPEN',  # just open, not initialize for test
			  'CLOSE',  # shutdown,need reopen again
			  'RUN',  # begin measure
			  'RDY',  # stop running,data is ready
			  'ERROR',  # instrument is in error state, need reset
			  'LOSE']  # can't contact with it
op_stat = 'LOSE'
reliab_ind = {'0': 'OK',
			  '3': 'Overdriven: input signal too high',
			  '4': 'Underdriven: input signal too low',
			  '6': 'Trig Timeout:No results available',
			  '7': 'Acquisit Error:No results available',
			  '8': 'Sync Error:No results available'}


def log(level='debug'):
	def logging_decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			if level == 'debug':
				logdebug('**** {}  ****		{}'.format(func.__name__, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
			if level == 'info':
				loginfo('**** {}  ****		{}'.format(func.__name__, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
			return func(*args, **kwargs)
		return wrapper
	return logging_decorator

class cmw_bt(object):
	def error_code(self, i):
		'''
		0 ("No Error"):
		Measurement values available, no error detected.
		•1 ("Measurement Timeout"):
		The measurement has been stopped after the configured measurement timeout. Measurement results can be available. However, at least a part of the measurement provides only INValid results or has not completed the full statistic count.
		•2 ("Capture Buffer Overflow"):
		The measurement configuration results in a capture length that exceeds the available memory.
		•3 ("Input Overdriven") / 4 ("Input Underdriven"):
		The accuracy of measurement results can be impaired because the input signal level was too high / too low.
		•6 ("Trigger Timeout"):
		The measurement could not be started or continued because no trigger event was detected.
		•7 ("Acquisition Error"):
		The R&S CMW could not properly decode the RF input signal.
		•8 ("Sync Error"):
		The R&S CMW could not synchronize to the RF input signal.
		•9 ("Uncal"):
		Due to an inappropriate configuration of resolution bandwidth, video bandwidth or sweep time, the measurement results are not within the specified data sheet limits.
		•15 ("Reference Frequency Error"):
		The instrument has been configured to use an external reference signal. But the reference oscillator could not be phase-locked to the external signal (for example signal level too low, frequency out of range or reference signal not available at all).
		•16 ("RF Not Available"):
		The measurement could not be started because the configured RF input path was not active. This problem can occur if a measurement is started in combined signal path mode and the master application has not yet activated the input path. The LEDs above the RF connectors indicate whether the input and output paths are active.
		•17 ("RF Level Not Settled") / 18 ("RF Frequency Not Settled"):
		The measurement could not be started because the R&S CMW was not yet ready to deliver stable results after a change of the input signal power / the input signal frequency.
		•19 ("Call Not Established"):
		For measurements: The measurement could not be started because no signaling connection to the DUT was established.
		•20 ("Call Type Not Usable"):
		For measurements: The measurement could not be started because the established signaling connection had wrong properties.
		•21 ("Call Lost"):
		For measurements: The measurement was interrupted because the signaling connection to the DUT was lost.
		•23 ("Missing Option"):
		An action cannot be executed due to a missing option.
		For GPRF generator: The ARB file cannot be played by the GPRF generator due to a missing option.
		•24 ("Invalid RF Setting"):
		The desired RF TX level or RF RX reference level could not be applied.
		•25 ("Level Overrange"):
		The RF TX level is in overrange. The signal quality can be degraded.
		•26 ("Resource Conflict"):
		The application could not be started or has been stopped due to a conflicting hardware resource or software option that is allocated by another application.
		Stop the application that has allocated the conflicting resources and try again.
		•28 ("Unexpected Parameter Change"):
		One or more measurement configuration parameters were changed while the measurement completed. The results were not obtained with these new parameter values. Repeat the measurement. This situation can only occur in remote single-shot mode.
		•29 ("Invalid RF Frequency Setting"):
		The desired RF TX frequency or RF RX frequency could not be applied.
		•30 ("File Not Found"):
		The specified file could not be found.
		•31 ("No DTM Reply"):
		The EUT did not reply to the direct test mode (DTM) command.
		•32 ("ACL Disconnected"):
		The ACL connection has been disconnected or lost.
		•40 ("ARB File CRC Error"):
		The cyclic redundancy check of the ARB file failed. The ARB file is corrupt and not reliable.
		•42 ("ARB Header Tag Invalid"):
		The ARB file selected in the GPRF generator contains an invalid header tag.
		•43 ("ARB Segment Overflow"):
		The number of segments in the multi-segment ARB file is higher than the allowed maximum.
		•44 ("ARB File Not Found"):
		The selected ARB file could not be found.
		•45 ("ARB Memory Overflow"):
		The ARB file length is greater than the available memory.
		•46 ("ARB Sample Rate Out of Range"):
		The clock rate of the ARB file is either too high or too low.
		•47 ("ARB Cycles Out of Range"):
		The repetition mode equals "Single Shot" and the playback length is greater than 40 s. Reduce the playback length or set the repetition mode to "Continuous".
		<Length> = (<Cycles> * <Samples> + <Additional Samples>) / <Clock Rate>
		•52 ("Connection Error")
		A connection setup failed or a connection was lost.
		For Bluetooth: The EUT has been disconnected from the R&S CMW.
		•60 ("Invalid RF-Connector Setting")
		The individual segments of a list mode measurement with R&S CMWS use different connector benches. All segments must use the same bench.
		Check the "Info" dialog for the relevant segment numbers.
		•70 ("Wrong Standard")
		The standard of the measured signal does not match the configured standard.
		•71 ("Wrong Bandwidth")
		The bandwidth of the measured signal does not match the configured bandwidth.
		•72 ("Wrong Burst Type")
		The burst type of the measured signal does not match the configured burst type.
		•73 ("MIMO Signal Detected")
		The measurement expects a SISO signal and detected a MIMO signal. Use a MIMO receive mode to measure this signal.
		•74 ("More Streams than Antennas")
		The measured signal has more streams than expected due to the configured number of antennas. Increase the configured number of antennas to measure this signal.
		•75 ("Matrix Inversion Failed")
		The inversion of the channel matrix failed for a MIMO measurement. Check that the antennas are connected correctly to the instrument.
		•76 ("SIG CRC Failed")
		The cyclic redundancy check of a SIGNAL field failed.
		•77 ("Parity Check Failed")
		The parity check of a SIGNAL field failed.
		•78 ("Bursts Not Identical")
		In training mode for composite MIMO measurements, at least some symbols of sequential bursts need to be identical to be used as training data. Setting a fix scrambler initialization can solve this problem.
		•79 ("Wrong Modulation")
		The modulation type of the measured signal does not match the configured modulation type.
		•93 ("OCXO Oven Temperature Too Low"):
		The accuracy of measurement results can be impaired because the oven-controlled crystal oscillator has a too low temperature. After switching-on the instrument, the OCXO requires a warm-up phase to reach its operating temperature.
		•101 ("Firmware Error"):
		Indicates a firmware or software error. If you encounter this error for the first time, restart the instrument.
		If the error occurs again, consider the following hints:
		– Firmware errors can often be repaired by restoring the factory default settings. To restore these settings, restart your instrument and press the "Factory Default" softkey during startup.
		– If a software package (update) has not been properly installed, this failure is often indicated in the "Setup" dialog, section "SW/HW-Equipment > Installed Software".
		– Check for software updates correcting the error. Updates are provided in the CMW customer web on GLORIS (registration required): https://gloris.rohde-schwarz.com.

		If you get firmware errors even with the properly installed latest software version, send a problem report including log files to Rohde & Schwarz.
		•102 ("Unidentified Error"):
		Indicates an error not covered by other reliability values. For troubleshooting, follow the steps described for "101 (firmware error)".
		•103 ("Parameter Error"):
		Indicates that the measurement could not be performed due to internal conflicting parameter settings.
		A good approach to localize the conflicting settings is to start with a reset or preset or even restore the factory default settings. Then reconfigure the measurement step by step and check when the error occurs for the first time.
		If you need assistance to localize the conflicting parameter settings, contact Rohde & Schwarz (see http://www.service.rohde-schwarz.com).
		•104 ("Not Functional"):
		The application could not be started with the configured parameter set.
		'''
		error_cose_dict = {0: 'No Error',
			  1: 'Measurement Timeout',
			  2: 'Capture Buffer Overflow',
			  3: 'Input Overdriven',
			  4: 'Input Underdriven',
			  6: 'Trigger Timeout',
			  7: 'Acquisition Error',
			  8: 'Sync Error',
			  9: 'Uncal',
			  15: 'Reference Frequency Error',
			  16: 'RF Not Available',
			  17: 'RF Level Not Settled',
			  18: 'RF Frequency Not Settled',
			  19: 'Call Not Established',
			  20: 'Call Type Not Usable',
			  21: 'Call Lost',
			  23: 'Missing Option',
			  24: 'Invalid RF Setting',
			  25: 'Level Overrange',
			  26: 'Resource Conflict',
			  28: 'Unexpected Parameter Change',
			  29: 'Invalid RF Frequency Setting',
			  30: 'File Not Found',
			  31: 'No DTM Reply',
			  32: 'ACL Disconnected',
			  40: 'ARB File CRC Error',
			  42: 'ARB Header Tag Invalid',
			  43: 'ARB Segment Overflow',
			  44: 'ARB File Not Found',
			  45: 'ARB Memory Overflow',
			  46: 'ARB Sample Rate Out of Range',
			  47: 'ARB Cycles Out of Range',
			  52: 'Connection Error',
			  60: 'Invalid RF-Connector Setting',
			  70: 'Wrong Standard',
			  71: 'Wrong Bandwidth',
			  72: 'Wrong Burst Type',
			  73: 'MIMO Signal Detected',
			  74: 'More Streams than Antennas',
			  75: 'Matrix Inversion Failed',
			  76: 'SIG CRC Failed',
			  77: 'Parity Check Failed',
			  78: 'Bursts Not Identical',
			  79: 'Wrong Modulation',
			  93: 'OCXO Oven Temperature Too Low',
			  101: 'Firmware Error',
			  102: 'Unidentified Error',
			  103: 'Parameter Error',
			  104: 'Not Functional'
			  }
		res = error_cose_dict[i]
		return res

	def isbusy(self, timeout=10):
		for i in range(0, timeout):
			res = self.device.device.ask('*OPC?')
			logdebug('*OPC?	{}'.format(res))
			if '1\n' == self.device.ask('*OPC?'):
				return False

			time.sleep(1)
		else:
			return True

	def wait(self):
		self.device.write('*WAI')
		while self.isbusy() == True:
			logdebug('CMW is still busy...')

		return True

	def clean(self, timeout=10):
		self.device.write('*CLS')
		if False == self.isbusy(timeout):
			self.op_stat = 'OPEN'
			logdebug('CMW status clean ok!')
			return True
		else:
			logerror('CMW clean timeout %d sec!' % timeout)
			self.op_stat = 'ERROR'
			return False

	def reset(self, timeout=10):
		self.device.write('*RST')
		if False == self.isbusy(timeout):
			self.op_stat = 'OPEN'
			logdebug('CMW reset ok!')
			return True
		else:
			logerror('CMW reset timeout %d sec!' % timeout)
			self.op_stat = 'ERROR'
			return False

	def str_check(self, i):
		w_str = 'OFF' if i == 0 else 'ON'
		return w_str


	def __init__(self, device_name="CMW", num_of_machine=0):
		if platform.platform().find("Linux") != -1:
			from GPIBImpl import GPIBLinux
			self.device = GPIBLinux.GPIBDevice(device_name,num_of_machine)
		else:
			from GPIBImpl import GPIBWindows
			self.device = GPIBWindows.GPIBDevice(device_name)
			self.device.device.timeout = 40000
		pass
		self.modelist = ['BR', 'EDR', 'LE1M', 'LE2M', 'LRANge', 'LE']
		self.data_type_list = ['CURR', 'AVER', 'MIN', 'MAX', 'XMIN', 'XMAX']

	@log()
	def rf_port(self, mode=0, rfport=2, atten=0):
		'''
		mode:
		0	Standalone (non-signaling) TX measure
		1	Standalone (non-signaling) RX measure
		2	Combined signal path (signaling)
		Defines an external attenuation (or gain, if the value is negative), to be applied to the RF input connector.
		Range:  -50 dB  to  90 dB
		'''
		if atten < -50 or atten > 90:
			logerror('ext_att out of range(-50,90)')
			return False
		else:
			if mode == 0 or mode == 'tx':
				self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:TOUT 10')
				self.wait()
				self.device.write('ROUTe:BLUetooth:MEAS:SCENario:SALone RF%dC,RX%d' % (rfport, rfport))
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:RFSettings:EATTenuation {}'.format(atten))
				self.wait()
				logdebug('Standalone (non-signaling) TX measure')
			elif mode == 1 or mode == 'rx':
				self.device.write('ROUTe:GPRF:GEN:SCENario:SALone RF{}C,TX{}'.format(rfport, rfport))
				self.wait()
				self.device.write('SOURce:GPRF:GEN:RFSettings:EATTenuation {}'.format(atten))
				self.wait()
				logdebug('Standalone (non-signaling) RX measure')
			else:
				self.device.write('ROUTe:BLUetooth:MEAS:SCENario:CSPath "Bluetooth Sig1"')
				self.wait()
				self.device.write('ROUTe:BLUetooth:SIGN:SCENario:OTRX RF%dC,RX1,RF%dC,TX1' % (rfport, rfport))
				self.wait()
				self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:EATTenuation:INPut {}'.format(atten))
				self.wait()
				self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:EATTenuation:OUTPut {}'.format(atten))
				self.wait()
				logdebug('Combined signal path (signaling)')

	@log()
	def chan_check(self, mode='LE', chan=0):
		if chan <= 80:
			if mode == 'LE':
				freq = (chan*2 + 2402) * 1E+6
			else:
				freq = (chan*1 + 2402) * 1E+6
		else:
			freq = chan
		return freq

class standalone_tx(cmw_bt):
	@log()
	def mode_set(self, mode='BR'):
		'''
		mode:	BR,EDR,LE1M,LE2M,LRANge
		'''
		if mode not in self.modelist:
			logerror('mode is wrong,must be in (BR,EDR,LE1M,LE2M,LRANge)')
			return False
		else:
			self.mode = mode

	@log()
	def analyzer_settings(self,  enpower=0, umargin=8, freq=2402):
		'''
		Parameters:
		enpower			Sets the expected nominal power of the measured RF signal.
						Range (Expected Nominal Power) = Range (Input Power) + External Attenuation - User Margin

		umargin			Sets the margin that the R&S CMW adds to the expected nominal power to determine the reference level.
						Range:  0 dB to (55 dB + external attenuation - expected nominal power)
		freq			Selects the center frequency of the RF analyzer.
						Range:	100E+6 Hz  to  6E+9 Hz
						unit:	Hz
		'''
		freq = freq*1e+6
		if freq < 100E+6 or freq > 6E+9:
			logerror('instrument freq set over range')
			return False
		self.device.write('CONFigure:BLUetooth:MEAS:RFSettings:ENPower %d' % enpower)
		self.wait()
		self.device.write('CONFigure:BLUetooth:MEAS:RFSettings:UMARgin %d' % umargin)
		self.wait()
		self.device.write('CONFigure:BLUetooth:MEAS:RFSettings:FREQuency %d' % freq)
		self.wait()
		logdebug('analyzer set success')

	@log()
	def input_signal_settings(self, dmode='AUTO', asyn='ON', btype='BR', phy='LE1M', ptype='DH1', pattern='PRBS9 ', plength=27, bdaddr='050604010203'):
		'''
		Parameters:
		dmode			Selects an algorithm which the R&S CMW uses to detect the measured burst.
						MANual | AUTO
						when dmode is MANual:
						btype	Specifies the measured burst / packet type.
								BR | EDR | LE
						phy		Selects the physical layer used for LE measurements.
								LE1M | LE2M | LELR
						ptype	Specifies the BR/EDR packet type of the measured signal.
								BR:		DH1 | DH3 | DH5
								EDR		E21P | E23P | E25P | E31P | E33P | E35P
										2-DH1, 2-DH3, 2-DH5, 3-DH1, 3-DH3, or 3-DH5 packets
						pattern		ALL0 | ALL1 | P11 | P44 | PRBS9 | ALT
									ALL0: 00000000
									ALL1: 11111111
									P11: 10101010
									P44: 11110000
									PRBS9: pseudo-random bit sequences of a length of 9 bits (transmission of identical packet series)
									ALT: the periodical alternation of the pattern P11 and P44
						bdaddr	Specifies the Bluetooth device address that the R&S CMW expects the EUT to use to generate its access code.
								12-digit hex number
								Range:	#H0 to #HFFFFFFFFFFFF
		asyn			Disables / enables automatic synchronization to the captured signal for an unspecified Bluetooth device address.
						OFF | ON
		'''
		if btype not in ['BR','EDR','LE']:
			logerror('btype is wrong,must be BR,EDR,LE')
		if phy not in ['LE1M','LE2M','LELR']:
			logerror('phy is wrong,must be LE1M,LE2M,LELR')
		if dmode == 'AUTO':
			self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:ASYNchronize %s' % asyn)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:BDADdress #H%s' % bdaddr)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:DMODe %s' % dmode)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:BTYPe %s' % btype)
			self.wait()
			if btype == 'LE':
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:LENergy:PHY %s' % phy)
				self.wait()
			logdebug('input_signal para set AUTO success')
		else:
			if btype == 'BR':
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:BTYPe BR')
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:PTYPe:BRate %s' % ptype)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:PATTern %s' % pattern)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:PLENgth:BRATe?')
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:BDADdress #H%s' % bdaddr)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:ASYNchronize OFF')
				self.wait()
			elif btype == 'EDR':
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:BTYPe EDR')
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:PTYPe:EDRate %s' % ptype)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:PATTern %s' % pattern)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:PLENgth:EDRATe?')
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:BDADdress #H%s' % bdaddr)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:ISIGnal:ASYNchronize OFF')
				self.wait()

	@log()
	def trigger_settings(self, source='power', threshold=-30, tout=1):
		'''
		Parameters:
		source		Selects the source of the trigger events. Some values are always available in this firmware application.
					They are listed below. Depending on the installed options, additional values are available.
					A complete list of all supported values can be displayed using TRIGger:...:CATalog:SOURce?.
		threshold	Defines the trigger threshold for the power trigger.
					Range:  -50 dB  to  0 dB
		tout		Selects the maximum time that the R&S CMW waits for a trigger event before it stops the measurement in remote control mode or indicates a trigger timeout in manual operation mode.
					Range:	0.01 s  to  167772.15 s
					unit:	s
		'''
		self.device.write('TRIGger:BLUetooth:MEAS:MEValuation:SOURce %s' % source)
		self.device.write('TRIGger:BLUetooth:MEAS:MEValuation:THREShold %d' % threshold)
		self.device.write('TRIGger:BLUetooth:MEAS:MEValuation:TOUT %d' % tout)

	@log()
	def get_trigger_source(self):
		'''
		Comma-separated list of all supported values. Each value is represented as a string.
		Lists all trigger source values that can be set using TRIGger:​BLUetooth:​MEAS<i>:​MEValuation:​SOURce.
		'''
		res = self.device.ask('TRIGger:BLUetooth:MEAS:MEValuation:CATalog:SOURce?')
		return res

	@log()
	def measure_states(self, state=0):
		'''
		state:	0|1|2
		0		The measurement enters the "RUN" state.
		1		The measurement enters the "RDY" state. Measurement results are kept. The resources remain allocated to the measurement.
		2		The measurement enters the "OFF" state. All measurement values are set to NAV. Allocated resources are released.
		'''
		if state == 0 or state == 'RUN':
			self.device.write('INIT:BLUetooth:MEAS:MEValuation')
			loginfo('The TX measurement enters the "RUN" state')
		elif state == 1 or state == 'RDY':
			self.device.write('STOP:BLUetooth:MEAS:MEValuation')
			loginfo('The TX measurement enters the "RDY" state')
		else:
			self.device.write('ABORt:BLUetooth:MEAS:MEValuation')
			loginfo('The TX measurement enters the "OFF" state')

	@log()
	def get_measure_states(self):
		'''
		Return values:
		<MeasState>		OFF | RUN | RDY
						OFF: Measurement switched off, no resources allocated, no results available (when entered after ABORt...)
						RUN: Measurement running (after INITiate..., READ...), synchronization pending or adjusted, resources active or queued
						RDY: Measurement has been terminated, valid results are available
		'''
		res = self.device.ask('FETCh:BLUetooth:MEAS:MEValuation:STATe?')
		return res

	@log()
	def measure_display(self, case='OVER'):
		'''
		case:	OVERview | PVTime | DEVM | PDIFference | IQABs | IQDiff | IQERr | FDEViation | SOBW | SACP | SGACp | MODulation | POWer | FRANge | PENCoding
				OVERview: "Overview" (BR, EDR, LE)
				PVTime: "Power vs Tim"e (BR, EDR, LE)
				DEVM: "DEVM" (EDR)
				PDIFference: "Phase Differen"ce (EDR)
				IQABs: "IQ Constellation Absolute" (EDR)
				IQDiff: "IQ Constellation Differentia"l (EDR)
				IQERr: "IQ Constellation Error" (EDR)
				FDEViation: "Frequency Deviation" (BR, LE)
				SOBW: "Spectrum 20 dB Bandwidth" (BR)
				SACP: "Spectrum AC"P (BR, LE)
				SGACp: "Spectrum Gated ACP" (EDR)
				MODulation: "Modulation Scalars" (BR, EDR, LE)
				POWer: "Power Scalars" (BR, EDR, LE)
				FRANge: "Frequency Rang"e (BR)
				PENCoding: "Differential Phase Encoding" (EDR)
		'''
		self.device.write('CONFigure:BLUetooth:MEAS:DISPlay %s' % case)

	@log()
	def measure_para(self, tout=5, repetition='SINGleshot', count=20, MOEXception='OFF' ):
		'''
		tout:	Defines a timeout for the measurement.
		repetition:		Specifies the repetition mode of the measurement.
						The repetition mode specifies whether the measurement is stopped after a single shot or repeated continuously.
						SINGleshot | CONTinuous
						SINGleshot: Single-shot measurement
						CONTinuous: Continuous measurement
		count:			Valid when repetition is SINGleshot,The statistic count is equal to the number of measurement intervals per single shot.
		'''
		if repetition not in ('SINGleshot','SING','CONTinuous','CONT'):
			logerror('repetition is wrong,must be SINGleshot|SING|CONTinuous|CONT')
			return False
		self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:TOUT %d' % tout)
		self.wait()
		self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:REPetition %s' % repetition)
		self.wait()
		self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:MOEXception %s' % MOEXception)
		self.wait()
		if repetition == 'SINGleshot':
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:MODulation %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:PENCoding %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:PVTime  %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:SOBW  %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:FRANge %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:SACP %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:SGACp  %d' % count)
			self.wait()
			logdebug('repetition is SINGleshot,count is %d' % count)
		else:
			logdebug('repetition is CONTinuous')

	@log()
	def get_power_measure_res(self, data_type='AVER', cmd_type='READ'):
		'''
		mode:	BR,EDR,LE1M,LE2M,LRANge
		data_type:	CURR, AVER, MIN, MAX
		cmd_type:	FETCH, READ, CALCulate
		Returns the power results for BR/EDR/LE packets.
		The values described below are returned by FETCh and READ commands. CALCulate commands return limit check results instead, one value for each result listed below.
		The number to the left of each result parameter is provided for easy identification of the parameter position within the result array.
		BR		Return values:
					<1_Reliability>		error code,Reliability Indicator
					<2_Out of Tol>		Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see "Power Limits".
										Range:  0 %  to  100 %
										Default unit:  %

					<3_Nominal Pow>		Average power during the carrier-on state
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
					<4_Peak Pow>		Peak power during the carrier-on state
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
					<5_Leakage Pow>		Average power during the carrier-off state
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
					<6_PacketTiming>	Time between the expected and actual start of the first symbol of the Bluetooth burst
										Range:  -20.00 µs to 20.00 µs
										Default unit:  s
					<7_GFSK_Pow>		Average power within the access code and header portion of the BR burst (first 126 symbols).
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
		EDR		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see "Power Limits".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Nominal Pow>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<4_GFSK Pow>
					Average power in the GFSK portion of the burst
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<5_DPSK Pow>
					Average power in the DPSK portion of the burst
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<6_DPSK - GFSK>
					Difference between DPSK and GFSK power
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<7_Guard Period>
					Length of the guard band between the packet header and the synchronization sequence
					Range:  0 µs  to  9.99 µs
					Default unit:  s
					<8_PacketTiming>
					Time between the expected and actual start of the first symbol of the Bluetooth burst
					Range:  -20.00 µs to 20.00 µs
					Default unit:  s
					<9_PeakPower>
					Maximum power within the whole burst. The result is only available via remote command.
					Range:  -99.99 dBm  to  99.99 dBm
					Default unit:  dBm
		LE1M		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_OutofTol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​LENergy[:​LE1M]:​PVTime.
					Range:  0 %  to  100 %
					Default unit:  %
					<3_AveragePower>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<4_PeakPower>
					Peak power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<5_LeakagePower>
					Average power during the carrier-off state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<6_PeakMinAvgPow>
					Peak power minus average power
					Range:  0 dB to 158 dB
		LE2M/LRANge	Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_BurstOutOfTol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​LENergy:​LE2M:​PVTime and CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​LENergy:​LRANge:​PVTime.
					Range:  0 %  to  100 %
					Default unit:  %
					<3_NominalPower>
					Average power during the carrier-on state
					Range:  -128 dBm to 30 dBm
					Default unit:  dBm
					<4_PeakPower>
					Peak power during the carrier-on state
					Range:  -128 dBm to 30 dBm
					Default unit:  dBm
					<5_LeakagePower>
					Average power during the carrier-off state
					Range:  -128 dBm to 30 dBm
					Default unit:  dBm
					<6_PeakMinAvgPow>
					Peak power minus average power
					Range:  0 dB to 158 dB
					Default unit:  dB
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		if data_type not in self.data_type_list:
			logerror('data_type is wrong,must be in (CURR, AVER, MIN, MAX)')
			return False
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'BR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PVTime:BRATe:%s?' % (cmd_type, data_type))
			elif self.mode == 'EDR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PVTime:EDRATe:%s?' % (cmd_type, data_type))
			else:
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PVTime:LENergy:%s:%s?' % (cmd_type, self.mode, data_type))
			res = res.replace('\n','').split(',')
			for i in range(len(res)):
				if res[i] == 'NCAP':
					res[i] = '-999'
			if eval(res[0]) == 0:
				logdebug('get pvt measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(1)
		return res
				# return self.error_code(eval(res[0]))
	@log()
	def get_modulation_measure_res(self, data_type='AVER', cmd_type='READ'):
		'''
		mode:	BR,EDR,LE1M,LE2M,LRANge
		data_type:	CURR, AVER, MIN, MAX
		cmd_type:	FETCH, READ, CALCulate
		BR		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "BR".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Δf2 99.9%>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<4_Freq. Accuracy>
					Range:  -250.0 kHz  to  +250.0 kHz
					Default unit:  Hz
					<5_Freq. Drift>
					Range:  -250.0 kHz  to  +250.0 kHz
					Default unit:  Hz
					<6_Max. Drift Rate>
					Range:  -0.99999E+6 Hz/50 μs  to  0.99999E+6 Hz/50 μs
					Default unit:  Hz/50 μs
					<7_Δf1 avg>
					Frequency deviation results
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<8_Δf1 min>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<9_Δf1 max>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<10_Δf2 avg>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<11_Δf2 min>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<12_Δf2 max>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<13_Nominal Pow>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<14_ModRatio>
					Modulation ratio Δf2 avg / Δf1 avg
					Range:  0 to >1
		EDR		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "EDR".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_ωi>
					Initial center frequency error
					Range:  -240.0 kHz  to  +240.0 kHz
					Default unit:  Hz
					<4_ω0 + ωi>
					Overall uncompensated frequency error
					Range:  -240.0 kHz  to  +240.0 kHz
					Default unit:  Hz
					<5_ω0max>
					Maximum compensated frequency error
					Range:  -240.0 kHz  to  +240.0 kHz
					Default unit:  Hz
					<6_RMS DEVM>
					Differential EVM results
					Range:  0.000  to  1.000
					Default unit:  1
					<7_Peak DEVM>
					Range:  0.000  to  1.000
					Default unit:  1
					<8_P99 DEVM>
					Range:  0.000  to  1.000
					Default unit:  1
					<9_Nominal Pow>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
		LE1M/LE2M	Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "Limits (Modulation LE)".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Δf2 99.9%>
					Range:  0 Hz  to  250.0 kHz
					Default unit:  Hz
					<4_Freq. Accuracy>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<5_Freq. Drift>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<6_Max. Drift Rate>
					Range:  -0.99999E+6 Hz/50 μs  to  0.99999E+6 Hz/50 μs
					Default unit:  Hz/50 μs
					<7_Δf1 avg>
					Frequency deviation results
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<8_Δf1 min>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<9_Δf1 max>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<10_Δf2 avg>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<11_Δf2 min>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<12_Δf2 max>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<13_Nominal Pow>
					Range:  -99.99 dBm  to  99.99 dBm
					Default unit:  dBm
					<14_ModRatio>
					Modulation ratio Δf2 avg / Δf1 avg
					Range:  0 to >1
					<15_Freq. Offset>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<16_Initial Freq. Drift>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
		LRANge	Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "Limits (Modulation LE)".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Δf1 99.9%>
					Range:  0 Hz  to  250.0 kHz
					Default unit:  Hz
					<4_Freq. Accuracy>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<5_Freq. Drift>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<6_Max. Drift Rate>
					Range:  -0.99999E+6 Hz/50 μs  to  0.99999E+6 Hz/50 μs
					Default unit:  Hz/50 μs
					<7_Δf1 avg>
					Frequency deviation results
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<8_Δf1 min>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<9_Δf1 max>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<10_Nominal Pow>
					Range:  -99.99 dBm  to  99.99 dBm
					Default unit:  dBm
					<11_Freq. Offset>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		if data_type not in self.data_type_list:
			logerror('data_type is wrong,must be in (CURR, AVER, MIN, MAX)')
			return False
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'BR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:MODulation:BRATe:%s?' % (cmd_type, data_type))
			elif self.mode == 'EDR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:MODulation:EDRATe:%s?' % (cmd_type, data_type))
			else:
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:MODulation:LENergy:%s:%s?' % (cmd_type, self.mode, data_type))
			res = res.replace('\n','').split(',')
			for i in range(len(res)):
				if res[i] == 'NCAP':
					res[i] = '-999'
			if eval(res[0]) == 0:
				logdebug('get mod measure result success')
				break
			elif k == 4:
				# return self.error_code(eval(res[0]))
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(1)
		return res
				# return False
				# return res
	@log()
	def acp_meas_settings(self, opt='CH21'):
		'''
		Selects the measured ACP channel range.
		BR/EDR:
			The ACP can be measured over the expected transmit channel +/- 10 channels (21 channels in total) or over the entire Bluetooth regulatory range (79 channels).
			CH79 | CH21
			Measure 79 or 21 channels
		LE:
			Can be selected to cover either the full LE frequency band (forty 2 MHz channels) or only the adjacency of the current LE channel (ten 2 MHz channels).
			Although LE channels are 2 MHz wide, the channel width in ACP measurements is always 1 MHz ("half-channel").
			CH40 | CH10
			CH10: Covers the current and its 10 adjacent 2 MHz LE channels (5 to the left, 5 to the right). The R&S CMW measures the 1 MHz channels centered at fTX – 10 MHz, ..., fTX + 10 MHz.
			CH40: Covers all 40 LE channels. The R&S CMW measures the 81 half-channels centered at 2401 MHz, 2402 MHz, ..., 2481 MHz.
		'''

		if self.mode in ('BR', 'EDR'):
			if opt not in ('CH79', 'CH21'):
				logerror('opt is wrong,must be CH21 or CH79 for BR/EDR')
				return False
			else:
				self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SACP:BRATe:MEASurement:MODE %s' % opt)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SACP:EDRATe:MEASurement:MODE %s' % opt)
				self.wait()
		elif self.mode in ('LE1M', 'LE2M'):
			if opt not in ('CH40', 'CH10'):
				logerror('opt is wrong,must be CH40 or CH10 for LE')
				return False
			else:
				self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SACP:LENergy:%s:MEASurement:MODE %s' % (self.mode, opt))
				self.wait()
				logdebug('acp measure set success')
		else:
			logerror('mode is wrong')
			return False

	@log()
	def get_acp_res(self, cmd_type='READ'):
		'''
		Returns the "Spectrum ACP" results
		The number to the left of each result parameter is provided for easy identification of the parameter position within the result array.
		BR	Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_Out of Tol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​SACP) exceeding the specified limits, see "Spectrum Limits".
			Range:  0 %  to  100 %
			Default unit:  %
			<3_Nominal Pow>
			Average power during the carrier-on state
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<4_No of Except>
			Number of exceptions (channels ±3, ±4 ... with an ACP above the "Exception PTx" threshold )
			Range:  0  to  74
			<5_ACP_1>
			...
			<83_ACP_79>
			79 ACP results
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm

		'''
		cmd_tpye_list = ['FETCH', 'READ']
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'EDR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:TRACe:SGACp:MAXimum?' % cmd_type)
			else:
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:TRACe:SACP:MAXimum?' % cmd_type)
			time.sleep(2)
			res = res.replace('\n','').split(',')
			for i in range(len(res)):
				if res[i] == 'NCAP':
					res[i] = '-999'
			if eval(res[0]) == 0:
				logdebug('get acp measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			# time.sleep(1)
		return res
				# return self.error_code(eval(res[0]))
	@log()
	def get_acp_res_edr(self, cmd_type='READ'):
		'''
		Returns the "Spectrum ACP" results
		The number to the left of each result parameter is provided for easy identification of the parameter position within the result array.
		BR	Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_Out of Tol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​SACP) exceeding the specified limits, see "Spectrum Limits".
			Range:  0 %  to  100 %
			Default unit:  %
			<3_Nominal Pow>
			Average power during the carrier-on state
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<4_No of Except>
			Number of exceptions (channels ±3, ±4 ... with an ACP above the "Exception PTx" threshold )
			Range:  0  to  74
			<5_ACP_1>
			...
			<83_ACP_79>
			79 ACP results
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm

		'''
		cmd_tpye_list = ['FETCH', 'READ']
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'EDR':
				res1 = self.device.ask('%s:BLUetooth:MEAS:MEValuation:SGACp:EDRate?' % cmd_type)
				res2 = self.device.ask('%s:BLUetooth:MEAS:MEValuation:TRACe:SGACp:MAXimum?' % cmd_type)
			else:
				logerror('mode is wrong, must be edr')
			res1 = res1.replace('\n','').split(',')
			res2 = res2.replace('\n','').split(',')
			for i in range(len(res1)):
				if res1[i] == 'NCAP':
					res1[i] = '-999'
			for i in range(len(res2)):
				if res2[i] == 'NCAP':
					res2[i] = '-999'
			if eval(res1[0]) == 0 and eval(res2[0]) == 0:
				logdebug('get acp measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res1[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(1)
		return [res1, res2]
				# return [self.error_code(eval(res1[0])), self.error_code(eval(res2[0]))]

	@log()
	def get_diff_phase_encoding_res(self, cmd_type='READ'):
		'''
		only for EDR
		Returns the "Differential Phase Encoding" results for EDR packets (single values).
		Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_NominalPower>
			Average power during the carrier-on state
			Range:  -128 dBm to 30 dBm
			Default unit:  dBm
			<3_BitErrorRate>
			Number of bit errors in the received burst, as a percentage of the total number of bits received
			Range:  0 %  to  100 %
			Default unit:  %
			<4_Packets0Errors>
			Number of bit error free packets received, as a percentage of all the bursts received
			Range:  0 %  to  100 %
			Default unit:  %
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		for k in range(5):
			if self.mode == 'EDR':
				if cmd_type not in cmd_tpye_list:
					logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
					return False
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PENCoding:EDRATe:CURRent?' % cmd_type)
				res = res.replace('\n','').split(',')
				for i in range(len(res)):
					if res[i] == 'NCAP':
						res[i] = '-999'
				if eval(res[0]) == 0:
					logdebug('get diff_phase_encoding measure result success')
					break
				elif k == 4:
					err = self.error_code(eval(res[0]))
					logerror('{} ,try agian {}'.format(err,k))
				time.sleep(1)
					# return self.error_code(eval(res[0]))
			else:
				logerror('mode is wrong,must be EDR')
				break
		return res

	@log()
	def get_obw_res(self, cmd_type='READ'):
		'''
		for only BR
		Returns the "Spectrum 20 dB Bandwidth" results.
		Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_Out of Tol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​SOBW) exceeding the specified limits, see "Spectrum Limits".
			Range:  0 %  to  100 %
			Default unit:  %
			<3_Nominal Pow>
			Average power during the carrier-on state
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<4_Peak Emission>
			Peak power in the measured spectral range
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<5_fL>
			Lower frequency where the transmit power drops 20 dB below the peak emission
			Range:  -1.000 MHz  to  +1.000 MHz
			Default unit:  Hz
			<6_fH>
			Higher frequency where the transmit power drops 20 dB below the peak emission
			Range:  -1.000 MHz  to  +1.000 MHz
			Default unit:  Hz
			<7_fH - fL>
			20 dB bandwidth; difference between fH – fL.
			Range:  0.000 MHz  to  +2.000 MHz
			Default unit:  Hz
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		for k in range(5):
			if self.mode == 'BR':
				if cmd_type not in cmd_tpye_list:
					logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
					return False
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:SOBW:BRATe:MAXimum?' % cmd_type)
				res = res.replace('\n','').split(',')
				for i in range(len(res)):
					if res[i] == 'NCAP':
						res[i] = '-999'
				if eval(res[0]) == 0:
					logdebug('get obw measure result success')
					break
				elif k == 4:
					err = self.error_code(eval(res[0]))
					logerror('{} ,try agian {}'.format(err,k))
				time.sleep(1)
					# return self.error_code(eval(res[0]))
			else:
				logerror('mode is wrong,must be BR')
				break
		return res

	@log()
	def get_frange_res(self, cmd_type='READ'):
		'''
		Returns the "Frequency Range" results for BR.
		Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_BurstOutOfTol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​FRANge) exceeding the specified limits, see CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​FRANge.
			Additional ON/OFF enables/disables the out of tolerance evaluation.
			Range:  0 %  to  100 %
			<3_NominalPower>
			Average power during the carrier-on state
			Range:  -128 dBm to 30 dBm
			Default unit:  dBm
			<4_fL>
			Lowest frequency at which spectral power density drops below specified threshold
			Range:  -1 MHz to +1 MHz
			Default unit:  Hz
			<5_fH>
			Highest frequency at which spectral power density drops below specified threshold
			Range:  -1 MHz to +1 MHz
			Default unit:  Hz
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		for k in range(5):
			if self.mode == 'BR':
				if cmd_type not in cmd_tpye_list:
					logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
					return False
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:FRANge:BRATe:CURRent?' % cmd_type)
				res = res.replace('\n','').split(',')
				for i in range(len(res)):
					if res[i] == 'NCAP':
						res[i] = '-999'
				if eval(res[0]) == 0:
					logdebug('get freq range measure result success')
					break
				elif k == 4:
					err = self.error_code(eval(res[0]))
					logerror('{} ,try agian {}'.format(err,k))
				time.sleep(1)
					# return self.error_code(eval(res[0]))
			else:
				logerror('mode is wrong,must be BR')
				break
		return res

class standalone_rx(cmw_bt):
	@log()
	def measurement_states(self, state=0):
		'''
		state:	0|1|2
		0		The measurement enters the "RUN" state.
		1		The measurement enters the "RDY" state. Measurement results are kept. The resources remain allocated to the measurement.
		2		The measurement enters the "OFF" state. All measurement values are set to NAV. Allocated resources are released.
		'''
		if state == 0 or 'RUN':
			self.device.write('INIT:BLUetooth:MEAS:RXQuality')
			loginfo('The TX measurement enters the "RUN" state')
		elif state == 1 or 'RDY':
			self.device.write('STOP:BLUetooth:MEAS:RXQuality')
			loginfo('The TX measurement enters the "RDY" state')
		else:
			self.device.write('ABORt:BLUetooth:MEAS:RXQuality')
			loginfo('The TX measurement enters the "OFF" state')

	@log()
	def gen_switch(self, status='ON'):
		'''
		Turns the generator on or off.
		Setting parameters: ON | OFF
		Return values:
			OFF | PENDing | ON | RDY
			OFF: generator switched off
			PEND: generator switched on but no signal available yet
			ON: generator switched on, signal available
			RDY: generator switched off, ARB file processing complete in smart channel mode
		'''
		self.device.write('SOUR:GPRF:GEN:STAT %s' % status)
		self.wait()
		logdebug('Turns the generator {}'.format(status))

	@log()
	def gen_wave(self, repeat=0, data_rate='1M_DH1', dirty_en=0):
		arbfile_dic = {'1M_DH1' :'BT/BR_1M_DH1_PN9.wv',
					   '1M_DH1_00001111': 'BT/BR_1M_DH1_00001111.wv',
					   '1M_DH1_01010101': 'BT/BR_1M_DH1_01010101.wv',
					   '1M_DH3' :'BT/BR_1M_DH3_PN9.wv',
					   '1M_DH3_00001111': 'BT/BR_1M_DH3_00001111.wv',
					   '1M_DH3_01010101': 'BT/BR_1M_DH3_01010101.wv',
					   '1M_DH5' :'BT/BR_1M_DH5_PN9.wv',
					   '1M_DH5_00001111': 'BT/BR_1M_DH5_00001111.wv',
					   '1M_DH5_01010101': 'BT/BR_1M_DH5_01010101.wv',
					   '2M_DH1' :'BT/BR_2M_DH1_PN9.wv',
					   '2M_DH1_00001111': 'BT/BR_2M_DH1_00001111.wv',
					   '2M_DH1_01010101': 'BT/BR_2M_DH1_01010101.wv',
					   '2M_DH3' :'BT/BR_2M_DH3_PN9.wv',
					   '2M_DH3_00001111': 'BT/BR_2M_DH3_00001111.wv',
					   '2M_DH3_01010101': 'BT/BR_2M_DH3_01010101.wv',
					   '2M_DH5' :'BT/BR_2M_DH5_PN9.wv',
					   '2M_DH5_00001111': 'BT/BR_2M_DH5_00001111.wv',
					   '2M_DH5_01010101': 'BT/BR_2M_DH5_01010101.wv',
					   '3M_DH1' :'BT/BR_3M_DH1_PN9.wv',
					   '3M_DH1_00001111': 'BT/BR_3M_DH1_00001111.wv',
					   '3M_DH1_01010101': 'BT/BR_3M_DH1_01010101.wv',
					   '3M_DH3' :'BT/BR_3M_DH3_PN9.wv',
					   '3M_DH3_00001111': 'BT/BR_3M_DH3_00001111.wv',
					   '3M_DH3_01010101': 'BT/BR_3M_DH3_01010101.wv',
					   '3M_DH5' :'BT/BR_3M_DH5_PN9.wv',
					   '3M_DH5_00001111': 'BT/BR_3M_DH5_00001111.wv',
					   '3M_DH5_01010101': 'BT/BR_3M_DH5_01010101.wv',
					   'LE_1M' : 'BT/LE_1M_PN9_37B.wv',
					   'LE_1M_00001111': 'BT/LE_1M_00001111_37B.wv',
					   'LE_1M_01010101': 'BT/LE_1M_01010101_37B.wv',
					   'LE_2M' : 'BT/LE_2M_PN9_37B.wv',
					   'LE_2M_00001111': 'BT/LE_2M_00001111_37B.wv',
					   'LE_2M_01010101': 'BT/LE_2M_01010101_37B.wv',
					   'LE_500k' : 'BT/LE_500k_PN9_37B.wv',
					   'LE_125k' : 'BT/LE_125k_PN9_37B.wv'}
		arbfile_dic_dirty = {'1M_DH1' :'BT/BR_1M_DH1_PN9_dirty.wv',
							'1M_DH3' :'BT/BR_1M_DH3_PN9_dirty.wv',
							'1M_DH5' :'BT/BR_1M_DH5_PN9_dirty.wv',
							'2M_DH1' :'BT/BR_2M_DH1_PN9_dirty.wv',
							'2M_DH3' :'BT/BR_2M_DH3_PN9_dirty.wv',
							'2M_DH5' :'BT/BR_2M_DH5_PN9_dirty.wv',
							'3M_DH1' :'BT/BR_3M_DH1_PN9_dirty.wv',
							'3M_DH3' :'BT/BR_3M_DH3_PN9_dirty.wv',
							'3M_DH5' :'BT/BR_3M_DH5_PN9_dirty.wv',
							'LE_1M' : 'BT/LE_1M_PN9_37B_dirty.wv',
							'LE_2M' : 'BT/LE_2M_PN9_37B_dirty.wv',
							'LE_500k' : 'BT/LE_500k_PN9_37B_dirty.wv',
							'LE_125k' : 'BT/LE_125k_PN9_37B_dirty.wv',
							'LE_1M_stable': 'BT/LE_1M_PN9_37B_dirty_stable.wv',
							'LE_2M_stable': 'BT/LE_2M_PN9_37B_dirty_stable.wv',
							'LE_500k_stable': 'BT/LE_500k_PN9_37B_dirty_stable.wv',
							'LE_125k_stable': 'BT/LE_125k_PN9_37B_dirty_stable.wv'}
		fold_path = 'D:/waveform/'
		self.device.write('SOUR:GPRF:GEN:LIST OFF')
		self.device.write('SOURce:GPRF:GEN:BBMode ARB')
		if repeat==0:
			self.device.write('SOUR:GPRF:GEN:ARB:REP CONT')
		elif repeat > 10000:
			logerror('repeate times out of maximum range!')
			return False
		else:
			self.device.write('SOUR:GPRF:GEN:ARB:REP SING')
			self.device.write('SOURce:GPRF:GEN:ARB:CYCles %d' % repeat)
			self.device.write('SOURce:GPRF:GEN:ARB:ASAMPles 0')
		if dirty_en == 0:
			arb_file = arbfile_dic[data_rate]
		else:
			arb_file = arbfile_dic_dirty[data_rate]
		self.device.write('SOUR:GPRF:GEN:ARB:FILE %s' % ('\''+fold_path+arb_file+'\''))
		self.device.write('TRIG:GPRF:GEN:ARB:RETR ON')
		self.device.write('TRIG:GPRF:GEN:ARB:AUT OM')
		self.device.write('TRIG:GPRF:GEN:ARB:SOUR Manual')
		return True

	@log()
	def trig_wave(self):
		'''
		Generates a trigger event for the ARB trigger.
		The trigger causes the generator to start the selected waveform file.
		'''
		self.device.write('TRIG:GPRF:GEN:ARB:MAN:EXEC')
		time.sleep(1)

	@log()
	def para_settings(self, freq=2402, level=-30):
		'''
		Selects the frequency of the RF generator (generator frequency).
		Some of the baseband modes (modulation types) modify the generator frequency.
		Sets the base RMS level of the constant-frequency RF generator.
		Parameters:
			freq	Range:  70E+6 Hz  to  6E+9 Hz
					Default unit:  Hz
			level	Range:  -130 dBm to 0 dBm at RF 1 COM and RF 2 COM, -120 dBm to 13 dBm at RF 1 OUT;
							notice the ranges quoted in the data sheet
					Default unit:  dBm
		'''
		freq = freq*1e+6
		if freq < 70e+6 or freq > 6e+9:
			logerror('instrument freq set over range')
			return False
		self.device.write('SOURce:GPRF:GEN:RFSettings:FREQuency {}'.format(freq))
		self.wait()
		self.device.write('SOURce:GPRF:GEN:RFSettings:LEVel %d' % level)
		self.wait()
		logdebug('parameter set success,freq is {} Hz,output power level is {} dBm'.format(freq, level))

class combined_signal_path(cmw_bt):
	# def str_check(self, i):
	# 	w_str = 'OFF' if i == 0 else 'ON'
	# 	return w_str
	@log()
	def signaling_switch(self, en=0):
		'''
		Sets/gets the main state of the "Bluetooth Signaling" application.
		0:	off
		1:	on	,When turned ON, the R&S CMW switches to standby state
		'''
		self.device.write('SOURce:BLUetooth:SIGN:STATe %s' % self.str_check(en))
		self.wait()
	@log()
	def retrieve_eut_information(self):
		'''
		Gets the name of the connected device.
		Return values:
		<Name>		Up to 255 characters

		Gets LMP_version_res information.
		Return values:
		<LMP>		Textual representation of the LMP version (VersNr) as defined in http://www.bluetooth.org/Technical/AssignedNumbers/link_manager.htm
		<Company>	Textual representation of the company identifier (CompId) as defined in http://www.bluetooth.org/Technical/AssignedNumbers/identifiers.htm
		<LMPSubversion>	LMP subversion number (SubVersNr), a company-internal version number

		Gets the address (BD_ADDR) of the connected Bluetooth device.
		Return values:
		<BDAddress>		The Bluetooth device address in hexadecimal notation.
		Range:  #H0  to  #HFFFFFFFFFFFF (12 hexadecimal digits)
		'''
		# eut_name = self.device.ask('SENSe:BLUetooth:SIGN:EUT:INFormation:NAME?')
		# self.wait()
		eut_version = self.device.ask('SENSe:BLUetooth:SIGN:EUT:INFormation:VERSion?')
		self.wait()
		eut_bdaddr = self.device.ask('SENSe:BLUetooth:SIGN:EUT:INFormation:BDADdress?')
		self.wait()
		return [eut_version,eut_bdaddr]

	@log()
	def hopping_en(self, en=0):
		'''
		#蓝牙跳频使能
		0:	off
		1:	on
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:HOPPing %s' % self.str_check(en))
		self.wait()

	@log()
	def sig_opmode(self, mode='RFTest'):
		'''
		#信令测试模式设置
		CNTest | RFTest | ECMode | PROFiles
		Connection test, RF test, audio echo mode, audio profiles
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:OPMode %s' % mode)
		self.wait()

	@log()
	def sig_std(self, std='LE'):
		'''
		#蓝牙协议选择
		CLAS or LE
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:OPMode %s' % std)
		self.wait()

	@log()
	def sig_le_phy(self, phy='LE1M'):
		'''
		<PHY>
		LE1M | LE2M | LELR
		LE1M: LE 1 Msymbol/s uncoded PHY
		LE2M: LE 2 Msymbol/s uncoded PHY
		LELR: LE 1 Msymbol/s long range (LE coded PHY)
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PHY:LENergy {}'.format(phy))
		self.wait()

	@log()
	def sig_le_lr_coding(self, coding='S2'):
		'''
		Defines coding S for LE coded PHY according to the core specification version 5.0 for Bluetooth wireless technology.
		S8 | S2
		Coding S = 8 or S = 2
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:FEC:LENergy:LRANge {}'.format(coding))
		self.wait()

	@log()
	def sig_btype(self, btype='BR'):
		'''
		Defines the Bluetooth burst type to be used for RF tests.
		BR | EDR | LE
		BR: "Basic Rate"
		EDR: "Enhanced Data Rate"
		LE: "Low Energy"
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:BTYPe %s' % btype)
		self.wait()
		self.mode = btype

	@log()
	def RF_Frequency_Settings_rx(self, mode='DTM', ch_tx=19, ch_rx=38):
		'''
		mode:
			DTM:Configures the channel number for direct test mode,for le
				Range:  0 Ch  to  39 Ch
			LOOP:Defines the channels used by the loopback test
				Range:  0 Ch  to  78 Ch
			TXT:Defines the channels used by the TX test.
				Range:  0 Ch  to  78 Ch
		'''
		# ch_rx = 0 if ch_tx > 39 else 78
		if mode == 'DTM':
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:CHANnel:DTMode %d' % ch_tx)
			self.wait()
		elif mode == 'LOOP':
			self.device.write('CONFigure:BLUetooth:SIGN:TMODe LOOPback')
			self.wait()
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:CHANnel:LOOPback %d,%d' % (ch_tx,ch_rx))
			self.wait()
		elif mode == 'TXT':
			self.device.write('CONFigure:BLUetooth:SIGN:TMODe TXTest ')
			self.wait()
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:CHANnel:TXTest  %d' % ch_tx)
			self.wait()

	@log()
	def RF_Frequency_Settings_tx(self, mode='DTM', ch_tx=19):
		'''
		mode:
			DTM:Configures the channel number for direct test mode,for le
				Range:  0 Ch  to  39 Ch
			LOOP:Defines the channels used by the loopback test
				Range:  0 Ch  to  78 Ch
			TXT:Defines the channels used by the TX test.
				Range:  0 Ch  to  78 Ch
		'''
		ch_rx = ch_tx-39 if ch_tx > 39 else ch_tx+39
		if mode == 'DTM':
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:CHANnel:DTMode %d' % ch_tx)
			self.wait()
		elif mode == 'LOOP':
			self.device.write('CONFigure:BLUetooth:SIGN:TMODe LOOPback')
			self.wait()
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:CHANnel:LOOPback %d,%d' % (ch_tx, ch_rx))
			self.wait()
		elif mode == 'TXT':
			self.device.write('CONFigure:BLUetooth:SIGN:TMODe TXTest ')
			self.wait()
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:CHANnel:TXTest  %d' % ch_tx)
			self.wait()

	@log()
	def RF_Power_settings(self, rx_level=-40, tx_power=15, margin=8):
		'''
		AutoRanging off
		Parameters:
		rx_level	Defines the absolute TX level of the R&S CMW (master) signal.
					The allowed value range can be calculated as follows:
						Range (Level) = Range (Output Power) - External Attenuation
						Range (Output Power) = -130 dBm to 0 dBm (RFx COM) or -120 dBm to 8 dBm (RFx OUT);
		tx_power	Sets the expected nominal power of the EUT signal.
					The range of the expected nominal power can be calculated as follows:
						Range (Expected Nominal Power) = Range (Input Power) + External Attenuation - User Margin
		margin		Sets the margin that the R&S CMW adds to the expected nominal power to determine the reference level.
					Range:  0 dB to (55 dB + external attenuation - expected nominal power)
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:ARANging OFF')
		self.wait()
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:ENPower %d ' % tx_power)
		self.wait()
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:LEVel %d ' % rx_level)
		self.wait()
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:UMARgin %d ' % margin)
		self.wait()

	@log()
	def RF_Power_settings_autoranging(self):
		'''
		AutoRanging on
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:ARANging ON')
		self.wait()

	@log()
	def dirty_tx_settings(self, en=0, mode='BR'):
		'''
		en:		Enables/disables the dirty transmitter.
		mode:	Commands for BR (...:BRATe...), EDR (...:EDRate...), LE 1M PHY (...:LE1M...), LE 2M PHY (...:LE2M...),
				and LE coded PHY (...:LRANge...) are available.
		'''
		if mode == 'BR':
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:DTX:MODE:BRATe SPEC')
			self.wait()
		elif mode == 'EDR':
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:DTX:MODE:EDRate SPEC')
			self.wait()
		elif mode == 'LE1M':
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:DTX:MODE:LENergy:LE1M SPEC')
			self.wait()
		elif mode == 'LE2M':
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:DTX:MODE:LENergy:LE2M SPEC')
			self.wait()
		elif mode == 'LRANge':
			self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:DTX:MODE:LENergy:LRANge SPEC')
			self.wait()
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:DTX %s' % self.str_check(en))
		self.wait()

	@log()
	def stack_delay_ctrl(self, ptimeout=2, act_delay=2):
		'''
		Parameters:
		ptimeout		Sets delay for the processing of HCI commands.
						If set to 100 ms, maximally one HCI command is processed every 100 ms.
						Range:  1 ms to 100 ms
		act_delay		Specifies delay for test mode activation. The delay is applied after acknowledgment from EUT that it has received activate test mode command.
						Range:  1 ms to 100 ms
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:DELay:PTIMeout %d' % ptimeout)
		self.wait()
		self.device.write('CONFigure:BLUetooth:SIGN:DELay:TMODe %d' % act_delay)
		self.wait()

	@log()
	def config_power_control(self, para='MAX'):
		'''
		Sends a command to the EUT to increase/decrease power.
		Setting parameters:
		<para>	UP | DOWN | MAX
		One step up, one step down, command to maximum EUT power
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PCONtrol:STEP:ACTion {}'.format(para))
		self.wait()

	def config_power_control_state(self):
		'''
		Return values:
		<PowChangeGFSK>
		 NNE | UP | DOWN | MAX
		NNE: none
		UP: power up command accepted
		DOWN: power down command accepted
		MAX: maximum power command accepted
		<PowMinMaxGFSK>
		 NOTS | CHANged | MAX | MIN | NNM
		NOTS: not supported (command not accepted by the EUT)
		CHANged: changed one step
		MAX: max power reached
		MIN: min power reached
		NNM: no new message
		<PowChangeDQPSK>
		 NNE | UP | DOWN | MAX
		<PowMinMaxDQPSK>
		 NOTS | CHANged | MAX | MIN | NNM
		<PowChangeDPSK>
		 NNE | UP | DOWN | MAX
		<PowMinMaxDPSK>
		NOTS | CHANged | MAX | MIN | NNM
		'''
		res = self.device.ask('SENSe:BLUetooth:SIGN:EUT:PCONtrol:STATe?')
		res = res.replace('\n','').replace('\r','')
		logdebug(res)
		return res

	@log()
	def get_bt_connect_state(self):
		'''
		Returns the signaling state of the R&S CMW for BR/EDR. State changes are initiated using the CALL:​BLUetooth:​SIGN<i>:​CONNection:​ACTion command
		'''
		res = self.device.ask('FETCh:BLUetooth:SIGN:CONNection:STATe?')
		res = res.replace('\n','').replace('\r','')
		logdebug(res)
		return res

	@log()
	def get_le_state(self):
		'''
		Returns the signaling state of the R&S CMW for LE direct test connections.
		'''
		res = self.device.ask('FETCh:BLUetooth:SIGN:LENergy:STATe?')
		res = res.replace('\n','').replace('\r','')
		logdebug(res)
		return res

	@log()
	def get_le_connect_state(self):
		'''
		Returns the signaling state of the R&S CMW for LE. State changes are initiated using the CALL:​BLUetooth:​SIGN<i>:​CONNection:​ACTion:​LESignaling command.
		'''
		res = self.device.ask('FETCh:BLUetooth:SIGN:CONNection:STATe:LESignaling?')
		res = res.replace('\n','').replace('\r','')
		logdebug(res)
		return res

	@log()
	def bt_connect_action(self, action='INQuire '):
		'''
		Requests the R&S CMW to perform certain signaling actions for BR/EDR. It has no query form: the current signaling state can be retrieved using the FETCh:​BLUetooth:​SIGN<i>:​CONNection:​STATe? command.
		<Action>
		INQuire | SINQuiry | SCONnecting | STMode | CONNect | TMConnect | DETach | REController | EMConnect | EXEMode | ENEMode | HFPConnect | EXHFp | ENHFp | AGConnect | ENAGate | EXAGate | ADConnect

		INQuire: Switch on master signal and start inquiry for Bluetooth devices within range

		Inquiry stops after a configurable maximum duration (see CONFigure:​BLUetooth:​SIGN<i>:​CONNection:​INQuiry:​ILENgth) or after a configurable number of responses (see CONFigure:​BLUetooth:​SIGN<i>:​CONNection:​INQuiry:​NOResponses)

		SINQuiry: Stop inquiry, switch off master signal and return to standby state

		SCONnecting: Stop an ongoing connection setup, switch off the master signal and return to standby state

		STMode: Stop a test mode connection, switch off the master signal and return to standby state

		CONNect: Switch on master signal, start paging the selected Bluetooth device and establish an ACL connection

		TMConnect: Switch on master signal, start paging the selected Bluetooth device and establish a test mode connection

		DETach: Detach an established connection, switch off the master signal and return to standby state

		REController: Run EUT controller to reset and initialize the EUT via USB connection

		EMConnect: Connect audio echo mode

		EXEMode: Exit audio echo mode

		ENEMode: Enter audio echo mode

		HFPConnect: Connect hands-free profile

		EXHFp: Exit hands-free profile

		ENHFp: Enter hands-free profile

		AGConnect: Connect hands-free audio gateway profile

		ENAGate: Enter hands-free audio gateway profile

		EXAGate: Exit hands-free audio gateway profile

		ADConnect: Connect A2DP
		'''
		if action not in ('INQuire', 'SINQuiry', 'SCONnecting', 'STMode', 'CONNect', 'TMConnect', 'DETach', 'REController', 'EMConnect', 'EXEMode', 'ENEMode',
						  'HFPConnect', 'EXHFp', 'ENHFp', 'AGConnect', 'ENAGate', 'EXAGate', 'ADConnect','INQ', 'SINQ','SCON', 'STM', 'CONN', 'TMC', 'DET',
						  'REC', 'EMC', 'EXEM', 'ENEM','HFPC', 'EXHF', 'ENHF', 'AGC', 'ENAG', 'EXAG', 'ADC'):
			return False
		self.device.write('CALL:BLUetooth:SIGN:CONNection:ACTion {}'.format(action))
		self.wait()

	@log()
	def le_connect_action(self, action='INQuire '):
		'''
		quests the R&S CMW to perform certain signaling actions for LE. It has no query form: the current signaling state can be retrieved using the FETCh:​BLUetooth:​SIGN<i>:​CONNection:​STATe:​LESignaling? command.
		<Action>	INQuire | SINQuiry | CONNect | SCONnecting | DETach
		'''
		if action not in ('INQuire', 'SINQuiry','SCONnecting','CONNect','DETach','INQ', 'SINQ','SCON', 'CONN', 'DET'):
			logerror('action is wrong command')
			return False
		self.device.write('CALL:BLUetooth:SIGN:CONNection:ACTion:LESignaling {}'.format(action))
		self.wait()

	@log()
	def check_le_connect_usb(self):
		'''
		Checks the LE connection via USB.
		'''
		self.le_reset_eut()
		time.sleep(1)
		res = self.device.ask('CALL:BLUetooth:SIGN:CONNection:CHECk:LENergy?')
		logdebug(res)
		if res.find('PASS') != -1:
			logdebug('LE comport connect success')
		else:
			raise StandardError("LE comport connect fail")

	@log()
	def le_reset_eut(self):
		'''
		Sends the HCI reset command to the EUT via USB.
		'''
		self.device.write('CALL:BLUetooth:SIGN:LENergy:RESet')
		self.wait()

	@log()
	def config_sig_testmode(self, testmode='LOOPback'):
		'''
		Selects the test mode that the EUT enters in a test mode connection.
		TestMode>	LOOPback | TXTest
		LOOPback: BR/EDR loopback test mode
		TXTest: BR/EDR transmitter test mode
		'''
		self.device.write('CALL:BLUetooth:SIGN:TMODe {}'.format(testmode))
		self.wait()

	@log()
	def config_delay_tmode(self, delay=2):
		self.device.write('CONFigure:BLUetooth:SIGN:DELay:TMODe {}'.format(delay))
		self.wait()

	@log()
	def config_connect_le_packet_pattern(self, rate='LE1M', pattern='PRBS9'):
		if rate == 'LELR':
			rate = 'LRANge'
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PATTern:LENergy:{} {}'.format(rate,pattern))
		self.wait()

	@log()
	def config_connect_br_packet_pattern(self,  pattern='PRBS9'):
		'''
		<Pattern Type>
		ALL0 | ALL1 | P11 | P44 | PRBS9 | ALT
		ALL0: 00000000
		ALL1: 11111111
		P11: 10101010
		P44: 11110000
		PRBS9: pseudo-random bit sequences of a length of 9 bits (transmission of identical packet series)
		ALT: the periodical alternation of the pattern P11 and P44
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PATTern:BRATe {}'.format(pattern))
		self.wait()

	@log()
	def config_connect_edr_packet_pattern(self,  pattern='PRBS9'):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PATTern:EDRate {}'.format(pattern))
		self.wait()

	@log()
	def config_connect_le_packet_len(self, rate='LE1M', len=37):
		if rate == 'LELR':
			rate = 'LRANge'
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PLENgth:LENergy:{} {}'.format(rate,len))
		self.wait()

	@log()
	def config_connect_br_packet_len(self,  len=27):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PLENgth:BRATe {}'.format(len))
		self.wait()

	@log()
	def config_connect_edr_packet_len(self,  len=54):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PLENgth:EDRate {}'.format(len))
		self.wait()

	@log()
	def config_connect_br_packet_ptype(self, ptype='DH1'):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PTYPe:BRATe {}'.format(ptype))
		self.wait()

	@log()
	def config_connect_edr_packet_ptype(self, ptype='E21P'):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PACKets:PTYPe:EDRate  {}'.format(ptype))
		self.wait()

	@log()
	def config_connect_whitening(self, en='OFF'):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:WHITening {}'.format(en))
		self.wait()

	@log()
	def config_connect_le_synword(self, synword='#H71764129'):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:SYNWord:LENergy {}'.format(synword))
		self.wait()

	@log()
	def config_paging_classic_bdaddr(self, cmw_addr='#H123456123456', eut_addr='#H654321654321'):
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:BDADdress:CMW {}'.format(cmw_addr))
		self.wait()
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:BDADdress:EUT {}'.format(eut_addr))
		self.wait()

	@log()
	def config_paging_classic_svtimeout(self, svtimeout=8000):
		'''
		Sets/gets the LMP supervision timeout.
		Range:  400 slots  to  65535 slots
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:SVTimeout {}'.format(svtimeout))
		self.wait()

	@log()
	def config_paging_classic_ilength(self, ilength=8000):
		'''
		Sets/gets the Inquiry_Length parameter, i.e. the total duration of the inquiry mode.
		The inquiry length in units of 1.28 s
		Range:  1  to  24
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:INQuiry:ILENgth {}'.format(ilength))
		self.wait()

	@log()
	def config_paging_classic_NOResponses(self, NOResponses=1):
		'''
		Sets/gets the maximum number of responses recorded during an inquiry.
		The maximum number of responses, where 0 means "unlimited".
		Range:  0  to  12
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:INQuiry:NOResponses {}'.format(NOResponses))
		self.wait()

	@log()
	def config_paging_classic_tout(self, tout=8000):
		'''
		Sets/gets the Page_Timeout configuration parameter, i.e. the maximum time the local link manager waits for a baseband page response from the EUT.
		Range:  22  to  65535
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PAGing:TOUT {}'.format(tout))
		self.wait()

	@log()
	def get_paging_classic_target(self):
		'''
		This query returns a list of all targets available for paging.
		If no inquiry was made before, this list only contains the default device (see CONFigure:​BLUetooth:​SIGN<i>:​CONNection:​BDADdress:​EUT). After inquiry, it also contains the devices that were responding (in chronological order).
		Return values:
		<NoDiscoveredDevices>		The number of devices discovered during inquiry
		{<ItemNumber>,<DiscoveredEUT>}	A comma-separated list of Bluetooth devices, where each device is represented by an item number and its BD_Address in hexadecimal notation. Item number 0 always represents the default target.
		'''
		res = self.device.ask('CONFigure:BLUetooth:SIGN:CONNection:INQuiry:PTARgets:CATalog?')
		return res

	@log()
	def config_paging_classic_target(self, target=1):
		'''
		Selects the device to page from the paging target catalog (see CONFigure:​BLUetooth:​SIGN<i>:​CONNection:​INQuiry:​PTARgets:​CATalog?).
		After a reset, if no inquiry was made before or if no device was detected during the previous inquiry, only the default device (<Target>=0) can be selected. After a successful inquiry, the first discovered device (<Target>=1) is pre-selected.
		<Target>	Index of the device in the paging target catalog, where 0 always corresponds to the default device.
					If an invalid index is selected, an error message is returned.
					Range:  Integer >= 0
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:CONNection:PAGing:PTARget {}'.format(target))
		self.wait()

	@log()
	def config_hwinterface(self, interface='RS232'):
		'''
		Defines interface used for tests.
		<no>
		1..4

		1: HW interface for LE tests

		2: HW interface for BR / EDR tests
		<HwInterface>
		NONE | RS232 | USB

		RS232: USB connection with USB to RS232 adapter

		NONE: no control via USB to be used

		USB: direct USB connection
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:HWINterface1 {}'.format(interface))
		self.wait()

	@log()
	def config_connect_ereset(self, en='ON'):
		self.device.write('CONFigure:BLUetooth:SIGN:COMSettings1:ERESet {}'.format(en))
		self.wait()

	@log()
	def config_comport(self):
		'''
		Queries the COM ports used by an EUT. The command is relevant for the USB connection with USB-to-serial converter ("HW Interface" = USB to RS232 adapter).

		Results are returned for each used USB port: <NoDevices>, {1, <DiscoveredPort>}1, ..., {<NoDevices>, <DiscoveredPort>}<NoDevices>
		'''
		res = self.device.ask('CONFigure:BLUetooth:SIGN:COMSettings:PORTs:CATalog?')
		loginfo(res)

	@log()
	def config_comport_baudrate(self, baudrate='B115k'):
		'''
		<BaudRate>	B110 | B300 | B600 | B12K | B24K | B48K | B96K | B14K | B19K | B28K | B38K | B57K | B115k | B234k | B460k | B500k | B576k | B921k | B1M | B1M5 | B2M | B3M | B3M5 | B4M

		Data transmission rate in symbol: 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 2000000, 3000000, 3500000, 4000000
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:COMSettings1:BAUDrate {}'.format(baudrate))
		self.wait()

	@log()
	def per_meas_state(self, state=0):
		if state == 0 or state == 'RUN':
			self.device.write('INITiate:BLUetooth:SIGN:RXQuality:PER')
			self.wait()
			loginfo('The RX measurement enters the "RUN" state')
		elif state == 1 or state == 'RDY':
			self.device.write('STOP:BLUetooth:SIGN:RXQuality:PER')
			self.wait()
			loginfo('The RX measurement enters the "RDY" state')
		else:
			self.device.write('ABORt:BLUetooth:SIGN:RXQuality:PER')
			self.wait()
			loginfo('The RX measurement enters the "OFF" state')

	@log()
	def per_search_meas_state(self, state=0):
		if state == 0 or state == 'RUN':
			self.device.write('INITiate:BLUetooth:SIGN:RXQuality:SEARch:PER')
			self.wait()
			loginfo('The RX measurement enters the "RUN" state')
		elif state == 1 or state == 'RDY':
			self.device.write('STOP:BLUetooth:SIGN:RXQuality:SEARch:PER')
			self.wait()
			loginfo('The RX measurement enters the "RDY" state')
		else:
			self.device.write('ABORt:BLUetooth:SIGN:RXQuality:SEARch:PER')
			self.wait()
			loginfo('The RX measurement enters the "OFF" state')

	@log()
	def ber_meas_state(self, state=0):
		if state == 0 or state == 'RUN':
			self.device.write('INITiate:BLUetooth:SIGN:RXQuality:BER')
			self.wait()
			loginfo('The RX measurement enters the "RUN" state')
		elif state == 1 or state == 'RDY':
			self.device.write('STOP:BLUetooth:SIGN:RXQuality:BER')
			self.wait()
			loginfo('The RX measurement enters the "RDY" state')
		else:
			self.device.write('ABORt:BLUetooth:SIGN:RXQuality:BER')
			self.wait()
			loginfo('The RX measurement enters the "OFF" state')

	@log()
	def ber_search_meas_state(self, state=0):
		if state == 0 or state == 'RUN':
			self.device.write('INITiate:BLUetooth:SIGN:RXQuality:SEARch:BER')
			self.wait()
			loginfo('The RX measurement enters the "RUN" state')
		elif state == 1 or state == 'RDY':
			self.device.write('STOP:BLUetooth:SIGN:RXQuality:SEARch:BER')
			self.wait()
			loginfo('The RX measurement enters the "RDY" state')
		else:
			self.device.write('ABORt:BLUetooth:SIGN:RXQuality:SEARch:BER')
			self.wait()
			loginfo('The RX measurement enters the "OFF" state')

	@log()
	def get_ber_search_meas_state(self):
		res = self.device.ask('FETCh:BLUetooth:SIGN:RXQuality:SEARch:BER:STATe?')
		res = res.replace('\n','').replace('\r','')
		logdebug(res)
		return res

	@log()
	def get_ber_meas_state(self):
		res = self.device.ask('FETCh:BLUetooth:SIGN:RXQuality:BER:STATe?')
		res = res.replace('\n','').replace('\r','')
		logdebug(res)
		return res

	@log()
	def config_rxq_repetion(self, rep='SING'):
		'''
		<Repetition>	SINGleshot | CONTinuous
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:REPetition {}'.format(rep))
		self.wait()

	@log()
	def config_rxq_le_packets(self, rate='LE1M', num=1500):
		'''
		Defines the number of data packets to be measured per measurement cycle (statistics cycle).

		Commands for LE 1M PHY - uncoded (...:LE1M...), LE 2M PHY - uncoded (...:LE2M...), and LE coded PHY (...:LRANge...) are available.
		<NumberPackets> Range:  1  to  30E+3
		'''
		if rate not in ('LE1M','LE2M','LRANge'):
			logerror('rate  is wrong command')
			return False
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:PACKets:LENergy:{} {}'.format(rate,num))
		self.wait()

	@log()
	def config_rxq_le_integrity(self, rate='LE1M', en='OFF'):
		'''
		Sets the ratio of the test packets with correct CRC transmitted by the R&S CMW.
		<ReportIntegrity>	OFF | ON

		OFF: 100% of packets generated with correct CRC

		ON: 50% of packets generated with correct CRC
		'''
		if rate not in ('LE1M','LE2M','LRANge'):
			logerror('rate  is wrong command')
			return False
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:RINTegrity:LENergy:{} {}'.format(rate,en))
		self.wait()

	@log()
	def config_rxq_le_mod_index(self, en='OFF'):
		'''
		Selects the standard or stable modulation index.
		<ModIndexType>	OFF | ON

		OFF: standard modulation index is used

		ON: stable modulation index is used
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:SMINdex:LENergy {}'.format(en))
		self.wait()

	@log()
	def config_rxq_br_packets(self, num=1500):
		'''
		Defines the number of data packets to be measured per measurement cycle (statistics cycle).
		<NumberPackets> Range:  1  to  30E+3
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:PACKets {}'.format(num))
		self.wait()

	@log()
	def config_rxq_br_search_tout(self, tout=100):
		'''
		Defines a timeout for the measurement. The timer is started when the measurement is initiated via a READ or INIT command. It is not started if the measurement is initiated manually ([ON | OFF]
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:SEARch:TOUT {}'.format(tout))
		self.wait()

	@log()
	def config_rxq_br_tout(self, tout=10):
		'''
		Defines a timeout for the measurement. The timer is started when the measurement is initiated via a READ or INIT command. It is not started if the measurement is initiated manually ([ON | OFF]
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:TOUT {}'.format(tout))
		self.wait()

	@log()
	def config_rxq_br_search_packets(self, num=1500):
		'''
		Defines the number of data packets to be measured per measurement cycle (statistics cycle).
		<NumberPackets> Range:  1  to  30E+3
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:SEARch:PACKets {}'.format(num))
		self.wait()

	@log()
	def config_rxq_br_search_step(self, step=0.5):
		'''
		Specifies the power step for the BR/EDR search iteration of BER search measurements.
		<LevelStep>		Range:  0.01 dB  to  5 dB
		'''
		self.device.write('CONFigure:BLUetooth:SIGN:RXQuality:SEARch:STEP:BREDr {}'.format(step))
		self.wait()

	@log()
	def config_rx_level(self, rxpwr=-40):
		self.device.write('CONFigure:BLUetooth:SIGN:RFSettings:LEVel {}'.format(rxpwr))
		self.wait()

	@log()
	def meas_le_per_res(self, cmd_type='READ', rate='LE1M'):
		'''
		Return values:
			<Reliability>
			See "Reliability Indicator"
			<PER>
			Packet error rate
			Range:  0 %  to  100 %
			Default unit:  %
			<PacketsReceived>
			Number of correct packets received and reported by the EUT.
			Range:  0  to  30E+3
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			res = self.device.ask('{}:BLUetooth:SIGN:RXQuality:PER:LENergy:{}?'.format(cmd_type, rate))
			logdebug(res)
			res = res.replace('\n','').split(',')

			if eval(res[0]) == 0:
				logdebug('get le per measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(0.5)
		return res

	@log()
	def meas_bt_ber_res(self, cmd_type='READ'):
		'''
		<1_Reliability>		See "Reliability Indicator"
		<2_BER>
		Bit error rate
		Range:  0 %  to  100 %
		Default unit:  %
		<3_PER>
		Packet error rate
		Default unit:  %
		<4_BitErrors>
		Sum of received erroneous data bits
		Range:  0  to  184467440737096E+5
		<5_MissingPackets>
		Difference between the number of packets sent and the number of packets received in percentage
		Default unit:  %
		<6_NAK>
		Percentage of packets not acknowledged by the EUT positively
		Default unit:  %
		<7_HEC_Errors>
		Percentage of packets with the bit errors in the header
		Default unit:  %
		<8_CRC_Errors>
		Percentage of packets with the bit errors in the payload
		Default unit:  %
		<9_WrongPackType>
		Received packets of a different type to the one originally transmitted
		Default unit:  %
		<10_WrongPaylRate>
		Received packets of a different payload length to the one originally transmitted
		Default unit:  %
		<11_PackReceived>
		Total number of packets successfully received (without bad packets)
		Range:  0  to  200E+6
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			res = self.device.ask('{}:BLUetooth:SIGN:RXQuality:BER?'.format(cmd_type))
			res = res.replace('\n','').split(',')

			if eval(res[0]) == 0:
				logdebug('get le per measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(0.5)
		return res

	@log()
	def meas_bt_ber_search_res(self, cmd_type='READ'):
		'''
		<1_Reliability>		See "Reliability Indicator"
		<2_BER>
		Bit error rate
		Range:  0 %  to  100 %
		Default unit:  %
		<3_PER>
		Packet error rate
		Default unit:  %
		<4_BitErrors>
		Sum of received erroneous data bits
		Range:  0  to  184467440737096E+5
		<5_MissingPackets>
		Difference between the number of packets sent and the number of packets received in percentage
		Default unit:  %
		<6_NAK>
		Percentage of packets not acknowledged by the EUT positively
		Default unit:  %
		<7_HEC_Errors>
		Percentage of packets with the bit errors in the header
		Default unit:  %
		<8_CRC_Errors>
		Percentage of packets with the bit errors in the payload
		Default unit:  %
		<9_WrongPackType>
		Received packets of a different type to the one originally transmitted
		Default unit:  %
		<10_WrongPaylRate>
		Received packets of a different payload length to the one originally transmitted
		Default unit:  %
		<11_PackReceived>
		Total number of packets successfully received (without bad packets)
		Range:  0  to  200E+6
		<12_SearchResult>
		TX level of the R&S CMW resulting in the configured BER search limit
		Range:  -100 dBm  to  0 dBm
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			res = self.device.ask('{}:BLUetooth:SIGN:RXQuality:SEARch:BER?'.format(cmd_type))
			res = res.replace('\n','').split(',')

			if eval(res[0]) == 0:
				logdebug('get br/edr ber measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(0.5)
		return res

	@log()
	def mode_set(self, mode='BR'):
		'''
		mode:	BR,EDR,LE1M,LE2M,LRANge
		'''
		if mode not in self.modelist:
			logerror('mode is wrong,must be in (BR,EDR,LE1M,LE2M,LRANge)')
			return False
		else:
			self.mode = mode

	@log()
	def tx_measure_states(self, state=0):
		'''
		state:	0|1|2
		0		The measurement enters the "RUN" state.
		1		The measurement enters the "RDY" state. Measurement results are kept. The resources remain allocated to the measurement.
		2		The measurement enters the "OFF" state. All measurement values are set to NAV. Allocated resources are released.
		'''
		if state == 0 or state == 'RUN':
			self.device.write('INIT:BLUetooth:MEAS:MEValuation')
			loginfo('The TX measurement enters the "RUN" state')
		elif state == 1 or state == 'RDY':
			self.device.write('STOP:BLUetooth:MEAS:MEValuation')
			loginfo('The TX measurement enters the "RDY" state')
		else:
			self.device.write('ABORt:BLUetooth:MEAS:MEValuation')
			loginfo('The TX measurement enters the "OFF" state')

	@log()
	def get_tx_measure_states(self):
		'''
		Return values:
		<MeasState>		OFF | RUN | RDY
						OFF: Measurement switched off, no resources allocated, no results available (when entered after ABORt...)
						RUN: Measurement running (after INITiate..., READ...), synchronization pending or adjusted, resources active or queued
						RDY: Measurement has been terminated, valid results are available
		'''
		res = self.device.ask('FETCh:BLUetooth:MEAS:MEValuation:STATe?')
		res = res.replace('\n', '').replace('\r', '')
		return res

	@log()
	def tx_measure_display(self, case='OVER'):
		'''
		case:	OVERview | PVTime | DEVM | PDIFference | IQABs | IQDiff | IQERr | FDEViation | SOBW | SACP | SGACp | MODulation | POWer | FRANge | PENCoding
				OVERview: "Overview" (BR, EDR, LE)
				PVTime: "Power vs Tim"e (BR, EDR, LE)
				DEVM: "DEVM" (EDR)
				PDIFference: "Phase Differen"ce (EDR)
				IQABs: "IQ Constellation Absolute" (EDR)
				IQDiff: "IQ Constellation Differentia"l (EDR)
				IQERr: "IQ Constellation Error" (EDR)
				FDEViation: "Frequency Deviation" (BR, LE)
				SOBW: "Spectrum 20 dB Bandwidth" (BR)
				SACP: "Spectrum AC"P (BR, LE)
				SGACp: "Spectrum Gated ACP" (EDR)
				MODulation: "Modulation Scalars" (BR, EDR, LE)
				POWer: "Power Scalars" (BR, EDR, LE)
				FRANge: "Frequency Rang"e (BR)
				PENCoding: "Differential Phase Encoding" (EDR)
		'''
		self.device.write('CONFigure:BLUetooth:MEAS:DISPlay %s' % case)

	@log()
	def tx_measure_para(self, tout=5, repetition='SINGleshot', count=20, MOEXception='OFF' ):
		'''
		tout:	Defines a timeout for the measurement.
		repetition:		Specifies the repetition mode of the measurement.
						The repetition mode specifies whether the measurement is stopped after a single shot or repeated continuously.
						SINGleshot | CONTinuous
						SINGleshot: Single-shot measurement
						CONTinuous: Continuous measurement
		count:			Valid when repetition is SINGleshot,The statistic count is equal to the number of measurement intervals per single shot.
		'''
		if repetition not in ('SINGleshot','SING','CONTinuous','CONT'):
			logerror('repetition is wrong,must be SINGleshot|SING|CONTinuous|CONT')
			return False
		self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:TOUT %d' % tout)
		self.wait()
		self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:REPetition %s' % repetition)
		self.wait()
		self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:MOEXception %s' % MOEXception)
		self.wait()
		if repetition == 'SINGleshot':
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:MODulation %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:PENCoding %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:PVTime  %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:SOBW  %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:FRANge %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:SACP %d' % count)
			self.wait()
			self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SCOunt:SGACp  %d' % count)
			self.wait()
			logdebug('repetition is SINGleshot,count is %d' % count)
		else:
			logdebug('repetition is CONTinuous')

	@log()
	def get_power_measure_res(self, rate='LE1M', data_type='AVER', cmd_type='READ'):
		'''
		mode:	BR,EDR,LE1M,LE2M,LRANge
		data_type:	CURR, AVER, MIN, MAX
		cmd_type:	FETCH, READ, CALCulate
		Returns the power results for BR/EDR/LE packets.
		The values described below are returned by FETCh and READ commands. CALCulate commands return limit check results instead, one value for each result listed below.
		The number to the left of each result parameter is provided for easy identification of the parameter position within the result array.
		BR		Return values:
					<1_Reliability>		error code,Reliability Indicator
					<2_Out of Tol>		Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see "Power Limits".
										Range:  0 %  to  100 %
										Default unit:  %

					<3_Nominal Pow>		Average power during the carrier-on state
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
					<4_Peak Pow>		Peak power during the carrier-on state
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
					<5_Leakage Pow>		Average power during the carrier-off state
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
					<6_PacketTiming>	Time between the expected and actual start of the first symbol of the Bluetooth burst
										Range:  -20.00 µs to 20.00 µs
										Default unit:  s
					<7_GFSK_Pow>		Average power within the access code and header portion of the BR burst (first 126 symbols).
										Range:  -128 dBm to 30 dBm
										Default unit:  dBm
		EDR		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see "Power Limits".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Nominal Pow>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<4_GFSK Pow>
					Average power in the GFSK portion of the burst
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<5_DPSK Pow>
					Average power in the DPSK portion of the burst
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<6_DPSK - GFSK>
					Difference between DPSK and GFSK power
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<7_Guard Period>
					Length of the guard band between the packet header and the synchronization sequence
					Range:  0 µs  to  9.99 µs
					Default unit:  s
					<8_PacketTiming>
					Time between the expected and actual start of the first symbol of the Bluetooth burst
					Range:  -20.00 µs to 20.00 µs
					Default unit:  s
					<9_PeakPower>
					Maximum power within the whole burst. The result is only available via remote command.
					Range:  -99.99 dBm  to  99.99 dBm
					Default unit:  dBm
		LE1M		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_OutofTol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​LENergy[:​LE1M]:​PVTime.
					Range:  0 %  to  100 %
					Default unit:  %
					<3_AveragePower>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<4_PeakPower>
					Peak power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<5_LeakagePower>
					Average power during the carrier-off state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<6_PeakMinAvgPow>
					Peak power minus average power
					Range:  0 dB to 158 dB
		LE2M/LRANge	Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_BurstOutOfTol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​PVTime) exceeding the specified limits, see CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​LENergy:​LE2M:​PVTime and CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​LENergy:​LRANge:​PVTime.
					Range:  0 %  to  100 %
					Default unit:  %
					<3_NominalPower>
					Average power during the carrier-on state
					Range:  -128 dBm to 30 dBm
					Default unit:  dBm
					<4_PeakPower>
					Peak power during the carrier-on state
					Range:  -128 dBm to 30 dBm
					Default unit:  dBm
					<5_LeakagePower>
					Average power during the carrier-off state
					Range:  -128 dBm to 30 dBm
					Default unit:  dBm
					<6_PeakMinAvgPow>
					Peak power minus average power
					Range:  0 dB to 158 dB
					Default unit:  dB
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		if data_type not in self.data_type_list:
			logerror('data_type is wrong,must be in (CURR, AVER, MIN, MAX)')
			return False
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'BR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PVTime:BRATe:%s?' % (cmd_type, data_type))
			elif self.mode == 'EDR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PVTime:EDRATe:%s?' % (cmd_type, data_type))
			else:
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PVTime:LENergy:%s:%s?' % (cmd_type, rate, data_type))
			res = res.replace('\n','').split(',')
			for i in range(len(res)):
				if res[i] == 'NCAP':
					res[i] = '-999'
			if eval(res[0]) == 0:
				logdebug('get pvt measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(1)
		return res
				# return self.error_code(eval(res[0]))
	@log()
	def get_modulation_measure_res(self, rate='LE1M', data_type='AVER', cmd_type='READ'):
		'''
		mode:	BR,EDR,LE1M,LE2M,LRANge
		data_type:	CURR, AVER, MIN, MAX
		cmd_type:	FETCH, READ, CALCulate
		BR		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "BR".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Δf2 99.9%>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<4_Freq. Accuracy>
					Range:  -250.0 kHz  to  +250.0 kHz
					Default unit:  Hz
					<5_Freq. Drift>
					Range:  -250.0 kHz  to  +250.0 kHz
					Default unit:  Hz
					<6_Max. Drift Rate>
					Range:  -0.99999E+6 Hz/50 μs  to  0.99999E+6 Hz/50 μs
					Default unit:  Hz/50 μs
					<7_Δf1 avg>
					Frequency deviation results
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<8_Δf1 min>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<9_Δf1 max>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<10_Δf2 avg>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<11_Δf2 min>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<12_Δf2 max>
					Range:  0 Hz  to  +250.0 kHz
					Default unit:  Hz
					<13_Nominal Pow>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
					<14_ModRatio>
					Modulation ratio Δf2 avg / Δf1 avg
					Range:  0 to >1
		EDR		Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "EDR".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_ωi>
					Initial center frequency error
					Range:  -240.0 kHz  to  +240.0 kHz
					Default unit:  Hz
					<4_ω0 + ωi>
					Overall uncompensated frequency error
					Range:  -240.0 kHz  to  +240.0 kHz
					Default unit:  Hz
					<5_ω0max>
					Maximum compensated frequency error
					Range:  -240.0 kHz  to  +240.0 kHz
					Default unit:  Hz
					<6_RMS DEVM>
					Differential EVM results
					Range:  0.000  to  1.000
					Default unit:  1
					<7_Peak DEVM>
					Range:  0.000  to  1.000
					Default unit:  1
					<8_P99 DEVM>
					Range:  0.000  to  1.000
					Default unit:  1
					<9_Nominal Pow>
					Average power during the carrier-on state
					Range:  -128.0 dBm  to  +30.0 dBm
					Default unit:  dBm
		LE1M/LE2M	Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "Limits (Modulation LE)".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Δf2 99.9%>
					Range:  0 Hz  to  250.0 kHz
					Default unit:  Hz
					<4_Freq. Accuracy>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<5_Freq. Drift>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<6_Max. Drift Rate>
					Range:  -0.99999E+6 Hz/50 μs  to  0.99999E+6 Hz/50 μs
					Default unit:  Hz/50 μs
					<7_Δf1 avg>
					Frequency deviation results
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<8_Δf1 min>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<9_Δf1 max>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<10_Δf2 avg>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<11_Δf2 min>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<12_Δf2 max>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<13_Nominal Pow>
					Range:  -99.99 dBm  to  99.99 dBm
					Default unit:  dBm
					<14_ModRatio>
					Modulation ratio Δf2 avg / Δf1 avg
					Range:  0 to >1
					<15_Freq. Offset>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<16_Initial Freq. Drift>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
		LRANge	Return values:
					<1_Reliability>
					error code,Reliability Indicator
					<2_Out of Tol>
					Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​MODulation) exceeding the specified limits, see "Limits (Modulation LE)".
					Range:  0 %  to  100 %
					Default unit:  %
					<3_Δf1 99.9%>
					Range:  0 Hz  to  250.0 kHz
					Default unit:  Hz
					<4_Freq. Accuracy>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<5_Freq. Drift>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<6_Max. Drift Rate>
					Range:  -0.99999E+6 Hz/50 μs  to  0.99999E+6 Hz/50 μs
					Default unit:  Hz/50 μs
					<7_Δf1 avg>
					Frequency deviation results
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<8_Δf1 min>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<9_Δf1 max>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
					<10_Nominal Pow>
					Range:  -99.99 dBm  to  99.99 dBm
					Default unit:  dBm
					<11_Freq. Offset>
					Range:  -0.99999E+6 Hz  to  0.99999E+6 Hz
					Default unit:  Hz
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		if data_type not in self.data_type_list:
			logerror('data_type is wrong,must be in (CURR, AVER, MIN, MAX)')
			return False
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'BR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:MODulation:BRATe:%s?' % (cmd_type, data_type))
			elif self.mode == 'EDR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:MODulation:EDRATe:%s?' % (cmd_type, data_type))
			else:
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:MODulation:LENergy:%s:%s?' % (cmd_type, rate, data_type))
			while 1:
				state = self.get_tx_measure_states()
				logdebug('measure state {}'.format(state))
				if state == 'RDY':
					break
			res = res.replace('\n','').split(',')
			for i in range(len(res)):
				if res[i] == 'NCAP':
					res[i] = '-999'
			if eval(res[0]) == 0:
				logdebug('get mod measure result success')
				break
			elif k == 4:
				# return self.error_code(eval(res[0]))
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(1)
		return res
				# return False
				# return res
	@log()
	def acp_meas_settings(self, opt='CH21'):
		'''
		Selects the measured ACP channel range.
		BR/EDR:
			The ACP can be measured over the expected transmit channel +/- 10 channels (21 channels in total) or over the entire Bluetooth regulatory range (79 channels).
			CH79 | CH21
			Measure 79 or 21 channels
		LE:
			Can be selected to cover either the full LE frequency band (forty 2 MHz channels) or only the adjacency of the current LE channel (ten 2 MHz channels).
			Although LE channels are 2 MHz wide, the channel width in ACP measurements is always 1 MHz ("half-channel").
			CH40 | CH10
			CH10: Covers the current and its 10 adjacent 2 MHz LE channels (5 to the left, 5 to the right). The R&S CMW measures the 1 MHz channels centered at fTX – 10 MHz, ..., fTX + 10 MHz.
			CH40: Covers all 40 LE channels. The R&S CMW measures the 81 half-channels centered at 2401 MHz, 2402 MHz, ..., 2481 MHz.
		'''

		if self.mode in ('BR', 'EDR'):
			if opt not in ('CH79', 'CH21'):
				logerror('opt is wrong,must be CH21 or CH79 for BR/EDR')
				return False
			else:
				self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SACP:BRATe:MEASurement:MODE %s' % opt)
				self.wait()
				self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SACP:EDRATe:MEASurement:MODE %s' % opt)
				self.wait()
		elif self.mode in ('LE1M', 'LE2M'):
			if opt not in ('CH40', 'CH10'):
				logerror('opt is wrong,must be CH40 or CH10 for LE')
				return False
			else:
				self.device.write('CONFigure:BLUetooth:MEAS:MEValuation:SACP:LENergy:%s:MEASurement:MODE %s' % (self.mode, opt))
				self.wait()
				logdebug('acp measure set success')
		else:
			logerror('mode is wrong')
			return False

	@log()
	def get_acp_res(self, cmd_type='READ'):
		'''
		Returns the "Spectrum ACP" results
		The number to the left of each result parameter is provided for easy identification of the parameter position within the result array.
		BR	Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_Out of Tol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​SACP) exceeding the specified limits, see "Spectrum Limits".
			Range:  0 %  to  100 %
			Default unit:  %
			<3_Nominal Pow>
			Average power during the carrier-on state
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<4_No of Except>
			Number of exceptions (channels ±3, ±4 ... with an ACP above the "Exception PTx" threshold )
			Range:  0  to  74
			<5_ACP_1>
			...
			<83_ACP_79>
			79 ACP results
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm

		'''
		cmd_tpye_list = ['FETCH', 'READ']
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'EDR':
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:TRACe:SGACp:MAXimum?' % cmd_type)
			else:
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:TRACe:SACP:MAXimum?' % cmd_type)
			time.sleep(2)
			res = res.replace('\n','').split(',')
			for i in range(len(res)):
				if res[i] == 'NCAP':
					res[i] = '-999'
			if eval(res[0]) == 0:
				logdebug('get acp measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res[0]))
				logerror('{} ,try agian {}'.format(err,k))
			# time.sleep(1)
		return res
				# return self.error_code(eval(res[0]))
	@log()
	def get_acp_res_edr(self, cmd_type='READ'):
		'''
		Returns the "Spectrum ACP" results
		The number to the left of each result parameter is provided for easy identification of the parameter position within the result array.
		BR	Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_Out of Tol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​SACP) exceeding the specified limits, see "Spectrum Limits".
			Range:  0 %  to  100 %
			Default unit:  %
			<3_Nominal Pow>
			Average power during the carrier-on state
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<4_No of Except>
			Number of exceptions (channels ±3, ±4 ... with an ACP above the "Exception PTx" threshold )
			Range:  0  to  74
			<5_ACP_1>
			...
			<83_ACP_79>
			79 ACP results
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm

		'''
		cmd_tpye_list = ['FETCH', 'READ']
		if cmd_type not in cmd_tpye_list:
			logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
			return False
		for k in range(5):
			if self.mode == 'EDR':
				res1 = self.device.ask('%s:BLUetooth:MEAS:MEValuation:SGACp:EDRate?' % cmd_type)
				res2 = self.device.ask('%s:BLUetooth:MEAS:MEValuation:TRACe:SGACp:MAXimum?' % cmd_type)
			else:
				logerror('mode is wrong, must be edr')
			res1 = res1.replace('\n','').split(',')
			res2 = res2.replace('\n','').split(',')
			for i in range(len(res1)):
				if res1[i] == 'NCAP':
					res1[i] = '-999'
			for i in range(len(res2)):
				if res2[i] == 'NCAP':
					res2[i] = '-999'
			if eval(res1[0]) == 0 and eval(res2[0]) == 0:
				logdebug('get acp measure result success')
				break
			elif k == 4:
				err = self.error_code(eval(res1[0]))
				logerror('{} ,try agian {}'.format(err,k))
			time.sleep(1)
		return [res1, res2]
				# return [self.error_code(eval(res1[0])), self.error_code(eval(res2[0]))]

	@log()
	def get_diff_phase_encoding_res(self, cmd_type='READ'):
		'''
		only for EDR
		Returns the "Differential Phase Encoding" results for EDR packets (single values).
		Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_NominalPower>
			Average power during the carrier-on state
			Range:  -128 dBm to 30 dBm
			Default unit:  dBm
			<3_BitErrorRate>
			Number of bit errors in the received burst, as a percentage of the total number of bits received
			Range:  0 %  to  100 %
			Default unit:  %
			<4_Packets0Errors>
			Number of bit error free packets received, as a percentage of all the bursts received
			Range:  0 %  to  100 %
			Default unit:  %
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		for k in range(5):
			if self.mode == 'EDR':
				if cmd_type not in cmd_tpye_list:
					logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
					return False
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:PENCoding:EDRATe:CURRent?' % cmd_type)
				res = res.replace('\n','').split(',')
				for i in range(len(res)):
					if res[i] == 'NCAP':
						res[i] = '-999'
				if eval(res[0]) == 0:
					logdebug('get diff_phase_encoding measure result success')
					break
				elif k == 4:
					err = self.error_code(eval(res[0]))
					logerror('{} ,try agian {}'.format(err,k))
				time.sleep(1)
					# return self.error_code(eval(res[0]))
			else:
				logerror('mode is wrong,must be EDR')
				break
		return res

	@log()
	def get_obw_res(self, cmd_type='READ'):
		'''
		for only BR
		Returns the "Spectrum 20 dB Bandwidth" results.
		Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_Out of Tol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​SOBW) exceeding the specified limits, see "Spectrum Limits".
			Range:  0 %  to  100 %
			Default unit:  %
			<3_Nominal Pow>
			Average power during the carrier-on state
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<4_Peak Emission>
			Peak power in the measured spectral range
			Range:  -128.0 dBm  to  +30.0 dBm
			Default unit:  dBm
			<5_fL>
			Lower frequency where the transmit power drops 20 dB below the peak emission
			Range:  -1.000 MHz  to  +1.000 MHz
			Default unit:  Hz
			<6_fH>
			Higher frequency where the transmit power drops 20 dB below the peak emission
			Range:  -1.000 MHz  to  +1.000 MHz
			Default unit:  Hz
			<7_fH - fL>
			20 dB bandwidth; difference between fH – fL.
			Range:  0.000 MHz  to  +2.000 MHz
			Default unit:  Hz
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		for k in range(5):
			if self.mode == 'BR':
				if cmd_type not in cmd_tpye_list:
					logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
					return False
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:SOBW:BRATe:MAXimum?' % cmd_type)
				res = res.replace('\n','').split(',')
				for i in range(len(res)):
					if res[i] == 'NCAP':
						res[i] = '-999'
				if eval(res[0]) == 0:
					logdebug('get obw measure result success')
					break
				elif k == 4:
					err = self.error_code(eval(res[0]))
					logerror('{} ,try agian {}'.format(err,k))
				time.sleep(1)
					# return self.error_code(eval(res[0]))
			else:
				logerror('mode is wrong,must be BR')
				break
		return res

	@log()
	def get_frange_res(self, cmd_type='READ'):
		'''
		Returns the "Frequency Range" results for BR.
		Return values:
			<1_Reliability>
			error code,Reliability Indicator
			<2_BurstOutOfTol>
			Out of tolerance result, i.e. percentage of measurement intervals of the statistic count (CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​SCOunt:​FRANge) exceeding the specified limits, see CONFigure:​BLUetooth:​MEAS<i>:​MEValuation:​LIMit:​FRANge.
			Additional ON/OFF enables/disables the out of tolerance evaluation.
			Range:  0 %  to  100 %
			<3_NominalPower>
			Average power during the carrier-on state
			Range:  -128 dBm to 30 dBm
			Default unit:  dBm
			<4_fL>
			Lowest frequency at which spectral power density drops below specified threshold
			Range:  -1 MHz to +1 MHz
			Default unit:  Hz
			<5_fH>
			Highest frequency at which spectral power density drops below specified threshold
			Range:  -1 MHz to +1 MHz
			Default unit:  Hz
		'''
		cmd_tpye_list = ['FETCH', 'READ', 'CALCulate']
		for k in range(5):
			if self.mode == 'BR':
				if cmd_type not in cmd_tpye_list:
					logerror('cmd_type is wrong,must be in (FETCH, READ, CALCulate)')
					return False
				res = self.device.ask('%s:BLUetooth:MEAS:MEValuation:FRANge:BRATe:CURRent?' % cmd_type)
				res = res.replace('\n','').split(',')
				for i in range(len(res)):
					if res[i] == 'NCAP':
						res[i] = '-999'
				if eval(res[0]) == 0:
					logdebug('get freq range measure result success')
					break
				elif k == 4:
					err = self.error_code(eval(res[0]))
					logerror('{} ,try agian {}'.format(err,k))
				time.sleep(1)
					# return self.error_code(eval(res[0]))
			else:
				logerror('mode is wrong,must be BR')
				break
		return res
