#Filename: iqv.py
from baselib.loglib.log_lib import *
import time
from baselib.plot import *
from baselib.test_channel import *
from rftest.rflib import rfglobal
#--------------------------------------------
# In Shell, some commands already registered:
# iqview_ctrl.open(), return handler
#---------------------------------------------
class tester:
    iqv_port_dic={'off':1,'left':2,'right':3};
    iqmod_dic={'11b':0,'11g':1,'11a':2,'11n_20':3,'11n_40':4,'bt':5};
    iq_mode='11g';
    data_rate='1m';
    frmcnt=0;
    txpwr=-15;
    rxmaxpwr=0;
    ex_att=2.5;
    txrf_freqMhz=2484;
    rxrf_freqMhz=2484;
    rate_dic     = {
        'lr_0_0.125m' :'11b', 'lr_1_0.25m' :'11b', 'lr_2_0.5m' :'11b' ,'lr_3_0.25m' :'11b' ,
        'lr_4_0.5m'   :'11b', 'lr_5_1m'    :'11b', 'lr_6_0.25m':'11b' ,'lr_7_0.5m'  :'11b' ,
        '1m'   :'11b', '2m'   :'11b', '5.5m' :'11b', '11m'  :'11b',
                       '2ml'  :'11b', '5.5ml':'11b', '11ml' :'11b',
                       '2ms'  :'11b', '5.5ms':'11b', '11ms' :'11b',
        '6m'   :'11g', '9m'   :'11g', '12m'  :'11g', '18m'  :'11g',
        '24m'  :'11g', '36m'  :'11g', '48m'  :'11g', '54m'  :'11g',
	'3m_10'  :'11p_10', '4.5m_10' :'11p_10', '6m_10'  :'11p_10', '9m_10'  :'11p_10',
	'12m_10' :'11p_10', '18m_10'  :'11p_10', '24m_10' :'11p_10', '27m_10' :'11p_10',
	'1.5m_5' :'11p_5',  '2.25m_5' :'11p_5',  '3m_5'   :'11p_5',  '4.5m_5' :'11p_5',
	'6m_5'   :'11p_5',  '9m_5'    :'11p_5',  '12m_5'  :'11p_5',  '13.5m_5':'11p_5',
        'mcs0' :'11n_20', 'mcs1' :'11n_20', 'mcs2' :'11n_20', 'mcs3' :'11n_20',
        'mcs4' :'11n_20', 'mcs5' :'11n_20', 'mcs6' :'11n_20', 'mcs7' :'11n_20',
        'mcs0_40' :'11n_40', 'mcs1_40' :'11n_40', 'mcs2_40' :'11n_40', 'mcs3_40' :'11n_40', 'mcs4_40' :'11n_40',
        'mcs5_40' :'11n_40', 'mcs6_40' :'11n_40', 'mcs7_40' :'11n_40', 'mcs32'   :'11n_40', 'mcs32_40':'11n_40',
        'mcs0_sgi' :'11n_20', 'mcs1_sgi' :'11n_20', 'mcs2_sgi' :'11n_20', 'mcs3_sgi' :'11n_20',
        'mcs4_sgi' :'11n_20', 'mcs5_sgi' :'11n_20', 'mcs6_sgi' :'11n_20', 'mcs7_sgi' :'11n_20',
        'mcs0_40_sgi' :'11n_40', 'mcs1_40_sgi' :'11n_40', 'mcs2_40_sgi' :'11n_40', 'mcs3_40_sgi' :'11n_40', 'mcs4_40_sgi' :'11n_40',
        'mcs5_40_sgi' :'11n_40', 'mcs6_40_sgi' :'11n_40', 'mcs7_40_sgi' :'11n_40', 'mcs32_sgi'   :'11n_40', 'mcs32_40_sgi':'11n_40',
        'test' : '11n_20',
        'tone' : 'sin_wave',
        '1M_DH1_1010':'bt','1M_DH1_00001111':'bt','1M_DH1_prbs9':'bt','1M_DH3_1010':'bt','1M_DH3_00001111':'bt',
        '1M_DH3_prbs9':'bt','1M_DH5_1010':'bt','1M_DH5_00001111':'bt','1M_DH5_prbs9':'bt',
        '2M_DH1_1010':'bt','2M_DH1_00001111':'bt','2M_DH1_prbs9':'bt','2M_DH3_1010':'bt','2M_DH3_00001111':'bt','2M_DH3_prbs9':'bt',
        '2M_DH5_1010':'bt','2M_DH5_00001111':'bt','2M_DH5_prbs9':'bt', '3M_DH1_1010':'bt','3M_DH1_00001111':'bt','3M_DH1_prbs9':'bt',
        '3M_DH3_1010':'bt','3M_DH3_00001111':'bt','3M_DH3_prbs9':'bt','3M_DH5_1010':'bt','3M_DH5_00001111':'bt','3M_DH5_prbs9':'bt',
        'LE_1010':'bt','LE_00001111':'bt','LE_prbs9':'bt'

    };

    #for tx, chan_est is repeat num
    #mode: {measure, source,cw}
    #testpara: to source, it is frmcount
    #          to cw, no sense
    #          to measure, it is para_str list, default set to ''
    def __init__(self,rf_freqMhz,pwr,data_rate,testpara='',unit_no=1,mode='measure',ex_att=0,timeout=10,isreset=1,auto_range=1,trigpretime=20):

        rfglobal.iqv_arg= {
          "rf_freq":    rf_freqMhz,
          "pwr":        pwr,
          "data_rate":  data_rate,
          "chan_est":   testpara,
          "unit_no":    unit_no,
          "mode":       mode,
          "ex_att":     ex_att,
          "timeout":    timeout,
          "auto_range": auto_range,
          "trigpretime":trigpretime,  ## bt=150us,wifi=20us
          }
    #11agp rxmode param
        self.ph_corr_mode     = 'sym_by_sym'
        self.ch_estimate      = 'raw_long'
        self.sym_tim_corr     = 'on'
        self.freq_sync        = 'long_train'
        self.ampl_track       = 'off'
    #11p rxmode param
    	self.ofdm_mode        = 'half'
    #11b rxmode param
        self.eq_taps          = '5_taps'
        self.DCremove11b_flag = 'off'
        self.method_11b       = 'std_tx_gac'

    #11n rxmode param
        self.rxtype           = 'EWC'
        self.mode             = 'nxn'
        self.enablePhaseCorr  = 1
        self.enableSymTimingCorr = 1
        self.enableAmplitudeTracking = 0
        self.decodePSDU       = 1
        self.enableFullPacketChannelEst = 0
        self.packetFormat     = 'mixed'
        self.frequencyCorr    = 'ltf'

    #bt mode param
        self.bt_data_rate        = '1M_BDR'
        self.analysis_type    = 'All'

##        try:
        if isreset==1:
            self.reset();
        if mode=='source':
            if testpara!='':
                frmcnt=testpara;
            else:
                frmcnt=100;
            self.sigout(rf_freqMhz,pwr,ex_att,data_rate,frmcnt,unit_no);
        elif mode=='measure':
            self.rxmaxpwr=pwr;
            self.ex_att=ex_att;
            self.rxrf_freqMhz=rf_freqMhz;
            self.iq_mode=self.rate_dic[data_rate];

            self.setvsa(rf_freqMhz,pwr,ex_att,unit_no,auto_range,self.iq_mode);
            time.sleep(0.5)
            self.capture(5000,0,auto_range,trigpretime);
            #self.setvsa(rf_freqMhz,-100,ex_att);
            self.iq_mode=self.rate_dic[data_rate];
            print self.iq_mode
            if self.iq_mode=='11b':
                if testpara!='':
                    self.set11brxmethod(testpara[0],testpara[1],testpara[2]);
                else:
                    self.set11brxmethod('','','');
            elif self.iq_mode=='11g':
                if testpara!='':
                    self.set11agrxmethod(testpara[0],testpara[1],testpara[2],testpara[3],testpara[4]);
                else:
                    self.set11agrxmethod('','','','','');
            elif self.iq_mode=='11p_10' or self.iq_mode=='11p_5':
                if testpara!='':
                    self.set11prxmethod(testpara[0],testpara[1],testpara[2],testpara[3],testpara[4],testpara[5]);
                else:
                    self.set11prxmethod('','','','','','');
            elif self.iq_mode=='bt':
                if testpara!='':
                    self.setbtrxmethod(testpara[0],testpara[1]);
                else:
                    self.setbtrxmethod('','');
            elif self.iq_mode=='11n_20' or self.iq_mode=='11n_40':
                if testpara!='':
                    self.set11nrxmethod(testpara[0],testpara[1],testpara[2],testpara[3],testpara[4],testpara[5],testpara[6],testpara[7],testpara[8]);
                else:
                    self.set11nrxmethod('','','','','','','','','');
            else:
                self.capture_free_run(5000)
            self.capture(5000,0,auto_range,trigpretime);
        else:
            self.txrf_freqMhz=rf_freqMhz;
            self.txpwr=pwr;
            self.ex_att=ex_att;
            self.txcw(rf_freqMhz,pwr,unit_no);
            self.txenable(1);

##        except:
##            logerror("Fail to operate tester!");
##            return;

        return;

    def print_setting(self):
        if self.iq_mode in ['11g','11a']:
            print "ph_corr_mode              =", self.ph_corr_mode
            print "ch_estimate               =", self.ch_estimate
            print "sym_time_corr             =", self.sym_tim_corr
            print "freq_sync                 =", self.freq_sync
            print "ampl_track                =", self.ampl_track
        elif self.iq_mode in ['11p_10','11p_5']:
            print "ph_corr_mode              =", self.ph_corr_mode
            print "ch_estimate               =", self.ch_estimate
            print "sym_time_corr             =", self.sym_tim_corr
            print "freq_sync                 =", self.freq_sync
            print "ampl_track                =", self.ampl_track
            print "ofdm_mode                 =", self.ofdm_mode
        elif self.iq_mode=='11b':
            print "eq_taps                   =", self.eq_taps
            print "DCremove11b_flag          =", self.DCremove11b_flag
            print "method_11b                =", self.method_11b
        elif self.iq_mode=='bt':
            print "bt_data_rate              =",  self.bt_data_rate
            print "analysis_type             =",  self.analysis_type
        else:
            print "rxtype                    =", self.rxtype
            print "mode                      =", self.mode
            print "enablPhaseCorr            =", self.enablePhaseCorr
            print "enableSymTimingCorr       =", self.enableSymTimingCorr
            print "decodePSDU                =", self.decodePSDU
            print "packetFormet              =", self.packetFormat
            print "frequencyCorr             =", self.frequencyCorr
            print "enableAmplitudeTracking   =", self.enableAmplitudeTracking
            print "enablFullPacketChannelEst =", self.enableFullPacketChannelEst

    def run_setcmd(self,cmd_ln):
        result=sock.req(cmd_ln);
        res_lst=result.split(',');
        res_lst[0]=int(res_lst[0],10);
        #loginfo(res_lst[1]);
        return res_lst[0];

    def run_getcmd(self,cmd_ln):
        result=sock.req(cmd_ln);
        res_lst=result.split(',');
        res_lst[0]=int(res_lst[0],10);
        if res_lst[0]!=0:
           #loginfo(res_lst[1]);
            return 'NAV';
        else:
            res=[float(data) for data in res_lst[1:]];
            if len(res_lst)>2:
                return res;
            else:
                return res[0];

    def reset(self):
        return self.run_setcmd("reset");

    def init(self):
        return self.run_setcmd("init");

    def open(self):
        return self.run_setcmd("open");

    def close(self):
        return self.run_setcmd("close");

    def setvsg(self,freqMhz,pwrdBm,unit_no):
        return self.run_setcmd("setvsg %f %f %d"%(freqMhz,pwrdBm,unit_no));

##    def setvsg_left(self,freqMhz,pwrdBm):
##        return self.run_setcmd("setvsg_left %f %f"%(freqMhz,pwrdBm));

    def setrate(self,rate):
        return self.run_setcmd("setrate %s"%rate);

    def txfrmcnt(self,frmcnt):
        return self.run_setcmd("txfrmcnt %d"%frmcnt);

    def txenable(self,enable):
        return self.run_setcmd("txenable %d"%enable);

    def txcw(self,freqMhz,pwrdBm,unit_no):
        pwrdBm += self.ex_att
        return self.run_setcmd("txcw %f %f %d"%(freqMhz,pwrdBm,unit_no));

##    def txcw_left(self,freqMhz,pwrdBm):
##        return self.run_setcmd("txcw_left %f %f"%(freqMhz,pwrdBm));

    def attencfg(self,att_value):
        return self.txcw(self.txrf_freqMhz,self.txpwr-att_value,unit_no);

    def setvsa(self,freqMhz,rxmaxpwr,exAttenDb,unit_no,auto_range,iq_mode):
        return self.run_setcmd("setvsa %f %f %f %d %d %s"%(freqMhz,rxmaxpwr,exAttenDb,unit_no,auto_range,iq_mode));

    def SetLargePowerIFGSwitch(self,swState=1):
        return self.run_setcmd("SetLargePowerIFGSwitch %d "%(swState))

##    def setvsa_right(self,freqMhz,rxmaxpwr,exAttenDb):
##        return self.run_setcmd("setvsa_right %f %f %f"%(freqMhz,rxmaxpwr,exAttenDb));

    def setvsa_bt(self,freqMhz,rxmaxpwr,exAttenDb,unit_no):
        return self.run_setcmd("setvsa_bt %f %f %f %d"%(freqMhz,rxmaxpwr,exAttenDb,unit_no));

##    def setvsa_bt_right(self,freqMhz,rxmaxpwr,exAttenDb):
##        return self.run_setcmd("setvsa_bt_right %f %f %f"%(freqMhz,rxmaxpwr,exAttenDb));

    def capture(self,smplTm_microSecs=5000,isht40Mode=0,auto_range=1,trigpretime=20):
        return self.run_setcmd("capture %f %d %d %d"%(smplTm_microSecs,isht40Mode,auto_range,trigpretime));

    def capture_free_run(self,smplTm_microSecs=5000,isht40Mode=0):
        return self.run_setcmd("capture_free_run %f %d"%(smplTm_microSecs,isht40Mode));

    def analyzePower(self,T_interval=0,max_pow_diff_dB=0):
        return self.run_setcmd("analyzePower %f %f"%(T_interval,max_pow_diff_dB));

    def analyzeCW(self):
        return self.run_setcmd("analyzeCW")

    def restart(self,smplTm_microSecs=5000,isht40Mode=0,auto_range=1,trigpretime=20):
        self.capture(smplTm_microSecs,isht40Mode,auto_range,trigpretime);
        self.restorerxmode(self.iq_mode);



    iqv_ph_corr_dic={'off':1,            #Indicates that Phase correction is off,
             'sym_by_sym':2,     #Indicates symbol-by-symbol correction. default value
             'moving_avg':3      #Indicates moving avg. correction
                    };

    iqv_ch_est_dic= {'raw':1,      #Raw Channel Estimate on long training field
                     'raw_long':1, #long train.
                     '2nd_ord': 2, #2nd Order Polyfit.
                     'raw_full':3  #Raw Channel Estimate on full packet
                    };

    iqv_sym_tim_dic={'off':1,  #Symbol Timing Correction Off.
             'on': 2   #Symbol Timing Correction On
                    };

    iqv_freq_sync_dic={    'short_train':1, #Indicates frequency synchronization on short training symbol
                        'long_train' :2, #Indicates frequency synchronization on short and long training symbol
                        'full_packet':3  #Indicates frequency synchronization on full data packet
                    };

    iqv_ampl_track_dic={'off':1,     #Amplitude tracking off.
                'on' : 2     #Amplitude tracking on
                       };

    def set11agrxmethod(self, ph_corr_mode = '', ch_estimate  = '', sym_tim_corr = '', freq_sync    = '', ampl_track   = ''):

        if ph_corr_mode !='': self.ph_corr_mode = ph_corr_mode
        if ch_estimate  !='': self.ch_estimate  = ch_estimate
        if sym_tim_corr !='': self.sym_tim_corr = sym_tim_corr
        if freq_sync    !='': self.freq_sync    = freq_sync
        if ampl_track   !='': self.ampl_track   = ampl_track

        cmd_ln = "set11agrxmethod %d %d %d %d %d" % ( \
            self.iqv_ph_corr_dic[self.ph_corr_mode]  ,
            self.iqv_ch_est_dic[self.ch_estimate]    ,
            self.iqv_sym_tim_dic[self.sym_tim_corr]  ,
            self.iqv_freq_sync_dic[self.freq_sync]   ,
            self.iqv_ampl_track_dic[self.ampl_track]
        )
        return self.run_setcmd(cmd_ln)

    iqv_ofdm_mode_dic={'half' : 2, # 11p-10M
		       'quar' : 3  # 11p-5m
					   };
    def set11prxmethod(self, ph_corr_mode = '', ch_estimate  = '', sym_tim_corr = '', freq_sync    = '', ampl_track   = '', ofdm_mode   = ''):

        if ph_corr_mode !='': self.ph_corr_mode = ph_corr_mode
        if ch_estimate  !='': self.ch_estimate  = ch_estimate
        if sym_tim_corr !='': self.sym_tim_corr = sym_tim_corr
        if freq_sync    !='': self.freq_sync    = freq_sync
        if ampl_track   !='': self.ampl_track   = ampl_track
        if ofdm_mode    !='': self.ofdm_mode    = ofdm_mode

        cmd_ln = "set11prxmethod %d %d %d %d %d %d" % ( \
            self.iqv_ph_corr_dic[self.ph_corr_mode]  ,
            self.iqv_ch_est_dic[self.ch_estimate]    ,
            self.iqv_sym_tim_dic[self.sym_tim_corr]  ,
            self.iqv_freq_sync_dic[self.freq_sync]   ,
            self.iqv_ampl_track_dic[self.ampl_track]   ,
            self.iqv_ofdm_mode_dic[self.ofdm_mode]
        )
        return self.run_setcmd(cmd_ln)

    #11b vsa set functions
    iqv_eq_dic= {'off':1,    #Equalizer Off.
                 '5_taps':5, #5 taps equalizer(default)
                 '7_taps':7, #7 taps equalizer.
                 '9_taps':9  #9 taps equalizer.
        };
    iqv_dc_removal_dic={'off':0,    #DC removal Off(default)
                        'on' :1     #DC removal On.
                       };
    iqv_11b_method_dic={'std_tx_gac': 1,    #Use 11b standard TX accuracy(default)
                        'rms_error_vect': 2 #Use 11b RMS error vector.
                       };

    def set11brxmethod(self,
            eq_taps          = '',
            DCremove11b_flag = '',
            method_11b       = ''
        ):

        if eq_taps          !='': self.eq_taps = eq_taps
        if DCremove11b_flag !='': self.DCremove11b_flag = DCremove11b_flag
        if method_11b       !='': self.method_11b = method_11b

        return self.run_setcmd("set11brxmethod %d %d %d" % (
            self.iqv_eq_dic[self.eq_taps],
            self.iqv_dc_removal_dic[self.DCremove11b_flag],
            self.iqv_11b_method_dic[self.method_11b]
        ))


    type_lst=['EWC','11a'];
    mode_lst=['nxn','composite','sequential_mimo'];
    packet_format_dic={'auto_detect':0, 'mixed':1, 'greenfield':2};
    freq_corr_dic={'ltf':2,     #frequency correction on short and long legacy training fields
           'full':3,    #frequency correction based on full packet
           'ltf_sig':4  #frequency correction on signal fields (legacy and HT) in addition to short and long training fields
          };

    def set11nrxmethod(self,
        rxtype='',
        mode='',
        enablePhaseCorr='',
        enableSymTimingCorr='',
        enableAmplitudeTracking='',
        decodePSDU='',
        enableFullPacketChannelEst='',
        packetFormat='',
        frequencyCorr=''
        ):
        if rxtype!='': self.rxtype=rxtype;
        if mode!='': self.mode=mode;
        if enablePhaseCorr!='': self.enablePhaseCorr=enablePhaseCorr;
        if enableSymTimingCorr!='': self.enableSymTimingCorr=enableSymTimingCorr;
        if enableAmplitudeTracking!='': self.enableAmplitudeTracking=enableAmplitudeTracking;
        if decodePSDU!='': self.decodePSDU=decodePSDU;
        if enableFullPacketChannelEst!='': self.enableFullPacketChannelEst=enableFullPacketChannelEst;
        if self.packetFormat!='': self.packetFormat=packetFormat;
        if frequencyCorr!='': self.frequencyCorr=frequencyCorr;

        return self.run_setcmd("set11nrxmethod %s %s %d %d %d %d %d %d %d" % (
                self.rxtype,
                self.mode,
                self.enablePhaseCorr,
                self.enableSymTimingCorr,
                self.enableAmplitudeTracking,
                self.decodePSDU,
                self.enableFullPacketChannelEst,
                self.packet_format_dic[packetFormat],
                self.freq_corr_dic[frequencyCorr]
        ));


    def setbtrxmethod(self, bt_data_rate,analysis_type):
        if bt_data_rate !='': self.bt_data_rate = bt_data_rate;
        if analysis_type!='': self.analysis_type = analysis_type;
        print self.bt_data_rate,self.analysis_type
        return self.run_setcmd("setbtrxmethod %d %s" % (
                self.bt_data_rate ,
                self.analysis_type));

    def restorerxmode(self,iq_mode):
        if iq_mode=='11b':
            self.set11brxmethod(self.eq_taps,self.DCremove11b_flag,self.method_11b);
        elif iq_mode in ['11a','11g']:
            self.set11agrxmethod(self.ph_corr_mode,self.ch_estimate,self.sym_tim_corr,self.freq_sync,self.ampl_track);
        elif iq_mode in ['11p_10','11p_5']:
            self.set11prxmethod(self.ph_corr_mode,self.ch_estimate,self.sym_tim_corr,self.freq_sync,self.ampl_track,self.ofdm_mode);
        elif iq_mode == 'bt':
            self.setbtrxmethod(self.bt_data_rate,self.analysis_type);
        else:
            self.set11nrxmethod(self.rxtype,self.mode,self.enablePhaseCorr,self.enableSymTimingCorr,self.enableAmplitudeTracking,
            self.decodePSDU,self.enableFullPacketChannelEst,self.packetFormat,self.frequencyCorr);
        return;

##    def fft(self,technology=99, NFFT=0, res_bw=100000):
##        return self.run_getcmd("fft2 %f %f %f"%(technology, NFFT, res_bw));

##    def fft(self, NFFT=0, res_bw=100000, window_type):
##        return self.run_getcmd("fft2 %d %d %s"%(NFFT, res_bw, window_type));

    def fft(self,technology=3):
        result=self.run_setcmd("fft %d"%(technology));
        return result;



    def getmeas(self,iq_mode,meas_type):
        return self.run_getcmd('getmeas %s %s'%(iq_mode,meas_type));

    def getvect(self,iq_mode,vect_type):
        return self.run_getcmd('getvect %s %s'%(iq_mode,vect_type));


    def spmask(self,iq_mode):
        result=self.run_getcmd('spmask %s'%iq_mode);
        self.restorerxmode(self.iq_mode);
        return result;

    def spec(self,iq_mode):
        oldloglvl=loggetlevel();
        logsetlevel('INFO');
        result= self.run_getcmd('spec %s'%iq_mode);
        logsetlevel(oldloglvl);
        self.restorerxmode(self.iq_mode);
        return result;

    def loleakage(self,iq_mode):
        self.restorerxmode(iq_mode);
        return self.run_getcmd('loleakage %s'%iq_mode);

    def isflat(self,iq_mode):
        self.restorerxmode(iq_mode);
        result = self.run_getcmd('isflat %s'%iq_mode);
        return result;

    def pwrramp(self,iq_mode):
        self.restorerxmode(self.iq_mode);
        result=self.run_getcmd('pwrramp %s'%iq_mode);
        return result;

    def get_vect_result(self, vect_type):
        if self.iq_mode in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40','bt']:
            if vect_type=='spectrumMarginOffsetFreqHz':
                result=self.getvect(self.iq_mode, 'spectrumMarginOffsetFreqHz');
            elif vect_type=='spectrumMarginDb':
                result=self.getvect(self.iq_mode, 'spectrumMarginDb');
            elif vect_type=='spectralFlatness_margin':
                result=self.getvect(self.iq_mode, 'spectralFlatness_margin');
            elif vect_type=='maxPowerAcpDbm':
                result=self.getvect(self.iq_mode,'maxPowerAcpDbm');
            elif vect_type=='maxPowerAcpFreqHz':
                result=self.getvect(self.iq_mode,'maxPowerAcpFreqHz');

        if result!='NAV':
            return result;
        else:
            return 'NAV';

    def get_result(self,mea_type,data_type='AVER',uint_no=1):
        if self.iq_mode in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40']:
            if mea_type=='maxrxpwr':
                result=self.getmeas(self.iq_mode,'maxrxpwr');
            elif mea_type=='BUR_PWR':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5']:
                    result=self.getmeas(self.iq_mode,'rmsPowerNoGap');
                else:
                    result=self.getmeas(self.iq_mode,'rxRmsPowerDb');
            elif mea_type=='EVM_ALL':
                if self.iq_mode in ['11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'evmAvgAll');
                else:
                    result=self.getmeas(self.iq_mode,'evmAll');
            elif mea_type=='EVM_RMS':
                resultdB=self.getmeas(self.iq_mode,'evmAll');
                result=10**(resultdB/10);
            elif mea_type=='GAIN_IMB':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5']:
                    result=self.getmeas(self.iq_mode,'ampErrDb');
                else:
                    result=self.getmeas(self.iq_mode,'IQImbal_amplDb');
            elif mea_type=='QUADERR':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5']:
                    result=self.getmeas(self.iq_mode,'phaseErr');
                else:
                    result=self.getmeas(self.iq_mode,'IQImbal_phaseDeg');
            elif mea_type=='FREQ_ERR':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5']:
                    result=self.getmeas(self.iq_mode,'freqErr');
                else:
                    result=self.getmeas(self.iq_mode,'freqErrorHz');
            elif mea_type=='CLK_ERR':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5']:
                    result=self.getmeas(self.iq_mode,'clockErr');
                else:
                    result=self.getmeas(self.iq_mode,'symClockErrorPpm');
##            elif mea_type=='IQ_OFF':
##                result=self.loleakage(self.iq_mode);
            elif mea_type=='IQ_OFF':
                if self.iq_mode in ['11b']:
                    result=self.getmeas(self.iq_mode,'loLeakageDb');
                else:
                    result=self.getmeas(self.iq_mode,'dcLeakageDbc');
            elif mea_type=='RAMP_UP_DOWN':
                if self.iq_mode in ['11b']:
                    rampup,rampdown = self.pwrramp(self.iq_mode);
            elif mea_type=='valid':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'valid');
            elif mea_type=='length':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'length');
            elif mea_type=='spectrumAverViolationPercentage':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'spectrumAverViolationPercentage');
            elif mea_type=='spectrumAverObw':
                if self.iq_mode in ['11b','11g','11a','11p_10','11p_5','11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'spectrumAverObw')
            elif mea_type=='flatness_passed_wt200':
                if self.iq_mode in ['11g','11a','11p_10','11p_5','11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'flatness_passed_wt200')
            elif mea_type=='DATA_RATE':
                if self.iq_mode in ['11g','11a','11p_10','11p_5']:
                    result=self.getmeas(self.iq_mode,'dataRate')
                elif self.iq_mode in ['11b']:
                    result=self.getmeas(self.iq_mode,'bitRate')
                elif self.iq_mode in ['11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'rateInfo_dataRateMbps')
            elif mea_type=='PSDU_CRC':
            	if self.iq_mode in ['11g','11a','11p_10','11p_5','11b']:
                    result=1-self.getmeas(self.iq_mode,'psduCrcFail')
            	elif self.iq_mode in ['11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'psduCRC')
            elif mea_type=='PSDU_LEN':
            	if self.iq_mode in ['11g','11a','11p_10','11p_5','11b']:
                    result=self.getmeas(self.iq_mode,'numPsduBytes')
            	elif self.iq_mode in ['11n_20','11n_40']:
                    result=self.getmeas(self.iq_mode,'htSig1_htLength')
            elif mea_type=='PK_PWR':
            	if self.iq_mode in ['11g','11a','11p_10','11p_5','11b']:
                    result=self.getmeas(self.iq_mode,'pkPower')
        else:

            if mea_type=='dataRateDetect':
                result=self.getmeas(self.iq_mode,'dataRateDetect');
            if mea_type=='valid':
                result=self.getmeas(self.iq_mode,'valid');
            if mea_type=='bandwidth20dB':
                result=self.getmeas(self.iq_mode,'bandwidth20dB');
            if mea_type=='P_av_each_burst_dBm':
                result=self.getmeas(self.iq_mode,'P_av_each_burst_dBm');
            if mea_type=='P_av_each_burst':
                result=self.getmeas(self.iq_mode,'P_av_each_burst');
            if mea_type=='P_peak_all_dBm':
                result=self.getmeas(self.iq_mode,'P_peak_all_dBm');
            if mea_type=='P_pk_each_burst_dBm':
                result=self.getmeas(self.iq_mode,'P_pk_each_burst_dBm');
            if mea_type=='P_pk_each_burst':
                result=self.getmeas(self.iq_mode,'P_pk_each_burst');
            if mea_type=='frequency':
                result=self.getmeas(self.iq_mode,'frequency');
            if mea_type=='freq_est':
                result=self.getmeas(self.iq_mode,'freq_est');
            if mea_type=='freq_drift':
                result=self.getmeas(self.iq_mode,'freq_drift');
            if  mea_type=='deltaF1Average':
                result=self.getmeas(self.iq_mode,'deltaF1Average');
            if  mea_type=='deltaF2Max':
                result=self.getmeas(self.iq_mode,'deltaF2Max');
            if  mea_type=='deltaF2Average':
                result=self.getmeas(self.iq_mode,'deltaF2Average');
            if mea_type=='deltaF2MaxAccess':
                result=self.getmeas(self.iq_mode,'deltaF2MaxAccess');
            if mea_type=='deltaF2AvAccess':
                result=self.getmeas(self.iq_mode,'deltaF2AvAccess');
            if mea_type=='EdrEVMvalid':
                result=self.getmeas(self.iq_mode,'EdrEVMvalid');
            if mea_type=='EdrPowDiffdB':
                result=self.getmeas(self.iq_mode,'EdrPowDiffdB');

            if  mea_type=='EdrEVMAv':
                result=self.getmeas(self.iq_mode,'EdrEVMAv');
            if  mea_type=='EdrEVMpk':
                result=self.getmeas(self.iq_mode,'EdrEVMpk');

            if mea_type=='freq_deviation':
                result=self.getmeas(self.iq_mode,'freq_deviation');
            if mea_type=='freq_deviationpktopk':
                result=self.getmeas(self.iq_mode,'freq_deviationpktopk');
            if mea_type=='EdrFreqExtremeEdronly':
                result=self.getmeas(self.iq_mode,'EdrFreqExtremeEdronly');
            if mea_type=='EdrprobEVM99pass':
                result=self.getmeas(self.iq_mode,'EdrprobEVM99pass');
            if mea_type=='EdrEVMvsTime':
                result=self.getmeas(self.iq_mode,'EdrEVMvsTime');
            if mea_type=='validInput':
                result=self.getmeas(self.iq_mode,'validInput');
            if mea_type=='maxfreqDriftRate':
                result=self.getmeas(self.iq_mode,'maxfreqDriftRate');
            if mea_type=='EdrOmegaI':
                result=self.getmeas(self.iq_mode,'EdrOmegaI');
            if mea_type=='EdrExtremeOmega0':
                result=self.getmeas(self.iq_mode,'EdrExtremeOmega0');
            if mea_type=='EdrExtremeOmegaI0':
                result=self.getmeas(self.iq_mode,'EdrExtremeOmegaI0');
            if mea_type=='payloadErrors':
                result=self.getmeas(self.iq_mode,'payloadErrors');
            if mea_type=='maxPowerAcpDbm':
                result=self.getmeas(self.iq_mode,'maxPowerAcpDbm');
            if mea_type=='maxPowerAcpFreqHz':
                result=self.getmeas(self.iq_mode,'maxPowerAcpFreqHz');
            if mea_type=='maxPowerEdrDbm':
                result=self.getmeas(self.iq_mode,'maxPowerEdrDbm');
            if mea_type=='meanNoGapPowerCenterDbm':
                result=self.getmeas(self.iq_mode,'meanNoGapPowerCenterDbm');
            if mea_type=='sequenceDefinition':
                result=self.getmeas(self.iq_mode,'sequenceDefinition');
            if mea_type=='sequenceDefinition':
                result=self.getmeas(self.iq_mode,'sequenceDefinition');
            if mea_type=='acpErrValid':
                result=self.getmeas(self.iq_mode,'acpErrValid');


        if result!='NAV':
            return '%4.2f'%result;
        else:
            return '0';


    def read_spmsk(self,data_type='AVER',unit_no=1):
        result=self.spmask(self.iq_mode);
        if result=='NAV':
            return [];
        else:
            return [-1*data for data in result];

    def read_spec(self,data_type='AVER',plot_en=1,unit_no=1):
        result=self.spec(self.iq_mode);
        if result=='NAV':
            return [];
        else:
            if plot_en==1:
                x=range(0,len(result));
                myplot.plot_curve(x,result,'Pwr','freq','amp','Spectrum');
        return result;

    def fcc(self,iq_mode,pwr_lmt=-41,freq_zone=12.5):
        result=self.run_getcmd('fcc %s %f %f'%(iq_mode,pwr_lmt,freq_zone));
        self.restorerxmode(self.iq_mode);
        return result;

    #bur_pwr and mode not need, keep for compatible with cmw
    def fcc_check(self,bur_pwr=-10,mode='11b',pwr_lmt=-41,freq_zone=12.5):
        res=self.fcc(self.iq_mode,pwr_lmt,freq_zone);
        if res=='NAV':
            return ['NAV','NAV','NAV'];

        if res[0]==0:
            check='PASS';
        else:
           check='FAIL';
        return [check,(res[1],res[2]),(res[3],res[4])];

    def sigout(self,rf_freqMhz,pwr,ex_att,data_rate,frmcnt,unit_no):
##        self.SetLargePowerIFGSwitch(1)
        self.setvsg(rf_freqMhz,pwr+ex_att,unit_no);
##        if unit_no==1:
##            self.setvsg(rf_freqMhz,pwr+ex_att);
##        else:
##            self.setvsg_left(rf_freqMhz,pwr+ex_att);
        self.setrate(data_rate);
        self.txenable(1);
        self.frmcnt=frmcnt;
        self.txpwr=pwr;
        self.ex_att=ex_att;
        self.txrf_freqMhz=rf_freqMhz;
        self.txfrmcnt(1);
        self.txenable(0);
        logdebug('TX RF is ready!');

    def sigout_txfrmcnt(self,rf_freqMhz,pwr,ex_att,data_rate,frmcnt,unit_no):
        self.setvsg(rf_freqMhz,pwr+ex_att,unit_no)
        self.setrate(data_rate)
        self.txenable(1)
        self.txfrmcnt(frmcnt)

    def trig_wave(self,unit_no=1):
        self.txenable(1);
        self.txfrmcnt(self.frmcnt);

    def set_pwr(self,power,mixoffset=10,unit_no=1,mode='measure',auto_range=0):
        if mode=='source':
            self.setvsg(self.txrf_freqMhz,power+self.ex_att,unit_no);
        elif mode=="cw":
            self.txcw(self.txrf_freqMhz,power,unit_no)
        else:
            self.setvsa(self.rxrf_freqMhz,power,self.ex_att,unit_no,auto_range,self.iq_mode);

    def gen_switch(self,status='ON',unit_no=1):
        switch_dic={'ON':1,'OFF':0};
        if status not in switch_dic:
            logerror('status params is error!');
            return False;
        self.txenable(switch_dic[status]);
        return True;

    def get_iq_mode(self):
        return self.iq_mode;

