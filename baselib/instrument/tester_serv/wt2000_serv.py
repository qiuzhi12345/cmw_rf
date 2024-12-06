#Filename: usb.py
import os
import sys
import platform
from baselib.loglib.log_lib import *

sys.path.append('../../lib/wt2000_ctrl');
sys.path.append('./loglib');
sys.path.append('./baselib/test_channel');

try:
  import wt2000_ctrl
  loginfo('Load IQview Control Module OK!')
except:
  logwarn("import wt2000_ctrl fail")
  if platform.platform().find("Linux") != -1:
    logwarn("platform is not support IQview(%s)"%(platform.platform()))
  else:
    logwarn("make sure software is installed.")
from log_lib import *
from server import *
import time
#--------------------------------------------
# In Shell, some commands already registered:
# wt2000_ctrl.open(), return handler
#---------------------------------------------
wt2000_port_dic={'off':1,'left':2,'right':3};
iqmod_dic={'11b':0,'11g':1,'11a':2,'11n_20':3,'11n_40':4};
global maxsiglevel;

def init():
    result=1; #0:ok,-1:err,1:except
    try:
       result=wt2000_ctrl.WT_Initilaze();
       if result==0:
          reply_info='WT200 Library load ok!';
       else:
	  reply_info='WT2000 Library fail to load!';
    except:
       reply_info='Exception occur when initialize WT2000 Library!';
    return ('%d,%s'%(result,reply_info));

def term():
    result=1;
    try:
       result=wt2000_ctrl.WT_Terminate();
       if result==0:
          reply_info='Disconnect with WT2000 and unload Library ok!';
       else:
	  reply_info='Fail to disconnect with WT2000 and unload library!';
    except:
       reply_info='Exception occur when disconnect with WT2000!';
    return ('%d,%s'%(result,reply_info));

def open():
    result=1;
    ipaddr="192.168.100.251";
    try:
       result=wt2000_ctrl.WT_Connect(ipaddr);
       if result==0:
          reply_info='Connect with WT2000 ok!';
       else:
	  reply_info='Fail to connect with WT2000!';
    except:
       reply_info='Exception occur when connect with WT2000!';
    return ('%d,%s'%(result,reply_info));

def close():
    result=1;
    try:
       result=wt2000_ctrl.WT_DisConnect();
       if result==0:
          reply_info='Disconnect with WT2000!';
       else:
	  reply_info='Fail to disconnect with WT2000!';
    except:
       reply_info='Exception occur when disconnect with WT2000!';
    return  ('%d,%s'%(result,reply_info));

def reset():
    result=1;
    ipaddr="192.168.100.251";
    try:
       #result=wt2000_ctrl.LP_Reset();
       #result=wt2000_ctrl.WT_DisConnect();
       result=wt2000_ctrl.WT_Initilaze();
       result = wt2000_ctrl.WT_Connect(ipaddr);
       #result = 0;
       if result==0:
          reply_info='Reset WT2000 Ok!';
       else:
	  reply_info='Fail to Reset WT2000!';
    except:
       reply_info='Exception occur when reset WT2000!';
    return ('%d,%s'%(result,reply_info));

def setvsg(freqMhz,pwrdBm):
    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
       reply_info="freq value out of range!";
       return ('%d,%s'%(-1,reply_info));

    if pwrdBm>10:
       loginfo("power value too great out of range(10 -98)!");
       pwrdBm=10;
    if pwrdBm<-98:
       loginfo("power value too great out of range(10 -98)!");
       pwrdBm=-98;

    result=1;
    try:
       result=wt2000_ctrl.WT_SetTxGen(freqMhz*1e6,pwrdBm,wt2000_port_dic['right']);
       if result==0:
          reply_info='VSG configure ok!';
       else:
	  reply_info='Fail to configure VSG!';
    except:
       reply_info='Exception occur when configure VSG!';
    return ('%d,%s'%(result,reply_info));

def setvsg_left(freqMhz,pwrdBm):
    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
       reply_info="freq value out of range!";
       return ('%d,%s'%(-1,reply_info));

    if pwrdBm>10:
       loginfo("power value too great out of range(10 -98)!");
       pwrdBm=10;
    if pwrdBm<-98:
       loginfo("power value too great out of range(10 -98)!");
       pwrdBm=-98;

    result=1;
    #try:
    if True:
       logdebug("setvsg_left");
       result=wt2000_ctrl.WT_SetTxGen(freqMhz*1e6,pwrdBm,wt2000_port_dic['left']);
       logdebug("setvsg_left 222");
       if result==0:
          reply_info='VSG configure ok!';
       else:
        reply_info='Fail to configure VSG!';
    #except:
    #   reply_info='Exception occur when configure VSG!';
    #   logdebug(reply_info)
    return ('%d,%s'%(result,reply_info));

def ldmodfile(filename):
    '''filename start dir is at ./baselib/instrument/iqv/iqview_ctrl/mod/'''
    result=1;
    dirpath='..\\..\\lib\\wt2000_ctrl\\wave\\120M\\'
    try:
       result=wt2000_ctrl.WT_SetTxModulation(dirpath+filename);
       if result==0:
          reply_info='Load Waveform file ok!';
       else:
	  reply_info='Fail to load waveform file!';
    except:
       reply_info='Exception occur when load waveform file!';
    return ('%d,%s'%(result,reply_info));

def setrate(rate):
    rate_file_dic={
		    #'1m':'performance/wave_1m_1024B_idle_30us.mod',
		    #'2ms':'performance/wave_2ms_1024B_idle_30us.mod',
		    #'2ml':'performance/wave_2ml_1024B_idle_30us.mod',
		    #'5.5ms':'performance/wave_5p5ms_1024B_idle_30us.mod',
		    #'5.5ml':'performance/wave_5p5ml_1024B_idle_30us.mod',
		    #'11ms':'performance/wave_11ms_1024B_idle_30us.mod',
		    #'11ml':'performance/wave_11ml_1024B_idle_30us.mod',
                    '1m':'1 Mbps(DSSS).csv',
		    '2m':'2 Mbps(DSSS).csv',
                    '2ms':'2 Mbps(DSSS).csv',
		    '2ml':'2 Mbps(DSSS).csv',
		    '5.5m':'5.5 Mbps(DSSS).csv',
                    '5.5ms':'5.5 Mbps(DSSS).csv',
		    '5.5ml':'5.5 Mbps(DSSS).csv',
		    '11m':'11 Mbps(DSSS).csv',
                    '11ms':'11 Mbps(DSSS).csv',
		    '11ml':'11 Mbps(DSSS).csv',
		    '6m':'6 Mbps(OFDM).csv',
		    '9m':'9 Mbps(OFDM).csv',
		    '12m':'12 Mbps(OFDM).csv',
		    '18m':'18 Mbps(OFDM).csv',
		    '24m':'24 Mbps(OFDM).csv',
		    '36m':'36 Mbps(OFDM).csv',
		    '48m':'48 Mbps(OFDM).csv',
		    '54m':'54 Mbps(OFDM).csv',
            #'54m':'performance/54 Mbps(OFDM).bwv',
                    #'6m':'performance/wave_6m_1024B_idle_30us.mod',
		    #'9m':'performance/wave_9m_1024B_idle_30us.mod',
		    #'12m':'performance/wave_12m_1024B_idle_30us.mod',
		    #'18m':'performance/wave_18m_1024B_idle_30us.mod',
		    #'24m':'performance/wave_24m_1024B_idle_30us.mod',
		    #'36m':'performance/wave_36m_1024B_idle_30us.mod',
		    #'48m':'performance/wave_48m_1024B_idle_30us.mod',
                    #'54m':'performance/wave_54m_1024B_idle_30us.mod',
                    'mcs0':'HT20-MCS0.csv',
		    'mcs1':'HT20-MCS1.csv',
		    'mcs2':'HT20-MCS2.csv',
		    'mcs3':'HT20-MCS3.csv',
		    'mcs4':'HT20-MCS4.csv',
		    'mcs5':'HT20-MCS5.csv',
		    'mcs6':'HT20-MCS6.csv',
		    'mcs7':'HT20-MCS7.csv',
                    #'mcs0':'performance/test/mcs0_1024byte_40us.mod',
                    #'mcs1':'performance/test/mcs1_1024byte_40us.mod',
		    #'mcs2':'performance/test/mcs2_1024byte_40us.mod',
		    #'mcs3':'performance/test/mcs3_1024byte_40us.mod',
                    #'mcs4':'performance/test/mcs4_1024byte_40us.mod',
		    #'mcs5':'performance/test/mcs5_1024byte_40us.mod',
                    #'mcs6':'performance/test/mcs6_1024byte_40us.mod',
		    #'mcs7':'performance/test/mcs7_1024byte_40us.mod',
                    'mcs0r':'HT20-MCS0.csv',
		    'mcs1r':'HT20-MCS1.csv',
		    'mcs2r':'HT20-MCS2.csv',
		    'mcs3r':'HT20-MCS3.csv',
		    'mcs4r':'HT20-MCS4.csv',
		    'mcs5r':'HT20-MCS5.csv',
		    'mcs6r':'HT20-MCS6.csv',
		    'mcs7r':'HT20-MCS7.csv',
                    'test':'HT20-MCS0.csv'
                    };
    if rate in rate_file_dic:
       return ldmodfile(rate_file_dic[rate]);
    else:
       rate_file = 'performance/with_noise/'+rate+'.mod';
       print(rate_file);
       return ldmodfile(rate_file);
       #return '-1, rate is invalid';

def txfrmcnt(framecnt):
    '''framecnt: 0 means continuous run, more than 0 means stop when framecnt frame tx over'''
    result=1;
    try:
       result=wt2000_ctrl.WT_SetTxCount(framecnt);
       if result==0:
	  if framecnt!=0:
	     txstate=wt2000_ctrl.WT_TxDone();
	     while 0!=txstate:
                txstate=wt2000_ctrl.WT_TxDone();
	        time.sleep(1);
             reply_info='WT2000 tx %d frame ok!'%framecnt;
          else:
	     reply_info='WT2000 continuous tx ok!';
       else:
	  reply_info='WT2000 fail to tx %d frme!'%framecnt;
    except:
       reply_info='Exception occur when IQiew tx %d waveform,state:%d!'%(framecnt,txstate);
    return ('%d,%s'%(result,reply_info));

def txenable(enabled):
    '''enabled: 0 switch off, 1 switch on'''
    rf_switch_dic={0:'switch off', 1:'switch on'};
    result=1;
    try:
       logdebug("txenable:%d"%enabled);
       #result=wt2000_ctrl.WT_StartTx(enabled);
       result=0;
       if result==0:
          reply_info='WT2000 tx %s ok!'%rf_switch_dic[enabled];
       else:
	  reply_info='WT2000 fail to tx %s!'%rf_switch_dic[enabled];
    except:
       reply_info='Exception occur when WT2000 tx %s!'%rf_switch_dic[enabled];
    return ('%d,%s'%(result,reply_info));

def txcw(freqMhz,pwrdBm):
    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
       reply_info="freq value out of range!";
       return ('%d,%s'%(-1,reply_info));

    if pwrdBm>10:
       loginfo("power value too great out of range(10 -98)!");
       pwrdBm=10;
    if pwrdBm<-98:
       loginfo("power value too great out of range(10 -98)!");
       pwrdBm=-98;

    result=1;
    try:
       #result=wt2000_ctrl.LP_SetVsgCw(freqMhz*1e6,0,pwrdBm,wt2000_port_dic['right']);
       result=0;
       if result==0:
          reply_info='WT2000 tx sine wave ok!';
       else:
	  reply_info='WT2000 fail to tx sine wave!';
    except:
       reply_info='Exception occur when WT2000 tx sine wave!';
    return ('%d,%s'%(result,reply_info));

def setvsa(freqMhz,rxmaxpwr,exAttenDb):
    '''rxmaxpwr:expected signal peak power(-60~30dBm), if less than -98, means to use agc'''
    global maxsiglevel;
    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
       reply_info="freq value out of range!";
       return ('%d,%s'%(-1,reply_info));

    if rxmaxpwr <-60:
       loginfo("use agc mode to rx!");
    elif rxmaxpwr>30:
       reply_info="power value out of range(10 -98)!";
       return ('%d,%s'%(-1,reply_info));

    result=1;
    try:
       #AGC enable when rxmaxpwr set less than -98
       if rxmaxpwr <-60:
          result=wt2000_ctrl.WT_SetRx(freqMhz*1e6,0,wt2000_port_dic['left'],exAttenDb,-10,1e-6);
	  time.sleep(0.1);
	  if result==0:
             #maxsiglevel=wt2000_ctrl.LP_Agc();
             maxsiglevel!=-100
	     if maxsiglevel!=-100:
	        loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
	     else:
                loginfo("fail to enable Agc!");
		result=-1;
       else:
          result=wt2000_ctrl.WT_SetRx(freqMhz*1e6,rxmaxpwr,wt2000_port_dic['left'],exAttenDb,-25,1e-6);
	  maxsiglevel=rxmaxpwr;

       if result==0:
	  reply_info='real rxpwr:%f'%maxsiglevel;
       else:
	  reply_info='Fail to configure VSA!';
    except:
       reply_info='Exception occur when configure VSA!';
    return ('%d,%s'%(result,reply_info));

def setvsa_right(freqMhz,rxmaxpwr,exAttenDb):
    '''rxmaxpwr:expected signal peak power(-60~30dBm), if less than -98, means to use agc'''
    global maxsiglevel;
    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
       reply_info="freq value out of range!";
       return ('%d,%s'%(-1,reply_info));

    if rxmaxpwr <-60:
       loginfo("use agc mode to rx!");
    elif rxmaxpwr>30:
       reply_info="power value out of range(10 -98)!";
       return ('%d,%s'%(-1,reply_info));

    result=1;
    try:
       #AGC enable when rxmaxpwr set less than -98
       if rxmaxpwr <-60:
          result=wt2000_ctrl.WT_SetRx(freqMhz*1e6,0,wt2000_port_dic['right'],exAttenDb,-10,1e-6);
	  time.sleep(0.1);
	  if result==0:
             #maxsiglevel=wt2000_ctrl.LP_Agc();
             maxsiglevel=-100
	     if maxsiglevel!=-100:
	        loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
	     else:
                loginfo("fail to enable Agc!");
		result=-1;
       else:
          result=wt2000_ctrl.WT_SetRx(freqMhz*1e6,rxmaxpwr,wt2000_port_dic['right'],exAttenDb,-25,1e-6);
	  maxsiglevel=rxmaxpwr;

       if result==0:
	  reply_info='real rxpwr:%f'%maxsiglevel;
       else:
	  reply_info='Fail to configure VSA!';
    except:
       reply_info='Exception occur when configure VSA!';
    return ('%d,%s'%(result,reply_info));

def capture(smplTm_microSecs=1000,isht40Mode=0):
    '''isht40Mode:0 normal signal, 1:40M signal for 11n'''
    trig_type_dic={'auto':-6, 'free':1, 'ext':2, 'if':6, 'ext_n':7, 'ext2':8, 'ext2_n':9};

    if smplTm_microSecs<=0 or smplTm_microSecs>12.5e3:
       reply_info="sample time length is error!";
       return ('%d,%s'%(-1,reply_info));

    result=1;
    try:
       result=wt2000_ctrl.WT_DataCapture(smplTm_microSecs*1e6,trig_type_dic['if'],80e6,isht40Mode);
       if result==0:
          reply_info='WT2000 capture data ok!';
       else:
	  reply_info='WT2000 fail to capture data!';
    except:
       reply_info='Exception occur when WT2000 capture data!';
    return ('%d,%s'%(result,reply_info));

def savesigfile(sigfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/wt2000_ctrl/capture/sig'''

    result=1;
    dirpath='./baselib/wt2000_ctrl/capture/sig/'
    try:
       result=wt2000_ctrl.WT_SaveVsaSignalFile(dirpath+sigfilename);
       if result==0:
          reply_info='Save captured data as %s ok!'%(dirpath+sigfilename);
       else:
	  reply_info='Fail to save capture data as signal file!';
    except:
       reply_info='Exception occur when save capture data as signal file!';
    return ('%d,%s'%(result,reply_info));

def savemodfile(modfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/wt2000_ctrl/capture/mod'''

    result=1;
    dirpath='./baselib/wt2000_ctrl/capture/mod/'
    try:
       result=wt2000_ctrl.WT_SaveVsaGeneratorFile(dirpath+modfilename);
       if result==0:
          reply_info='Save captured data as %s ok!'%(dirpath+modfilename);
       else:
	  reply_info='Fail to save capture data as mod file!';
    except:
       reply_info='Exception occur when save capture data as mod file!';
    return ('%d,%s'%(result,reply_info));

def set11agrxmethod(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track):
    result=1;
    try:
       result=wt2000_ctrl.WT_Analyze80211ag(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track);
       if result==0:
          reply_info='Set 11ag rx analyze parameters ok!';
       else:
          reply_info='Set 11ag rx analyze parameters FAIL!';#'%s'%(wt2000_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11ag rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11brxmethod(eq_taps, DCremove11b_flag, method_11b):
    result=1
    if eq_taps > 1:
        eq_taps = 2;
    try:
        result=wt2000_ctrl.WT_Analyze80211b(eq_taps,DCremove11b_flag,method_11b);
        if result==0:
            reply_info='Set 11b rx analyze parameters ok!';
        else:
	       reply_info='Set 11b rx analyze parameters FAIL';#'%s'%(wt2000_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11b rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11nrxmethod(rxtype='EWC',mode='nxn',enablePhaseCorr=1,enableSymTimingCorr=1,enableAmplitudeTracking=0,
		decodePSDU=1,enableFullPacketChannelEst=0,packetFormat=1,frequencyCorr=2):
    result=1;
    try:
       result=wt2000_ctrl.WT_Analyze80211n(rxtype,mode,enablePhaseCorr,enableSymTimingCorr,enableAmplitudeTracking,
            decodePSDU,enableFullPacketChannelEst,packetFormat,frequencyCorr);
       if result==0:
          reply_info='Set 11n rx analyze parameters ok!';
       else:
	  reply_info='Set 11n rx analyze parameters FAIL!';#'%s'%(wt2000_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11n rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

WT_ANA_PARM_FRAME_COUNT=0				#???
WT_ANA_PARM_FRAME_POW=1					#Power,dBm
WT_ANA_PARM_POW_ALL=2					#???Power ALL,dBm
WT_ANA_PARM_CARRIER_FREQ_ERROR=3			#????,ppm
WT_ANA_PARM_CARRIER_FREQ_ERROR_HZ=4		#????,Hz
WT_ANA_PARM_SYMBOL_CLOCK_ERROR=5			#????,ppm
WT_ANA_PARM_CARRIER_LEAKAGE=6			#????,dB
WT_ANA_PARM_OCCUPIED_BANDWIDTH=7			#(99%)OBW,MHz

WT_ANA_PARM_SPECTRUM_MASK_ERROR=8		#????????%
WT_ANA_PARM_EVM=9						#EVM,dB
WT_ANA_PARM_POW_RAMP_ON_TIME=10			#????,us
WT_ANA_PARM_POW_RAMP_OFF_TIME=11			#????,us
WT_ANA_PARM_FRAME_FREQ_ERROR=12			#Frame frequency error,ppm
WT_ANA_PARM_FRAME_FREQ_ERROR_HZ=13		#Frame frequency error,Hz

WT_ANA_PARM_NON=999			#non this params

##WT_ANA_PARM_BT_CARR_FREQ_TOL=14			#BT BR Initial freq error,Hz
##WT_ANA_PARM_BT_CARR_FREQ_DRIFT=15		#BT BR Freq.Drift,Hz(Payload 10101010)
##WT_ANA_PARM_BT_DELTA_F1_VALID=16		#BT BR Delta F1(and WT_ANA_PARM_BT_CARR_FREQ_DRIFT) valid
##WT_ANA_PARM_BT_DELTA_F1_AVG=17			#BT BR Delta F1 avg,Hz(Payload 00001111)
##WT_ANA_PARM_BT_DELTA_F2_VALID=18		#BT BR Delta F2 valid
##WT_ANA_PARM_BT_DELTA_F2_AVG=19			#BT BR Delta F2 avg,Hz(Payload 10101010)
##WT_ANA_PARM_BT_DELTA_F2_MAX=20			#BT BR Delta F2 max,Hz(Payload 10101010)
##
##WT_ANA_PARM_BT_BT_DEVM_VALID=21			#BT EDR DEVM????
##WT_ANA_PARM_BT_BT_DEVM=22				#BT EDR DEVM,%
##WT_ANA_PARM_BT_BT_DEVM_PEAK=23			#BT EDR DEVM Peak,%
##WT_ANA_PARM_BT_BT_POW_DIFF=24			#BT EDR Power Diff,dB
##WT_ANA_PARM_BT_BT_99PCT=25				#BT EDR DEVM ?BT 3M???20%, 2M???30%)???
##WT_ANA_PARM_BT_BT_Omega_I=26			#BT EDR Omega I,Hz
##WT_ANA_PARM_BT_BT_Omega_O=27			#BT EDR Omega O,Hz
##WT_ANA_PARM_BT_BT_Omega_IO=28			#BT EDR Omega IO,Hz


def getmeasdata(iq_mode,meas_type):
    '''meas_type include 11ag,11b,11n all scalar measure result'''
    global maxsiglevel;

    ieee11ag_meas_type_lst=['psduCrcFail','plcpCrcPass','dataRate','numSymbols','numPsduBytes',
		            'evmAll','evmData','evmPilot','codingRate','freqErr','clockErr',
			    'ampErr','ampErrDb','phaseErr','rmsPhaseNoise','rmsPowerNoGap',
			    'rmsPower','pkPower','rmsMaxAvgPower','maskerr','on_time','off_time','maxrxpwr'];

    #not include maxFreqErr
    ieee11b_meas_type_lst=['lockedClock','plcpCrcFail','psduCrcFail','longPreamble','numPsduBytes','bitRateInMHz',
		    'evmPk','bitRate','dataRate','modType','evmAll','evmInPreamble','evmInPsdu','freqErr','clockErr','ampErr','ampErrDb',
		    'phaseErr','rmsPhaseNoise','rmsPowerNoGap','rmsPower','pkPower','rmsMaxAvgPower','loLeakageDb','maskerr','on_time',
		    'off_time','maxrxpwr'];

    #not include:completePacket,htSigFieldCRC,idxAnalyzedSigs,idxDataTones,idxPilotTones,preambleFreqErrorHz
    #legacyLength,legacyRate,htSig2_aggregation,htSig2_stbc,htSig2_shortGI,htSig2_numHTLF,htSig2_soundingPacket,rateInfo_modulation,
    #rateInfo_codingRate,mainPathStreamPowerDb
    ieee11n_meas_type_lst=['evmAvgAll','packetDetection','psduCRC','acquisition','demodulation','dcLeakageDbc',
		    'rxRmsPowerDb','isolationDb','freqErrorHz','symClockErrorPpm','PhaseNoiseDeg_RmsAll','IQImbal_amplDb',
		    'IQImbal_phaseDeg','rateInfo_bandwidthMhz','rateInfo_dataRateMbps','rateInfo_spatialStreams',
		    'analyzedRange','htSig1_htLength','htSig1_mcsIndex','htSig1_bandwidth','htSig2_advancedCoding',
		    'rateInfo_spaceTimeStreams','maxrxpwr'];

    fft_meas_lst=['delta_freq','length','valid'];

    wt2000_meas_val_dict={
     'psduCrcFail': WT_ANA_PARM_NON,
     'plcpCrcPass': WT_ANA_PARM_NON,
     'dataRate': WT_ANA_PARM_NON,
     'numSymbols': WT_ANA_PARM_NON,
     'numPsduBytes': WT_ANA_PARM_NON,
     'evmAll':WT_ANA_PARM_EVM,
     'evmData':WT_ANA_PARM_EVM,
     'evmPilot':WT_ANA_PARM_EVM,
     'codingRate': WT_ANA_PARM_NON,
     'freqErr':WT_ANA_PARM_FRAME_FREQ_ERROR_HZ,
     'clockErr':WT_ANA_PARM_SYMBOL_CLOCK_ERROR,
	 'ampErr': WT_ANA_PARM_NON,
     'ampErrDb': WT_ANA_PARM_NON,
     'phaseErr': WT_ANA_PARM_NON,
     'rmsPhaseNoise': WT_ANA_PARM_NON,
     'rmsPowerNoGap': WT_ANA_PARM_FRAME_POW,
	 'rmsPower': WT_ANA_PARM_POW_ALL,
     'pkPower': WT_ANA_PARM_NON,
     'rmsMaxAvgPower': WT_ANA_PARM_NON,
     'maskerr':WT_ANA_PARM_SPECTRUM_MASK_ERROR,
     'on_time':WT_ANA_PARM_POW_RAMP_ON_TIME,
     'off_time':WT_ANA_PARM_POW_RAMP_OFF_TIME,

     'lockedClock': WT_ANA_PARM_NON,
     'plcpCrcFail': WT_ANA_PARM_NON,
     'longPreamble': WT_ANA_PARM_NON,
     'bitRateInMHz': WT_ANA_PARM_NON,
	 'evmPk': WT_ANA_PARM_NON,
     'bitRate': WT_ANA_PARM_NON,
     'modType': WT_ANA_PARM_NON,
     'evmInPreamble': WT_ANA_PARM_NON,
     'evmInPsdu': WT_ANA_PARM_NON,
     'loLeakageDb': WT_ANA_PARM_NON,

     'evmAvgAll' : WT_ANA_PARM_EVM,
     'packetDetection':WT_ANA_PARM_NON,
     'psduCRC':WT_ANA_PARM_NON,
     'acquisition':WT_ANA_PARM_NON,
     'demodulation':WT_ANA_PARM_NON,
     'dcLeakageDbc':WT_ANA_PARM_CARRIER_LEAKAGE,
     'rxRmsPowerDb':WT_ANA_PARM_FRAME_POW,
     'isolationDb':WT_ANA_PARM_NON,
     'freqErrorHz':WT_ANA_PARM_FRAME_FREQ_ERROR_HZ,
     'symClockErrorPpm':WT_ANA_PARM_SYMBOL_CLOCK_ERROR,
     'PhaseNoiseDeg_RmsAll':WT_ANA_PARM_NON,
     'IQImbal_amplDb':WT_ANA_PARM_NON,
     'IQImbal_phaseDeg':WT_ANA_PARM_NON,
     'rateInfo_bandwidthMhz':WT_ANA_PARM_NON,
     'rateInfo_dataRateMbps':WT_ANA_PARM_NON,
     'rateInfo_spatialStreams':WT_ANA_PARM_NON,
     'analyzedRange':WT_ANA_PARM_NON,
     'htSig1_htLength':WT_ANA_PARM_NON,
     'htSig1_mcsIndex':WT_ANA_PARM_NON,
     'htSig1_bandwidth':WT_ANA_PARM_NON,
     'htSig2_advancedCoding':WT_ANA_PARM_NON,
     'rateInfo_spaceTimeStreams':WT_ANA_PARM_NON,
     'maxrxpwr':WT_ANA_PARM_NON,
     'delta_freq':WT_ANA_PARM_NON,
     'length':WT_ANA_PARM_NON,
     'valid':WT_ANA_PARM_NON
     }

    meas_type_dic={'11b':ieee11b_meas_type_lst,
		    '11a':ieee11ag_meas_type_lst,
		    '11g':ieee11ag_meas_type_lst,
		    '11n_20':ieee11n_meas_type_lst,
		    '11n_40':ieee11n_meas_type_lst,
		    'fft':fft_meas_lst};

    result=-99999.99;  #no correct result return

    if iq_mode not in ['11b','11g','11a','11n_20','11n_40','fft']:
       reply_info='iq_mode is error!';
       return [-1,reply_info];

    if meas_type not in meas_type_dic[iq_mode]:
       reply_info='meas_type is not valid measure type!';
       return [-1,reply_info];

    meas_type = wt2000_meas_val_dict[meas_type];

    try:
       #if meas_type!='maxrxpwr':
       if meas_type!=WT_ANA_PARM_NON:
          logdebug("WT_GetScalarMeasurement:%d"%meas_type);
          result=wt2000_ctrl.WT_GetScalarMeasurement(meas_type,0);
       else:
          result=maxsiglevel;
       if result==-99999.99:
          return [-1,'data is error'];
       else:
          return [0,result];
    except:
       reply_info='Exception occur when get scalar result!';
       return [1,reply_info];

def getmeas(iq_mode,meas_type):
    res=getmeasdata(iq_mode,meas_type);
    if res[0]!=0:
       return ('%d,%s'%(res[0],res[1]));
    else:
       return ('%d,%f'%(res[0],res[1]));

def getvect(iq_mode,vect_type):
    #not include:freq_vector,freq_vector_time,evmSymbols
    ieee11ag_vect_type_lst=['hhEst','psdu','startPointers','plcp'];
    ieee11ag_vect_len_dic={'hhEst':64,'psdu':'frm_len*8','startPointers':1,'plcp':'plcp_len*8'};

    #not include:psdu,eye,scramblerInit,plcp,freqErrTimeVect,freqErrVect
    ieee11b_vect_type_lst=['evmInPlcp','evmErr'];
    ieee11b_vect_len_dic={'evmInPlcp':'sym_in_plcp_num','evmErr':'sym_num'};

    #not include:CCDF_xPowerDb,CCDF_yProb,slicedSymbols,psduBits,serviceField,preambleFreqErrorTimeUs
    #legacyBits,htSig1_bits,htSig2_bits
    ieee11n_vect_type_lst=['channelEst','evmSymbols','evmTones','PhaseNoiseDeg_Symbols','demodSymbols'];
    ieee11n_vect_len_dic={'channelEst':'NStreams x Ntones x NRx',
		          'evmSymbols':'NStreams x NSymbols',
			  'evmTones':'NStreams x Ntones',
			  'PhaseNoiseDeg_Symbols':'NRx x Nsymbols',
			  'demodSymbols':'NTones x NSymbols X Nstreams'};

    fft_vect_type_lst=['x','y','xy','mask'];
    fft_vect_len_dic={'x':4096,'y':4096,'xy':4096,'mask':4096};

    vect_type_dic={'11b':ieee11b_vect_type_lst,
	           '11a':ieee11ag_vect_type_lst,
		   '11g':ieee11ag_vect_type_lst,
		   '11n_20':ieee11n_vect_type_lst,
		   '11n_40':ieee11n_vect_type_lst,
		   'fft':fft_vect_type_lst};

    vect_len_dic= {'11b':ieee11b_vect_len_dic,
	           '11a':ieee11ag_vect_len_dic,
		   '11g':ieee11ag_vect_len_dic,
		   '11n_20':ieee11n_vect_len_dic,
		   '11n_40':ieee11n_vect_len_dic,
		   'fft':fft_vect_len_dic};
    result=[];
    if iq_mode not in ['11b','11g','11a','11n_20','11n_40','fft']:
       logerror('iq_mode is error!');
       return result;

    if vect_type not in vect_type_dic[iq_mode]:
       logerror('vect_type is not valid vector type!');
       return result;
    vectlen_dic=vect_len_dic[iq_mode];
    vectlen=vectlen_dic[vect_type];
    try:
       res=wt2000_ctrl.WT_GetVectorMeasurement(vect_type,vectlen);
       if res!=-1:
          result=res;
    except:
       logerror('Exception occur when get vector!');

    return result;

def plotcapture():
    result=0;
    try:
       result=wt2000_ctrl.WT_PlotDataCapture();
       if result==0:
          loginfo('Plot captured data ok!');
       else:
	  logerror('Fail to plot captured data!');
    except:
       logerror('Exception occur when plot captured data!');
    return result;

def plot(vector_x, vector_y, plotArgs='', title='y=f(x)', xtitle='x', ytitle='y', keepPlot=0):
    '''plotArgs: string combined from:
	color-r(red),g(green),b(blue),c(cyan),m(magenta),y(yello),k(black)
	shape-.(point),o(circle),x(x-mark),+(plus),start,s(square),d(diamond),v(down triangle),^(up triangle)
	      <(left triangle),>(right triangle),p(pentagram),h(hexagram),.(solid),:(dotted),-.(dashdot),-(dashed)
    '''
    result=0;
    try:
       result=wt2000_ctrl.WT_Plot(vector_x,vector_y,plotArgs,title,xtitle,ytitle,keepPlot);
       if result==0:
          loginfo('Plot curve ok!');
       else:
	  logerror('Fail to plot curve!');
    except:
       logerror('Exception occur when plot curve!');
    return result;

def fft(iq_mode, NFFT, res_bw, window_type):
    '''iq_mode:11b,11g,11a,11n_20,11n_40
        window_type: blackmanharris(default), hanning,flattop,rect
	             if set to '',means to use default value
    '''
    result=0;
    try:
       result=-1; #wt2000_ctrl.LP_AnalyzeFFT(iqmod_dic[iq_mode],NFFT,res_bw,window_type);
       if result==0:
	  loginfo('FFT analyze ok!');
       else:
	  logerror('Fail to FFT analyze!');
    except:
       logerror('Exception occur when FFT analyze!');
    return result;

def spmask(iq_mode):
    result=-99999.990;
    spmask_margin=[];
    try:
       result=-1; #fft(iq_mode,2048,10e4,'blackmanharris');
       if result==0:
          [ind,maskerr]=getmeasdata(iq_mode,"maskerr");
          if ind==0:
             spmask_margin=0;#wt2000_ctrl.Get_SPmask(iqmod_dic[iq_mode]);
	     margin_str='';
	     for margin in spmask_margin:
	         margin_str=margin_str+',%5.2f'%margin;
	     loginfo('err:%f margin:%s'%(maskerr,margin_str));
	     return ('%d%s'%(0,margin_str));
          else:
	     return ('%d,%s'%(ind,maskerr));
       else:
	  reply_info='Fail to Spectral Mask Margin!';
	  return ('%d,%s'%(-1,reply_info));
    except:
       reply_info='Exception occur when get Spectral Mask!';
       return ('%d,%s'%(1,reply_info));

def spec(iq_mode):
    result=-99999.990;
    spec=[];
    try:
       result=fft(iq_mode,2048,10e4,'blackmanharris');
       if result==0:
          result=getvect('fft','xy');
	  if len(result)==0:
             return '-1';
          else:
	     [ind,freq_step]=getmeasdata('fft','delta_freq');
             res_str='0';
             for data in result:
	         res_str=res_str+(',%4.2f'%data[1]);
             return res_str;
       else:
	  reply_info='Fail to get spectrum!';
	  return ('%d,%s'%(-1,reply_info));
    except:
       print "Unexpected error:",sys.exc_info();
       reply_info='Exception occur when get spectrum!';
       return ('%d,%s'%(1,reply_info));

def loleakage(iq_mode):
    result=-99999.990;
    try:
       if iq_mode=='11b':
          [ind,result]=getmeasdata(iq_mode,'loLeakageDb');
	  if ind!=0:
	     return ('%d,%s'%(ind,result));
       elif iq_mode in ['11g','11a']:
          result=0; #wt2000_ctrl.OFDM_LO_Results(iqmod_dic[iq_mode]);
       else:
          [ind,result]=getmeasdata(iq_mode,'dcLeakageDbc');
	  if ind!=0:
	     return ('%d,%s'%(ind,result));
    except:
       reply_info='Exception occur when get LO leakage!';
       return ('%d,%s'%(1,reply_info));

    if result==-99999.990:
       return ('%d,%s'%(-1,'data is error'));
    else:
       return '%d,%f'%(0,result);

def isflat(iq_mode):
    '''return 1:pass, 0: fail'''
    result=1;
    if iq_mode not in ['11g','11a','11n_20','11n_40']:
       reply_info='iq_mode is error!';
       return ('%d,%s'%(-1,reply_info));

    try:
       result=0; #wt2000_ctrl.OFDM_Flatness_Results(iqmod_dic[iq_mode]);
       return ('%d,%d'%(0,result));
    except:
       reply_info='Exception occur when get flatness!';
       return ('%d,%s'%(1,reply_info));

def pwrramp(iq_mode):
    result=-99999.990;
    try:
       if iq_mode=='11b':
          result=0; #wt2000_ctrl.LP_AnalyzePowerRamp80211b();
       else:
          result=0; #wt2000_ctrl.LP_AnalyzePowerRampOFDM();

       if result==0:
          [indup,tmdata]=getmeasdata(iq_mode,"on_time");
	  if indup==0:
             RampUp_usec=tmdata*1e6;
	  [inddn,tmdata]=getmeasdata(iq_mode,"off_time");
	  if inddn==0:
             RampDown_usec=tmdata*1e6;
	  loginfo("Ramp OnTime: %6.2f usec\nRamp OffTime: %6.2f usec\n"%(RampUp_usec,RampDown_usec));
    except:
       reply_info='Exception occur when get power ramp!';
       return ('%d,%s'%(1,reply_info));

    if RampUp_usec==-99999.990 or RampDown_usec==-99999.990 or indup!=0 or inddn!=0:
       return '%d,%s'%(-1,'data is error');
    else:
       return '%d,%f,%f'%(0,RampUp_usec,RampDown_usec);

def fcc(iq_mode,pwr_lmt=-41,freq_zone=12.5):
    sp_str=spec(iq_mode);
    sp_lst=sp_str.split(',');
    if sp_lst[0]!='0':
       return '-1,NAV,NAV,NAV,NAV';
    sp=[float(data) for data in sp_lst[1:]];

    [ind,freq_stephz]=getmeasdata('fft','delta_freq');
    [ind,sample_num]=getmeasdata('fft','length');
    freq_step=freq_stephz/1e6;

    pwr_db2dbm=0;
    #spec 1600 point for -40M to 40M
    spec_dbm=[data+pwr_db2dbm for data in sp];
    max_left_pwr=max(spec_dbm[:int(sample_num/2)-int(freq_zone/freq_step)]);
    max_left_index=spec_dbm[:int(sample_num/2)-int(freq_zone/freq_step)].index(max_left_pwr);
    max_left_freq=(max_left_index-int(sample_num/2))*freq_step;

    max_right_pwr=max(spec_dbm[int(sample_num/2)+int(freq_zone/freq_step):]);
    max_right_index=spec_dbm[int(sample_num/2)+int(freq_zone/freq_step):].index(max_right_pwr);
    max_right_freq=freq_zone+(max_right_index*freq_step);

    if max_left_pwr>pwr_lmt or max_right_pwr>pwr_lmt:
       check=1;
    else:
       check=0;
    return '0,%d,%f,%f,%f,%f'%(check,max_left_pwr-pwr_lmt,max_left_freq,max_right_pwr-pwr_lmt,max_right_freq);

def IQvLog(que):
     servaddr= que.getsockname();
     ln1= "****************************************\n";
     ln2= "*                                      *\n";
     ln3= "*     Welcom From WT2000 Tester!       *\n";
     ln4= "*     Address:"+servaddr[0]+" Port:"+str(servaddr[1])+" *\n";
     ln5= "*                                      *\n";
     ln6= "****************************************\n";

     prnstr=ln1+ln2+ln3+ln4+ln5+ln6;
     que.sendall(prnstr);

def readcmd(que):
    try:
      cmdln=que.recv(1024);
      if cmdln=="login":
  	 loginfo("client login!");
	 IQvLog(que);
	 que.sendall('ExitLog');
	 return True;
      elif cmdln=='shutdown':
	 return False;
      else:#Analyze command string from client
	 logdebug("Command From Client:%s"%cmdln);
	 cmd_lst=cmdln.split();
	 if cmd_lst[0]=='reset':
	    reply=reset();
	 elif cmd_lst[0]=='open':
	    reply=open();
	 elif cmd_lst[0]=='close':
	    reply=close();
	 elif cmd_lst[0]=='setvsg':
	    reply=setvsg(float(cmd_lst[1]),float(cmd_lst[2]));
         elif cmd_lst[0]=='setvsg_left':
	    reply=setvsg_left(float(cmd_lst[1]),float(cmd_lst[2]));
 	 elif cmd_lst[0]=='setrate':
	    reply=setrate(cmd_lst[1]);
 	 elif cmd_lst[0]=='txfrmcnt':
	    reply=txfrmcnt(int(cmd_lst[1],10));
 	 elif cmd_lst[0]=='txenable':
	    reply=txenable(int(cmd_lst[1],10));
 	 elif cmd_lst[0]=='txcw':
	    reply=txcw(float(cmd_lst[1]),float(cmd_lst[2]));
 	 elif cmd_lst[0]=='setvsa':
	    reply=setvsa(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
 	 elif cmd_lst[0]=='setvsa_right':
	    reply=setvsa_right(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
 	 elif cmd_lst[0]=='capture':
	    reply=capture(float(cmd_lst[1]),int(cmd_lst[2]));
 	 elif cmd_lst[0]=='set11agrxmethod':
	    reply=set11agrxmethod(int(cmd_lst[1],10),int(cmd_lst[2],10),int(cmd_lst[3],10),int(cmd_lst[4],10),int(cmd_lst[5],10));
 	 elif cmd_lst[0]=='set11brxmethod':
	    reply=set11brxmethod(int(cmd_lst[1],10),int(cmd_lst[2],10),int(cmd_lst[3],10));
 	 elif cmd_lst[0]=='set11nrxmethod':
	    reply=set11nrxmethod(cmd_lst[1],cmd_lst[2],int(cmd_lst[3],10),int(cmd_lst[4],10),int(cmd_lst[5],10),int(cmd_lst[6],10),
			    int(cmd_lst[7],10),int(cmd_lst[8],10),int(cmd_lst[9],10));
 	 elif cmd_lst[0]=='getmeas':
	    reply=getmeas(cmd_lst[1],cmd_lst[2]);
 	 elif cmd_lst[0]=='spmask':
	    reply=spmask(cmd_lst[1]);
 	 elif cmd_lst[0]=='loleakage':
	    reply=loleakage(cmd_lst[1]);
 	 elif cmd_lst[0]=='isflat':
	    reply=isflat(cmd_lst[1]);
 	 elif cmd_lst[0]=='pwrramp':
	    reply=pwrramp(cmd_lst[1]);
 	 elif cmd_lst[0]=='spec':
	    reply=spec(cmd_lst[1]);
 	 elif cmd_lst[0]=='fcc':
	    reply=fcc(cmd_lst[1],float(cmd_lst[2]),float(cmd_lst[3]));
         else:
	    reply='WT2000 have no such command!';
         que.sendall(reply);
         return True;
    except:
      logwarn("Client socket forcely disconnect...");
      return False;

if __name__ == '__main__':
    init();
    open();
    while True:
        que= serverOpen('WT2000');
        if que!=None:
	   while True:
              sockstat=readcmd(que);
	      if sockstat==False:
		 break;
        else:
           logwarn('Fail to open Socket Server!');
           break;

    input('Press Ctrl+C terminate process...');
    close();
    term();
