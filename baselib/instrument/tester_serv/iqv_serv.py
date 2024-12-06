import os
import sys
import platform
import argparse
from baselib.loglib.log_lib import *
sys.path.append('../../lib/iqview_ctrl/IQviewExecution');
sys.path.append('E:/chip/chip_7.1/py_script/loglib');
sys.path.append('./baselib/test_channel');

try:
  import iqview_ctrl
  loginfo('Load IQview Control Module OK!')
except:
  logwarn("import iqview_ctrl fail")
  if platform.platform().find("Linux") != -1:
    logwarn("platform is not support IQview(%s)"%(platform.platform()))
  else:
    logwarn("make sure IQview is installed.")

# from server import *
import time
#--------------------------------------------
# In Shell, some commands already registered:
# iqview_ctrl.open(), return handler
#---------------------------------------------
iqv_port_dic={'off':1,'left':2,'right':3};
iqmod_dic={'11b':0,'11g':1,'11a':2,'11n_20':3,'11n_40':4,'bt':5};
global maxsiglevel;

def init():
    result=1; #0:ok,-1:err,1:except
    try:
       result=iqview_ctrl.LP_Init();
       if result==0:
          reply_info='IQview Library load ok!';
       else:
	  reply_info='IQview Library fail to load!';
    except:
       reply_info='Exception occur when initialize IQview Library!';
    return ('%d,%s'%(result,reply_info));

def term():
    result=1;
    try:
       result=iqview_ctrl.LP_Term();
       if result==0:
          reply_info='Disconnect with IQview and unload Library ok!';
       else:
	  reply_info='Fail to disconnect with IQview and unload library!';
    except:
       reply_info='Exception occur when disconnect with IQview!';
    return ('%d,%s'%(result,reply_info));

def open_instru(_ipaddr):
    result=1;
    try:
       result=iqview_ctrl.LP_InitTester(_ipaddr);
       if result==0:
          reply_info='Connect with IQview ok!';
       else:
	  reply_info='Fail to connect with IQview!';
    except:
       reply_info='Exception occur when connect with IQview!';
    return ('%d,%s'%(result,reply_info));

def close():
    result=1;
    try:
       result=iqview_ctrl.LP_ConClose();
       if result==0:
          reply_info='Disconnect with IQview!';
       else:
	  reply_info='Fail to disconnect with IQview!';
    except:
       reply_info='Exception occur when disconnect with IQview!';
    return  ('%d,%s'%(result,reply_info));

def reset():
    result=1;
    try:
       result=iqview_ctrl.LP_Reset();
       if result==0:
          reply_info='Reset IQview Ok!';
       else:
	  reply_info='Fail to Reset IQview!';
    except:
       reply_info='Exception occur when reset IQview!';
    return ('%d,%s'%(result,reply_info));

def setvsg(freqMhz,pwrdBm,iqv_no):

    if iqv_no==1:
       iqv_port=iqv_port_dic['left']
    else:
       iqv_port=iqv_port_dic['right']
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
       result=iqview_ctrl.LP_SetVsg(freqMhz*1e6,pwrdBm,iqv_port);
       if result==0:
          reply_info='VSG configure ok!';
       else:
	  reply_info='Fail to configure VSG!';
    except:
       reply_info='Exception occur when configure VSG!';
    return ('%d,%s'%(result,reply_info));

##def setvsg_left(freqMhz,pwrdBm):
##    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
##       reply_info="freq value out of range!";
##       return ('%d,%s'%(-1,reply_info));
##
##    if pwrdBm>10:
##       loginfo("power value too great out of range(10 -98)!");
##       pwrdBm=10;
##    if pwrdBm<-98:
##       loginfo("power value too great out of range(10 -98)!");
##       pwrdBm=-98;
##
##    result=1;
##    try:
##       result=iqview_ctrl.LP_SetVsg(freqMhz*1e6,pwrdBm,iqv_port_dic['left']);
##       if result==0:
##          reply_info='VSG configure ok!';
##       else:
##        reply_info='Fail to configure VSG!';
##    except:
##       reply_info='Exception occur when configure VSG!';
##    return ('%d,%s'%(result,reply_info));

def ldmodfile(filename):
    '''filename start dir is at ./baselib/instrument/iqv/iqview_ctrl/mod/'''
    result=1;
    dirpath='../../lib/iqview_ctrl/mod/'
    print(dirpath+filename);
    try:
       result=iqview_ctrl.LP_SetVsgModulation(dirpath+filename);
       if result==0:
          reply_info='Load Waveform file ok!';
       else:
	  reply_info='Fail to load waveform file!';
    except:
       reply_info='Exception occur when load waveform file!';
    return ('%d,%s'%(result,reply_info));

def setrate(rate):
    subrate=[]
    subrate= rate.split('_')
    print subrate
    rate_file_dic={
		    #'1m':'performance/wave_1m_1024B_idle_30us.mod',
		    #'2ms':'performance/wave_2ms_1024B_idle_30us.mod',
		    #'2ml':'performance/wave_2ml_1024B_idle_30us.mod',
		    #'5.5ms':'performance/wave_5p5ms_1024B_idle_30us.mod',
		    #'5.5ml':'performance/wave_5p5ml_1024B_idle_30us.mod',
		    #'11ms':'performance/wave_11ms_1024B_idle_30us.mod',
		    #'11ml':'performance/wave_11ml_1024B_idle_30us.mod',
                    '1m':'performance/1m.mod',
                    '2m':'performance/2m.mod',
		    '2ms':'performance/2m.mod',
		    '2ml':'performance/2m.mod',
                    '5.5m':'performance/5p5m.mod',
		    '5.5ms':'performance/5p5m.mod',
		    '5.5ml':'performance/5p5m.mod',
                    '11m':'performance/11m.mod',
		    '11ms':'performance/11m.mod',
		    '11ml':'performance/11m.mod',
                    'lr0':'performance/LRmode0_len128.mod',
		    'lr1':'performance/LRmode1_len256.mod',
                    'lr2':'performance/LRmode2_len512.mod',
		    'lr3':'performance/LRmode3_len1024.mod',
            'lr4':'performance/LRmode4_len256.mod',
		    'lr5':'performance/LRmode5_len512.mod',
		    'lr6':'performance/LRmode6_len256.mod',
		    'lr7':'performance/LRmode7_len512.mod',
		    '6m':'performance/6m.mod',
		    '9m':'performance/9m.mod',
		    '12m':'performance/12m.mod',
		    '18m':'performance/18m.mod',
		    '24m':'performance/24m.mod',
		    '36m':'performance/36m.mod',
		    '48m':'performance/48m.mod',
		    '54m':'performance/54m.mod',
		    '1.5m_5':'performance/1.5m_5.mod',
		    '2.25m_5':'performance/2.25m_5.mod',
		    '3m_5':'performance/3m_5.mod',
		    '4.5m_5':'performance/4.5m_5.mod',
		    '6m_5':'performance/6m_5.mod',
		    '9m_5':'performance/9m_5.mod',
		    '12m_5':'performance/12m_5.mod',
		    '13.5m_5':'performance/13.5m_5.mod',
		    '3m_10':'performance/3m_10.mod',
		    '4.5m_10':'performance/4.5m_10.mod',
		    '6m_10':'performance/6m_10.mod',
		    '9m_10':'performance/9m_10.mod',
		    '12m_10':'performance/12m_10.mod',
		    '18m_10':'performance/18m_10.mod',
		    '24m_10':'performance/24m_10.mod',
		    '27m_10':'performance/27m_10.mod',
		    '6m_dup':'performance/6m_dup.mod',
		    '9m_dup':'performance/9m_dup.mod',
		    '12m_dup':'performance/12m_dup.mod',
		    '18m_dup':'performance/18m_dup.mod',
		    '24m_dup':'performance/24m_dup.mod',
		    '36m_dup':'performance/36m_dup.mod',
		    '48m_dup':'performance/48m_dup.mod',
		    '54m_dup':'performance/54m_dup.mod',
                    #'6m':'performance/wave_6m_1024B_idle_30us.mod',
		    #'9m':'performance/wave_9m_1024B_idle_30us.mod',
		    #'12m':'performance/wave_12m_1024B_idle_30us.mod',
		    #'18m':'performance/wave_18m_1024B_idle_30us.mod',
		    #'24m':'performance/wave_24m_1024B_idle_30us.mod',
		    #'36m':'performance/wave_36m_1024B_idle_30us.mod',
		    #'48m':'performance/wave_48m_1024B_idle_30us.mod',
                    #'54m':'performance/wave_54m_1024B_idle_30us.mod',
                    'mcs0':'performance/mcs0_4096byte_40us.mod',
		    'mcs1':'performance/mcs1_4096byte_40us.mod',
		    'mcs2':'performance/mcs2_4096byte_40us.mod',
		    'mcs3':'performance/mcs3_4096byte_40us.mod',
		    'mcs4':'performance/mcs4_4096byte_40us.mod',
		    'mcs5':'performance/mcs5_4096byte_40us.mod',
		    'mcs6':'performance/mcs6_4096byte_40us.mod',
		    'mcs7':'performance/mcs7_4096byte_40us.mod',
		    'mcs0_40':'performance/mcs0_40m_4096byte_40us.mod',
		    'mcs1_40':'performance/mcs1_40m_4096byte_40us.mod',
		    'mcs2_40':'performance/mcs2_40m_4096byte_40us.mod',
		    'mcs3_40':'performance/mcs3_40m_4096byte_40us.mod',
		    'mcs4_40':'performance/mcs4_40m_4096byte_40us.mod',
		    'mcs5_40':'performance/mcs5_40m_4096byte_40us.mod',
		    'mcs6_40':'performance/mcs6_40m_4096byte_40us.mod',
		    'mcs7_40':'performance/mcs7_40m_4096byte_40us.mod',
		    # 'mcs7_40':'performance/mcs6_40m_2048B_0us_ldpc_5us_mcs7_40m_1024B_0us_bcc_5us.mod',
		    # 'mcs7_40':'performance/mcs6_40m_2048B_0us_ldpc_10us_mcs7_40m_1024B_0us_bcc_10us.mod',
		    # 'mcs7_40':'performance/mcs6_40m_2048B_0us_ldpc_20us_mcs7_40m_1024B_0us_bcc_20us.mod',
		    # 'mcs7_40':'performance/mcs6_40m_2048B_0us_ldpc_30us_mcs7_40m_1024B_0us_bcc_30us.mod',
		    # 'mcs7_40':'performance/mcs6_40m_2048B_0us_ldpc_40us_mcs7_40m_1024B_0us_bcc_40us.mod',
		    'mcs32_40':'performance/mcs32_40m_4096byte_40us.mod',
		    'mcs0_sgi':'performance/mcs0_sgi_4096byte_40us.mod',
		    'mcs1_sgi':'performance/mcs1_sgi_4096byte_40us.mod',
		    'mcs2_sgi':'performance/mcs2_sgi_4096byte_40us.mod',
		    'mcs3_sgi':'performance/mcs3_sgi_4096byte_40us.mod',
		    'mcs4_sgi':'performance/mcs4_sgi_4096byte_40us.mod',
		    'mcs5_sgi':'performance/mcs5_sgi_4096byte_40us.mod',
		    'mcs6_sgi':'performance/mcs6_sgi_4096byte_40us.mod',
		    'mcs7_sgi':'performance/mcs7_sgi_4096byte_40us.mod',
                    'mcs0_s':'performance/mcs0_24byte_40us.mod',
		    'mcs1_s':'performance/mcs1_24byte_40us.mod',
		    'mcs2_s':'performance/mcs2_24byte_40us.mod',
		    'mcs3_s':'performance/mcs3_24byte_40us.mod',
		    'mcs4_s':'performance/mcs4_24byte_40us.mod',
		    'mcs5_s':'performance/mcs5_24byte_40us.mod',
		    'mcs6_s':'performance/mcs6_24byte_40us.mod',
		    'mcs7_s':'performance/mcs7_24byte_40us.mod',
		    'mcs0_40_s':'performance/mcs0_40m_24byte_40us.mod',
		    'mcs1_40_s':'performance/mcs1_40m_24byte_40us.mod',
		    'mcs2_40_s':'performance/mcs2_40m_24byte_40us.mod',
		    'mcs3_40_s':'performance/mcs3_40m_24byte_40us.mod',
		    'mcs4_40_s':'performance/mcs4_40m_24byte_40us.mod',
		    'mcs5_40_s':'performance/mcs5_40m_24byte_40us.mod',
		    'mcs6_40_s':'performance/mcs6_40m_24byte_40us.mod',
		    'mcs7_40_s':'performance/mcs7_40m_24byte_40us.mod',
		    'mcs32_40_s':'performance/mcs32_40m_24byte_40us.mod',
		    'mcs0_40_sgi':'performance/mcs0_40m_sgi_4096byte_40us.mod',
		    'mcs1_40_sgi':'performance/mcs1_40m_sgi_4096byte_40us.mod',
		    'mcs2_40_sgi':'performance/mcs2_40m_sgi_4096byte_40us.mod',
		    'mcs3_40_sgi':'performance/mcs3_40m_sgi_4096byte_40us.mod',
		    'mcs4_40_sgi':'performance/mcs4_40m_sgi_4096byte_40us.mod',
		    'mcs5_40_sgi':'performance/mcs5_40m_sgi_4096byte_40us.mod',
		    'mcs6_40_sgi':'performance/mcs6_40m_sgi_4096byte_40us.mod',
		    'mcs7_40_sgi':'performance/mcs7_40m_sgi_4096byte_40us.mod',
		    'mcs32_40_sgi':'performance/mcs32_40m_sgi_4096byte_40us.mod',
                    #'mcs0':'performance/test/mcs0_1024byte_40us.mod',
                    #'mcs1':'performance/test/mcs1_1024byte_40us.mod',
		    #'mcs2':'performance/test/mcs2_1024byte_40us.mod',
		    #'mcs3':'performance/test/mcs3_1024byte_40us.mod',
                    #'mcs4':'performance/test/mcs4_1024byte_40us.mod',
		    #'mcs5':'performance/test/mcs5_1024byte_40us.mod',
                    #'mcs6':'performance/test/mcs6_1024byte_40us.mod',
		    #'mcs7':'performance/test/mcs7_1024byte_40us.mod',
                    'mcs0r':'performance/mcs0_4096byte_2us.mod',
		    'mcs1r':'performance/mcs1_4096byte_2us.mod',
		    'mcs2r':'performance/mcs2_4096byte_2us.mod',
		    'mcs3r':'performance/mcs3_4096byte_2us.mod',
		    'mcs4r':'performance/mcs4_4096byte_2us.mod',
		    'mcs5r':'performance/mcs5_4096byte_2us.mod',
		    'mcs6r':'performance/mcs6_4096byte_2us.mod',
		    'mcs7r':'performance/mcs7_4096byte_2us.mod',
            '1M_DH1_prbs9' :'BT/1_dh1_prbs9.mod',
            '1M_DH3_prbs9' :'BT/1_dh3_prbs9.mod',
            '1M_DH5_prbs9' :'BT/1_dh5_prbs9.mod',
            '2M_DH1_prbs9' :'BT/2_dh1_prbs9.mod',
            '2M_DH3_prbs9' :'BT/2_dh3_prbs9.mod',
            '2M_DH5_prbs9' :'BT/2_dh5_prbs9.mod',
            '3M_DH1_prbs9' :'BT/3_dh1_prbs9.mod',
            '3M_DH3_prbs9' :'BT/3_dh3_prbs9.mod',
            '3M_DH5_prbs9' :'BT/3_dh5_prbs9.mod',
            #'AWGN_noise': 'noise/noise_snr0_idle0us.mod',
            'AWGN_noise': 'noise/awgn.mod',
            'LE_prbs9' : 'BT/LEwaveforms/DirtyPackets/LETestRun3b.mod',
                    'test':'performance/test_packet.mod'
                    };
    if rate in rate_file_dic:
        return ldmodfile(rate_file_dic[rate]);

    elif subrate[1] == 'offset':
            rate_file ='offset_mod/'+subrate[0]+'/'+subrate[0]+'_%s'%subrate[1]+subrate[2]+'.mod';
            print (rate_file)
            return ldmodfile(rate_file)

    elif subrate[1] =='40' and subrate[2] == 'offset':
        rate_file ='offset_mod/HT40/'+subrate[0]+'_%s'%subrate[1]+'/'+subrate[0]+'_%s'%subrate[1]+'_%s'%subrate[2]+subrate[3]+'.mod';
        print (rate_file)
        return ldmodfile(rate_file)
    else:
       rate_file = 'performance/with_noise/'+rate+'.mod';
       print(rate_file);
       return ldmodfile(rate_file);
       #return '-1, rate is invalid';

def txfrmcnt(framecnt):
    '''framecnt: 0 means continuous run, more than 0 means stop when framecnt frame tx over'''
    result=1;
    try:
       result=iqview_ctrl.LP_SetFrameCnt(framecnt);
       if result==0:
	  if framecnt!=0:
	     txstate=iqview_ctrl.LP_TxDone();
	     while 0!=txstate:
                txstate=iqview_ctrl.LP_TxDone();
	        time.sleep(0.01);
             reply_info='IQview tx %d frame ok!'%framecnt;
          else:
	     reply_info='IQview continuous tx ok!';
       else:
	  reply_info='IQview fail to tx %d frme!'%framecnt;
    except:
       reply_info='Exception occur when IQiew tx %d waveform,state:%d!'%(framecnt,txstate);
    return ('%d,%s'%(result,reply_info));

def txenable(enabled):
    '''enabled: 0 switch off, 1 switch on'''
    rf_switch_dic={0:'switch off', 1:'switch on'};
    result=1;
    try:
       result=iqview_ctrl.LP_EnableVsgRF(enabled);
       if result==0:
          reply_info='IQview tx %s ok!'%rf_switch_dic[enabled];
       else:
	  reply_info='IQview fail to tx %s!'%rf_switch_dic[enabled];
    except:
       reply_info='Exception occur when IQview tx %s!'%rf_switch_dic[enabled];
    return ('%d,%s'%(result,reply_info));

def txcw(freqMhz,pwrdBm,iqv_no):

    if iqv_no==1:
        iqv_port=iqv_port_dic['left']
    else:
        iqv_port=iqv_port_dic['right']
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
       result=iqview_ctrl.LP_SetVsgCw(freqMhz*1e6,0,pwrdBm,iqv_port);
       if result==0:
          reply_info='IQview tx sine wave ok!';
       else:
	  reply_info='IQview fail to tx sine wave!';
    except:
       reply_info='Exception occur when IQview tx sine wave!';
    return ('%d,%s'%(result,reply_info));

def setvsa(freqMhz,rxmaxpwr,exAttenDb,iqv_no,auto_range,iq_mode):
    '''rxmaxpwr:expected signal peak power(-60~30dBm), if less than -98, means to use agc'''

    if iqv_no==1:
       iqv_port=iqv_port_dic['left']
    else:
       iqv_port=iqv_port_dic['right']
    global maxsiglevel;
##    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
    if freqMhz<2.4e3 or freqMhz>=6e3:
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
       #iq_mode = ''
       if rxmaxpwr <-60:
        if iq_mode == 'bt':
          #result=iqview_ctrl.LP_SetVsa(freqMhz*1e6,0,iqv_port,exAttenDb,-10,1e-6);
            result=iqview_ctrl.LP_SetVsaBluetooth(freqMhz*1e6,0,iqv_port,exAttenDb,-10,1e-6);
        else:
            result=iqview_ctrl.LP_SetVsa(freqMhz*1e6,0,iqv_port,exAttenDb,-10,1e-6);
        time.sleep(0.1);
        if result==0:
             maxsiglevel=iqview_ctrl.LP_Agc();
             if maxsiglevel!=-100:
                loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
             else:
                loginfo("fail to enable Agc!");
                result=-1;
       else:
        if iq_mode == 'bt':
          result=iqview_ctrl.LP_SetVsaBluetooth(freqMhz*1e6,rxmaxpwr,iqv_port,exAttenDb,-25,10e-6);
        else:
          result=iqview_ctrl.LP_SetVsa(freqMhz*1e6,rxmaxpwr,iqv_port,exAttenDb,-25,10e-6);
	  maxsiglevel=rxmaxpwr;

       if result==0:
	  reply_info='real rxpwr:%f'%maxsiglevel;
       else:
	  reply_info='Fail to configure VSA!';
    except:
       reply_info='Exception occur when configure VSA!';
    return ('%d,%s'%(result,reply_info));

##def setvsa_right(freqMhz,rxmaxpwr,exAttenDb):
##    '''rxmaxpwr:expected signal peak power(-60~30dBm), if less than -98, means to use agc'''
##    global maxsiglevel;
##    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
##       reply_info="freq value out of range!";
##       return ('%d,%s'%(-1,reply_info));
##
##    if rxmaxpwr <-60:
##       loginfo("use agc mode to rx!");
##    elif rxmaxpwr>30:
##       reply_info="power value out of range(10 -98)!";
##       return ('%d,%s'%(-1,reply_info));
##
##    result=1;
##    try:
##       #AGC enable when rxmaxpwr set less than -98
##       if rxmaxpwr <-60:
##          result=iqview_ctrl.LP_SetVsa(freqMhz*1e6,0,iqv_port_dic['right'],exAttenDb,-10,1e-6);
##	  time.sleep(0.1);
##	  if result==0:
##             maxsiglevel=iqview_ctrl.LP_Agc();
##	     if maxsiglevel!=-100:
##	        loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
##	     else:
##                loginfo("fail to enable Agc!");
##		result=-1;
##       else:
##          result=iqview_ctrl.LP_SetVsa(freqMhz*1e6,rxmaxpwr,iqv_port_dic['right'],exAttenDb,-25,1e-6);
##	  maxsiglevel=rxmaxpwr;
##
##       if result==0:
##	  reply_info='real rxpwr:%f'%maxsiglevel;
##       else:
##	  reply_info='Fail to configure VSA!';
##    except:
##       reply_info='Exception occur when configure VSA!';
##    return ('%d,%s'%(result,reply_info));

def capture(smplTm_microSecs=5000,isht40Mode=0):
    '''isht40Mode:0 normal signal, 1:40M signal for 11n'''
    trig_type_dic={'auto':-6, 'free':1, 'ext':2, 'if':6, 'ext_n':7, 'ext2':8, 'ext2_n':9};

    if smplTm_microSecs<=0 or smplTm_microSecs>12.5e3:
       reply_info="sample time length is error!";
       return ('%d,%s'%(-1,reply_info));

    result=1;
    try:
       result=iqview_ctrl.LP_VsaDataCapture(smplTm_microSecs*1e-6,trig_type_dic['if'],80e6,isht40Mode);
       if result==0:
          reply_info='IQview capture data ok!';
       else:
	  reply_info='IQview fail to capture data!';
    except:
       reply_info='Exception occur when IQview capture data!';
    return ('%d,%s'%(result,reply_info));


def savesigfile(sigfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/iqview_ctrl/capture/sig'''

    result=1;
    dirpath='./baselib/iqview_ctrl/capture/sig/'
    try:
       result=iqview_ctrl.LP_SaveVsaSignalFile(dirpath+sigfilename);
       if result==0:
          reply_info='Save captured data as %s ok!'%(dirpath+sigfilename);
       else:
	  reply_info='Fail to save capture data as signal file!';
    except:
       reply_info='Exception occur when save capture data as signal file!';
    return ('%d,%s'%(result,reply_info));

def savemodfile(modfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/iqview_ctrl/capture/mod'''

    result=1;
    dirpath='./baselib/iqview_ctrl/capture/mod/'
    try:
       result=iqview_ctrl.LP_SaveVsaGeneratorFile(dirpath+modfilename);
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
       result=iqview_ctrl.LP_Analyze80211ag(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track);
       if result==0:
          reply_info='Set 11ag rx analyze parameters ok!';
       else:
          reply_info='%s'%(iqview_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11ag rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11prxmethod(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track,ofdm_mode):
    result=1;
    try:
       result=iqview_ctrl.LP_Analyze80211p(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track,ofdm_mode);
       if result==0:
          reply_info='Set 11p rx analyze parameters ok!';
       else:
          reply_info='%s'%(iqview_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11p rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11brxmethod(eq_taps, DCremove11b_flag, method_11b):
    try:
       result=iqview_ctrl.LP_Analyze80211b(eq_taps,DCremove11b_flag,method_11b);
       if result==1:
          reply_info='Set 11b rx analyze parameters ok!';
       else:
	  reply_info='%s'%(iqview_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11b rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11nrxmethod(rxtype='EWC',mode='nxn',enablePhaseCorr=1,enableSymTimingCorr=1,enableAmplitudeTracking=0,
		decodePSDU=1,enableFullPacketChannelEst=0,packetFormat=1,frequencyCorr=2):
    result=1;
    try:
       result=iqview_ctrl.LP_Analyze80211n(rxtype,mode,enablePhaseCorr,enableSymTimingCorr,enableAmplitudeTracking,
            decodePSDU,enableFullPacketChannelEst,packetFormat,frequencyCorr);
       if result==0:
          reply_info='Set 11n rx analyze parameters ok!';
       else:
	  reply_info='%s'%(iqview_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11n rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def setbtrxmethod(bt_data_rate=1,analysis_type='ALL'):
    result=1;
    try:
       print bt_data_rate,analysis_type
       result=iqview_ctrl.LP_AnalyzeBluetooth(bt_data_rate,analysis_type);
       if result==0:
          reply_info='Set bt rx analyze parameters ok!';
       else:
	  reply_info='%s'%(iqview_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set bt rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));


def getmeasdata(iq_mode,meas_type):
    '''meas_type include 11ag,11b,11n all scalar measure result'''
    global maxsiglevel;

    ieee11ag_meas_type_lst=['psduCrcFail','plcpCrcPass','dataRate','numSymbols','numPsduBytes',
		            'evmAll','evmData','evmPilot','codingRate','freqErr','clockErr','dcLeakageDbc',
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
		    'rateInfo_spaceTimeStreams','maxrxpwr','maskerr'];
    bluetooth_meas_type_list =['dataRateDetect','valid','freq_est','bandwidth20dB','P_av_each_burst','P_av_each_burst_dBm','P_pk_each_burst','deltaF1Average','deltaF2Max','deltaF2Average','deltaF2MaxAccess',
            'deltaF2AvAccess','EdrEVMAv','EdrEVMpk','EdrOmegaI','EdrExtremeOmega0','EdrExtremeOmegaI0','EdrEVMvalid','EdrPowDiffdB','freq_deviation','freq_deviationpktopk','freq_estHeader',
            'EdrFreqExtremeEdronly','EdrprobEVM99pass','EdrEVMvsTime','P_av_no_gap_all','validInput','maxfreqDriftRate','payloadErrors','maxPowerAcpDbm','maxPowerEdrDbm','meanNoGapPowerCenterDbm','maxrxpwr'];

    fft_meas_lst=['delta_freq','length','valid'];

    meas_type_dic={'11b':ieee11b_meas_type_lst,
		    '11a':ieee11ag_meas_type_lst,
		    '11g':ieee11ag_meas_type_lst,
		    '11p_10':ieee11ag_meas_type_lst,
		    '11p_5' :ieee11ag_meas_type_lst,
		    '11n_20':ieee11n_meas_type_lst,
		    '11n_40':ieee11n_meas_type_lst,
            'bt' : bluetooth_meas_type_list,
		    'fft':fft_meas_lst};

    result=-99999.99;  #no correct result return

    if iq_mode not in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40','bt','fft']:
       reply_info='iq_mode is error!';
       return [-1,reply_info];

    if meas_type not in meas_type_dic[iq_mode]:
       reply_info='meas_type is not valid measure type!';
       return [-1,reply_info];

    try:
       if meas_type!='maxrxpwr':
          result=iqview_ctrl.LP_GetScalarMeasurement(meas_type,0);
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
    ieee11n_vect_type_lst=['channelEst','evmSymbols','evmTones','PhaseNoiseDeg_Symbols','demodSymbols','spectrumMarginOffsetFreqHz','spectrumMarginOffsetFreqHz','spectrumMarginDb','spectralFlatness_margin'];
    ieee11n_vect_len_dic={'channelEst':'NStreams x Ntones x NRx','evmSymbols':'NStreams x NSymbols','evmTones':'NStreams x Ntones','PhaseNoiseDeg_Symbols':'NRx x Nsymbols','demodSymbols':'NTones x NSymbols X Nstreams','spectrumMarginOffsetFreqHz':8,'spectrumMarginDb':8,'spectralFlatness_margin':4};

##    ieee11n_vect_type_lst=['channelEst','evmSymbols','evmTones','PhaseNoiseDeg_Symbols','demodSymbols'];
##    ieee11n_vect_len_dic={'channelEst':'NStreams x Ntones x NRx',
##		          'evmSymbols':'NStreams x NSymbols',
##			  'evmTones':'NStreams x Ntones',
##			  'PhaseNoiseDeg_Symbols':'NRx x Nsymbols',
##			  'demodSymbols':'NTones x NSymbols X Nstreams'};

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
       print "122"
       print vect_type,vectlen
       res=iqview_ctrl.LP_GetVectorMeasurement(vect_type,vectlen);
       print res
       if res!=-1:
          result=res;
    except:
       logerror('Exception occur when get vector!');

    return result;

def plotcapture():
    result=0;
    try:
       result=iqview_ctrl.LP_PlotDataCapture();
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
       result=iqview_ctrl.LP_Plot(vector_x,vector_y,plotArgs,title,xtitle,ytitle,keepPlot);
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
       result=iqview_ctrl.LP_AnalyzeFFT(iqmod_dic[iq_mode],NFFT,res_bw,window_type);
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
##       result=fft(iq_mode,0,10e4,'blackmanharris');
       result=fft(iq_mode,0,10e4,"NULL");
       if result==0:
          [ind,maskerr]=getmeasdata(iq_mode,"maskerr");
          if ind==0:
             spmask_margin=iqview_ctrl.Get_SPmask(iqmod_dic[iq_mode]);
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
##       elif iq_mode in ['11g','11a']:
##          result=iqview_ctrl.OFDM_LO_Results(iqmod_dic[iq_mode]);
       else:
          [ind,result]=getmeasdata(iq_mode,'dcLeakageDbc');
##          [ind,result]=getmeasdata(iq_mode,'dcLeakageDbc');
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
       result=iqview_ctrl.OFDM_Flatness_Results(iqmod_dic[iq_mode]);
       return ('%d,%d'%(0,result));
    except:
       reply_info='Exception occur when get flatness!';
       return ('%d,%s'%(1,reply_info));

def pwrramp(iq_mode):
    result=-99999.990;
    try:
       if iq_mode=='11b':
          result=iqview_ctrl.LP_AnalyzePowerRamp80211b();
       else:
          result=iqview_ctrl.LP_AnalyzePowerRampOFDM();

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
     ln3= "*     Welcom From IQview Tester!       *\n";
     ln4= "*     Address:"+servaddr[0]+" Port:"+str(servaddr[1])+" *\n";
     ln5= "*                                      *\n";
     ln6= "****************************************\n";

     prnstr=ln1+ln2+ln3+ln4+ln5+ln6;
     que.sendall(prnstr);
     que.sendall('IQview');# used to identify IQxel or WT-200 or IQview

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
	    reply=open_instru(_ipaddr=str(cmd_lst[1]));
	 elif cmd_lst[0]=='close':
	    reply=close();
	 elif cmd_lst[0]=='setvsg':
	    reply=setvsg(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
##         elif cmd_lst[0]=='setvsg_left':
##	    reply=setvsg_left(float(cmd_lst[1]),float(cmd_lst[2]));
 	 elif cmd_lst[0]=='setrate':
	    reply=setrate(cmd_lst[1]);
 	 elif cmd_lst[0]=='txfrmcnt':
	    reply=txfrmcnt(int(cmd_lst[1],10));
 	 elif cmd_lst[0]=='txenable':
	    reply=txenable(int(cmd_lst[1],10));
 	 elif cmd_lst[0]=='txcw':
	    reply=txcw(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
 	 elif cmd_lst[0]=='setvsa':
	    reply=setvsa(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]),float(cmd_lst[4]),int(cmd_lst[5],10),cmd_lst[6]);
##         elif cmd_lst[0]=='setvsa_right':
##	    reply=setvsa_right(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
 	 elif cmd_lst[0]=='capture':
	    reply=capture(float(cmd_lst[1]),int(cmd_lst[2]));
 	 elif cmd_lst[0]=='set11agrxmethod':
	    reply=set11agrxmethod(int(cmd_lst[1],10),int(cmd_lst[2],10),int(cmd_lst[3],10),int(cmd_lst[4],10),int(cmd_lst[5],10));
 	 elif cmd_lst[0]=='set11prxmethod':
	    reply=set11prxmethod(int(cmd_lst[1],10),int(cmd_lst[2],10),int(cmd_lst[3],10),int(cmd_lst[4],10),int(cmd_lst[5],10),int(cmd_lst[6],10));
 	 elif cmd_lst[0]=='set11brxmethod':
	    reply=set11brxmethod(int(cmd_lst[1],10),int(cmd_lst[2],10),int(cmd_lst[3],10));
 	 elif cmd_lst[0]=='setbtrxmethod':
	    reply=setbtrxmethod(int(cmd_lst[1],10),(cmd_lst[2]));
 	 elif cmd_lst[0]=='set11nrxmethod':
	    reply=set11nrxmethod(cmd_lst[1],cmd_lst[2],int(cmd_lst[3],10),int(cmd_lst[4],10),int(cmd_lst[5],10),int(cmd_lst[6],10),
			    int(cmd_lst[7],10),int(cmd_lst[8],10),int(cmd_lst[9],10));
 	 elif cmd_lst[0]=='getmeas':
	    reply=getmeas(cmd_lst[1],cmd_lst[2]);
 	 elif cmd_lst[0]=='getvect':
	    print "test start"
	    reply=getvect(cmd_lst[1],cmd_lst[2]);
	    print "test over"
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
	    reply='IQview have no such command!';
         que.sendall(reply);
         return True;
    except:
      logwarn("Client socket forcely disconnect...");
      return False;

if __name__ == '__main__':
    init();
    parser=argparse.ArgumentParser(description="input IP addr")
    parser.add_argument("address",help="please input instrument IP addr")
    result=parser.parse_args()
    _ipaddr=result.address
    _result=open_instru(_ipaddr).split(",");
    if _result[0]=='-1':
        logerror("instrument IP address not exist")
    else:
        while True:
            que= serverOpen('IQview',34020);
            if que!=None:
                while True:
                    sockstat=readcmd(que);
                    if sockstat==False:
                        break;
            else:
               logwarn('Fail to open Socket Server!');
               break;
##    input('Press Ctrl+C terminate process...');
    close();
    term();
