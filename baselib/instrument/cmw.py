#File for GPIB VISA control of CMW
from visa import *
import time
import fpformat
import re
from baselib.plot import *

class cmw(GpibInstrument):
    prim_addr=-1;
    op_statlst=['OPEN',    #just open, not initialize for test
		'CLOSE',   #shutdown,need reopen again
		'RUN',     #begin measure
		'RDY',     #stop running,data is ready
		'ERROR',   #instrument is in error state, need reset
		'LOSE'];   #can't contact with it
    op_stat='LOSE';
    reliab_ind={'0':'OK',
                '3':'Overdriven: input signal too high',
		'4':'Underdriven: input signal too low',
		'6':'Trig Timeout:No results available',
		'7':'Acquisit Error:No results available',
		'8':'Sync Error:No results available'};

    data_rate='1m';
    rate_dic={'1m'   :('11b_dss' ,'11b'),
	        '2m'   :('11b_dss' ,'11b'),
	        '5.5m' :('11b_dss' ,'11b'),
	        '11m'  :('11b_dss' ,'11b'),
	        '6m'   :('11g_ofdm','11g'),
	        '9m'   :('11g_ofdm','11g'),
	        '12m'  :('11g_ofdm','11g'),
	        '18m'  :('11g_ofdm','11g'),
	        '24m'  :('11g_ofdm','11g'),
	        '36m'  :('11g_ofdm','11g'),
	        '48m'  :('11g_ofdm','11g'),
	        '54m'  :('11g_ofdm','11g')};

    datatype_lst=['CURR','AVER','MAX'];
    mode_lst=['11b','11g','11n'];
    result_fetched = 0;
    s_curr_lst = [];
    s_avg_lst = [];
    s_max_lst = [];
    duration =[0,0];

    def isbusy(self,timeout=10):
    	for i in range(0,timeout):
    	    if '1'==self.ask('*OPC?'):
    	        return False;
        	    time.sleep(1);
    	return True;

    def wait(self):
        self.write('*WAI');
        while self.isbusy()==True:
	      print 'CMW is still busy...';
	   return True;

    def clean(self,timeout=10):
	self.write('*CLS');
	if False== self.isbusy(timeout):
	    self.op_stat='OPEN';
	    print 'CMW status clean ok!'
	    return True;
        else:
            print 'CMW clean timeout %d sec!'%timeout;
	    self.op_stat='ERROR';
	    return False;

    def reset(self,timeout=10):
    	self.write('*RST');
    	if False== self.isbusy(timeout):
    	    self.op_stat='OPEN';
    	    print 'CMW reset ok!'
    	    return True;
            else:
                print 'CMW reset timeout %d sec!'%timeout;
    	    self.op_stat='ERROR';
    	    return False;

    #mode: measure | source,chan_est for source is repeat_num
    def __init__(self,rf_freq,pwr,data_rate,chan_est='preamble',unit_no=1,mode='measure',ex_att=0,timeout=10): #IO response time in 5 seconds
    	try:
               #get instrument list on gpib bus
    	   instr_lst0=get_instruments_list();
    	   instr_lst=[];
    	   for i in range(0,len(instr_lst0)):
    	       if re.findall(r'^GPIB',instr_lst0[i],re.M)!=[]:
    	 	   instr_lst.append(instr_lst0[i]);
               if len(instr_lst)==0:
                  print 'Find no instrument on GPIB Bus!';
                  return;
               #try to get CMW
    	   self.prim_addr='';
               for i in range(0,len(instr_lst)):
                   instr=instrument(instr_lst[i]);
                   answer=instr.ask('*IDN?');
    	       if answer.find('Rohde&Schwarz,CMW')!=-1:
    	          self.prim_addr=instr_lst[i];
    		  print 'Find CMW, Address is %s'%instr_lst[i];
    	          break;

    	   #check search result
    	   if self.prim_addr=='':
    	       print 'Sorry, find no CMW exist!';
    	       return;

    	   #get handler for CMW
    	   GpibInstrument.__init__(self,self.prim_addr);
    	   print 'Open CMW Successfully!';
    	   self.op_stat='OPEN';
    	   self.timeout=timeout;

    	except:
    	   print "Fail to operate GPIB bus!"
    	   return;

            if data_rate not in self.rate_dic:
               print 'unkonwn data rate';
               return;

            #instrument initialize
            self.data_rate=data_rate;
           # self.reset();
           # self.wait();
           # self.clean();
           # self.wait();

    	if mode=='measure':
            self.rf_port(ex_att);
            #self.set_chan(rf_chan);
            self.set_freq(rf_freq);
            self.set_pwr(pwr,10);
            self.sigmode(self.rate_dic[data_rate][0]);
            self.meas_ctrl();
            self.set_chan_est(chan_est);
            self.meas_all('ON');
        else:
    	   self.sigout(rf_freq,pwr,ex_att,data_rate,chan_est,unit_no);

    	print 'Initialize CMW OK!'

    #CMW related command below:
    def meas_stat(self,unit_no=1):
        return self.ask('FETCh:WLAN:MEAS%d:MEV:STAT?'%unit_no);

    def meas_start(self,unit_no=1):
    	self.write('INIT:WLAN:MEAS%d:MEValuation'%unit_no);
    	if False==self.isbusy() and self.meas_stat()=='RUN':
    	   self.op_stat='RUN';
               return True;
        else:
    	   self.op_stat='ERROR';
    	   return False;

    def meas_abort(self,unit_no=1):
    	self.write('ABORt:WLAN:MEAS%d:MEValuation'%unit_no);
    	if False==self.isbusy() and self.meas_stat()=='OFF':
    	   self.op_stat='OPEN';
               return True;
        else:
    	   self.op_stat='ERROR';
    	   return False;

    def meas_stop(self,unit_no=1):
    	self.write('STOP:WLAN:MEAS%d:MEValuation'%unit_no);
    	if False==self.isbusy() and self.meas_stat()=='RDY':
    	   self.op_stat='RDY';
               return True;
        else:
    	   self.op_stat='ERROR';
    	   return False;

    def rf_port(self,ext_att=0,unit_no=1,port='RF1C',mode='measure'):
        u2_port_dic={ 'RF1C': 'RF3C',
		      'RF2C': 'RF4C',
		      'RF1O': 'RF3O'};

	if port!='RF1C' and port!='RF2C' and port!='RF1O':
        print 'port name not correct, should be RF1C, RF2C,RF1O';
        return False;
	if ext_att<-50 or ext_att>90:
	   print 'ext_att out of range(-50,90)';
	   return False;

        if unit_no==2:
           port=u2_port_dic[port];

        if mode=='measure':
	   self.write('ROUTe:WLAN:MEAS%d:SCENario:SALone %s, RX1'%(unit_no,port));
	   self.write('CONF:WLAN:MEAS%d:RFS:EATT %3.2f'%(unit_no,ext_att));
        else:
           self.write('ROUTe:GPRF:GEN%d:RFSettings:CONNector %s'%(unit_no,port));
           self.write('SOURce:GPRF:GEN%d:RFSettings:EATT %3.2f'%(unit_no,ext_att));

	if False==self.isbusy():
           return True;
        else:
	   return False;

    def set_chan(self,chan,unit_no=1):
	chn_map={1:'2.412E+9', 2:'2.417E+9', 3:'2.422E+9', 4:'2.427E+9', 5:'2.432E+9',
	  	 6:'2.437E+9', 7:'2.442E+9', 8:'2.447E+9', 9:'2.452E+9',10:'2.457E+9',
		11:'2.462E+9',12:'2.467E+9',13:'2.472E+9',14: '2.484E+9'};

	self.write('CONF:WLAN:MEAS%d:RFS:FREQ:BAND B24Ghz'%unit_no);

	if chan in chn_map:
	    frq=chn_map[chan];
	    self.write('CONF:WLAN:MEAS%d:RFS:FREQ %s'%(unit_no,frq));
	    if False==self.isbusy():
               return True;
            else:
	       return False;
	else:
            print 'chan out of channel range';
	    return False;

    def set_pwr(self,power,mixoffset=10,unit_no=1,mode='measure'):
	if mode=='measure':
           if power<-47 or power>34:
               print 'power out of range!';
	       return False;
           else:
	       self.write('CONF:WLAN:MEAS%d:RFS:ENP %d'%(unit_no,power));
	       self.write('CONF:WLAN:MEAS%d:RFS:UMAR 0'%unit_no);
	       self.write('CONF:WLAN:MEAS%d:RFS:MLOF %d'%(unit_no,mixoffset));
	       if False==self.isbusy():
                  return True;
               else:
	          return False;
	else:
	   if power<-130 or power>0:
               print 'power out of range!';
	       return False;
           else:
               self.write('SOUR:GPRF:GEN%d:RFS:LEV %d'%(unit_no,power));
               self.write('SOUR:GPRF:GEN%d:RFS:DGA %d'%(unit_no,mixoffset));

    def sigmode(self,standard,unit_no=1):
	stan_map={'11b_dss':'BDSS','11g_dss':'GDSS','11g_ofdm':'GOFD','11n':'NOFD'};
	if standard in stan_map:
            self.write('CONF:WLAN:MEAS%d:ISIG:STAN %s'%(unit_no,stan_map[standard]));
            self.write('CONF:WLAN:MEAS%d:ISIG:BTYP:NOFDm MIX'%unit_no);
	    self.write('CONF:WLAN:MEAS%d:ISIG:NOFD:BWIDth BW20'%unit_no);
	    self.write('CONF:WLAN:MEAS%d:ISIG:NOFD:ELEN WHOL'%unit_no);
	    if False==self.isbusy():
               return True;
            else:
	       return False;
        else:
	    print 'standard error, available standard: 11b_dss,11g_dss,11g_ofdm,11n';
	    return False;

    def meas_ctrl(self,count=10,thr=-20,unit_no=1):
	self.write('CONF:WLAN:MEAS%d:MEV:REP SING'%unit_no);
	self.write('CONF:WLAN:MEAS%d:MEV:SCON NONE'%unit_no);
	self.write('CONF:WLAN:MEAS%d:MEV:MOEX ON'%unit_no);
	self.write('CONF:WLAN:MEAS%d:MEV:COMP:TRAC:PHAS ON'%unit_no);
	self.write('CONF:WLAN:MEAS%d:MEV:COMP:TRAC:TIM ON'%unit_no);
	self.write('CONF:WLAN:MEAS%d:MEV:COMP:TRAC:LEV OFF'%unit_no);
	#self.write('CONF:WLAN:MEAS%d:MEV:COMP:CEST PRE'%unit_no);

	if count<=0 or count>1000:
	   print 'count out of range(1,1000)!';
	   return False;
	self.write('CONF:WLAN:MEAS%d:MEV:SCO:MOD %d'%(unit_no,count));
	self.write('CONF:WLAN:MEAS%d:MEV:SCO:TSM %d'%(unit_no,count));

        self.write('CONF:WLAN:MEAS%d:MEV:TSM:TROT 0.0001'%unit_no);
	self.write('CONF:WLAN:MEAS%d:MEV:TSM:AFFT 5'%unit_no);

	#disable List mode
	self.write('CONF:WLAN:MEAS%d:MEV:LIST OFF'%unit_no);

        self.write('TRIG:WLAN:MEAS%d:MEV:SLOP REDG'%unit_no);
	if thr<-50 or thr>0:
            print 'trig threshold out of range(-50,0)';
	    return False;

        self.write('TRIG:WLAN:MEAS%d:MEV:THR %d'%(unit_no,thr));
        self.write('TRIG:WLAN:MEAS%d:MEV:TOUT 2'%(unit_no));
	self.write('TRIG:WLAN:MEAS%d:MEV:MGAP 0.000005'%(unit_no)); #time below trigger point:5us
	#trig mode set:Free Run,IF Power
        self.write('TRIG:WLAN:MEAS%d:MEV:SOUR \'IF Power\''%unit_no);
	#self.write('TRIG:WLAN:MEAS%d:MEV:SOUR \'Free Run\''%unit_no);
	self.wait();
        return True;

    def modsca_en(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
           self.write('CONF:WLAN:MEAS%d:MEV:RES:MSC %s'%(unit_no,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    def evmchip_en(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
           self.write('CONF:WLAN:MEAS%d:MEV:RES:EVM %s'%(unit_no,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    def evmsym_en(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
           self.write('CONF:WLAN:MEAS%d:MEV:RES:EVMS %s'%(unit_no,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    def evmcarr_en(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
           self.write('CONF:WLAN:MEAS%d:MEV:RES:EVMC %s'%(unit_no,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    def evmiq_en(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
           self.write('CONF:WLAN:MEAS%d:MEV:RES:IQC %s'%(unit_no,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    def specfl_en(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
           self.write('CONF:WLAN:MEAS%d:MEV:RES:SFL %s'%(unit_no,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    def spcmsk_en(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
           self.write('CONF:WLAN:MEAS%d:MEV:RES:TSM %s'%(unit_no,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    def meas_all(self,op,unit_no=1):
        if op=='ON' or op=='OFF':
	   self.write('CONF:WLAN:MEAS%d:MEV:RES %s,%s,%s,%s,%s,%s,%s'%(unit_no,op,op,op,op,op,op,op));
	   return True;
        else:
           print 'op wrong, either ON or OFF';
	   return False;

    #EVM limit
    def ofdm_evm_lmt(self,lmt,mode='11g',unit_no=1):
	evm_dic={0:'6M',1:'9M',2:'12M',3:'18M',4:'24M',5:'36M',6:'48M',8:'54M'};
        evmn_dic={0:'BR12',1:'QR12',2:'QR34',3:'Q1M12',4:'Q1M34',5:'Q6M12',6:'Q6M34',8:'Q6M56'}
	if mode!='11n' and mode!='11g':
	   print 'mode should be 11n or 11g';
	   return False;

	if len(lmt)!=8:
	   print 'limit not cover all rate!';
	   return False;

        lmtlst=[];
        #check value validity
        for i in range(0,len(lmt)):
	    lmtlst.append('%d'%lmt[i]);
	    if lmt[i]<-100 or lmt[i]>0:
	       if mode=='11g':
		  rate=evm_dic[i];
	       else:
		  rate=evmn_dic[i];
	       print '%s evm limit out of range(-100,0)'%rate;
	       return False;
        delimiter=',';
	if mode=='11g':
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:OFDM:EVM %s'%(unit_no,delimiter.join(lmtlst)));
        else:
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:NOFDM:EVM %s'%(unit_no,delimiter.join(lmtlst)));
        return True;

    def ofdm_evmp_lmt(self,evmp=-8,mode='11g',unit_no=1):
	if evmp<-100 or evmp>0:
           print 'pilot carriers evm limit out of range(-100,0)';
	   return False;
	if mode!='11n' and mode!='11g':
	   print 'mode should be 11n or 11g';
	   return False;

        if mode=='11g':
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:OFDM:EVMP %d'%(unit_no,evmp));
        else:
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:NOFDM:EVMP %d'%(unit_no,evmp));
        return True;

    def ofdm_iqof_lmt(self,iqof=-15,mode='11g',unit_no=1):
	if iqof<-100 or iqof>0:
           print 'I/Q origin offset limit out of range(-100,0)';
	   return False;
	if mode!='11n' and mode!='11g':
	   print 'mode should be 11n or 11g';
	   return False;

        if mode=='11g':
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:OFDM:IQOF %d'%(unit_no,iqof));
	else:
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:NOFDM:IQOF %d'%(unit_no,iqof));
	return True;

    def ofdm_frqer_lmt(self,frqer=48000,mode='11g',unit_no=1):
	if frqer<0 or frqer>48000:
           print 'center freq error limit out of range(0,48000)';
	   return False;
	if mode!='11n' and mode!='11g':
	   print 'mode should be 11n or 11g';
	   return False;

        if mode=='11g':
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:OFDM:CFER %s'%(unit_no,fpformat.sci(frqer,2)));
        else:
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:NOFDM:CFER %s'%(unit_no,fpformat.sci(frqer,2)));
        return True;

    def ofdm_ppmer_lmt(self,ppmer=25,mode='11g',unit_no=1):
	if ppmer<0 or ppmer>25:
           print 'center freq error ppm limit out of range(0,25)';
	   return False;
   	if mode!='11n' and mode!='11g':
	   print 'mode should be 11n or 11g';
	   return False;

        if mode=='11g':
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:OFDM:SCER %d'%(unit_no,ppmer));
        else:
           self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:NOFDM:SCER %d'%(unit_no,ppmer));
        return True;

    def dss_evmp_lmt(self,evmp=35,unit_no=1):
	if evmp<0 or evmp>100:
           print 'evm peak value limit out of range(0,100)';
	   return False;
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:DSSS:EVMP %d'%(unit_no,evmp));
        return True;

    def dss_evmr_lmt(self,evmr=35,unit_no=1):
	if evmr<0 or evmr>100:
           print 'evm rms value limit out of range(0,100)';
	   return False;
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:DSSS:EVMR %d'%(unit_no,evmr));
        return True;

    def dss_iqof_lmt(self,iqof=-15,unit_no=1):
	if iqof<-100 or iqof>0:
           print 'I/Q origin offset limit out of range(-100,0)';
	   return False;
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:DSSS:IQOF %d'%(unit_no,iqof));
	return True;

    def dss_frqer_lmt(self,frqer=60000,unit_no=1):
	if frqer<0 or frqer>60000:
           print 'center freq error limit out of range(0,60000)';
	   return False;
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:DSSS:CFER %s'%(unit_no,fpformat.sci(frqer,2)));
        return True;

    def dss_ppmer_lmt(self,ppmer=25,unit_no=1):
	if ppmer<0 or ppmer>25:
           print 'center freq error ppm out of range(0,25)';
	   return False;
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:MOD:DSSS:CCER %d'%(unit_no,ppmer));
        return True;

    # Spectrum mask limit define
    def ofdm_spmsk_lmt(self,mask,mode='11g',unit_no=1):
	if mode!='11n' and mode!='11g':
	   print 'mode should be 11n or 11g';
	   return False;

	if mode=='11g' and len(mask)!=4:
	   print 'mask need include A,B,C,D!';
	   return False;
	if mode=='11n' and len(mask)!=5:
	   print 'mask need include A,B,C,D,ABSL!';
	   return False;

        for i in range(0,4):
           if mask[i]<-90 or mask[i]>10:
	      print 'mask limit out of range(-90,10)';
              return False;

        if mode=='11g':
            self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:OFDM:Y:A %d'%(unit_no,mask[0]));
	    self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:OFDM:Y:B %d'%(unit_no,mask[1]));
	    self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:OFDM:Y:C %d'%(unit_no,mask[2]));
	    self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:OFDM:Y:D %d'%(unit_no,mask[3]));
            self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:OFDM:ENAB ON'%unit_no);
        else:
            self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:NOFDM:Y:A %d'%(unit_no,mask[0]));
	    self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:NOFDM:Y:B %d'%(unit_no,mask[1]));
	    self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:NOFDM:Y:C %d'%(unit_no,mask[2]));
	    self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:NOFDM:Y:D %d'%(unit_no,mask[3]));
	    self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:NOFDM:ABSL %d'%(unit_no,mask[4]));
            self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:NOFDM:ENAB ON'%unit_no);
	return True;

    def dss_spmsk_lmt(self,mask,unit_no=1):
	if len(mask)!=2:
	   print 'mask need include AB,CD!';
	   return False;

        for i in range(0,2):
           if mask[i]<-90 or mask[i]>10:
	      print 'mask limit out of range(-90,10)';
              return False;
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:DSSS:Y:AB %d'%(unit_no,mask[0]));
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:DSSS:Y:CD %d'%(unit_no,mask[1]));
        self.write('CONF:WLAN:MEAS%d:MEV:LIM:TSM:DSSS:ENAB ON'%unit_no);

    #measurement result deal
    def result_check(self,result):
        result_lst=result.split(',');
	print self.reliab_ind[result_lst[0]];

	if result_lst[0] in ['0','3','4']:
	   if result.find('NCAP')!=-1 or result.find('NAV')!=-1:
	      print 'Fail to get measure result!';
	      return [];
           else:
	      return [float(x) for x in result_lst[1:]];
        else:
	   return [];

    #fetch and read evmsym, only for 11g,11n
    def fetch_evmsym(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst:
	   print 'mode should be 11b,11g,11n';
	   return [];

        if mode=='11g':
	   result=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:EVM:OFDM:SYMB:%s?'%(unit_no,data_type));
	else:
	   result=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:EVM:NOFDM:SYMB:%s?'%(unit_no,data_type));

	return self.result_check(result);

    def read_evmsym(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst:
	   print 'mode should be 11b,11g,11n';
	   return [];

        if mode=='11g':
	   result=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:EVM:OFDM:SYMB:%s?'%(unit_no,data_type));
	else:
	   result=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:EVM:NOFDM:SYMB:%s?'%(unit_no,data_type));

	return self.result_check(result);

    #fetch and read evmcarr, only for 11g,11n
    def fetch_evmcarr(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst[1:]:
	   print 'mode should be 11g,11n';
	   return [];

        if mode=='11g':
	   result=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:EVM:OFDM:CARR:%s?'%(unit_no,data_type));
	else:
	   result=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:EVM:NOFDM:CARR:%s?'%(unit_no,data_type));

	return self.result_check(result);

    def read_evmcarr(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst[1:]:
	   print 'mode should be 11g,11n';
	   return [];

        if mode=='11g':
	   result=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:EVM:OFDM:CARR:%s?'%(unit_no,data_type));
	else:
	   result=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:EVM:NOFDM:CARR:%s?'%(unit_no,data_type));

	return self.result_check(result);

    #IQ Constellation fetch and read
    def fetch_iqc(self,unit_no=1):
	mode=self.rate_dic[self.data_rate][1];
	if mode not in self.mode_lst[:2]:
	   print 'mode should be 11b,11g';
	   return [];

        if mode=='11g':
	   result_i=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:IQC:OFDM:INPH?'%unit_no);
	   result_q=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:IQC:OFDM:QUAD?'%unit_no);
	else:
	   result_i=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:IQC:DSSS:INPH?'%unit_no);
	   result_q=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:IQC:DSSS:QUAD?'%unit_no);

	i_lst= self.result_check(result_i);
   	q_lst= self.result_check(result_q);
	if len(i_lst)==len(q_lst) and len(i_lst)!=0:
	    plot.plot_scatter(i_lst,q_lst);
        else:
            print 'Fail to get IQ data';

    def read_iqc(self,unit_no=1):
	mode=self.rate_dic[self.data_rate][1];
	if mode not in self.mode_lst[:2]:
	   print 'mode should be 11b,11g';
	   return [];

        if mode=='11g':
	   result_i=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:IQC:OFDM:INPH?'%unit_no);
	   result_q=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:IQC:OFDM:QUAD?'%unit_no);
	else:
	   result_i=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:IQC:DSSS:INPH?'%unit_no);
	   result_q=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:IQC:DSSS:QUAD?'%unit_no);

	i_lst= self.result_check(result_i);
   	q_lst= self.result_check(result_q);
	if len(i_lst)==len(q_lst) and len(i_lst)!=0:
	    plot.plot_scatter(i_lst,q_lst);
        else:
            print 'Fail to get IQ data';

    #spectrum read and fetch
    def fetch_spec(self,data_type='AVER',plot_en=1,unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];
        result=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:TSM:%s?'%(unit_no,data_type));
	ydata=self.result_check(result);
	if len(ydata)!=0:
           xdata=[ 0.05*(i-800) for i in range(0,len(ydata)-1)];
	   if plot_en==1:
	      plot.plot_curve(xdata,ydata[:len(ydata)-1],'Pwr/MHz','MHz','dB','Spectrum');
	   return ydata[:len(ydata)-1];
        else:
	   return [];

    def read_spec(self,data_type='AVER',plot_en=1,unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];
        result=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:TSM:%s?'%(unit_no,data_type));
	ydata=self.result_check(result);
	if len(ydata)!=0:
           xdata=[ 0.05*(i-800) for i in range(0,len(ydata)-1)];
	   if plot_en==1:
	      plot.plot_curve(xdata,ydata[:len(ydata)-1],'Pwr/MHz','MHz','dB','Spectrum');
	   #add sample_num and freq_step
	   return ydata[:len(ydata)-1];
        else:
	   return [];

    def fcc_check(bur_pwr,mode='11b',pwr_lmt=-41,freq_zone=12.5):
	spec=self.read_spec('AVER',0);
	sample_num=1600;
	freq_step=0.05;
        if spec==[]:
           return ['NAV','NAV','NAV'];
        if mode=='11g':
           #Power=Pk+10*log10(160),plus 3 for mask 3 db margin
           pwr_db2dbm=bur_pwr-22+3;
        else:
           #Power=Pk+10*log10(110)
           pwr_db2dbm=bur_pwr-20.4+3;

        #spec 1600 point for -40M to 40M
        spec_dbm=[data+pwr_db2dbm for data in spec];
        max_left_pwr=max(spec_dbm[:int(sample_num/2)-int(freq_zone/freq_step)]);
        max_left_index=spec_dbm[:int(sample_num/2)-int(freq_zone/freq_step)].index(max_left_pwr);
        max_left_freq=(max_left_index-int(sample_num/2))*freq_step;

        max_right_pwr=max(spec_dbm[int(sample_num/2)+int(freq_zone/freq_step):]);
        max_right_index=spec_dbm[int(sample_num/2)+int(freq_zone/freq_step):].index(max_right_pwr);
        max_right_freq=freq_zone+(max_right_index*freq_step);

        if max_left_pwr>pwr_lmt or max_right_pwr>pwr_lmt:
           check='FAIL';
        else:
           check='PASS';
        return [check,(max_left_pwr-pwr_lmt,max_left_freq),(max_right_pwr-pwr_lmt,max_right_freq)];

    #spectrum flatness read and fetch
    def fetch_spfl(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];
        result=self.ask('FETCH:WLAN:MEAS%d:MEV:TRAC:SFL:%s?'%(unit_no,data_type));
	return self.result_check(result);

    def read_spfl(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];
        result=self.ask('READ:WLAN:MEAS%d:MEV:TRAC:SFL:%s?'%(unit_no,data_type));
	return self.result_check(result);

    #modulation read and fetch
    def fetch_modsta(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst and data_type!='SDEV':
	   print 'data_type is not correct,should be MAX,AVER,CURR,SDEV';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst:
	   print 'mode should be 11b,11g,11n';
	   return [];

        if mode=='11b':
	    result=self.ask('FETCH:WLAN:MEAS%d:MEV:MOD:DSSS:%s?'%(unit_no,data_type));
        else:
	    result=self.ask('FETCH:WLAN:MEAS%d:MEV:MOD:OFDM:%s?'%(unit_no,data_type));

	result_lst=result.split(',');
	if result_lst[0] in ['0','3','4']:
	   if ('NCAP' in result_lst[0:10]) or ('NAV' in result_lst[0:10]):
	      print 'Fail to get measure result!';
	      return [];
           else:
              return result_lst;
        else:
	   return [];

    def read_modsta(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst and data_type!='SDEV':
	   print 'data_type is not correct,should be MAX,AVER,CURR,SDEV';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst:
	   print 'mode should be 11b,11g,11n';
	   return [];

        if mode=='11b':
	    result=self.ask('READ:WLAN:MEAS%d:MEV:MOD:DSSS:%s?'%(unit_no,data_type));
        else:
	    result=self.ask('READ:WLAN:MEAS%d:MEV:MOD:OFDM:%s?'%(unit_no,data_type));

	result_lst=result.split(',');
	if result_lst[0] in ['0','3','4']:
	   if ('NCAP' in result_lst[0:10]) or ('NAV' in result_lst[0:10]):
	      print 'Fail to get measure result!';
	      return [];
           else:
              return result_lst;
        else:
	   return [];

    #display mod result
    def show_mod(self,unit_no=1):
        curr_lst=self.read_modsta('CURR',unit_no);
	avg_lst=self.fetch_modsta('AVER',unit_no);
	max_lst=self.fetch_modsta('MAX',unit_no);
	if curr_lst==[] or avg_lst==[] or max_lst==[]:
	   print 'Fail to get modulate test result!';
	   return;

	if '11b'== self.rate_dic[self.data_rate][1]:
	    print 'result status:%s\n'%self.reliab_ind[curr_lst[0]];
	    print 'modulation type:%s\n'%curr_lst[1];
 	    print 'PLCP type:%s\n'%curr_lst[2];
	    print 'Load len(byte):%s\n'%curr_lst[3];
	    print 'Burst Pwr(dBm):%4.1f\n'%(float(curr_lst[4]));
	    print '                Curr   AVER      MAX\n';
            print 'EVM Peak(%)   :'+' %4.1f   %4.1f      %4.1f\n'%(float(curr_lst[5]),float(avg_lst[5]),float(max_lst[5]));
            print 'EVM RMS(%)    :'+' %4.1f   %4.1f      %4.1f\n'%(float(curr_lst[6]),float(avg_lst[6]),float(max_lst[6]));
            print 'FREQ ERROR(Hz): %4.1f %4.1f   %4.1f\n'%(float(curr_lst[7]),float(avg_lst[7]),float(max_lst[7]));
            print 'CLK ERROR(ppm): %4.1f   %4.1f      %4.1f\n'%(float(curr_lst[8]),float(avg_lst[8]),float(max_lst[8]));
            print 'IQ Offset(dB) : %4.1f   %4.1f     %4.1f\n'%(float(curr_lst[9]),float(avg_lst[9]),float(max_lst[9]));
            print 'GainImbal(dB) : %s     %s      %s\n'%(curr_lst[10],avg_lst[10],max_lst[10]);
            print 'QuadError(deg): %s     %s      %s\n'%(curr_lst[11],avg_lst[11],max_lst[11]);
        else:
            print 'result status:%s\n'%self.reliab_ind[curr_lst[0]];
	    print 'modulation type:%s\n'%curr_lst[1];
	    print 'Load len(byte):%s\n'%curr_lst[2];
	    print 'Burst Pwr(dBm):%4.1f\n'%(float(curr_lst[3]));
	    print '                Curr   AVER      MAX\n';
            print 'EVMAllCarr(dB)   :'+' %4.1f   %4.1f      %4.1f\n'%(float(curr_lst[4]),float(avg_lst[4]),float(max_lst[4]));
            print 'EVMDataCarr(dB)  :'+' %4.1f   %4.1f      %4.1f\n'%(float(curr_lst[5]),float(avg_lst[5]),float(max_lst[5]));
            print 'EVMPilotCarr(dB) :'+' %4.1f   %4.1f      %4.1f\n'%(float(curr_lst[6]),float(avg_lst[6]),float(max_lst[6]));
            print 'FREQ ERROR(Hz): %4.1f %4.1f   %4.1f\n'%(float(curr_lst[7]),float(avg_lst[7]),float(max_lst[7]));
            print 'CLK ERROR(ppm): %4.1f   %4.1f      %4.1f\n'%(float(curr_lst[8]),float(avg_lst[8]),float(max_lst[8]));
            print 'IQ Offset(dB) : %4.1f   %4.1f     %4.1f\n'%(float(curr_lst[9]),float(avg_lst[9]),float(max_lst[9]));
            print 'GainImbal(dB) : %s     %s      %s\n'%(curr_lst[10],avg_lst[10],max_lst[10]);
            print 'QuadError(deg): %s     %s      %s\n'%(curr_lst[11],avg_lst[11],max_lst[11]);

    #spectrum mask read and fetch
    def fetch_spmsk(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst:
	   print 'mode should be 11b,11g,11n';
	   return [];

        if mode=='11b':
	    result=self.ask('FETCH:WLAN:MEAS%d:MEV:TSM:DSSS:%s?'%(unit_no,data_type));
	elif mode=='11g':
	    result=self.ask('FETCH:WLAN:MEAS%d:MEV:TSM:OFDM:%s?'%(unit_no,data_type));
        else:
	    result=self.ask('FETCH:WLAN:MEAS%d:MEV:TSM:NOFDM:%s?'%(unit_no,data_type));

	return self.result_check(result);

    def read_spmsk(self,data_type='AVER',unit_no=1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return [];

        mode=self.rate_dic[self.data_rate][1];
        if mode not in self.mode_lst:
	   print 'mode should be 11b,11g,11n';
	   return [];

        if mode=='11b':
	    result=self.ask('READ:WLAN:MEAS%d:MEV:TSM:DSSS:%s?'%(unit_no,data_type));
	elif mode=='11g':
	    result=self.ask('READ:WLAN:MEAS%d:MEV:TSM:OFDM:%s?'%(unit_no,data_type));
        else:
	    result=self.ask('READ:WLAN:MEAS%d:MEV:TSM:NOFDM:%s?'%(unit_no,data_type));

	return self.result_check(result);

    def show_spmask(self,unit_no=1):
        curr_lst=self.read_spmsk('CURR');
	avg_lst=self.fetch_spmsk('AVER');
	max_lst=self.fetch_spmsk('MAX');
	if curr_lst!=[] and avg_lst!=[] and max_lst!=[]:
  	   if '11b'== self.rate_dic[self.data_rate][1]:
	       print '              AB          CD         DC          BA\n';
	       print 'Freq(MHz)     (-40,-22)   (-22,-11)  (11,22)     (22,40)\n';
	       print 'Limit(dB)     (-50,-50)   (-30,-30)  (-30,-30)   (-50,50)\n';
	       print 'Margin_CURR   %3.1f        %3.1f      %3.1f      %3.1f\n'%(curr_lst[0],curr_lst[1],curr_lst[2],curr_lst[3]);
	       print 'Margin_AVER   %3.1f        %3.1f      %3.1f      %3.1f\n'%(avg_lst[0],avg_lst[1],avg_lst[2],avg_lst[3]);
	       print 'Margin_MAX    %3.1f        %3.1f      %3.1f      %3.1f\n'%(max_lst[0],max_lst[1],max_lst[2],max_lst[3]);
	   else:
	       print '             AB        BC        CD        DE       ED      DC        CB        BA\n';
	       print 'Freq(MHz)    (-40,-30) (-30,-20) (-20,-11) (-11,-9) (9,11)  (11,20)   (20,30)   (30,40)\n';
	       print 'Limit(dB)    (-40,-40) (-40,-28) (-28,-20) (-20,0)  (0,-20) (-20,-28) (-28,-40) (-40,-40)\n';
	       print 'Margin_CURR  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f\n'%(curr_lst[0],curr_lst[1],curr_lst[2],curr_lst[3],curr_lst[4],curr_lst[5],curr_lst[6],curr_lst[7]);
	       print 'Margin_AVER  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f\n'%(avg_lst[0],avg_lst[1],avg_lst[2],avg_lst[3],avg_lst[4],avg_lst[5],avg_lst[6],avg_lst[7]);
	       print 'Margin_MAX   %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f  %3.1f\n'%(max_lst[0],max_lst[1],max_lst[2],max_lst[3],max_lst[4],max_lst[5],max_lst[6],max_lst[7]);
	else:
	   print 'Fail to get spectrum mask';
    def restart(self,smplTm_microSecs=1000,isht40Mode=0):
	self.meas_all('OFF');
	self.result_fetched = 0;
	self.meas_all('ON');

    def get_result(self, name, data_type = 'AVER', uint_no = 1):
	if data_type not in self.datatype_lst:
	   print 'data_type is not correct,should be MAX,AVER,CURR';
	   return 'DATA TYPE ERROR';
   	if self.result_fetched == 0:
	    self.result_fetched =1;
	    self.s_curr_lst = self.read_modsta('CURR', uint_no);
	    self.s_avg_lst = self.fetch_modsta('AVER', uint_no);
	    self.s_max_lst = self.fetch_modsta('MAX', uint_no);
	if data_type == 'CURR':
	    lst = self.s_curr_lst;
	elif data_type == 'AVER':
	    lst = self.s_avg_lst;
	elif data_type == 'MAX':
	    lst = self.s_max_lst;

	if lst==[]:
           return 'NAV';
	if '11b' == self.rate_dic[self.data_rate][1]:
	    if name == 'RES_STA':
		return self.reliab_ind[lst[0]];
	    elif name == 'MOD_TYPE':
		return lst[1];
	    elif name == 'PLCP_TYPE':
		return lst[2];
	    elif name == 'LOAD_LEN':
		return lst[3];
	    elif name == 'BUR_PWR':
		return '%4.2f'%(float(lst[4]));
	    elif name == 'EVM_PEAK':
		return '%4.2f'%(float(lst[5]));
	    elif name == 'EVM_RMS':
		return '%4.2f'%(float(lst[6]));
	    elif name == 'FREQ_ERR':
		return '%4.2f'%(float(lst[7]));
	    elif name == 'CLK_ERR':
		return '%4.2f'%(float(lst[8]));
	    elif name == 'IQ_OFF':
		return '%4.2f'%(float(lst[9]));
	    #1m test have no iqmismatch
	    elif name == 'GAIN_IMB':
	       if 'NCAP'==lst[10] or 'NAV'==lst[10]:
	          return '0.01';
	       else:
	          return '%4.2f'%(float(lst[10]));
	    elif name == 'QUADERR':
	       if 'NCAP'==lst[11] or 'NAV'==lst[11]:
	          return '0.01';
	       else:
		return '%4.2f'%(float(lst[11]));
	    else:
		return 'DATA NAME ERROR';
	else:
	    if name == 'RES_STA':
		return self.reliab_ind[lst[0]];
	    elif name == 'MOD_TYPE':
		return lst[1];
	    elif name == 'LOAD_LEN':
		return lst[2];
	    elif name == 'BUR_PWR':
		return '%4.2f'%(float(lst[3]));
	    elif name == 'EVM_ALL':
		return '%4.2f'%(float(lst[4]));
	    elif name == 'EVM_DATA':
		return '%4.2f'%(float(lst[5]));
	    elif name == 'EVM_PILO':
		return '%4.2f'%(float(lst[6]));
	    elif name == 'FREQ_ERR':
		return '%4.2f'%(float(lst[7]));
	    elif name == 'CLK_ERR':
		return '%4.2f'%(float(lst[8]));
	    elif name == 'IQ_OFF':
		return '%4.2f'%(float(lst[9]));
	    elif name == 'GAIN_IMB':
	       if 'NCAP'==lst[10] or 'NAV'==lst[10]:
	          return '0.01';
	       else:
		  return '%4.2f'%(float(lst[10]));
	    elif name == 'QUADERR':
	       if 'NCAP'==lst[11] or 'NAV'==lst[11]:
	          return '0.01';
	       else:
		  return '%4.2f'%(float(lst[11]));
	    else:
		return 'DATA NAME ERROR';

    def set_freq(self,freq,unit_no=1,mode='measure'):
	freq ='%4.3e'%(float(freq)*1E6);
	if mode=='measure':
	    self.write('CONF:WLAN:MEAS%d:RFS:FREQ:BAND B24Ghz'%unit_no);
	    self.write('CONF:WLAN:MEAS%d:RFS:FREQ %s'%(unit_no,freq));
        else:
            self.write('SOURce:GPRF:GEN%d:RFS:FREQ %s'%(unit_no,freq));

	if False==self.isbusy():
       	    return True;
        else:
	    return False;

    def set_chan_est(self,chan_est,unit_no=1):
	if chan_est == 'payload':
	    self.write('CONF:WLAN:MEAS%d:MEV:COMP:CEST PAYL'%unit_no);
        elif chan_est == 'preamble':
	    self.write('CONF:WLAN:MEAS%d:MEV:COMP:CEST PRE'%unit_no);
	else:
            print 'wrong parameter.\n';
	    return False;
	if False==self.isbusy():
       	    return True;
        else:
	    return False;

    def genwave(self,data_rate,repeat=0,unit_no=1):
	arbfile_dic={'1m'   :'wlan11b_1m_len1024_nonoise.wv',
	             '2m'   :'wlan11b_2ml_len1024_nonoise.wv',
	             '2ml'  :'wlan11b_2ml_len1024_nonoise.wv',
	             '2ms'  :'wlan11b_2ms_len1024_nonoise.wv',
	             '5.5m' :'wlan11b_5ml_len1024_nonoise.wv',
	             '5.5ml':'wlan11b_5ml_len1024_nonoise.wv',
	             '5.5ms':'wlan11b_5ms_len1024_nonoise.wv',
	             '11m'  :'wlan11b_11ml_len1024_nonoise.wv',
	             '11ml' :'wlan11b_11ml_len1024_nonoise.wv',
	             '11ms' :'wlan11b_11ms_len1024_nonoise.wv',
	             '6m'   :'wlan11g_6m_len1024_nonoise.wv',
	             '9m'   :'wlan11g_9m_len1024_nonoise.wv',
	             '12m'  :'wlan11g_12m_len1024_nonoise.wv',
	             '18m'  :'wlan11g_18m_len1024_nonoise.wv',
	             '24m'  :'wlan11g_24m_len1024_nonoise.wv',
	             '36m'  :'wlan11g_36m_len1024_nonoise.wv',
	             '48m'  :'wlan11g_48m_len1024_nonoise.wv',
	             '54m'  :'wlan11g_54m_len1024_nonoise.wv',
	             'mcs0' :'wlan11n_mcs0_6d5m_len4096_nonoise.wv',
	             'mcs1' :'wlan11n_mcs1_13m_len4096_nonoise.wv',
	             'mcs2' :'wlan11n_mcs2_19d5m_len4096_nonoise.wv',
	             'mcs3' :'wlan11n_mcs3_26m_len4096_nonoise.wv',
	             'mcs4' :'wlan11n_mcs4_39m_len4096_nonoise.wv',
	             'mcs5' :'wlan11n_mcs5_52m_len4096_nonoise.wv',
	             'mcs6' :'wlan11n_mcs6_58d5m_len4096_nonoise.wv',
	             'mcs7' :'wlan11n_mcs7_65m_len4096_nonoise.wv'};
	fold_path='D:/Rohde-Schwarz/CMW/Data/waveform/fpga_test/1_frame/';

        self.write('SOUR:GPRF:GEN%d:LIST OFF'%unit_no);
	self.write('SOUR:GPRF:GEN%d:BBM ARB'%unit_no);
	if repeat==0:
	   self.write('SOUR:GPRF:GEN%d:ARB:REP CONT'%unit_no);
	elif repeat > 10000:
	   print 'repeate times out of maximum range!';
	   return False;
	else:
	   self.write('SOUR:GPRF:GEN%d:ARB:REP SING'%unit_no);
	   self.write('SOUR:GPRF:GEN%d:ARB:CYCL %d'%(unit_no,repeat));
	   self.write('SOUR:GPRF:GEN%d:ARB:ASAM 0'%unit_no);

	self.write('SOUR:GPRF:GEN%d:ARB:FILE %s'%(unit_no,'\''+fold_path+arbfile_dic[data_rate]+'\''));
	self.write('TRIG:GPRF:GEN%d:ARB:RETR ON'%unit_no);
	self.write('TRIG:GPRF:GEN%d:ARB:AUT OM'%unit_no);
	self.write('TRIG:GPRF:GEN%d:ARB:SOUR Manual'%unit_no);
	return True;

    def gen_switch(self,status='ON',unit_no=1):
	self.write('SOUR:GPRF:GEN%d:STAT %s'%(unit_no,status));

    def trig_wave(self,unit_no=1):
	self.write('TRIG:GPRF:GEN%d:ARB:MAN:EXEC'%unit_no);
	time.sleep(1.0+self.duration[unit_no-1]);

    def sigout(self,rf_freq,pwr,ex_att,data_rate,repeat,unit_no):
	self.rf_port(ex_att,unit_no,'RF1C','source');
        self.set_freq(rf_freq,unit_no,'source');
        self.set_pwr(pwr,0,unit_no,'source');
	self.genwave(data_rate,repeat,unit_no);
	self.gen_switch('ON',unit_no);
	#calculate duration time
	if repeat!=0:
	   clk_rate=self.ask('SOUR:GPRF:GEN%d:ARB:CRAT?'%unit_no);
	   clk_rate=float(clk_rate);
	   smp_num=self.ask('SOUR:GPRF:GEN%d:ARB:SAMP?'%unit_no);
	   smp_num=float(smp_num);
	   elapsetm=(smp_num/clk_rate)*repeat;
	   self.duration[unit_no-1]=elapsetm;
           time.sleep(2+elapsetm);
