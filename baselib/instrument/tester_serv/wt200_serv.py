import os
import sys
import platform
import argparse
from baselib.loglib.log_lib import *
sys.path.append('E:/chip/lib/wt200_ctrl/WTexecution');
sys.path.append('./loglib');
sys.path.append('./baselib/test_channel');
try:
    import wt200_ctrl
    loginfo('Load WT200 Control Module OK!')
except:
    logwarn("import wt200_ctrl fail")
    if platform.platform().find("Linux") != -1:
        logwarn("platform is not support IQview(%s)"%(platform.platform()))
    else:
        logwarn("make sure WT200 is installed.")

# from server import *
import time
#--------------------------------------------

# In Shell, some commands already registered:
# wt200_ctrl.open(), return handler
#---------------------------------------------
wt200_port_dic={'off':1,'left':2,'right':3};
iqmod_dic={'11b':0,'11g':1,'11a':2,'11n_20':3,'11n_40':4,'bt':5};
global maxsiglevel;
_connID=2
ipaddr="192.168.100.250"
def init():
    result=1; #0:ok,-1:err,1:except
    try:
        result=wt200_ctrl.WT_Initilaze();
        if result==0:
            reply_info='WT200 Library load ok!';
        else:
            reply_info='wt200 Library fail to load!';
    except:
        reply_info='Exception occur when initialize wt200 Library!';
    return ('%d,%s'%(result,reply_info));

def term():
    result=1;
    loginfo(_connID)
    try:
        result=wt200_ctrl.WT_Terminate(_connID);
        if result==0:
            reply_info='Disconnect with wt200 and unload Library ok!';
        else:
            reply_info='Fail to disconnect with wt200 and unload library!';
    except:
        reply_info='Exception occur when disconnect with wt200!';
    return ('%d,%s'%(result,reply_info));

def open_instru(_ipaddr):
    global _connID
    global ipaddr
    ipaddr=_ipaddr
    result=1;
    try:
        result=wt200_ctrl.WT_Connect(_ipaddr);
        _connID=result[1]
        if result[0]==0:
            reply_info='Connect with wt200 ok!';
        else:
            reply_info='Fail to connect with wt200!';
    except:
        reply_info='Exception occur when connect with wt200!';
    return ('%d,%d,%s'%(result[0],result[1],reply_info));

def close():
    result=1;
    loginfo(_connID)
    try:
        result=wt200_ctrl.WT_DisConnect(_connID);
        if result==0:
            reply_info='Disconnect with wt200!';
        else:
            reply_info='Fail to disconnect with wt200!';
    except:
        reply_info='Exception occur when disconnect with wt200!';
    return  ('%d,%s'%(result,reply_info));

def reset():
    result=1;
    loginfo(ipaddr)
    try:
       #result=wt200_ctrl.LP_Reset();
##        result=wt200_ctrl.WT_DisConnect();
        result=wt200_ctrl.WT_DisConnect(_connID);
        #result=wt200_ctrl.WT_Terminate(_connID)
        #result=wt200_ctrl.WT_Initilaze();
        result = int(open_instru(ipaddr).split(",")[0]);
        if result==0:
            reply_info='Reset wt200 Ok!';
        else:
            reply_info='Fail to Reset wt200!';
    except:
        reply_info='Exception occur when reset wt200!';
    return ('%d,%s'%(result,reply_info));


def setvsg(freqMhz,pwrdBm,iqv_no):

    if iqv_no==1:
        iqv_port=wt200_port_dic['left']
    else:
        iqv_port=wt200_port_dic['right']
    if freqMhz<2.4e3 or freqMhz>=6e3 or (freqMhz>2.5e3 and freqMhz<4.9e3):
        reply_info="freq value out of range!";
        return ('%d,%s'%(-1,reply_info));

    if pwrdBm>20:
        loginfo("power value too great out of range(20 -98)!");
        pwrdBm=20;
    if pwrdBm<-98:
        loginfo("power value too great out of range(20 -98)!");
        pwrdBm=-98;

    result=1;
    try:
        result=wt200_ctrl.WT_SetTxGen(freqMhz*1e6,pwrdBm,iqv_port);
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
##    #try:
##    if True:
##       logdebug("setvsg_left");
##       result=wt200_ctrl.WT_SetTxGen(freqMhz*1e6,pwrdBm,wt200_port_dic['left']);
##       logdebug("setvsg_left 222");
##       if result==0:
##          reply_info='VSG configure ok!';
##       else:
##        reply_info='Fail to configure VSG!';
##    #except:
##    #   reply_info='Exception occur when configure VSG!';
##    #   logdebug(reply_info)
##    return ('%d,%s'%(result,reply_info));

def ldmodfile(filename):
    '''filename start dir is at ./baselib/instrument/iqv/iqview_ctrl/mod/'''
    result=1;
    dirpath='D:\\chip\\lib\\wt200_ctrl\\wave\\120M\\'
    try:
        result=wt200_ctrl.WT_SetTxModulation(dirpath+filename);
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
    rate_file_dic={
            #'1m':'performance/wave_1m_1024B_idle_30us.mod',
            #'2ms':'performance/wave_2ms_1024B_idle_30us.mod',
            #'2ml':'performance/wave_2ml_1024B_idle_30us.mod',
            #'5.5ms':'performance/wave_5p5ms_1024B_idle_30us.mod',
            #'5.5ml':'performance/wave_5p5ml_1024B_idle_30us.mod',
            #'11ms':'performance/wave_11ms_1024B_idle_30us.mod',
            #'11ml':'performance/wave_11ml_1024B_idle_30us.mod',
##            '1m':'1 Mbps(DSSS).csv',
##            '2m':'2 Mbps(DSSS).csv',
##            '2ms':'2 Mbps(DSSS).csv',
##            '2ml':'2 Mbps(DSSS).csv',
##            '5.5m':'5.5 Mbps(DSSS).csv',
##            '5.5ms':'5.5 Mbps(DSSS).csv',
##            '5.5ml':'5.5 Mbps(DSSS).csv',
##            '11m':'11 Mbps(DSSS).csv',
##            '11ms':'11 Mbps(DSSS).csv',
##            '11ml':'11 Mbps(DSSS).csv',
##            '6m':'6 Mbps(OFDM).csv',
##            '9m':'9 Mbps(OFDM).csv',
##            '12m':'12 Mbps(OFDM).csv',
##            '18m':'18 Mbps(OFDM).csv',
##            '24m':'24 Mbps(OFDM).csv',
##            '36m':'36 Mbps(OFDM).csv',
##            '48m':'48 Mbps(OFDM).csv',
##            '54m':'54 Mbps(OFDM).csv',
            '1m':'1 Mbps(DSSS).bwv',
            '2m':'2 Mbps(DSSS).bwv',
            '2ms':'2 Mbps(DSSS).bwv',
            '2ml':'2 Mbps(DSSS).bwv',
            '5.5m':'5.5 Mbps(CCK).bwv',
            '5.5ms':'5.5 Mbps(CCK).bwv',
            '5.5ml':'5.5 Mbps(CCK).bwv',
            '11m':'11 Mbps(CCK).bwv',
            '11ms':'11 Mbps(CCK).bwv',
            '11ml':'11 Mbps(CCK).bwv',
            '6m':'6 Mbps(OFDM).bwv',
            '9m':'9 Mbps(OFDM).bwv',
            '12m':'12 Mbps(OFDM).bwv',
            '18m':'18 Mbps(OFDM).bwv',
            '24m':'24 Mbps(OFDM).bwv',
            '36m':'36 Mbps(OFDM).bwv',
            '48m':'48 Mbps(OFDM).bwv',
            '54m':'54 Mbps(OFDM).bwv',
            #'54m':'performance/54 Mbps(OFDM).bwv',
                    #'6m':'performance/wave_6m_1024B_idle_30us.mod',
            #'9m':'performance/wave_9m_1024B_idle_30us.mod',
            #'12m':'performance/wave_12m_1024B_idle_30us.mod',
            #'18m':'performance/wave_18m_1024B_idle_30us.mod',
            #'24m':'performance/wave_24m_1024B_idle_30us.mod',
            #'36m':'performance/wave_36m_1024B_idle_30us.mod',
            #'48m':'performance/wave_48m_1024B_idle_30us.mod',
                    #'54m':'performance/wave_54m_1024B_idle_30us.mod',
##            'mcs0':'HT20-MCS0.csv',
##            'mcs1':'HT20-MCS1.csv',
##            'mcs2':'HT20-MCS2.csv',
##            'mcs3':'HT20-MCS3.csv',
##            'mcs4':'HT20-MCS4.csv',
##            'mcs5':'HT20-MCS5.csv',
##            'mcs6':'HT20-MCS6.csv',
##            'mcs7':'HT20-MCS7.csv',
##            'mcs0_40':'HT40-MCS0.CSV',
##            'mcs1_40':'HT40-MCS1.CSV',
##            'mcs2_40':'HT40-MCS2.CSV',
##            'mcs3_40':'HT40-MCS3.CSV',
##            'mcs4_40':'HT40-MCS4.CSV',
##            'mcs5_40':'HT40-MCS5.CSV',
##            'mcs6_40':'HT40-MCS6.CSV',
##            'mcs7_40':'HT40-MCS7.CSV',
            'mcs0':'HT20-MCS0.bwv',
            'mcs1':'HT20-MCS1.bwv',
            'mcs2':'HT20-MCS2.bwv',
            'mcs3':'HT20-MCS3.bwv',
            'mcs4':'HT20-MCS4.bwv',
            'mcs5':'HT20-MCS5.bwv',
            'mcs6':'HT20-MCS6.bwv',
            'mcs7':'HT20-MCS7.bwv',
            'mcs0_40':'HT40-MCS0.bwv',
            'mcs1_40':'HT40-MCS1.bwv',
            'mcs2_40':'HT40-MCS2.bwv',
            'mcs3_40':'HT40-MCS3.bwv',
            'mcs4_40':'HT40-MCS4.bwv',
            'mcs5_40':'HT40-MCS5.bwv',
            'mcs6_40':'HT40-MCS6.bwv',
            'mcs7_40':'HT40-MCS7.bwv',
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
            '6m_D100':'noise/6m_duty100per.bwv',
            '24m_D100':'noise/24m_duty100per.bwv',
            '1M_DH1_prbs9' :'BT/1_DH1_prbs9_27byte_2slot.bwv',
            '1M_DH3_prbs9' :'BT/1_DH3_prbs9_183byte_4slot.bwv',
            '1M_DH5_prbs9' :'BT/1_DH5_prbs9_339_byte.bwv',
            '2M_DH1_prbs9' :'BT/2_DH1_prbs9_54byte_2slot.bwv',
            '2M_DH3_prbs9' :'BT/2_DH3_prbs9_367byte_4slot.bwv',
            '2M_DH5_prbs9' :'BT/2_DH5_prbs9_679byte.bwv',
            '3M_DH1_prbs9' :'BT/3_DH1_prbs9_83byte_2slot.bwv',
            '3M_DH3_prbs9' :'BT/3_DH3_prbs9_552byte_4slot.bwv',
            '3M_DH5_prbs9' :'BT/3_DH5_prbs9_1021byte.bwv',
            'LE_prbs9' : 'BT/BLE_prbs9_30byte_mi05.bwv',
                    'test':'HT20-MCS0.csv'
                    };

    if rate in rate_file_dic:
        return ldmodfile(rate_file_dic[rate]);
    elif subrate[1] == 'offset':
        rate_file ='offset_wave/'+subrate[0]+'/'+subrate[0]+'_%s'%subrate[1]+subrate[2]+'.bwv';
        print (rate_file)
        return ldmodfile(rate_file)
    elif subrate[1] =='40':
        rate_file ='offset_wave/HT40/'+subrate[0]+'_%s'%subrate[1]+'/'+subrate[0]+'_%s'%subrate[1]+'_%s'%subrate[2]+subrate[3]+'.bwv';
        print (rate_file)
        return ldmodfile(rate_file)
    else:
        rate_file = 'performance/with_noise/'+rate+'.mod';
        print(rate_file);
        return ldmodfile(rate_file);
       #return '-1, rate is invalid';

def txfrmcnt(framecnt,wave_gap=100,swState=1):
    '''framecnt: 0 means continuous run, more than 0 means stop when framecnt frame tx over
    wave_gap unit: microsecond'''
    result=1;
    loginfo(_connID)
    try:
        result=wt200_ctrl.WT_SetTxCount(framecnt,wave_gap,_connID,swState);
        if result==0:
            if framecnt!=0:
                txstate=wt200_ctrl.WT_TxDone();
                while 0!=txstate:
                    txstate=wt200_ctrl.WT_TxDone();
                    time.sleep(0.01);
                reply_info='wt200 tx %d frame ok!'%framecnt;
            else:
                reply_info='wt200 continuous tx ok!';
        else:
            reply_info='wt200 fail to tx %d frme!'%framecnt;
    except:
        reply_info='Exception occur when IQiew tx %d waveform,state:!'%(framecnt);
    return ('%d,%s'%(result,reply_info));

def txenable(enabled):
    '''enabled: 0 switch off, 1 switch on'''
    rf_switch_dic={0:'switch off', 1:'switch on'};
    result=1;
    loginfo(_connID)
    try:
        logdebug("txenable:%d"%enabled);
        result=wt200_ctrl.WT_StartTx(enabled,_connID);
        result=0;
        if result==0:
            reply_info='wt200 tx %s ok!'%rf_switch_dic[enabled];
        else:
            reply_info='wt200 fail to tx %s!'%rf_switch_dic[enabled];
    except:
        reply_info='Exception occur when wt200 tx %s!'%rf_switch_dic[enabled];
    return ('%d,%s'%(result,reply_info));

def txcw(freqMhz,pwrdBm,iqv_no=1):
    #_connID=rfglobal.connID
    loginfo(_connID)
    if iqv_no==1:
        iqv_port=wt200_port_dic['left']
    else:
        iqv_port=wt200_port_dic['right']
    dirpath='D:\\chip\\lib\\wt200_ctrl\\wave\\120M\\'
    offsetFreq=0
    if offsetFreq==0:
        file_name='Sin0Hz.bwv'
    elif offsetFreq==1: #offsetFreq=1MHz
        file_name='Sin1MHz.bwv'
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
        result=wt200_ctrl.WT_SetVsgCw(freqMhz*1e6,pwrdBm,iqv_port,dirpath+file_name,_connID);
       #result=wt200_ctrl.LP_SetVsgCw(freqMhz*1e6,0,pwrdBm,wt200_port_dic['right']);
        #result=0;
        if result==0:
            reply_info='wt200 tx sine wave ok!';
        else:
            reply_info='wt200 fail to tx sine wave!';
    except:
        reply_info='Exception occur when wt200 tx sine wave!';
    return ('%d,%s'%(result,reply_info));

##def txcw_left(freqMhz,pwrdBm,offsetFreq=0):
##    dirpath='D:\\chip\\lib\\wt200_ctrl\\wave\\120M\\'
##    if offsetFreq==0:
##       file_name='Sin0Hz.bwv'
##    elif offsetFreq==1: #offsetFreq=1MHz
##       file_name='Sin1MHz.bwv'
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
##       result=wt200_ctrl.WT_SetVsgCw(freqMhz*1e6,pwrdBm,wt200_port_dic['left'],dirpath+file_name);
##       #result=wt200_ctrl.LP_SetVsgCw(freqMhz*1e6,0,pwrdBm,wt200_port_dic['right']);
##       result=0;
##       if result==0:
##          reply_info='wt200 tx sine wave ok!';
##       else:
##      reply_info='wt200 fail to tx sine wave!';
##    except:
##       reply_info='Exception occur when wt200 tx sine wave!';
##    return ('%d,%s'%(result,reply_info));

def setvsa(freqMhz,rxmaxpwr,exAttenDb,iqv_no,auto_range):
    '''rxmaxpwr:expected signal peak power(-60~30dBm), if less than -98, means to use agc'''

    if iqv_no==1:
        iqv_port=wt200_port_dic['left']
    else:
        iqv_port=wt200_port_dic['right']
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
        if rxmaxpwr <-60:
            result=wt200_ctrl.WT_SetRx(freqMhz*1e6,0,iqv_port,exAttenDb,-10,1e-6,auto_range);
        time.sleep(0.1);
        if result==0:
             #maxsiglevel=wt200_ctrl.LP_Agc();
            maxsiglevel!=-100
            if maxsiglevel!=-100:
                loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
            else:
                loginfo("fail to enable Agc!");
                result=-1;
        else:
            result=wt200_ctrl.WT_SetRx(freqMhz*1e6,rxmaxpwr,iqv_port,exAttenDb,-25,1e-6,auto_range);

            maxsiglevel=rxmaxpwr;

        if result==0:
            reply_info='real rxpwr:%f'%maxsiglevel;
        else:
            reply_info='Fail to configure VSA!';
    except:
        reply_info='Exception occur when configure VSA!';
    print 'auto_range1=%d'%auto_range
    return ('%d,%s'%(result,reply_info));


##def setvsa_right(freqMhz,rxmaxpwr,exAttenDb):
##    print freqMhz,rxmaxpwr,exAttenDb
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
##          result=wt200_ctrl.WT_SetRx(freqMhz*1e6,0,wt200_port_dic['right'],exAttenDb,-10,20);
##      time.sleep(0.1);
##      if result==0:
##             #maxsiglevel=wt200_ctrl.LP_Agc();
##             maxsiglevel=-100
##         if maxsiglevel!=-100:
##            loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
##         else:
##                loginfo("fail to enable Agc!");
##        result=-1;
##       else:
##          result=wt200_ctrl.WT_SetRx(freqMhz*1e6,rxmaxpwr,wt200_port_dic['right'],exAttenDb,-25,20);
##      maxsiglevel=rxmaxpwr;
##
##       if result==0:
##      reply_info='real rxpwr:%f'%maxsiglevel;
##       else:
##      reply_info='Fail to configure VSA!';
##    except:
##       reply_info='Exception occur when configure VSA!';
##    return ('%d,%s'%(result,reply_info));

def capture(smplTm_microSecs=5000,isht40Mode=0,auto_range=1,trigpretime=20):
    '''isht40Mode:0 normal signal, 1:40M signal for 11n'''
##    trig_type_dic={'auto':-6, 'free':1, 'ext':2, 'if':6, 'ext_n':7, 'ext2':8, 'ext2_n':9};
    trig_type_dic={'auto':-6, 'free':0, 'ext':1, 'if':2, 'ext_n':7, 'ext2':8, 'ext2_n':9};

    if smplTm_microSecs<=0 or smplTm_microSecs>12.5e3:
        reply_info="sample time length is error!";
        return ('%d,%s'%(-1,reply_info));

    result=1;
    print 'hhhhhhhhhhht40',isht40Mode
    try:
        result=wt200_ctrl.WT_DataCapture(2000,trig_type_dic['if'],trigpretime,80e6,isht40Mode,auto_range);

        if result==0:
            reply_info='wt200 capture data ok!';
        else:
            reply_info='wt200 fail to capture data!';
    except:
        reply_info='Exception occur when wt200 capture data!';
    return ('%d,%s'%(result,reply_info));

def savesigfile(sigfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/wt200_ctrl/capture/sig'''

    result=1;
    dirpath='./baselib/wt200_ctrl/capture/sig/'
    try:
        result=wt200_ctrl.WT_SaveVsaSignalFile(dirpath+sigfilename);
        if result==0:
            reply_info='Save captured data as %s ok!'%(dirpath+sigfilename);
        else:
            reply_info='Fail to save capture data as signal file!';
    except:
        reply_info='Exception occur when save capture data as signal file!';
    return ('%d,%s'%(result,reply_info));

def savemodfile(modfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/wt200_ctrl/capture/mod'''

    result=1;
    dirpath='./baselib/wt200_ctrl/capture/mod/'
    try:
        result=wt200_ctrl.WT_SaveVsaGeneratorFile(dirpath+modfilename);
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
        result=wt200_ctrl.WT_Analyze80211ag(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track);
        if result==0:
            reply_info='Set 11ag rx analyze parameters ok!';
        else:
            reply_info='Set 11ag rx analyze parameters FAIL!';#'%s'%(wt200_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set 11ag rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11brxmethod(eq_taps, DCremove11b_flag, method_11b):
    result=1
    if eq_taps > 1:
        eq_taps = 2;
    try:
        result=wt200_ctrl.WT_Analyze80211b(eq_taps,DCremove11b_flag,method_11b);
        if result==0:
            reply_info='Set 11b rx analyze parameters ok!';
        else:
            reply_info='Set 11b rx analyze parameters FAIL!';#'%s'%(wt200_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set 11b rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11nrxmethod(rxtype='EWC',mode='nxn',enablePhaseCorr=1,enableSymTimingCorr=1,enableAmplitudeTracking=0,
        decodePSDU=1,enableFullPacketChannelEst=0,packetFormat=1,frequencyCorr=2):
    result=1;
    try:
        result=wt200_ctrl.WT_Analyze80211n(rxtype,mode,enablePhaseCorr,enableSymTimingCorr,enableAmplitudeTracking,
            decodePSDU,enableFullPacketChannelEst,packetFormat,frequencyCorr);
        if result==0:
            reply_info='Set 11n rx analyze parameters ok!';
        else:
            reply_info='Set 11n rx analyze parameters FAIL!';#'%s'%(wt200_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set 11n rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

##WT_ANA_PARM_FRAME_COUNT=0                #???
##WT_ANA_PARM_FRAME_POW=1                    #Power,dBm
##WT_ANA_PARM_POW_ALL=2                    #???Power ALL,dBm
##WT_ANA_PARM_CARRIER_FREQ_ERROR=3            #????,ppm
##WT_ANA_PARM_CARRIER_FREQ_ERROR_HZ=4        #????,Hz
##WT_ANA_PARM_SYMBOL_CLOCK_ERROR=5            #????,ppm
##WT_ANA_PARM_CARRIER_LEAKAGE=6            #????,dB
##WT_ANA_PARM_OCCUPIED_BANDWIDTH=7            #(99%)OBW,MHz
##
##WT_ANA_PARM_SPECTRUM_MASK_ERROR=8        #????????%
##WT_ANA_PARM_EVM=9                        #EVM,dB
##WT_ANA_PARM_POW_RAMP_ON_TIME=10            #????,us
##WT_ANA_PARM_POW_RAMP_OFF_TIME=11            #????,us
##WT_ANA_PARM_FRAME_FREQ_ERROR=12            #Frame frequency error,ppm
##WT_ANA_PARM_FRAME_FREQ_ERROR_HZ=13        #Frame frequency error,Hz
##
##WT_ANA_PARM_NON=999            #non this params
##
##WT_ANA_PARM_BT_CARR_FREQ_TOL=14            #BT BR Initial freq error,Hz
##WT_ANA_PARM_BT_CARR_FREQ_DRIFT=15        #BT BR Freq.Drift,Hz(Payload 10101010)
##WT_ANA_PARM_BT_DELTA_F1_VALID=16        #BT BR Delta F1(and WT_ANA_PARM_BT_CARR_FREQ_DRIFT) valid
##WT_ANA_PARM_BT_DELTA_F1_AVG=17            #BT BR Delta F1 avg,Hz(Payload 00001111)
##WT_ANA_PARM_BT_DELTA_F2_VALID=18        #BT BR Delta F2 valid
##WT_ANA_PARM_BT_DELTA_F2_AVG=19            #BT BR Delta F2 avg,Hz(Payload 10101010)
##WT_ANA_PARM_BT_DELTA_F2_MAX=20            #BT BR Delta F2 max,Hz(Payload 10101010)
##
##WT_ANA_PARM_BT_BT_DEVM_VALID=21            #BT EDR DEVM????
##WT_ANA_PARM_BT_BT_DEVM=22                #BT EDR DEVM,%
##WT_ANA_PARM_BT_BT_DEVM_PEAK=23            #BT EDR DEVM Peak,%
##WT_ANA_PARM_BT_BT_POW_DIFF=24            #BT EDR Power Diff,dB
##WT_ANA_PARM_BT_BT_99PCT=25                #BT EDR DEVM ?BT 3M???20%, 2M???30%)???
##WT_ANA_PARM_BT_BT_Omega_I=26            #BT EDR Omega I,Hz
##WT_ANA_PARM_BT_BT_Omega_O=27            #BT EDR Omega O,Hz
##WT_ANA_PARM_BT_BT_Omega_IO=28            #BT EDR Omega IO,Hz
##WT_ANA_PARM_BT_BT_BW20dB_VALUE=29
##WT_ANA_PARM_POW_PEAK=30

def setbtrxmethod(bt_data_rate=1,analysis_type='ALL'):
    result=1;
    try:
        print bt_data_rate,analysis_type
        result=wt200_ctrl.WT_AnalyzeBluetooth(bt_data_rate,analysis_type);
        print result
        if result==0:
            reply_info='Set bt rx analyze parameters ok!';
        else:
            reply_info='Set bt rx analyze parameters FAIL!';#'%s'%(iqview_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set bt rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def SetLargePowerIFGSwitch(swState=1):
    loginfo(_connID)

##    try:
##        print _connID,swState
##        result = wt200_ctrl.WT_LargePowerIFGSwitch(_connID,swState);
##        print "result=%d"%result
##        if result==0:
##            reply_info='LargePowerIFGSwitch set ok!';
##        else:
##            reply_info='Fail to set!';
##    except:
##        reply_info='Exception occur when LargePowerIFGSwitch!';
##    print reply_info
    result = wt200_ctrl.WT_LargePowerIFGSwitch(_connID,swState);

    return ('%d'%(result));


def getmeasdata(iq_mode,meas_type):
    '''meas_type include 11ag,11b,11n all scalar measure result'''
    global maxsiglevel;

    ieee11ag_meas_type_lst=['psduCrcFail','plcpCrcPass','dataRate','numSymbols','numPsduBytes',
                    'evmAll','evmData','evmPilot','codingRate','freqErr','clockErr',
                'ampErr','ampErrDb','phaseErr','rmsPhaseNoise','rmsPowerNoGap',
                'rmsPower','pkPower','rmsMaxAvgPower','maskerr','on_time','off_time','maxrxpwr','dcLeakageDbc',
                'spectrumAverViolationPercentage','spectrumAverObw','flatness_passed_wt200'];

    #not include maxFreqErr
    ieee11b_meas_type_lst=['lockedClock','plcpCrcFail','psduCrcFail','longPreamble','numPsduBytes','bitRateInMHz',
            'evmPk','bitRate','dataRate','modType','evmAll','evmInPreamble','evmInPsdu','freqErr','clockErr','ampErr','ampErrDb',
            'phaseErr','rmsPhaseNoise','rmsPowerNoGap','rmsPower','pkPower','rmsMaxAvgPower','loLeakageDb','maskerr','on_time',
            'off_time','maxrxpwr','spectrumAverViolationPercentage','spectrumAverObw'];

    #not include:completePacket,htSigFieldCRC,idxAnalyzedSigs,idxDataTones,idxPilotTones,preambleFreqErrorHz
    #legacyLength,legacyRate,htSig2_aggregation,htSig2_stbc,htSig2_shortGI,htSig2_numHTLF,htSig2_soundingPacket,rateInfo_modulation,
    #rateInfo_codingRate,mainPathStreamPowerDb
    ieee11n_meas_type_lst=['evmAvgAll','packetDetection','psduCRC','acquisition','demodulation','dcLeakageDbc',
            'rxRmsPowerDb','isolationDb','freqErrorHz','symClockErrorPpm','PhaseNoiseDeg_RmsAll','IQImbal_amplDb',
            'IQImbal_phaseDeg','rateInfo_bandwidthMhz','rateInfo_dataRateMbps','rateInfo_spatialStreams',
            'analyzedRange','htSig1_htLength','htSig1_mcsIndex','htSig1_bandwidth','htSig2_advancedCoding',
            'rateInfo_spaceTimeStreams','maxrxpwr','spectrumAverViolationPercentage','spectrumAverObw','flatness_passed_wt200'];

    bluetooth_meas_type_list =['dataRateDetect','valid','freq_est','bandwidth20dB','P_av_each_burst','P_av_each_burst_dBm','P_pk_each_burst','P_pk_each_burst_dBm','deltaF1Average','deltaF2Max','deltaF2Average','deltaF2MaxAccess',
            'deltaF2AvAccess','EdrEVMAv','EdrEVMpk','EdrOmegaI','EdrExtremeOmega0','EdrExtremeOmegaI0','EdrEVMvalid','EdrPowDiffdB','freq_deviation','freq_deviationpktopk','freq_estHeader',
            'EdrFreqExtremeEdronly','EdrprobEVM99pass','EdrEVMvsTime','P_av_no_gap_all','validInput','maxfreqDriftRate','payloadErrors','maxPowerAcpDbm','maxPowerEdrDbm','meanNoGapPowerCenterDbm','maxrxpwr'];

    fft_meas_lst=['delta_freq','length','valid'];

    wt200_meas_val_dict={

    'rmsPowerNoGap':"Pow_frame",
    'rxRmsPowerDb': "Pow_frame",   # WT-200 have only one name
    'pkPower':"Pow_peak",
    'evmAvgAll':"evm.all",
    'evmAll': "evm.all",
    'evmPk': "evm.pk",
    'evmPilot':"evm.pilot",
    'evmData':"evm.data",
    'freqErr':"signal.freqerr",
    'freqErrorHz':"signal.freqerr",   # WT-200 have only one name
    'clockErr':"signal.symclockerr",
    'symClockErrorPpm':"signal.symclockerr",  # WT-200 have only one name
    'IQImbal_amplDb':"iqmatch.amp",
    'ampErrDb':"iqmatch.amp",    # WT-200 have only one name
    'IQImbal_phaseDeg': "iqmatch.phase",
##    'phaseErr': "iqmatch.phase",  # WT-200 have only one name
    'phaseErr': "phase.error",
    'rmsPhaseNoise':"phase.error",
    'PhaseNoiseDeg_RmsAll':"phase.error", # WT-200 have only one name
    'on_time':"ramp.on_time",
    'off_time':"ramp.off_time",
    'maskerr':"Spec_mask_err",
    'loLeakageDb':"Spec_carrier_leakage",
    'dcLeakageDbc':"Spec_carrier_leakage",# WT-200 have only one name

    'spectrumAverViolationPercentage':"Spec_mask_err",
    'spectrumAverObw':"Spec_Obw",
    'flatness_passed_wt200':"flatness.passed",

     'P_av_each_burst_dBm':"Pow_frame",
     'P_pk_each_burst_dBm':"Pow_peak",
     'maxfreqDriftRate' :"BT_MAX_CARR_FREQ",
     'freq_est': "BT_MAX_CARR_FREQ",
     'bandwidth20dB':"BT_BW20dB_Value",
     'deltaF1Average':"BT_DELTA_F1_AVG",
     'deltaF2Max':"BT_DELTA_F2_MAX",
     'deltaF2Average': "BT_DELTA_F2_AVG",
     'EdrEVMAv':"BT_DEVM",
     'EdrEVMpk':"BT_DEVM_PEAK",
     'EdrEVMvalid':"BT_DEVM_VALID",
     'EdrPowDiffdB':"BT_POW_DIFF",
     'EdrOmegaI':"BT_Omega_I",
     'EdrExtremeOmega0':"BT_Omega_O",
     'EdrExtremeOmegaI0':"BT_Omega_IO",
     'EdrprobEVM99pass':"BT_99PCT",


     }

    meas_type_dic={'11b':ieee11b_meas_type_lst,
            '11a':ieee11ag_meas_type_lst,
            '11g':ieee11ag_meas_type_lst,
            '11n_20':ieee11n_meas_type_lst,
            '11n_40':ieee11n_meas_type_lst,
            'bt' : bluetooth_meas_type_list,
            'fft':fft_meas_lst};

    result=-99999.99;  #no correct result return

    if iq_mode not in ['11b','11g','11a','11n_20','11n_40','bt','fft']:
        reply_info='iq_mode is error!';
        return [-1,reply_info];

    if meas_type not in meas_type_dic[iq_mode]:
        reply_info='meas_type is not valid measure type!';
        return [-1,reply_info];

    meas_type = wt200_meas_val_dict[meas_type];
    print meas_type
    try:
       #if meas_type!='maxrxpwr':
        if meas_type !='':
            logdebug("WT_GetScalarMeasurement:%s"%meas_type);
            result=wt200_ctrl.WT_GetScalarMeasurement(meas_type);
            print "wt200_ctrl.WT_GetScalarMeasurement",result
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

def getvectdata(iq_mode,vect_type):
    #not include:freq_vector,freq_vector_time,evmSymbols
    ieee11ag_vect_type_lst=['hhEst','psdu','startPointers','plcp','spectrumMarginOffsetFreqHz','spectrumMarginDb','spectralFlatness_margin'];

    #not include:psdu,eye,scramblerInit,plcp,freqErrTimeVect,freqErrVect
    ieee11b_vect_type_lst=['evmInPlcp','evmErr','spectrumMarginOffsetFreqHz','spectrumMarginDb'];

    #not include:CCDF_xPowerDb,CCDF_yProb,slicedSymbols,psduBits,serviceField,preambleFreqErrorTimeUs
    #legacyBits,htSig1_bits,htSig2_bits
    ieee11n_vect_type_lst=['channelEst','evmSymbols','evmTones','PhaseNoiseDeg_Symbols','demodSymbols','spectrumMarginOffsetFreqHz','spectrumMarginDb','spectralFlatness_margin'];

    ieeebt_vect_type_lst =['maxPowerAcpDbm','maxPowerAcpFreqHz'];

    vect_type_dic={    '11b':ieee11b_vect_type_lst,
                    '11a':ieee11ag_vect_type_lst,
                    '11g':ieee11ag_vect_type_lst,
                    '11n_20':ieee11n_vect_type_lst,
                    '11n_40':ieee11n_vect_type_lst,
                    'bt':ieeebt_vect_type_lst,
                    };
    wt200_vect_val_dict={    'spectrumMarginOffsetFreqHz':"Spec_margin",
                            'spectrumMarginDb': "Spec_margin",   # WT-200 have only one name
                            'spectralFlatness_margin': "flatness.section.margin", # WT-200 have only one name
                            'maxPowerAcpDbm': "BT_Spectrum_Acp",
                            'maxPowerAcpFreqHz': "BT_Spectrum_Acp",
                            }
    result=[];
    res=[];
    if iq_mode not in ['11b','11g','11a','11n_20','11n_40','bt']:#,'fft'
        logerror('iq_mode is error!');
        return result;

    if vect_type not in vect_type_dic[iq_mode]:
        logerror('vect_type is not valid vector type!');
        return result;

    vect_type = wt200_vect_val_dict[vect_type];
    print vect_type
    try:
        res=wt200_ctrl.WT_GetVectorMeasurement('Spec_margin');
        print res[0],res[1],res[2],res[3]
        print "wt200_ctrl.WT_GetVectorMeasurement",res

        if res!=-1:
##            result=res;
            result=[0]
            for i in range(0,len(res)):
                result.append(res[i])
            print  'result=',result;
            return result   ##return a list[0,......]!!!!!!
        else:
            return [-1,'data is error'];
    except:
        reply_info='Exception occur when get vector!';
        return [1,reply_info];

def getvect(iq_mode,vect_type):
    res=getvectdata(iq_mode,vect_type);
    if iq_mode in ['11g','11n_20','11n_40']:
        if res[0]!=0:
            return ('%d,%s'%(res[0],res[1]));
        elif vect_type == 'spectrumMarginOffsetFreqHz':
            return ('%d,%f,%f,%f,%f,%f,%f,%f,%f'%(res[0],res[1],res[3],res[5],res[7],res[9],res[11],res[13],res[15]));
        elif vect_type == 'spectrumMarginDb':
            return ('%d,%f,%f,%f,%f,%f,%f,%f,%f'%(res[0],res[2],res[4],res[6],res[8],res[10],res[12],res[14],res[16]));
        elif vect_type == 'spectralFlatness_margin':
            return ('%d,%f,%f,%f,%f'%(res[0],res[2],res[4],res[6],res[8]));
        else:
            return ('%d,%f'%(res[0],res[1]));
    elif iq_mode in ['11b']:
        print res,'mdmdmdm'
        if res[0]!=0:
            return ('%d,%s'%(res[0],res[1]));
        elif vect_type == 'spectrumMarginOffsetFreqHz':
            return ('%d,%f,%f,%f,%f'%(res[0],res[1],res[3],res[5],res[7]));
        elif vect_type == 'spectrumMarginDb':
            return ('%d,%f,%f,%f,%f'%(res[0],res[2],res[4],res[6],res[8]));
        else:
            return ('%d,%f'%(res[0],res[1]));
    elif iq_mode in ['bt']:
        if res[0]!=0:
            return ('%d,%s'%(res[0],res[1]));
        if vect_type == 'maxPowerAcpFreqHz':
            return('%d,%f,%f,%f,%f,%f,%f'%(res[0],res[1],res[3],res[5],res[7],res[9],res[11]));
        if vect_type == 'maxPowerAcpDbm':
            return('%d,%f,%f,%f,%f,%f,%f'%(res[0],res[2],res[4],res[6],res[8],res[10],res[12]));
        else:
            return('%d,%f'%(res[0],res[1]));

def plotcapture():
    result=0;
    try:
        result=wt200_ctrl.WT_PlotDataCapture();
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
        result=wt200_ctrl.WT_Plot(vector_x,vector_y,plotArgs,title,xtitle,ytitle,keepPlot);
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
        result=-1; #wt200_ctrl.LP_AnalyzeFFT(iqmod_dic[iq_mode],NFFT,res_bw,window_type);
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
                spmask_margin=0;#wt200_ctrl.Get_SPmask(iqmod_dic[iq_mode]);
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
##          result=0; #wt200_ctrl.OFDM_LO_Results(iqmod_dic[iq_mode]);
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
        result=0; #wt200_ctrl.OFDM_Flatness_Results(iqmod_dic[iq_mode]);
        return ('%d,%d'%(0,result));
    except:
        reply_info='Exception occur when get flatness!';
        return ('%d,%s'%(1,reply_info));


def pwrramp(iq_mode):
    result=-99999.990;
    try:
        if iq_mode=='11b':
##            result=wt200_ctrl.WT_DataCapture(5000*1e6,6,80e6,0);
            result=wt200_ctrl.WT_DataCapture(5000,6,150,80e6,0,0)

        else:
##            result=wt200_ctrl.WT_DataCapture(5000*1e6,6,80e6,0);
            result=wt200_ctrl.WT_DataCapture(5000,6,150,80e6,0,0)

        if result==0:
            [indup,tmdata]=getmeasdata(iq_mode,"on_time");
            if indup==0:
                RampUp_usec=tmdata;
            [inddn,tmdata]=getmeasdata(iq_mode,"off_time");
            if inddn==0:
                RampDown_usec=tmdata;
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
     ln3= "*     Welcom From wt200 Tester!       *\n";
     ln4= "*     Address:"+servaddr[0]+" Port:"+str(servaddr[1])+" *\n";
     ln5= "*                                      *\n";
     ln6= "****************************************\n";

     prnstr=ln1+ln2+ln3+ln4+ln5+ln6;
     que.sendall(prnstr);
     que.sendall('wt200');# used to identify IQxel or WT-200

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
        elif cmd_lst[0]=='init':
            reply=init();
        elif cmd_lst[0]=='open':
            reply=open_instru(_ipaddr=(cmd_lst[1]));
        elif cmd_lst[0]=='close':
            reply=close();
        elif cmd_lst[0]=='setvsg':
            reply=setvsg(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
##         elif cmd_lst[0]=='setvsg_left':
##        reply=setvsg_left(float(cmd_lst[1]),float(cmd_lst[2]));
        elif cmd_lst[0]=='setrate':
            reply=setrate(cmd_lst[1]);
        elif cmd_lst[0]=='txfrmcnt':
            reply=txfrmcnt(int(cmd_lst[1],10));
        elif cmd_lst[0]=='txenable':
            reply=txenable(int(cmd_lst[1],10));
        elif cmd_lst[0]=='txcw':
            reply=txcw(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
##      elif cmd_lst[0]=='txcw_left':
##        reply=txcw_left(float(cmd_lst[1]),float(cmd_lst[2]));
        elif cmd_lst[0]=='setvsa':
            reply=setvsa(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]),float(cmd_lst[4]),int(cmd_lst[5]));

        elif cmd_lst[0]=='SetLargePowerIFGSwitch':
            reply=SetLargePowerIFGSwitch(int(cmd_lst[1],10))


##      elif cmd_lst[0]=='setvsa_right':
##        reply=setvsa_right(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
        elif cmd_lst[0]=='capture':
            reply=capture(float(cmd_lst[1]),int(cmd_lst[2]),int(cmd_lst[3]),int(cmd_lst[4]));
        elif cmd_lst[0]=='set11agrxmethod':
            reply=set11agrxmethod(int(cmd_lst[1],10),int(cmd_lst[2],10),int(cmd_lst[3],10),int(cmd_lst[4],10),int(cmd_lst[5],10));
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
            reply=getvect(cmd_lst[1],cmd_lst[2]);
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
            reply='wt200 have no such command!';
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
            que= serverOpen('wt200',34010);
            if que!=None:
                while True:
                    sockstat=readcmd(que);
                    if sockstat==False:
                        break;
            else:
                logwarn('Fail to open Socket Server!');
                break;
##    raw_input('Press Ctrl+C terminate process...');
    close();
    term();
##    sys.exit()
