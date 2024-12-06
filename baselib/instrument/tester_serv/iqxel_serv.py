import os
import sys
import platform
import argparse
from baselib.loglib.log_lib import *
sys.path.append('../../lib/iqxel_ctrl/IQexecution');
sys.path.append('E:/chip/chip_7.1/py_script/loglib');
sys.path.append('./baselib/test_channel');
try:
    import iqxel_ctrl
    loginfo('Load IQxel Control Module OK!')
except:
    logwarn("import iqxel_ctrl fail")
    if platform.platform().find("Linux") != -1:
        logwarn("platform (%s) is not support IQview"%(platform.platform()))
    else:
        logwarn("make sure IQxel is installed.")
# from server import *
import time
#--------------------------------------------
# In Shell, some commands already registered:
# iqxel_ctrl.open(), return handler
#---------------------------------------------
iqv_port_dic={'off':1,'left':2,'right':3};
iqmod_dic={'11b':0,'11g':1,'11a':2,'11n_20':3,'11n_40':4,'bt':5};
global maxsiglevel;

def init():
    result=1; #0:ok,-1:err,1:except
    try:
        result=iqxel_ctrl.LP_Init();
        if result==0:
            reply_info='IQxel Library load ok!';
        else:
            reply_info='IQxel Library fail to load!';
    except:
        reply_info='Exception occur when initialize IQxel Library!';
    return ('%d,%s'%(result,reply_info));

def term():
    result=1;
    try:
        result=iqxel_ctrl.LP_Term();
        if result==0:
            reply_info='Disconnect with IQxel and unload Library ok!';
        else:
            reply_info='Fail to disconnect with IQxel and unload library!';
    except:
        reply_info='Exception occur when disconnect with IQxel!';
    return ('%d,%s'%(result,reply_info));

def open_instru(_ipaddr):
    result=1;
    try:
        result=iqxel_ctrl.LP_InitTester(_ipaddr);
        if result==0:
            reply_info='Connect with IQxel ok!';
        else:
            reply_info='Fail to connect with IQxel!';
    except:
        reply_info='Exception occur when connect with IQxel!';
    return ('%d,%s'%(result,reply_info));

def close():
    result=1;
    try:
        result=iqxel_ctrl.LP_ConClose();
        if result==0:
            reply_info='Disconnect with IQxel!';
        else:
            reply_info='Fail to disconnect with IQxel!';
    except:
        reply_info='Exception occur when disconnect with IQxel!';
    return  ('%d,%s'%(result,reply_info));

def reset():
    result=1;
    try:
        result=iqxel_ctrl.LP_Reset();
        if result==0:
            reply_info='Reset IQxel Ok!';
        else:
            reply_info='Fail to Reset IQxel!';
    except:
        reply_info='Exception occur when reset IQxel!';
    return ('%d,%s'%(result,reply_info));

def setvsg(freqMhz,pwrdBm,iqv_no):

    if iqv_no==1:
        iqv_port=iqv_port_dic['left']
    else:
        iqv_port=iqv_port_dic['right']

    if freqMhz<2.4e3 or freqMhz>=6e3: # or (freqMhz>2.5e3 and freqMhz<4.9e3):

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
        result=iqxel_ctrl.LP_SetVsg(freqMhz*1e6,pwrdBm,iqv_port);
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
##       result=iqxel_ctrl.LP_SetVsg(freqMhz*1e6,pwrdBm,iqv_port_dic['left']);
##       if result==0:
##          reply_info='VSG configure ok!';
##          return ('%d,%s'%(0,reply_info));
##       else:
##        reply_info='Fail to configure VSG!';
##        return ('%d,%s'%(-1,reply_info));
##    except:
##       reply_info='Exception occur when configure VSG!';
##    return ('%d,%s'%(result,reply_info));

def ldmodfile(filename):
    '''filename start dir is at ./baselib/instrument/iqv/iqxel_ctrl/mod/'''
    result=1;
    dirpath='../../lib/iqxel_ctrl/wave/up/'
    print(dirpath+filename);
    try:
        result=iqxel_ctrl.LP_SetVsgModulation(dirpath+filename);
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

            #'2ms':'performance/2m.mod',
            #'2ml':'performance/2m.mod',
##            '1m':'1m.iqvsg',
##            '2ms': '2ms.iqvsg',
##            '2ml': '2ml.iqvsg',
##            '5.5ms':'5.5ms.iqvsg',
##            '5.5ml':'5.5ml.iqvsg',
##            '11ms':'11ms.iqvsg',
##            '11ml':'11ml.iqvsg',
            '1m':'1m_1024B_40us.iqvsg',
            '2ms': '2ms_1024B_40us.iqvsg',
            '2ml': '2ml_1024B_40us.iqvsg',
            '2m': '2ml_1024B_40us.iqvsg',
            '5.5ms':'5.5ms_1024B_40us.iqvsg',
            '5.5ml':'5.5ml_1024B_40us.iqvsg',
            '5.5m':'5.5ml_1024B_40us.iqvsg',
            '11ms':'11ms_1024B_40us.iqvsg',
            '11ml':'11ml_1024B_40us.iqvsg',
            '11m':'11ml_1024B_40us.iqvsg',
            'lr0':'performance/LRmode0_len128.mod',
            'lr1':'performance/LRmode1_len256.mod',
            'lr2':'performance/LRmode2_len512.mod',
            'lr3':'performance/LRmode3_len1024.mod',
            'lr4':'performance/LRmode4_len256.mod',
            'lr5':'performance/LRmode5_len512.mod',
            'lr6':'performance/LRmode6_len256.mod',
            'lr7':'performance/LRmode7_len512.mod',
##            '6m':'6m.iqvsg',
##            '9m':'9m_test.iqvsg',
##            '12m':'12m.iqvsg',
##            '18m':'18m.iqvsg',
##            '24m':'24m.iqvsg',
##            '36m':'36m.iqvsg',
##            '48m':'48m.iqvsg',
##            '54m':'54m_download.iqvsg',
            '6m':'6m_1024B_40us.iqvsg',
            '9m':'9m_1024B_40us.iqvsg',
            '12m':'12m_1024B_40us.iqvsg',
            '18m':'18m_1024B_40us.iqvsg',
            '24m':'24m_1024B_40us.iqvsg',
            '36m':'36m_1024B_40us.iqvsg',
            '48m':'48m_1024B_40us.iqvsg',
            '54m':'54m_1024B_40us.iqvsg',
                    #'6m':'performance/wave_6m_1024B_idle_30us.mod',
            #'9m':'performance/wave_9m_1024B_idle_30us.mod',
            #'12m':'performance/wave_12m_1024B_idle_30us.mod',
            #'18m':'performance/wave_18m_1024B_idle_30us.mod',
            #'24m':'performance/wave_24m_1024B_idle_30us.mod',
            #'36m':'performance/wave_36m_1024B_idle_30us.mod',
            #'48m':'performance/wave_48m_1024B_idle_30us.mod',
                    #'54m':'performance/wave_54m_1024B_idle_30us.mod',
##            'mcs0':'mcs0_gen.iqvsg',
##            'mcs1':'mcs1_gen.iqvsg',
##            'mcs2':'WIFI_N_BW20_SS1_MCS2_BCC_Fs80M.iqvsg',
##            'mcs3':'mcs3_gen.iqvsg',
##            'mcs4':'mcs4_gen.iqvsg',
##            'mcs5':'mcs5_gen.iqvsg',
##            'mcs6':'mcs6_gen.iqvsg',
##            'mcs7':'mcs7_gen.iqvsg',
            'mcs0':'mcs0_4096B_40us.iqvsg',
            'mcs1':'mcs1_4096B_40us.iqvsg',
            'mcs2':'mcs2_4096B_40us.iqvsg',
            'mcs3':'mcs3_4096B_40us.iqvsg',
            'mcs4':'mcs4_4096B_40us.iqvsg',
            'mcs5':'mcs5_4096B_40us.iqvsg',
            'mcs6':'mcs6_4096B_40us.iqvsg',
            'mcs7':'mcs7_4096B_40us.iqvsg',
##            'mcs0_40':'mcs0_40.iqvsg',
##            'mcs1_40':'mcs1_40.iqvsg',
##            'mcs2_40':'mcs2_40.iqvsg',
##            'mcs3_40':'mcs3_40.iqvsg',
##            'mcs4_40':'mcs4_40.iqvsg',
##            'mcs5_40':'mcs5_40.iqvsg',
##            'mcs6_40':'mcs6_40.iqvsg',
##            'mcs7_40':'mcs7_40.iqvsg',
            'mcs0_40':'mcs0_40m_4096B_40us.iqvsg',
            'mcs1_40':'mcs1_40m_4096B_40us.iqvsg',
            'mcs2_40':'mcs2_40m_4096B_40us.iqvsg',
            'mcs3_40':'mcs3_40m_4096B_40us.iqvsg',
            'mcs4_40':'mcs4_40m_4096B_40us.iqvsg',
            'mcs5_40':'mcs5_40m_4096B_40us.iqvsg',
            'mcs6_40':'mcs6_40m_4096B_40us.iqvsg',
            'mcs7_40':'mcs7_40m_4096B_40us.iqvsg',
##            'mcs0_sgi':'performance/mcs0_sgi_4096byte_40us.mod',
##            'mcs1_sgi':'performance/mcs1_sgi_4096byte_40us.mod',
##            'mcs2_sgi':'performance/mcs2_sgi_4096byte_40us.mod',
##            'mcs3_sgi':'performance/mcs3_sgi_4096byte_40us.mod',
##            'mcs4_sgi':'performance/mcs4_sgi_4096byte_40us.mod',
##            'mcs5_sgi':'performance/mcs5_sgi_4096byte_40us.mod',
##            'mcs6_sgi':'performance/mcs6_sgi_4096byte_40us.mod',
##            'mcs7_sgi':'performance/mcs7_sgi_4096byte_40us.mod',
            'mcs0_sgi':'mcs0_sgi_4096B_40us.iqvsg',
            'mcs1_sgi':'mcs1_sgi_4096B_40us.iqvsg',
            'mcs2_sgi':'mcs2_sgi_4096B_40us.iqvsg',
            'mcs3_sgi':'mcs3_sgi_4096B_40us.iqvsg',
            'mcs4_sgi':'mcs4_sgi_4096B_40us.iqvsg',
            'mcs5_sgi':'mcs5_sgi_4096B_40us.iqvsg',
            'mcs6_sgi':'mcs6_sgi_4096B_40us.iqvsg',
            'mcs7_sgi':'mcs7_sgi_4096B_40us.iqvsg',
##            'mcs0_40_sgi':'performance/mcs0_40m_sgi_4096byte_40us.mod',
##            'mcs1_40_sgi':'performance/mcs1_40m_sgi_4096byte_40us.mod',
##            'mcs2_40_sgi':'performance/mcs2_40m_sgi_4096byte_40us.mod',
##            'mcs3_40_sgi':'performance/mcs3_40m_sgi_4096byte_40us.mod',
##            'mcs4_40_sgi':'performance/mcs4_40m_sgi_4096byte_40us.mod',
##            'mcs5_40_sgi':'performance/mcs5_40m_sgi_4096byte_40us.mod',
##            'mcs6_40_sgi':'performance/mcs6_40m_sgi_4096byte_40us.mod',
##            'mcs7_40_sgi':'performance/mcs7_40m_sgi_4096byte_40us.mod',
            'mcs0_40_sgi':'mcs0_40m_sgi_4096B_40us.iqvsg',
            'mcs1_40_sgi':'mcs1_40m_sgi_4096B_40us.iqvsg',
            'mcs2_40_sgi':'mcs2_40m_sgi_4096B_40us.iqvsg',
            'mcs3_40_sgi':'mcs3_40m_sgi_4096B_40us.iqvsg',
            'mcs4_40_sgi':'mcs4_40m_sgi_4096B_40us.iqvsg',
            'mcs5_40_sgi':'mcs5_40m_sgi_4096B_40us.iqvsg',
            'mcs6_40_sgi':'mcs6_40m_sgi_4096B_40us.iqvsg',
            'mcs7_40_sgi':'mcs7_40m_sgi_4096B_40us.iqvsg',
                    #'mcs0':'performance/test/mcs0_1024byte_40us.mod',
                    #'mcs1':'performance/test/mcs1_1024byte_40us.mod',
            #'mcs2':'performance/test/mcs2_1024byte_40us.mod',
            #'mcs3':'performance/test/mcs3_1024byte_40us.mod',
                    #'mcs4':'performance/test/mcs4_1024byte_40us.mod',
            #'mcs5':'performance/test/mcs5_1024byte_40us.mod',
                    #'mcs6':'performance/test/mcs6_1024byte_40us.mod',
            #'mcs7':'performance/test/mcs7_1024byte_40us.mod',
##            'mcs0r':'performance/mcs0_4096byte_2us.mod',
##            'mcs1r':'performance/mcs1_4096byte_2us.mod',
##            'mcs2r':'performance/mcs2_4096byte_2us.mod',
##            'mcs3r':'performance/mcs3_4096byte_2us.mod',
##            'mcs4r':'performance/mcs4_4096byte_2us.mod',
##            'mcs5r':'performance/mcs5_4096byte_2us.mod',
##            'mcs6r':'performance/mcs6_4096byte_2us.mod',
##            'mcs7r':'performance/mcs7_4096byte_2us.mod',
            '1M_DH1_prbs9' :'BT/1_dh1_prbs9.iqvsg',
            '1M_DH1_NONE_prbs9' :'BT/1_dh1_NONE_prbs9.iqvsg',
            '1M_DH1_1POS_prbs9' :'BT/1_dh1_1POS_prbs9.iqvsg',
            '1M_DH1_1NEG_prbs9' :'BT/1_dh1_1NEG_prbs9.iqvsg',
            '1M_DH1_2POS_prbs9' :'BT/1_dh1_2POS_prbs9.iqvsg',
            '1M_DH1_2NEG_prbs9' :'BT/1_dh1_2NEG_prbs9.iqvsg',
            '1M_DH1_3POS_prbs9' :'BT/1_dh1_3POS_prbs9.iqvsg',
            '1M_DH1_3NEG_prbs9' :'BT/1_dh1_3NEG_prbs9.iqvsg',
            '1M_DH1_4POS_prbs9' :'BT/1_dh1_4POS_prbs9.iqvsg',
            '1M_DH1_4NEG_prbs9' :'BT/1_dh1_4NEG_prbs9.iqvsg',
            '1M_DH1_5POS_prbs9' :'BT/1_dh1_5POS_prbs9.iqvsg',
            '1M_DH1_5NEG_prbs9' :'BT/1_dh1_5NEG_prbs9.iqvsg',
            '1M_DH1_6POS_prbs9' :'BT/1_dh1_6POS_prbs9.iqvsg',
            '1M_DH1_6NEG_prbs9' :'BT/1_dh1_6NEG_prbs9.iqvsg',
            '1M_DH1_7POS_prbs9' :'BT/1_dh1_7POS_prbs9.iqvsg',
            '1M_DH1_7NEG_prbs9' :'BT/1_dh1_7NEG_prbs9.iqvsg',
            '1M_DH1_8POS_prbs9' :'BT/1_dh1_8POS_prbs9.iqvsg',
            '1M_DH1_8NEG_prbs9' :'BT/1_dh1_8NEG_prbs9.iqvsg',
            '1M_DH1_9POS_prbs9' :'BT/1_dh1_9POS_prbs9.iqvsg',
            '1M_DH1_9NEG_prbs9' :'BT/1_dh1_9NEG_prbs9.iqvsg',
            '1M_DH1_10POS_prbs9' :'BT/1_dh1_10POS_prbs9.iqvsg',
            '1M_DH1_10NEG_prbs9' :'BT/1_dh1_10NEG_prbs9.iqvsg',
            '1M_DH3_prbs9' :'BT/1_dh3_prbs9.iqvsg',
            '1M_DH5_prbs9' :'BT/1_dh5_prbs9.iqvsg',
            '1M_DH5_NONE_prbs9' :'BT/1_dh5_NONE_prbs9.iqvsg',
            '1M_DH5_1POS_prbs9' :'BT/1_dh5_1POS_prbs9.iqvsg',
            '1M_DH5_1NEG_prbs9' :'BT/1_dh5_1NEG_prbs9.iqvsg',
            '1M_DH5_2POS_prbs9' :'BT/1_dh5_2POS_prbs9.iqvsg',
            '1M_DH5_2NEG_prbs9' :'BT/1_dh5_2NEG_prbs9.iqvsg',
            '1M_DH5_3POS_prbs9' :'BT/1_dh5_3POS_prbs9.iqvsg',
            '1M_DH5_3NEG_prbs9' :'BT/1_dh5_3NEG_prbs9.iqvsg',
            '1M_DH5_4POS_prbs9' :'BT/1_dh5_4POS_prbs9.iqvsg',
            '1M_DH5_4NEG_prbs9' :'BT/1_dh5_4NEG_prbs9.iqvsg',
            '1M_DH5_5POS_prbs9' :'BT/1_dh5_5POS_prbs9.iqvsg',
            '1M_DH5_5NEG_prbs9' :'BT/1_dh5_5NEG_prbs9.iqvsg',
            '1M_DH5_6POS_prbs9' :'BT/1_dh5_6POS_prbs9.iqvsg',
            '1M_DH5_6NEG_prbs9' :'BT/1_dh5_6NEG_prbs9.iqvsg',
            '1M_DH5_7POS_prbs9' :'BT/1_dh5_7POS_prbs9.iqvsg',
            '1M_DH5_7NEG_prbs9' :'BT/1_dh5_7NEG_prbs9.iqvsg',
            '1M_DH5_8POS_prbs9' :'BT/1_dh5_8POS_prbs9.iqvsg',
            '1M_DH5_8NEG_prbs9' :'BT/1_dh5_8NEG_prbs9.iqvsg',
            '1M_DH5_9POS_prbs9' :'BT/1_dh5_9POS_prbs9.iqvsg',
            '1M_DH5_9NEG_prbs9' :'BT/1_dh5_9NEG_prbs9.iqvsg',
            '1M_DH5_10POS_prbs9' :'BT/1_dh5_10POS_prbs9.iqvsg',
            '1M_DH5_10NEG_prbs9' :'BT/1_dh5_10NEG_prbs9.iqvsg',
            '2M_DH1_prbs9' :'BT/2_dh1_prbs9.iqvsg',
            '2M_DH3_prbs9' :'BT/2_dh3_prbs9.iqvsg',
            '2M_DH5_prbs9' :'BT/2_dh5_prbs9.iqvsg',
            '2M_DH5_NONE_prbs9' :'BT/2_dh5_NONE_prbs9.iqvsg',
            '2M_DH5_1POS_prbs9' :'BT/2_dh5_1POS_prbs9.iqvsg',
            '2M_DH5_1NEG_prbs9' :'BT/2_dh5_1NEG_prbs9.iqvsg',
            '2M_DH5_2POS_prbs9' :'BT/2_dh5_2POS_prbs9.iqvsg',
            '2M_DH5_2NEG_prbs9' :'BT/2_dh5_2NEG_prbs9.iqvsg',
            '2M_DH5_3POS_prbs9' :'BT/2_dh5_3POS_prbs9.iqvsg',
            '2M_DH5_3NEG_prbs9' :'BT/2_dh5_3NEG_prbs9.iqvsg',
            '3M_DH1_prbs9' :'BT/3_dh1_prbs9.iqvsg',
            '3M_DH3_prbs9' :'BT/3_dh3_prbs9.iqvsg',
            '3M_DH5_prbs9' :'BT/3_dh5_prbs9.iqvsg',
            '3M_DH5_NONE_prbs9' :'BT/3_dh5_NONE_prbs9.iqvsg',
            '3M_DH5_1POS_prbs9' :'BT/3_dh5_1POS_prbs9.iqvsg',
            '3M_DH5_1NEG_prbs9' :'BT/3_dh5_1NEG_prbs9.iqvsg',
            '3M_DH5_2POS_prbs9' :'BT/3_dh5_2POS_prbs9.iqvsg',
            '3M_DH5_2NEG_prbs9' :'BT/3_dh5_2NEG_prbs9.iqvsg',
            '3M_DH5_3POS_prbs9' :'BT/3_dh5_3POS_prbs9.iqvsg',
            '3M_DH5_3NEG_prbs9' :'BT/3_dh5_3NEG_prbs9.iqvsg',
            'LE_prbs9' : 'BT/LE_prbs9.iqvsg',
            'LE2M_NONE_prbs9'  : 'BT/LE2M_NONE_prbs9.iqvsg',
            'LE2M_1POS_prbs9'  : 'BT/LE2M_1POS_prbs9.iqvsg',
            'LE2M_1NEG_prbs9'  : 'BT/LE2M_1NEG_prbs9.iqvsg',
            'LE2M_2POS_prbs9'  : 'BT/LE2M_2POS_prbs9.iqvsg',
            'LE2M_2NEG_prbs9'  : 'BT/LE2M_2NEG_prbs9.iqvsg',
            'LE2M_3POS_prbs9'  : 'BT/LE2M_3POS_prbs9.iqvsg',
            'LE2M_3NEG_prbs9'  : 'BT/LE2M_3NEG_prbs9.iqvsg',
            'LE2M_4POS_prbs9'  : 'BT/LE2M_4POS_prbs9.iqvsg',
            'LE2M_4NEG_prbs9'  : 'BT/LE2M_4NEG_prbs9.iqvsg',
            'LE2M_5POS_prbs9'  : 'BT/LE2M_5POS_prbs9.iqvsg',
            'LE2M_5NEG_prbs9'  : 'BT/LE2M_5NEG_prbs9.iqvsg',
            'LE2M_6POS_prbs9'  : 'BT/LE2M_6POS_prbs9.iqvsg',
            'LE2M_6NEG_prbs9'  : 'BT/LE2M_6NEG_prbs9.iqvsg',
            'LE2M_7POS_prbs9'  : 'BT/LE2M_7POS_prbs9.iqvsg',
            'LE2M_7NEG_prbs9'  : 'BT/LE2M_7NEG_prbs9.iqvsg',
            'LE2M_8POS_prbs9'  : 'BT/LE2M_8POS_prbs9.iqvsg',
            'LE2M_8NEG_prbs9'  : 'BT/LE2M_8NEG_prbs9.iqvsg',
            'LE2M_9POS_prbs9'  : 'BT/LE2M_9POS_prbs9.iqvsg',
            'LE2M_9NEG_prbs9'  : 'BT/LE2M_9NEG_prbs9.iqvsg',
            'LE2M_10POS_prbs9' : 'BT/LE2M_10POS_prbs9.iqvsg',
            'LE2M_10NEG_prbs9' : 'BT/LE2M_10NEG_prbs9.iqvsg',
            'LE1M_NONE_prbs9'  : 'BT/LE1M_NONE_prbs9.iqvsg',
            'LE1M_NONE_s_prbs9'  : 'BT/LE1M_NONE_s_prbs9.iqvsg',
            'LE1M_1POS_prbs9'  : 'BT/LE1M_1POS_prbs9.iqvsg',
            'LE1M_1NEG_prbs9'  : 'BT/LE1M_1NEG_prbs9.iqvsg',
            'LE1M_2POS_prbs9'  : 'BT/LE1M_2POS_prbs9.iqvsg',
            'LE1M_2NEG_prbs9'  : 'BT/LE1M_2NEG_prbs9.iqvsg',
            'LE1M_3POS_prbs9'  : 'BT/LE1M_3POS_prbs9.iqvsg',
            'LE1M_3NEG_prbs9'  : 'BT/LE1M_3NEG_prbs9.iqvsg',
            'LE1M_4POS_prbs9'  : 'BT/LE1M_4POS_prbs9.iqvsg',
            'LE1M_4NEG_prbs9'  : 'BT/LE1M_4NEG_prbs9.iqvsg',
            'LE1M_5POS_prbs9'  : 'BT/LE1M_5POS_prbs9.iqvsg',
            'LE1M_5NEG_prbs9'  : 'BT/LE1M_5NEG_prbs9.iqvsg',
            'LE1M_6POS_prbs9'  : 'BT/LE1M_6POS_prbs9.iqvsg',
            'LE1M_6NEG_prbs9'  : 'BT/LE1M_6NEG_prbs9.iqvsg',
            'LE1M_7POS_prbs9'  : 'BT/LE1M_7POS_prbs9.iqvsg',
            'LE1M_7NEG_prbs9'  : 'BT/LE1M_7NEG_prbs9.iqvsg',
            'LE1M_8POS_prbs9'  : 'BT/LE1M_8POS_prbs9.iqvsg',
            'LE1M_8NEG_prbs9'  : 'BT/LE1M_8NEG_prbs9.iqvsg',
            'LE1M_9POS_prbs9'  : 'BT/LE1M_9POS_prbs9.iqvsg',
            'LE1M_9NEG_prbs9'  : 'BT/LE1M_9NEG_prbs9.iqvsg',
            'LE1M_10POS_prbs9' : 'BT/LE1M_10POS_prbs9.iqvsg',
            'LE1M_10NEG_prbs9' : 'BT/LE1M_10NEG_prbs9.iqvsg',
            'LE125K_NONE_prbs9'  : 'BT/LE125K_NONE_prbs9.iqvsg',
            'LE125K_1POS_prbs9'  : 'BT/LE125K_1POS_prbs9.iqvsg',
            'LE125K_1POS_prbs9_240'  : 'BT/LE125K_1POS_prbs9_240.iqvsg',
            'LE125K_1NEG_prbs9'  : 'BT/LE125K_1NEG_prbs9.iqvsg',
            'LE125K_2POS_prbs9'  : 'BT/LE125K_2POS_prbs9.iqvsg',
            'LE125K_2NEG_prbs9'  : 'BT/LE125K_2NEG_prbs9.iqvsg',
            'LE125K_3POS_prbs9'  : 'BT/LE125K_3POS_prbs9.iqvsg',
            'LE125K_3NEG_prbs9'  : 'BT/LE125K_3NEG_prbs9.iqvsg',
            'LE125K_4POS_prbs9'  : 'BT/LE125K_4POS_prbs9.iqvsg',
            'LE125K_4NEG_prbs9'  : 'BT/LE125K_4NEG_prbs9.iqvsg',
            'LE125K_5POS_prbs9'  : 'BT/LE125K_5POS_prbs9.iqvsg',
            'LE125K_5NEG_prbs9'  : 'BT/LE125K_5NEG_prbs9.iqvsg',
            'LE125K_6POS_prbs9'  : 'BT/LE125K_6POS_prbs9.iqvsg',
            'LE125K_6NEG_prbs9'  : 'BT/LE125K_6NEG_prbs9.iqvsg',
            'LE125K_7POS_prbs9'  : 'BT/LE125K_7POS_prbs9.iqvsg',
            'LE125K_7NEG_prbs9'  : 'BT/LE125K_7NEG_prbs9.iqvsg',
            'LE125K_8POS_prbs9'  : 'BT/LE125K_8POS_prbs9.iqvsg',
            'LE125K_8NEG_prbs9'  : 'BT/LE125K_8NEG_prbs9.iqvsg',
            'LE125K_9POS_prbs9'  : 'BT/LE125K_9POS_prbs9.iqvsg',
            'LE125K_9NEG_prbs9'  : 'BT/LE125K_9NEG_prbs9.iqvsg',
            'LE125K_10POS_prbs9' : 'BT/LE125K_10POS_prbs9.iqvsg',
            'LE125K_10NEG_prbs9' : 'BT/LE125K_10NEG_prbs9.iqvsg',
            'LE500K_NONE_prbs9'  : 'BT/LE500K_NONE_prbs9.iqvsg',
            'LE500K_1POS_prbs9'  : 'BT/LE500K_1POS_prbs9.iqvsg',
            'LE500K_1NEG_prbs9'  : 'BT/LE500K_1NEG_prbs9.iqvsg',
            'LE500K_2POS_prbs9'  : 'BT/LE500K_2POS_prbs9.iqvsg',
            'LE500K_2NEG_prbs9'  : 'BT/LE500K_2NEG_prbs9.iqvsg',
            'LE500K_3POS_prbs9'  : 'BT/LE500K_3POS_prbs9.iqvsg',
            'LE500K_3NEG_prbs9'  : 'BT/LE500K_3NEG_prbs9.iqvsg',
            'LE500K_4POS_prbs9'  : 'BT/LE500K_4POS_prbs9.iqvsg',
            'LE500K_4NEG_prbs9'  : 'BT/LE500K_4NEG_prbs9.iqvsg',
            'LE500K_5POS_prbs9'  : 'BT/LE500K_5POS_prbs9.iqvsg',
            'LE500K_5NEG_prbs9'  : 'BT/LE500K_5NEG_prbs9.iqvsg',
            'LE500K_6POS_prbs9'  : 'BT/LE500K_6POS_prbs9.iqvsg',
            'LE500K_6NEG_prbs9'  : 'BT/LE500K_6NEG_prbs9.iqvsg',
            'LE500K_7POS_prbs9'  : 'BT/LE500K_7POS_prbs9.iqvsg',
            'LE500K_7NEG_prbs9'  : 'BT/LE500K_7NEG_prbs9.iqvsg',
            'LE500K_8POS_prbs9'  : 'BT/LE500K_8POS_prbs9.iqvsg',
            'LE500K_8NEG_prbs9'  : 'BT/LE500K_8NEG_prbs9.iqvsg',
            'LE500K_9POS_prbs9'  : 'BT/LE500K_9POS_prbs9.iqvsg',
            'LE500K_9NEG_prbs9'  : 'BT/LE500K_9NEG_prbs9.iqvsg',
            'LE500K_10POS_prbs9' : 'BT/LE500K_10POS_prbs9.iqvsg',
            'LE500K_10NEG_prbs9' : 'BT/LE500K_10NEG_prbs9.iqvsg',
            'test':'performance/test_packet.mod'
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
        result=iqxel_ctrl.LP_SetFrameCnt(framecnt);
        if result==0:
            if framecnt!=0:
                txstate=iqxel_ctrl.LP_TxDone();
                while 0!=txstate:
                    txstate=iqxel_ctrl.LP_TxDone();
                    time.sleep(0.01);
                reply_info='IQxel tx %d frame ok!'%framecnt;
            else:
                reply_info='IQxel continuous tx ok!';
        else:
            reply_info='IQxel fail to tx %d frme!'%framecnt;
    except:
        reply_info='Exception occur when IQiew tx %d waveform,state:%d!'%(framecnt,txstate);
    return ('%d,%s'%(result,reply_info));

def txenable(enabled):
    '''enabled: 0 switch off, 1 switch on'''
    rf_switch_dic={0:'switch off', 1:'switch on'};
    result=1;
    try:
        result=iqxel_ctrl.LP_EnableVsgRF(enabled);
        if result==0:
            reply_info='IQxel tx %s ok!'%rf_switch_dic[enabled];
        else:
            reply_info='IQxel fail to tx %s!'%rf_switch_dic[enabled];
    except:
        reply_info='Exception occur when IQxel tx %s!'%rf_switch_dic[enabled];
    return ('%d,%s'%(result,reply_info));

def txcw(freqMhz,pwrdBm,iqv_no):

    if iqv_no==1:
        iqv_port=iqv_port_dic['left']
    else:
        iqv_port=iqv_port_dic['right']

    if freqMhz<2.4e3 or freqMhz>=6e3:# or (freqMhz>2.5e3 and freqMhz<4.9e3):
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
        result=iqxel_ctrl.LP_SetVsgCw(freqMhz*1e6,0,pwrdBm,iqv_port);
        if result==0:
            reply_info='IQxel tx sine wave ok!';
        else:
            reply_info='IQxel fail to tx sine wave!';
    except:
        reply_info='Exception occur when IQxel tx sine wave!';
    return ('%d,%s'%(result,reply_info));

##def txcw_left(freqMhz,pwrdBm):
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
##       result=iqxel_ctrl.LP_SetVsgCw(freqMhz*1e6,0,pwrdBm,iqv_port_dic['left']);
##       if result==0:
##          reply_info='IQxel tx sine wave ok!';
##       else:
##      reply_info='IQview fail to tx sine wave!';
##    except:
##       reply_info='Exception occur when IQview tx sine wave!';
##    return ('%d,%s'%(result,reply_info));

def setvsa(freqMhz,rxmaxpwr,exAttenDb,iqv_no,auto_range):
    '''rxmaxpwr:expected signal peak power(-60~30dBm), if less than -98, means to use agc'''

    if iqv_no==1:
        iqv_port=iqv_port_dic['left']
    else:
        iqv_port=iqv_port_dic['right']
    global maxsiglevel;
##    if freqMhz<2.4e3 or freqMhz>=6e3 : #or (freqMhz>2.5e3 and freqMhz<4.9e3):
##        reply_info="freq value out of range!";
##        return ('%d,%s'%(-1,reply_info));

    if rxmaxpwr <-60:
        loginfo("use agc mode to rx!");
    elif rxmaxpwr>30:
        reply_info="power value out of range(10 -98)!";
        return ('%d,%s'%(-1,reply_info));

    result=1;
    try:
       #AGC enable when rxmaxpwr set less than -98
        if rxmaxpwr <-60:
            result=iqxel_ctrl.LP_SetVsa(freqMhz*1e6,0,iqv_port,exAttenDb,-10,1e-6);
            time.sleep(0.1);
        if result==0:
            maxsiglevel=iqxel_ctrl.LP_Agc();
            if maxsiglevel!=-100:
                loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
            else:
                loginfo("fail to enable Agc!");
                result=-1;
        else:
            result=iqxel_ctrl.LP_SetVsa(freqMhz*1e6,rxmaxpwr,iqv_port,exAttenDb,-25,1e-6);
            if auto_range == 1:
                res_setwinT = iqxel_ctrl.LP_SetAgcWindowTime(0.02)
                res_trigger = iqxel_ctrl.LP_SetVsa_Trigger(6,0,-25,0,6e-6,10e-6,1.5)
                agc_mpwr = iqxel_ctrl.LP_Agc()
                print "LP_Agc11 agc_mpwr=%s , res_setwinT=%d, res_trigger=%d"%(agc_mpwr,res_setwinT,res_trigger)
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
##          result=iqxel_ctrl.LP_SetVsa(freqMhz*1e6,0,iqv_port_dic['right'],exAttenDb,-10,1e-6);
##      time.sleep(0.1);
##      if result==0:
##             maxsiglevel=iqxel_ctrl.LP_Agc();
##         if maxsiglevel!=-100:
##            loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
##         else:
##                loginfo("fail to enable Agc!");
##        result=-1;
##       else:
##          result=iqxel_ctrl.LP_SetVsa(freqMhz*1e6,rxmaxpwr,iqv_port_dic['right'],exAttenDb,-25,1e-6);
##      maxsiglevel=rxmaxpwr;
##
##       if result==0:
##      reply_info='real rxpwr:%f'%maxsiglevel;
##       else:
##      reply_info='Fail to configure VSA!';
##    except:
##       reply_info='Exception occur when configure VSA!';
##    return ('%d,%s'%(result,reply_info));



def setvsa_bt(freqMhz,rxmaxpwr,exAttenDb,iqv_no):
    '''rxmaxpwr:expected signal peak power(-60~30dBm), if less than -98, means to use agc'''

    if iqv_no==1:
        iqv_port=iqv_port_dic['left']
    else:
        iqv_port=iqv_port_dic['right']
    global maxsiglevel;
    if freqMhz<2.4e3 or freqMhz>=6e3 : #or (freqMhz>2.5e3 and freqMhz<4.9e3):
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
            result=iqxel_ctrl.LP_SetVsaBluetooth(freqMhz*1e6,0,iqv_port,exAttenDb,-10,10e-6);
            time.sleep(0.1);
            if result==0:
                maxsiglevel=iqxel_ctrl.LP_Agc();
                if maxsiglevel!=-100:
                    loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
                else:
                    loginfo("fail to enable Agc!");
                    result=-1;
            else:
                result=iqxel_ctrl.LP_SetVsaBluetooth(freqMhz*1e6,rxmaxpwr,iqv_port,exAttenDb,-25,10e-6);
                maxsiglevel=rxmaxpwr;

                if result==0:
                    reply_info='real rxpwr:%f'%maxsiglevel;
                else:
                    reply_info='Fail to configure VSA!';
    except:
        reply_info='Exception occur when configure VSA!';

    return ('%d,%s'%(result,reply_info));


##def setvsa_bt_right(freqMhz,rxmaxpwr,exAttenDb):
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
##          result=iqxel_ctrl.LP_SetVsaBluetooth(freqMhz*1e6,0,iqv_port_dic['right'],exAttenDb,-10,10e-6);
##      time.sleep(0.1);
##      if result==0:
##             maxsiglevel=iqxel_ctrl.LP_Agc();
##         if maxsiglevel!=-100:
##            loginfo("real rx maxpwr:%fdBm"%maxsiglevel);
##         else:
##                loginfo("fail to enable Agc!");
##        result=-1;
##       else:
##          result=iqxel_ctrl.LP_SetVsaBluetooth(freqMhz*1e6,rxmaxpwr,iqv_port_dic['right'],exAttenDb,-25,10e-6);
##      maxsiglevel=rxmaxpwr;
##
##       if result==0:
##      reply_info='real rxpwr:%f'%maxsiglevel;
##       else:
##      reply_info='Fail to configure VSA!';
##    except:
##       reply_info='Exception occur when configure VSA!';
##    return ('%d,%s'%(result,reply_info));

def capture(smplTm_microSecs=5000,isht40Mode=0,auto_range=0):
    '''isht40Mode:0 normal signal, 1:40M signal for 11n'''
    trig_type_dic={'auto':-6, 'free':1, 'ext':2, 'if':6, 'ext_n':7, 'ext2':8, 'ext2_n':9};

    if smplTm_microSecs<=0 or smplTm_microSecs>50e3:
        reply_info="sample time length is error!";
        return ('%d,%s'%(-1,reply_info));

    result=1;
    try:
        result=iqxel_ctrl.LP_VsaDataCapture(smplTm_microSecs*(1e-6),trig_type_dic['if'],160e6,isht40Mode);
        if result==0:
            reply_info='IQxel capture data ok!';
        else:
            reply_info='IQxel fail to capture data!';
    except:
        reply_info='Exception occur when IQxel capture data!';
    return ('%d,%s'%(result,reply_info));

def capture_free_run(smplTm_microSecs=5000,isht40Mode=0):
    '''isht40Mode:0 normal signal, 1:40M signal for 11n'''
    trig_type_dic={'auto':-6, 'free':1, 'ext':2, 'if':6, 'ext_n':7, 'ext2':8, 'ext2_n':9};

    if smplTm_microSecs<=0 or smplTm_microSecs>50e3:
        reply_info="sample time length is error!";
        return ('%d,%s'%(-1,reply_info));

    result=1;
    try:
        result=iqxel_ctrl.LP_VsaDataCapture(smplTm_microSecs*1e-6,trig_type_dic['free'],160e6,isht40Mode);
        if result==0:
            reply_info='IQxel capture data ok!';
        else:
            reply_info='IQxel fail to capture data!';
    except:
        reply_info='Exception occur when IQxel capture data!';
    return ('%d,%s'%(result,reply_info));

def analyzePower(T_interval=0,max_pow_diff_dB=0):#parament ignored
    result=1;
    try:
        result=iqxel_ctrl.LP_AnalyzePower(T_interval,max_pow_diff_dB);
        if result==0:
            reply_info='IQxel analyze power ok!';
        else:
            reply_info='IQxel fail to analyze power!';
    except:
        reply_info='Exception occur when IQxel analyze power!';
    return ('%d,%s'%(result,reply_info));

def analyzeCW():
    result=1;
    try:
        result=iqxel_ctrl.LP_AnalyzeCW();
        if result==0:
            reply_info='IQxel analyze CW ok!';
        else:
            reply_info='IQxel fail to analyze CW!';
    except:
        reply_info='Exception occur when IQxel analyze CW!';
    return ('%d,%s'%(result,reply_info));

def savesigfile(sigfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/iqxel_ctrl/capture/sig'''

    result=1;
    dirpath='./baselib/iqxel_ctrl/capture/sig/'
    try:
        result=iqxel_ctrl.LP_SaveVsaSignalFile(dirpath+sigfilename);
        if result==0:
            reply_info='Save captured data as %s ok!'%(dirpath+sigfilename);
        else:
            reply_info='Fail to save capture data as signal file!';
    except:
        reply_info='Exception occur when save capture data as signal file!';
    return ('%d,%s'%(result,reply_info));

def savemodfile(modfilename):
    '''root path at autotest.py folder, and filename will save at dir ./baselib/iqxel_ctrl/capture/mod'''

    result=1;
    dirpath='./baselib/iqxel_ctrl/capture/mod/'
    try:
        result=iqxel_ctrl.LP_SaveVsaGeneratorFile(dirpath+modfilename);
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
        result=iqxel_ctrl.LP_Analyze80211ag(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track);
        if result==0:
            reply_info='Set 11ag rx analyze parameters ok!';
        else:
            reply_info='%s'%(iqxel_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set 11ag rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11prxmethod(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track,ofdm_mode):
    result=1;
    try:
        result=iqxel_ctrl.LP_Analyze80211p(ph_corr_mode,ch_estimate,sym_tim_corr,freq_sync,ampl_track,ofdm_mode);
        if result==0:
            reply_info='Set 11p rx analyze parameters ok!';
        else:
            reply_info='%s'%(iqxel_ctrl.LP_GetErrorString(result));
    except:
       reply_info='Exception occur when set 11p rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11brxmethod(eq_taps, DCremove11b_flag, method_11b):
    try:
        result=iqxel_ctrl.LP_Analyze80211b(eq_taps,DCremove11b_flag,method_11b);
        if result==1:
            reply_info='Set 11b rx analyze parameters ok!';
        else:
            reply_info='%s'%(iqxel_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set 11b rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def set11nrxmethod(rxtype='EWC',mode='nxn',enablePhaseCorr=1,enableSymTimingCorr=1,enableAmplitudeTracking=0,
        decodePSDU=1,enableFullPacketChannelEst=0,packetFormat=1,frequencyCorr=2):
    result=1;
    try:
        result=iqxel_ctrl.LP_Analyze80211n(rxtype,mode,enablePhaseCorr,enableSymTimingCorr,enableAmplitudeTracking,
            decodePSDU,enableFullPacketChannelEst,packetFormat,frequencyCorr);
        if result==0:
            reply_info='Set 11n rx analyze parameters ok!';
        else:
            reply_info='%s'%(iqxel_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set 11n rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def setbtrxmethod(bt_data_rate=1,analysis_type='All'):
    result=1;
    try:
        print bt_data_rate,analysis_type
        result=iqxel_ctrl.LP_AnalyzeBluetooth(bt_data_rate,analysis_type);
        print result
        if result==0:
            reply_info='Set bt rx analyze parameters ok!';
        else:
            reply_info='%s'%(iqxel_ctrl.LP_GetErrorString(result));
    except:
        reply_info='Exception occur when set bt rx analyze parameters!';
    return ('%d,%s'%(result,reply_info));

def getmeasdata(iq_mode,meas_type):
    '''meas_type include 11ag,11b,11n all scalar measure result'''
    global maxsiglevel;

    ieee11ag_meas_type_lst=['psduCrcFail','plcpCrcPass','dataRate','numSymbols','numPsduBytes','dcLeakageDbc',
                    'evmAll','evmData','evmPilot','codingRate','freqErr','clockErr',
                'ampErr','ampErrDb','phaseErr','rmsPhaseNoise','rmsPowerNoGap',
                'rmsPower','pkPower','rmsMaxAvgPower','maskerr','on_time','off_time','maxrxpwr',
                'spectrumAverViolationPercentage','spectrumAverObw','valid','length'];

    #not include maxFreqErr
    ieee11b_meas_type_lst=['lockedClock','plcpCrcFail','psduCrcFail','longPreamble','numPsduBytes','bitRateInMHz',
            'evmPk','bitRate','dataRate','modType','evmAll','evmInPreamble','evmInPsdu','freqErr','clockErr','ampErr','ampErrDb',
            'phaseErr','rmsPhaseNoise','rmsPowerNoGap','rmsPower','pkPower','rmsMaxAvgPower','loLeakageDb','maskerr','on_time',
            'off_time','maxrxpwr','spectrumAverViolationPercentage','spectrumAverObw','valid','length'];

    #not include:completePacket,htSigFieldCRC,idxAnalyzedSigs,idxDataTones,idxPilotTones,preambleFreqErrorHz
    #legacyLength,legacyRate,htSig2_aggregation,htSig2_stbc,htSig2_shortGI,htSig2_numHTLF,htSig2_soundingPacket,rateInfo_modulation,
    #rateInfo_codingRate,mainPathStreamPowerDb
    ieee11n_meas_type_lst=['evmAvgAll','packetDetection','psduCRC','acquisition','demodulation','dcLeakageDbc',
            'rxRmsPowerDb','isolationDb','freqErrorHz','symClockErrorPpm','PhaseNoiseDeg_RmsAll','IQImbal_amplDb',
            'IQImbal_phaseDeg','rateInfo_bandwidthMhz','rateInfo_dataRateMbps','rateInfo_spatialStreams',
            'analyzedRange','htSig1_htLength','htSig1_mcsIndex','htSig1_bandwidth','htSig2_advancedCoding',
            'rateInfo_spaceTimeStreams','maxrxpwr','OBW_MHZ_VSA1',
            'spectrumAverViolationPercentage','spectrumAverObw','valid','length'];

    bluetooth_meas_type_list =['dataRateDetect','valid','freq_est','bandwidth20dB','P_av_each_burst','P_av_each_burst_dBm','P_pk_each_burst','P_pk_each_burst_dBm','deltaF1Average','deltaF2Max','deltaF2Average','deltaF2MaxAccess',
            'deltaF2AvAccess','EdrEVMAv','EdrEVMpk','EdrOmegaI','EdrExtremeOmega0','EdrExtremeOmegaI0','EdrEVMvalid','EdrPowDiffdB','freq_deviation','freq_deviationpktopk','freq_estHeader',
            'EdrFreqExtremeEdronly','EdrprobEVM99pass','EdrEVMvsTime','P_av_no_gap_all','validInput','maxfreqDriftRate','payloadErrors','maxPowerAcpDbm','maxPowerEdrDbm','meanNoGapPowerCenterDbm','maxrxpwr'];

    fft_meas_lst=['delta_freq','length','valid'];

    sin_wave_list=['P_peak_all_dBm','frequency'];

    meas_type_dic={'11b':ieee11b_meas_type_lst,
            '11a':ieee11ag_meas_type_lst,
            '11g':ieee11ag_meas_type_lst,
            '11p_10':ieee11ag_meas_type_lst,
            '11p_5' :ieee11ag_meas_type_lst,
            '11n_20':ieee11n_meas_type_lst,
            '11n_40':ieee11n_meas_type_lst,
            'bt' : bluetooth_meas_type_list,
            'fft':fft_meas_lst,
            'sin_wave':sin_wave_list};
    result=-99999.99;  #no correct result return

    if iq_mode not in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40','bt','fft','sin_wave']:
        print 'iq_mode include'
        reply_info='iq_mode is error!';
        return [-1,reply_info];

    if meas_type not in meas_type_dic[iq_mode]:
        reply_info='meas_type is not valid measure type!';
        return [-1,reply_info];

    try:
        if meas_type!='maxrxpwr':
            print meas_type
            result=iqxel_ctrl.LP_GetScalarMeasurement(meas_type,0);
            if iq_mode not in ['11n_20','11n_40']:
                if meas_type=='psduCrcFail':
                    result=1-result
            print result,'2323'
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
##    print res,'cecessdfdfs'
    if res[0]!=0:
        return ('%d,%s'%(res[0],res[1]));
    else:
        return ('%d,%f'%(res[0],res[1]));

def getvectdata(iq_mode,vect_type):
##    bufferReal = []
##    bufferImag = []
    #not include:freq_vector,freq_vector_time,evmSymbols
    ieee11ag_vect_type_lst=['hhEst','psdu','startPointers','plcp','spectrumMarginOffsetFreqHz','spectrumMarginDb','spectralFlatness_margin'];
    ieee11ag_vect_len_dic={'hhEst':64,'psdu':'frm_len*8','startPointers':1,'plcp':'plcp_len*8','spectrumMarginOffsetFreqHz':8,'spectrumMarginDb':8,'spectralFlatness_margin':4};

    #not include:psdu,eye,scramblerInit,plcp,freqErrTimeVect,freqErrVect
    ieee11b_vect_type_lst=['evmInPlcp','evmErr','spectrumMarginOffsetFreqHz','spectrumMarginDb'];
    ieee11b_vect_len_dic={'evmInPlcp':'sym_in_plcp_num','evmErr':'sym_num','spectrumMarginOffsetFreqHz':4,'spectrumMarginDb':4};

    #not include:CCDF_xPowerDb,CCDF_yProb,slicedSymbols,psduBits,serviceField,preambleFreqErrorTimeUs
    #legacyBits,htSig1_bits,htSig2_bits
    ieee11n_vect_type_lst=['channelEst','evmSymbols','evmTones','PhaseNoiseDeg_Symbols','demodSymbols','spectrumMarginOffsetFreqHz','spectrumMarginOffsetFreqHz','spectrumMarginDb','spectralFlatness_margin'];
    ieee11n_vect_len_dic={'channelEst':'NStreams x Ntones x NRx','evmSymbols':'NStreams x NSymbols','evmTones':'NStreams x Ntones','PhaseNoiseDeg_Symbols':'NRx x Nsymbols','demodSymbols':'NTones x NSymbols X Nstreams','spectrumMarginOffsetFreqHz':8,'spectrumMarginDb':8,'spectralFlatness_margin':4};

    bluetooth_vect_type_lst=['freq_drift','EdrExtremeOmegaIO'];
    bluetooth_vect_len_dic={'freq_drift':64,'EdrExtremeOmegaIO':64};

    fft_vect_type_lst=['x','y','xy','mask'];
    fft_vect_len_dic={'x':4096,'y':4096,'xy':4096,'mask':4096};

    vect_type_dic={'11b':ieee11b_vect_type_lst,'11a':ieee11ag_vect_type_lst,'11g':ieee11ag_vect_type_lst,'11n_20':ieee11n_vect_type_lst,'11n_40':ieee11n_vect_type_lst,'bt' :bluetooth_vect_type_lst,'fft':fft_vect_type_lst};

    vect_len_dic= {'11b':ieee11b_vect_len_dic,'11a':ieee11ag_vect_len_dic,'11g':ieee11ag_vect_len_dic,'11n_20':ieee11n_vect_len_dic,'11n_40':ieee11n_vect_len_dic,'bt':bluetooth_vect_len_dic,'fft':fft_vect_len_dic};
    result=[];


    if iq_mode not in ['11b','11g','11a','11n_20','11n_40','bt','fft']:
        reply_info='iq_mode is error!';
        return [-1,reply_info];

    if vect_type not in vect_type_dic[iq_mode]:
        reply_info='vect_type is not valid vector type!';
        return [-1,reply_info]

    vectlen_dic=vect_len_dic[iq_mode];
    vectlen=vectlen_dic[vect_type];
    print 'vect_type',vect_type
    try:
        print vect_type,vectlen
        res=iqxel_ctrl.LP_GetVectorMeasurement(vect_type,vectlen);## return a list in list!!!!!1
        print res
        if res!=-1:
##            result=res;
            result=[0]
            for i in range(0,len(res)):
                result.append(res[i][0])
            return result   ##return a list[0,......]!!!!!!
        else:
            return [-1,'data is error'];
    except:
        reply_info='Exception occur when get vector!';
        return [1,reply_info];
##    return result;  # return a list


def getvect(iq_mode,vect_type):
    res=getvectdata(iq_mode,vect_type);
    if iq_mode in ['11g','11n_20','11n_40']:
        if res[0]!=0:
            return ('%d,%s'%(res[0],res[1]));
        elif vect_type == 'spectrumMarginOffsetFreqHz':
            return ('%d,%f,%f,%f,%f,%f,%f,%f,%f'%(res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8]));
        elif vect_type == 'spectrumMarginDb':
            return ('%d,%f,%f,%f,%f,%f,%f,%f,%f'%(res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8]));
        elif vect_type == 'spectralFlatness_margin':
            return ('%d,%f,%f,%f,%f'%(res[0],res[1],res[2],res[3],res[4]));
        else:
            return ('%d,%f'%(res[0],res[1]));
    elif iq_mode in ['11b']:
        print res,'mdmdmdm'
        if res[0]!=0:
            return ('%d,%s'%(res[0],res[1]));
        elif vect_type == 'spectrumMarginOffsetFreqHz':
            return ('%d,%f,%f,%f,%f'%(res[0],res[1],res[2],res[3],res[4]));
        elif vect_type == 'spectrumMarginDb':
            return ('%d,%f,%f,%f,%f'%(res[0],res[1],res[2],res[3],res[4]));
        else:
            return ('%d,%f'%(res[0],res[1]));


def plotcapture():
    result=0;
    try:
        result=iqxel_ctrl.LP_PlotDataCapture();
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
        result=iqxel_ctrl.LP_Plot(vector_x,vector_y,plotArgs,title,xtitle,ytitle,keepPlot);
        if result==0:
            loginfo('Plot curve ok!');
        else:
            logerror('Fail to plot curve!');
    except:
        logerror('Exception occur when plot curve!');
    return result;

##def fft(iq_mode, NFFT, res_bw, window_type):
##    '''iq_mode:11b,11g,11a,11n_20,11n_40,bt
##        window_type: blackmanharris(default), hanning,flattop,rect
##                 if set to '',means to use default value
##    '''
##    result=0;
##    try:
##       result=iqxel_ctrl.LP_AnalyzeFFT(iqmod_dic[iq_mode],NFFT,res_bw,window_type);
##       if result==0:
##        print result
##        print 11111111111111111111111111111111111111111111111111111
##        loginfo('FFT analyze ok!');
##
##       else:
##      logerror('Fail to FFT analyze!');
##    except:
##       logerror('Exception occur when FFT analyze!');
##    return result;

##def fft2(technology, NFFT, res_bw):
##    '''iq_mode:11b,11g,11a,11n_20,11n_40,bt
##        window_type: blackmanharris(default), hanning,flattop,rect
##                 if set to '',means to use default value
##    '''
####    result1=0;
##    result2=0;
##    try:
####       result1=iqxel_ctrl.LP_SaveVsaSignalFile("SNR_Capture.sig");
##       result2=iqxel_ctrl.LP_AnalyzeTechnologyFFT(technology, NFFT, res_bw);
##       print  result2 ,'bbbbbbbbbbbbbbb'
##       if result2==0:
##        print result2
##        print 11111111111111111111111111111111111111111111111111111
##        loginfo('FFT analyze ok!');
##
##       else:
##      logerror('Fail to FFT analyze!');
##    except:
##       logerror('Exception occur when FFT analyze!');
##    return result2;

def fft2(technology):
    '''param[in] technology type, specify the which technology standard limit to be used;
        - 0  11ac (auto detect 20/40 Mhz bandwidth; Since 11ac is not defined in 2.4G band, will use 11n limit in 2.4G band)
        - 1  11n    (auto detect 20/40 Mhz bandwidth and 2.4G/5G band; )
        - 2  11ag
        - 3  11b
        - 4  11ac 80MHz and 160MHz
        - 99 Auto detect packet format (use when technology is unknown. Using raw data for result calculation is recommended.)
    '''
    result=1;
    try:
        result=iqxel_ctrl.LP_AnalyzeTechnologyFFT(technology);
        if result==0:
            reply_info='FFT analyze ok!';
        else:
            reply_info='Fail to FFT analyze!';
    except:
        reply_info='Exception occur when FFT analyze!';
    return ('%d,%s'%(result,reply_info));


def spmask(iq_mode):
    result=-99999.990;
    spmask_margin=[];
    try:
        result=fft(iq_mode,2048,10e4,'blackmanharris');
        if result==0:
            [ind,maskerr]=getmeasdata(iq_mode,"maskerr");
            if ind==0:
                spmask_margin=iqxel_ctrl.Get_SPmask(iqmod_dic[iq_mode]);
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
##          result=iqxel_ctrl.OFDM_LO_Results(iqmod_dic[iq_mode]);
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
    if iq_mode not in ['11g','11a','11n_20','11n_40','bt']:
        reply_info='iq_mode is error!';
        return ('%d,%s'%(-1,reply_info));

    try:
##       result=iqxel_ctrl.OFDM_Flatness_Results(iqmod_dic[iq_mode]);
        print '3333333333333333333333333333'
        result=iqxel_ctrl.OFDM_Flatness_and_LO_Results(iqmod_dic[iq_mode]);

        print result
        return ('%d,%d'%(0,result));
    except:
        reply_info='Exception occur when get flatness!';
        return ('%d,%s'%(1,reply_info));

def pwrramp(iq_mode):
    result=-99999.990;
    try:
        if iq_mode=='11b':
            result=iqxel_ctrl.LP_AnalyzePowerRamp80211b();
        else:
            result=iqxel_ctrl.LP_AnalyzePowerRampOFDM();

        if result==0:
            [indup,tmdata]=getmeasdata(iq_mode,"on_time");
            if indup==0:
                RampUp_usec=tmdata*1e6;
        else:
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
     ln3= "*     Welcom From IQxel Tester!       *\n";
     ln4= "*     Address:"+servaddr[0]+" Port:"+str(servaddr[1])+" *\n";
     ln5= "*                                      *\n";
     ln6= "****************************************\n";

     prnstr=ln1+ln2+ln3+ln4+ln5+ln6;
     que.sendall(prnstr);
     que.sendall('IQxel');# used to identify IQxel or WT-200 or IQview

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
            elif cmd_lst[0]=='fft':
                reply=fft2(int(cmd_lst[1]));
            elif cmd_lst[0]=='init':
                reply=init();
            elif cmd_lst[0]=='open':
                reply=open_instru(_ipaddr=(cmd_lst[1]));
            elif cmd_lst[0]=='close':
                reply=close();
            elif cmd_lst[0]=='setvsg':
                reply=setvsg(float(cmd_lst[1]),float(cmd_lst[2]),int(cmd_lst[3]));
##         elif cmd_lst[0]=='setvsg_left':
##        reply=setvsg_left(float(cmd_lst[1]),float(cmd_lst[2]));
            elif cmd_lst[0]=='setrate':
                reply=setrate(cmd_lst[1]);
            elif cmd_lst[0]=='txfrmcnt':
                reply=txfrmcnt(int(cmd_lst[1],10));
            elif cmd_lst[0]=='txenable':
                reply=txenable(int(cmd_lst[1],10));
            elif cmd_lst[0]=='txcw':
                reply=txcw(float(cmd_lst[1]),float(cmd_lst[2]),int(cmd_lst[3]));
##      elif cmd_lst[0]=='txcw_left':
##        reply=txcw_left(float(cmd_lst[1]),float(cmd_lst[2]));
            elif cmd_lst[0]=='setvsa':
                reply=setvsa(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]),int(cmd_lst[4]),int(cmd_lst[5]));
##         elif cmd_lst[0]=='setvsa_right':
##        reply=setvsa_right(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
            elif cmd_lst[0]=='setvsa_bt':
                reply=setvsa_bt(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]),int(cmd_lst[4]));
##      elif cmd_lst[0]=='setvsa_bt_right':
##        reply=setvsa_bt_right(float(cmd_lst[1]),float(cmd_lst[2]),float(cmd_lst[3]));
            elif cmd_lst[0]=='capture':
                reply=capture(float(cmd_lst[1]),int(cmd_lst[2]),int(cmd_lst[3]));
            elif cmd_lst[0]=='capture_free_run':
                reply=capture_free_run(float(cmd_lst[1]),int(cmd_lst[2]));
            elif cmd_lst[0]=='analyzePower':
                reply=analyzePower();
            elif cmd_lst[0]=='analyzeCW':
                reply=analyzeCW();
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
                reply='IQxel have no such command!';
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
            que= serverOpen('IQxel',34000);
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
