#File for GPIB VISA control of CMW
import time
import fpformat
import re
from baselib.plot import *
from math import *
from baselib.loglib.log_lib import *
import platform

class HP(object):
    #suspend all operation for delaysec seconds
    def wait(self,delaysec=1):
        self.device.write('WAIT %dSC;'%delaysec);
        return True;

    def clean(self):
        self.device.write('CLRW TRA;');
        return True;

    def reset(self,timeout=10):
        #self.device.write('IP;');
        self.device.write('TRPRST;');
        return True;

    def close(self,timeout=10):
        self.device.write('RELHPIB;');
        return True;

    #IO response time in 10 seconds,mode[SA:spectrum analyzer,SR:tracking generator]
    def __init__(self,mode='SA',cfreq=2400,rb=100,span=100,reflvl=10,timeout=10,vb=30):

        if platform.platform().find("Linux") != -1:
            from GPIBImpl import GPIBLinux
            self.device = GPIBLinux.GPIBDevice("") # HP
        else:
            from GPIBImpl import GPIBWindows
            self.device = GPIBWindows.GPIBDevice("")
        pass

        #instrument initialize
        self.reset();
        self.clean();
        self.wait(1);
        self.set_mode(mode);
        if mode=='SA':
            self.set_reflvl(reflvl);
        else:
            self.set_pwr(reflvl);
        self.set_param(cfreq,rb,span,vb);

        if self.get_span()!=span:
           self.set_span(span);

        self.sweep_ctrl();
        print 'Initialize Spectrum Analyzer OK!'

    #CMW related command below:
    def meas_stat(self):
        return self.device.ask('TRSTAT?');

    def meas_start(self):
        self.device.write('TS');  #take sweep
        return True;

    def meas_abort(self):
        self.device.write('ABORT;');
        return True;

    def meas_stop(self,unit_no=1):
        self.meas_abort();
        return True;

    def set_mode(self,mode):
        if mode=='SA':
            self.device.write("MEASURE SA;");
        else:
            self.device.write("MEASURE SR;");
        return True;

    def get_mode(self):
        return self.device.ask("MEASURE?");

    def set_pwr(self,pwr):
        self.device.write('SRCPWR %fDM'%pwr);
        return True;

    def pwroff(self):
        self.device.write('SRCPWR OFF');
        return True;

    def get_pwr(self):
        pwr=self.device.ask('SRCPWR?');
        return float(pwr);

    def set_cfreq(self,cfreq): #cfreq unit is MHz
        self.device.write('CF %fMHZ;'%cfreq);
        return True;

    def get_cfreq(self): #cfreq unit is MHz
        cfreq=self.device.ask('CF?;');
        return float(cfreq)/1000000.0;

    def set_rb(self,rb):
        self.device.write('RB %dKHZ;'%rb);
        return True;

    def get_rb(self): #unit is kHz
        rb=self.device.ask('RB?;');
        return float(rb)/1000.0;

    def set_vb(self,vb):
        self.device.write('VB %dKHZ;'%vb);
        return True;

    def set_span(self,span):
        self.device.write('SP %3.1fMHZ'%span);
        return True;

    def get_span(self):
        span=self.device.ask('SP?');
        return float(span)/1000000.0;

    def set_reflvl(self,reflvl):
        self.device.write('RL %dDM'%reflvl);
        return True;

    def get_reflvl(self):
        reflvl=self.device.ask('RL?');
        return float(reflvl);

    def sweep_ctrl(self):
        self.device.write('SNGLS;');
        return True;

    def get_trace(self):
        trace=self.device.ask('TRA?');
        curve=trace.split(',');
        return [float(x) for x in curve];

    def show(self):
        self.meas_start();
        ydata=self.get_trace();
        span=self.get_span();
        start_freq=float(self.device.ask('FA?;'))/1000000.0;
        step=span/len(ydata);
        xdata=[start_freq+step*i for i in range(0,len(ydata))];
        plot.plot_curve(xdata,ydata,'Pwr/MHz','MHz','dBm','Spectrum');

    #rb unit:KHz,span/cfreq unit MHz
    def set_param(self,cfreq,span=100,rb=100,vb=30):
        self.set_cfreq(cfreq);
        self.set_rb(rb);
        self.set_span(span);
        self.set_vb(vb);

    #search peaks in current span
    def pk_search(self,th=-60,pk_excursion=6):
        self.device.write('TH %dDM;MKPX %dDB;TS;'%(th,pk_excursion));
        self.device.write('MXMH TRA;');
        time.sleep(1); #delay for accumulate data
        pk_num=int(self.device.ask('PEAKS TRB,TRA,FRQ?;'));
        pklst=[];
        for i in range(1,pk_num+1):
            self.device.write('MKP TRB[%d]'%i);
##        self.device.write('MKP TRA;');
            amp=float(self.device.ask('MKA?;'));
            freq=float(self.device.ask('MKF?;'))/1000000.0;
            print 'amp:%ddBm,freq:%dMHz'%(amp,freq);
            pklst.append((freq,amp));
        return pklst;

    #search peaks in all measure range(1M-6GHz)
    def pk_scan(self,th=-60,pk_excursion=6,start_freq=1,end_freq=6000,store_path='null'):
        if start_freq<0 or end_freq>6000 or start_freq>=end_freq:
            print 'scan out of freq range';
            return [];

        span=self.get_span(); #unit: MHz
        rb=self.get_rb();     #unit:KHz
        overlap_span=10;      #unit:MHz to deal with boundary problem
        #scan include multi-segements
        seg_num=int(ceil((end_freq-start_freq)/span));
        pklst_all=[];
        last_index=-1;
        cfreq0=start_freq+span/2;
        for i in range(0,seg_num):
            cfreq=cfreq0+i*span-i*overlap_span;
            self.set_param(cfreq,span,rb);

            print '\nSearch peaks from %dMHz to %dMHz'%(cfreq-span/2,cfreq+span/2);
            pklst_new=self.pk_search(th,pk_excursion);
            #check if there have peaks overlap
            for j,pk_data in enumerate(pklst_new):
                if last_index>=0 and pk_data[0]<=pklst_all[last_index][0]+rb*0.001:
               #insert pk in suitable position
                    k=last_index;
                while pk_data[0]<=pklst_all[k][0]+rb*0.001:
                    if abs(pk_data[0]-pklst_all[k][0])<=rb*0.001:
                        print 'find overlap peak!';
                        j=-1; #flag the pk is dealt
                        break;
                    elif k==0:
                        pklst_all.insert(0,pk_data);
                        j=-1; #flag the pk is dealt
                        break;
                    else:
                        k=k-1;
                if j>=0:
                    pklst_all.insert(k+1,pk_data);

                else:
                    pklst_all.append(pk_data);

                last_index=len(pklst_all)-1;

        if store_path!='null':
            if False==createdir(store_path):
                logerror('Fail to create dir for log!');
                return [];
               #open log file to record result
                logname="%s/PeakScan"%store_path;
                createlog(logname,'csv');
               #record peaks information
            writelog('index,freq(MHz),amp(dBm),');
        for index,data in enumerate(pklst_all):
            writelog('%d,%4.1f,%3.1f,'%(index,data[0],data[1]));

            closelog();
            loginfo('\nSave peaks information in Peak_Scan.csv OK!');

        return pklst_all;

    def meas_pwr(self,reflvl,cfreq,span,rb,bdwdth_mhz,vavg_no=20,vb=30):
        self.device.write('ACPPAR 0;');  #0:manual, 1:auto
        self.device.write('VAVG OFF;');
        self.set_cfreq(cfreq);
        self.set_reflvl(reflvl);
        if self.get_span()!=span:
            self.set_span(span);
            self.set_rb(rb);
            self.set_vb(vb);

        self.device.write('ACPBW %dMHZ;'%bdwdth_mhz);
        self.device.write('CONTS;');  #SNGLS
        self.device.write('VAVG %d;TS'%vavg_no);
        self.wait(3);
        self.device.write('CHP;');

        if '0'!=self.device.ask('ACPERR?;'):
           print 'fail to get power value!';
           return [];
        else:
           ch_pwr=float(self.device.ask('CHPWR?;'));
           return [float('%4.1f'%ch_pwr)];

        #offset is phase_noise measure start freq distance from tone freq,unit MHz
        #offset deviate cause 0.3dB difference
    def phn_pwr(self,tone_freq,reflvl,offset=0.10):
        span=2;       #unit MHz
        rb=10;        #unit KHz
        bdwdth_mhz=1; #unit MHz

        #get tone correct freq
        self.set_reflvl(reflvl);
        self.set_param(tone_freq,span,rb);
        if self.get_span()!=span:
           self.set_span(span);
           self.set_rb(rb);
        self.device.write('MKPK HI');
        tone_freq=float(self.device.ask('MF?'))/1000000;

        cfreq=tone_freq+offset+(bdwdth_mhz/2.0);
        result=self.meas_pwr(reflvl,cfreq,span,rb,bdwdth_mhz);
        if result!=[]:
               return result[0]+3; #right and left band pwr add together
        else:
           return 0;

    def tone_pwr(self,tone_freq,reflvl):
        span=2;       #unit MHz
        rb=10;        #unit KHz
        bdwdth_mhz=1; #unit MHz
        cfreq=tone_freq;
        result=self.meas_pwr(reflvl,cfreq,span,rb,bdwdth_mhz);
        if result!=[]:
               return result[0];
        else:
           return 0;

        #flt_bwdth is half filter bandwidth,unit is MHz
    def fltn_pwr(self,tone_freq,reflvl,flt_bwdth=8):
        span=2;       #unit MHz
        rb=10;        #unit KHz
        bdwdth_mhz=1; #unit MHz
        offset=3;     #measure filter noise from 3 to 4MHz offset
        cfreq=tone_freq+offset+(bdwdth_mhz/2.0);
        result=self.meas_pwr(reflvl,cfreq,span,rb,bdwdth_mhz);
        if result!=[]:
               return result[0]+3.0+10*log10(flt_bwdth);
        else:
           return 0;

    def reflvl_srch(self,tone_freq,ini_reflvl=0):
        reflvl=ini_reflvl;
        pk_amp=reflvl;
        while pk_amp>(reflvl-4) or pk_amp<(reflvl-7):
            reflvl=pk_amp+5;
            self.set_reflvl(reflvl);
            self.meas_start();
            self.device.write('MKPK HI');
            pk_amp=float(self.device.ask('MKA?'));

        return int(reflvl);

    def pk_detect(self):
        self.device.write('TS;');
        self.device.write('MKPK HI');
        pk_amp=float(self.device.ask('MKA?'));
        freq=float(self.device.ask('MKF?;'))/1000000.0;
        return (freq,pk_amp);

    def get_result(self, name):
        if name == 'PEAK':
            return self.pk_detect();

class Agilent(object):
    #suspend all operation for delaysec seconds
##    def wait(self,delaysec=1):
##        self.device.write('WAIT %dSC;'%delaysec);
##    return True;
##
##    def clean(self):
##    self.device.write('CLRW TRA;');
##    return True;

    def reset(self,timeout=10):
    #self.device.write('IP;');
        self.device.write(':SYST:PRES');
        return True;

##    def close(self,timeout=10):
##    self.device.write('RELHPIB;');
##    return True;

    #IO response time in 10 seconds,mode[SA:spectrum analyzer,SR:tracking generator]
    def __init__(self,mode='SA',cfreq=2400,rb=100,span=100,reflvl=10,timeout=10,vb=30,device="N9020A"):

        if platform.platform().find("Linux") != -1:
            from GPIBImpl import GPIBLinux
            self.device = GPIBLinux.GPIBDevice(device) # HP
        else:
            from GPIBImpl import GPIBWindows
            self.device = GPIBWindows.GPIBDevice(device)

        pass

        #instrument initialize
        self.reset();
##        self.clean();
##        self.wait(1);
        self.set_mode(mode);
        if mode=='SA':
            self.set_reflvl(reflvl);
        else:
            self.set_pwr(reflvl);
        self.set_param(cfreq,rb,span,vb);

        if self.get_span()!=span:
            self.set_span(span);

##        self.sweep_ctrl();
        print 'Initialize Spectrum Analyzer OK!'

    #CMW related command below:
##    def meas_stat(self):
##        return self.device.ask('TRSTAT?');
##
##    def meas_start(self):
##	self.device.write('TS');  #take sweep
##	return True;
##
##    def meas_abort(self):
##	self.device.write('ABORT;');
##	return True;
##
##    def meas_stop(self,unit_no=1):
##	self.meas_abort();
##	return True;
##
    def set_mode(self,mode):
        if mode=='SA':
            self.device.write("INST:SEL SA");
        elif mode=='EMI':
            self.device.write("INST:SEL EMI");
        return True;
##
    def get_mode(self):
	return self.device.ask("INST:SEL?");
##
##    def set_pwr(self,pwr):
##        self.device.write('SRCPWR %fDM'%pwr);
##	return True;
##
##    def pwroff(self):
##        self.device.write('SRCPWR OFF');
##	return True;
##
##    def get_pwr(self):
##        pwr=self.device.ask('SRCPWR?');
##	return float(pwr);
##
    def set_cfreq(self,cfreq): #cfreq unit is MHz
	   self.device.write(':SENSE:FREQ:Center %fMHZ;'%cfreq);
	   return True;

    def get_cfreq(self): #cfreq unit is MHz
	   cfreq=self.device.ask(':SENSE:FREQ:Center?');
	   return float(cfreq)/1000000.0;

    def set_startfreq(self,startfreq):
	   self.device.write(':SENSE:FREQ:START %fMHZ;'%startfreq);
	   return True;

    def get_startfreq(self): #cfreq unit is MHz
	   startfreq=self.device.ask(':SENSE:FREQ:START?');
	   return float(startfreq)/1000000.0;

    def set_stopfreq(self,startfreq):
	   self.device.write(':SENSE:FREQ:STOP %fMHZ;'%stopfreq);
	   return True;

    def get_stopfreq(self): #cfreq unit is MHz
	   stopfreq=self.device.ask(':SENSE:FREQ:STOP?');
	   return float(stopfreq)/1000000.0;

    def set_rb(self,rb):
        self.device.write(':SENSE:BAND:RES %dKHZ;'%rb);
        return True;
##
    def get_rb(self): #unit is kHz
        rb=self.device.ask(':SENSE:BAND:RES?');
        return float(rb)/1000.0;
##
    def set_vb(self,vb):
        self.device.write(':SENSE:BAND:VIDeo %dKHZ;'%vb);
        return True;
##
    def get_vb(self,vb):
        self.device.ask(':SENSE:BAND:VIDeo?')
        return True
    def set_span(self,span):
        self.device.write(':SENSE:FREQ:SPAN %3.1fMHZ'%span);
        return True;

    def get_span(self):
        span=self.device.ask(':SENSE:FREQ:SPAN?');
        return float(span)/1000000.0;
##
    def set_reflvl(self,reflvl):
        self.device.write('DISP:WIND:TRAC:Y:RLEV %2.2fdbm'%reflvl);
        return True;

    def get_reflvl(self):
        reflvl=self.device.ask('DISP:WIND:TRAC:Y:RLEV?');
        return float(reflvl);
##
    def sweep_ctrl(self,sweep):
        self.device.write(':SENSE:SWEep:TIME %dms'%sweep);
        return True;

    def sweep_ctrl_auto(self,auto):                        #auto==0 or 1
        self.device.write(':SENSE:SWEep:TIME:AUTO %d'%auto)
        return True

    def trace_clearwrite(self,trace):
        self.device.write('TRAC%d:TYPE WRIT'%trace);
        return True

    def trace_maxhold(self,trace):
        self.device.write('TRAC%d:TYPE MAXH'%trace);
        return True

    def trace_minhold(self,trace):
        self.device.write('TRAC%d:TYPE MINH'%trace);
        return True

    def trace_detector(self,trace=1,method='AUTO'):
        if method=='AUTO':
            self.device.write('DET:TRACE%d:AUTO ON'%trace);

        else:
            self.device.write('DET:TRACE%d:AUTO OFF'%trace)
            self.device.write('DET:TRACE%d:%s'%(trace,method));

        return True


##    def get_trace(self):
##	trace=self.device.ask('TRA?');
##	curve=trace.split(',');
##	return [float(x) for x in curve];
##
##    def show(self):
##	self.meas_start();
##	ydata=self.get_trace();
##	span=self.get_span();
##	start_freq=float(self.device.ask('FA?;'))/1000000.0;
##	step=span/len(ydata);
##	xdata=[start_freq+step*i for i in range(0,len(ydata))];
##	plot.plot_curve(xdata,ydata,'Pwr/MHz','MHz','dBm','Spectrum');
##
##    #rb unit:KHz,span/cfreq unit MHz
    def set_param(self,cfreq,span=100,rb=100,vb=30):
        self.set_cfreq(cfreq);
        self.set_rb(rb);
        self.set_span(span);
        self.set_vb(vb);

    def mark(self,mark_num=1,mark_freq=2412.000):
        self.device.write(":CALC:MARK%d:MODE POS"%mark_num)
        self.device.write('CALC:MARK%d:X %f'%(mark_num,mark_freq*1e6));
        amp=float(self.device.ask('CALC:MARK%d:Y?'%mark_num))
        return amp

    #search peaks in current spa
    def pk_search(self,trace=1,mark=1):
        self.trace_clearwrite(trace)
        self.trace_maxhold(trace)
        time.sleep(1)
##        self.device.write('CALC:MARK%d:MAX'%mark);
        self.device.write('CALC:MARK%d:MAX'%mark);
        pklst=[];
##        amp=float(self.device.ask('CALC:TXP:MARK1:Y?'));CALC:MARK2:Y?
##        freq=float(self.device.ask('CALC:TXP:MARK1:X?'))/1000000.0;
        amp=float(self.device.ask('CALC:MARK1:Y?'));
        freq=float(self.device.ask('CALC:MARK1:X?'))/1000000.0;
        print 'amp:%fdBm,freq:%fMHz'%(amp,freq);
        pklst.append((freq,amp));
        return pklst;
##
##    def pk_search_H(self,th=-60,pk_excursion=6):
##        self.clean()
##        self.device.write('TH %dDM;MKPX %dDB;TS;'%(th,pk_excursion));
##        self.device.write('MXMH TRA;');
##        self.device.write('MKPK HI;')
##        time.sleep(0.1); #delay for accumulate data
##        pklst=[];
##
##        amp=float(self.device.ask('MKA?;'));
##        freq=float(self.device.ask('MKF?;'))/1000000.0;
##        #print 'amp:%ddBm,freq:%dMHz'%(amp,freq);
##        pklst.append((freq,amp));
##        return pklst;
##    #search peaks in all measure range(1M-6GHz)
##    def pk_scan(self,th=-60,pk_excursion=6,start_freq=1,end_freq=6000,store_path='null'):
##        if start_freq<0 or end_freq>6000 or start_freq>=end_freq:
##	   print 'scan out of freq range';
##           return [];
##
##	span=self.get_span(); #unit: MHz
##	rb=self.get_rb();     #unit:KHz
##	overlap_span=10;      #unit:MHz to deal with boundary problem
##	#scan include multi-segements
##        seg_num=int(ceil((end_freq-start_freq)/span));
##	pklst_all=[];
##	last_index=-1;
##	cfreq0=start_freq+span/2;
##	for i in range(0,seg_num):
##	    cfreq=cfreq0+i*span-i*overlap_span;
##	    self.set_param(cfreq,span,rb);
##
##	    print '\nSearch peaks from %dMHz to %dMHz'%(cfreq-span/2,cfreq+span/2);
##	    pklst_new=self.pk_search(th,pk_excursion);
##	    #check if there have peaks overlap
##	    for j,pk_data in enumerate(pklst_new):
##	        if last_index>=0 and pk_data[0]<=pklst_all[last_index][0]+rb*0.001:
##		   #insert pk in suitable position
##		   k=last_index;
##                   while pk_data[0]<=pklst_all[k][0]+rb*0.001:
##			 if abs(pk_data[0]-pklst_all[k][0])<=rb*0.001:
##			    print 'find overlap peak!';
##			    j=-1; #flag the pk is dealt
##                            break;
##		         elif k==0:
##			    pklst_all.insert(0,pk_data);
##			    j=-1; #flag the pk is dealt
##			    break;
##		         else:
##			    k=k-1;
##		   if j>=0:
##                      pklst_all.insert(k+1,pk_data);
##
##	        else:
##		   pklst_all.append(pk_data);
##
##	        last_index=len(pklst_all)-1;
##
##	if store_path!='null':
##           if False==createdir(store_path):
##	      logerror('Fail to create dir for log!');
##              return [];
##           #open log file to record result
##           logname="%s/PeakScan"%store_path;
##           createlog(logname,'csv');
##           #record peaks information
##	   writelog('index,freq(MHz),amp(dBm),');
##	   for index,data in enumerate(pklst_all):
##               writelog('%d,%4.1f,%3.1f,'%(index,data[0],data[1]));
##
##	   closelog();
##	   loginfo('\nSave peaks information in Peak_Scan.csv OK!');
##
##	return pklst_all;
##
##    def meas_pwr(self,reflvl,cfreq,span,rb,bdwdth_mhz,vavg_no=20,vb=30):
##	self.device.write('ACPPAR 0;');  #0:manual, 1:auto
##	self.device.write('VAVG OFF;');
##	self.set_cfreq(cfreq);
##	self.set_reflvl(reflvl);
##	if self.get_span()!=span:
##	   self.set_span(span);
##	self.set_rb(rb);
##        self.set_vb(vb);
##
##	self.device.write('ACPBW %dMHZ;'%bdwdth_mhz);
##	self.device.write('CONTS;');  #SNGLS
##	self.device.write('VAVG %d;TS'%vavg_no);
##	self.wait(3);
##	self.device.write('CHP;');
##
##	if '0'!=self.device.ask('ACPERR?;'):
##	   print 'fail to get power value!';
##	   return [];
##        else:
##	   ch_pwr=float(self.device.ask('CHPWR?;'));
##	   return [float('%4.1f'%ch_pwr)];
##
##    #offset is phase_noise measure start freq distance from tone freq,unit MHz
##    #offset deviate cause 0.3dB difference
##    def phn_pwr(self,tone_freq,reflvl,offset=0.10):
##	span=2;       #unit MHz
##	rb=10;        #unit KHz
##	bdwdth_mhz=1; #unit MHz
##
##	#get tone correct freq
##	self.set_reflvl(reflvl);
##	self.set_param(tone_freq,span,rb);
##	if self.get_span()!=span:
##	   self.set_span(span);
##	   self.set_rb(rb);
##	self.device.write('MKPK HI');
##	tone_freq=float(self.device.ask('MF?'))/1000000;
##
##	cfreq=tone_freq+offset+(bdwdth_mhz/2.0);
##        result=self.meas_pwr(reflvl,cfreq,span,rb,bdwdth_mhz);
##	if result!=[]:
##           return result[0]+3; #right and left band pwr add together
##        else:
##	   return 0;
##
##    def tone_pwr(self,tone_freq,reflvl):
##	span=2;       #unit MHz
##	rb=10;        #unit KHz
##	bdwdth_mhz=1; #unit MHz
##	cfreq=tone_freq;
##        result=self.meas_pwr(reflvl,cfreq,span,rb,bdwdth_mhz);
##	if result!=[]:
##           return result[0];
##        else:
##	   return 0;
##
##    #flt_bwdth is half filter bandwidth,unit is MHz
##    def fltn_pwr(self,tone_freq,reflvl,flt_bwdth=8):
##	span=2;       #unit MHz
##	rb=10;        #unit KHz
##	bdwdth_mhz=1; #unit MHz
##	offset=3;     #measure filter noise from 3 to 4MHz offset
##	cfreq=tone_freq+offset+(bdwdth_mhz/2.0);
##        result=self.meas_pwr(reflvl,cfreq,span,rb,bdwdth_mhz);
##	if result!=[]:
##           return result[0]+3.0+10*log10(flt_bwdth);
##        else:
##	   return 0;
##
##    def reflvl_srch(self,tone_freq,ini_reflvl=0):
##	reflvl=ini_reflvl;
##	pk_amp=reflvl;
##	while pk_amp>(reflvl-4) or pk_amp<(reflvl-7):
##	    reflvl=pk_amp+5;
##	    self.set_reflvl(reflvl);
##	    self.meas_start();
##	    self.device.write('MKPK HI');
##	    pk_amp=float(self.device.ask('MKA?'));
##
##	return int(reflvl);
##
##    def pk_detect(self):
##        self.device.write('TS;');
##	self.device.write('MKPK HI');
##	pk_amp=float(self.device.ask('MKA?'));
##	return pk_amp;
##
##    def get_result(self, name):
##	if name == 'PEAK':
##	    return self.pk_detect();
##
    def pk_detect(self):
##        self.device.write('TS;');
    	time.sleep(1)
    	self.device.write('CALC:MARK1:MAX');
    	pk_amp=float(self.device.ask('CALC:MARK1:Y?'));
        freq=float(self.device.ask('CALC:MARK1:X?'))/1000000.0;
    	return (freq,pk_amp);

    def get_result(self, name):
    	if name == 'PEAK':
    	    return self.pk_detect();

class phnoise(object):
    def reset(self,timeout=10):
#self.device.write('IP;');
        self.device.write(':SYST:PRES');
        return True;

    def __init__(self,mode=14,timeout=10,device="N9020A"):
        '''
        mode:   1:  SA
                14: phase noise test
                18: wlan
        '''
        if platform.platform().find("Linux") != -1:
            from GPIBImpl import GPIBLinux
            self.device = GPIBLinux.GPIBDevice(device) # HP
        else:
            from GPIBImpl import GPIBWindows
            self.device = GPIBWindows.GPIBDevice(device)

        pass

        #instrument initialize
        self.reset();

        self.set_mode(mode=mode);
        if mode==14:
            self.meas_avg_count(10)
            self.set_span(offset_start=1,offset_stop=40000)
            self.carrier_search()

        print 'Initialize Spectrum Analyzer OK!'

    def set_mode(self,mode=14):
        '''
        1:  SA
        14: phase noise test
        18: wlan
        '''
        self.device.write(':INSTrument:NSELect %d'%mode)
        if mode==14:
            self.device.write(':CONFigure:LPLot')

    def restart(self):
        '''
        commands will initiate the taking of measurement data without resetting any of the measurement settings that you have changed from their defaults.
        '''
        self.device.write('INITiate:RESTart')

    def carrier_search(self):
        self.device.write(':SENSe:FREQuency:CARRier:SEARch:AUTO ON')
        self.device.write(':SENSe:FREQuency:CARRier:SEARch')

    def carrier_freq_set(self,freq=2412):
        '''
        value unit: MHz

        '''
        self.device.write(':SENSe:FREQuency:CARRier:SEARch:AUTO OFF')
        self.device.write(':SENSe:FREQuency:CARRier %d'%(freq*1e6))

    def set_span(self,offset_start=1,offset_stop=40000):
        '''
        value unit: KHz

        '''
        self.device.write(':SENSe:LPLot:FREQuency:OFFSet:STARt %d'%(offset_start*1e3))
        self.device.write(':SENSe:LPLot:FREQuency:OFFSet:STOP %d'%(offset_stop*1e3))

    def meas_avg_count(self,num=10):
        self.device.write(':SENSe:LPLot:AVERage:STATe ON')
        self.device.write(':SENSe:LPLot:AVERage:COUNt %d'%num)

    def get_result(self,trace=1):
        res=self.device.ask(':READ:LPLot%d?'%(trace+2))
        time.sleep(2)
        return res




