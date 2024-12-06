import time
import re
import platform


class dm(object):
    prim_addr = -1
    sample_time=0.0006530386740331491712707182320442;
    op_statlst=['OPEN',    #just open, not initialize for test
                'CLOSE',   #shutdown,need reopen again
                'RUN',     #begin measure
                'RDY',     #stop running,data is ready
                'ERROR',   #instrument is in error state, need reset
                'LOSE'];   #can't contact with it
    op_stat='LOSE';

    def __init__(self, device_name="34401A", num_of_machine=0):
        if platform.platform().find("Linux") != -1:
            from GPIBImpl import GPIBLinux
            self.device = GPIBLinux.GPIBDevice(device_name,num_of_machine)
        else:
            from GPIBImpl import GPIBWindows
            self.device = GPIBWindows.GPIBDevice(device_name)
        pass

    #def dm_to_use(self,num_of_machine=0):
    #    self.device = self.device_prep.machine_to_use(num_of_machine)
    #    return self.device

    #def dm_to_use(self,num_of_machine=0):
    #    self.device.machine_to_use(num_of_machine)
    #    return

    def get_result(self,name ,data_type = 'MAX'):#data_type : MAX or MIN
        meas_dict = {'IDC':'CURR:DC',
                     'VDC':'VOLT:DC',
                     'IAC':'CURR:AC',
                     'VAC':'VOLT:AC'
                    }
        d_str = meas_dict.get(name)
        if d_str != -1: 
            val = float(self.device.ask("MEAS:%s? %s"%(d_str,data_type)))
            print ('MEASURE %s: %4.8f'%(name,val))
            return val
        else:
            return 'INPUT NAME ERROR, has to be "IDC, VDC, IAC, VAC"'
        # if name == 'IDC':
        #     val = float(self.device.ask("MEAS:CURR:DC? %s"%data_type))
        #     return '%4.8f'%(float(self.device.ask("MEAS:CURR:DC? %s"%data_type)));
        # elif name == 'VDC':
        #     return '%4.8f'%(float(self.device.ask("MEAS:VOLT:DC? %s"%data_type)));
        # elif name == 'IAC':
        #     return '%4.8f'%(float(self.device.ask("MEAS:CURR:AC? %s"%data_type)));
        # elif name == 'VAC':
        #     return '%4.8f'%(float(self.device.ask("MEAS:VOLT:AC? %s"%data_type)));
        # else:
        #     return 'DATA ERROR';

    def isbusy(self,timeout=10):
        for i in range(0,timeout):
            if self.device.ask('*OPC?').find("1") != -1:
                return False;
                time.sleep(1);
        return True;

    def reset(self):
        self.device.write("*RST");
        self.device.write("*CLS");
        if False== self.isbusy():
            print 'DM reset ok!'
            return True;
        else:
            print 'DM reset timeout %d sec!'%timeout;
            return False;

    def start(self,meastype='CURR',maxvalue=0.3,res=1E-3,sample_num=512):
        self.device.write("CONF:%s:DC DEF,DEF"%meastype);
        self.device.write("%s:DC:RANG %f"%(meastype,maxvalue));
        self.device.write("%s:DC:RES %f"%(meastype,res));
        self.device.write("%s:DC:NPLC MIN"%meastype);
        self.device.write("ZERO:AUTO OFF");
        self.device.write("DET:BAND MAX");
        self.device.write("TRIG:SOUR BUS");
        self.device.write("TRIG:SOUR IMM");
        self.device.write("TRIG:DEL:AUTO OFF");
        self.device.write("TRIG:DEL 0");
        self.device.write("SAMP:COUN %d"%sample_num);
        self.device.write("TRIG:COUN 1");
        self.device.write("INIT");


    def getcurve(self):
        self.device.write("*TRG");
        result=self.device.ask("FETC?");
        result_lst=result.split(',');
        curve=[float(data) for data in result_lst];
        return curve;

##    def start_rate(self,meastype='CURR',maxvalue=0.3,sample_num=512,sample_rate=0.001):
##        self.reset();
##        self.device.write("DISP OFF");
##        self.device.write("CONF:%s:DC DEF,DEF"%meastype);
##        self.device.write("%s:DC:RANG %f"%(meastype,maxvalue));
##        self.device.write("%s:DC:RES MAX"%meastype);
##        self.device.write("%s:DC:NPLC MIN"%meastype);
##        self.device.write("ZERO:AUTO OFF");
##        self.device.write("%s:DC:RANG AUTO OFF"%meastype);
##        self.device.write("CALC:STAT OFF");
##        self.device.write("TRIG:SOUR IMM");
##        delay=sample_rate-self.sample_time;
##        self.device.write("TRIG:DEL %f"%delay); # sample delay = 1ms - sample time (0.6538461528ms)
##        self.device.write("SAMP:COUN %d"%sample_num);
##        self.device.write("TRIG:COUN 1");
##        self.device.write("INIT");

    def start_rate(self,meastype='CURR',maxvalue=0.3,sample_num=512,sample_rate=0.001):
        #self.reset();
        self.device.write("DISP OFF");
        self.device.write("CONF:%s:DC DEF,DEF"%meastype);
        self.device.write("%s:DC:RANG %f"%(meastype,maxvalue));
        self.device.write("%s:DC:RES MIN"%meastype);
        self.device.write("%s:DC:NPLC MIN"%meastype);
        self.device.write("ZERO:AUTO OFF");
        self.device.write("%s:DC:RANG AUTO OFF"%meastype);#
        self.device.write("CALC:STAT OFF");
        self.device.write("TRIG:SOUR IMM");
        delay=sample_rate-self.sample_time;
        self.device.write("TRIG:DEL %f"%delay); # sample delay = 1ms - sample time (0.6538461528ms)
        self.device.write("SAMP:COUN %d"%sample_num);
        self.device.write("TRIG:COUN 1");
        self.device.write("INIT");

##    def start_rate(self,meastype='CURR',maxvalue=0.3,sample_num=512,sample_rate=0.001):
##        self.reset();
##        self.device.write("DISP OFF");
##        self.device.write("CONF:%s:DC DEF,DEF"%meastype);
##        self.device.write("%s:DC:RANG %f"%(meastype,maxvalue));
##        self.device.write("%s:DC:RES MAX"%meastype);
##        self.device.write("%s:DC:NPLC MIN"%meastype);
##        self.device.write("ZERO:AUTO OFF");
##        self.device.write("%s:DC:RANG AUTO OFF"%meastype);
##        self.device.write("CALC:STAT OFF");
##        self.device.write("TRIG:SOUR IMM");
##        delay=sample_rate-self.sample_time;
##        self.device.write("TRIG:DEL %f"%delay); # sample delay = 1ms - sample time (0.6538461528ms)
##        self.device.write("SAMP:COUN %d"%sample_num);
##        self.device.write("TRIG:COUN 1");
##        self.device.write("INIT");

    def display(self,cmdstr="READY"):
        self.device.write("DISP ON");
        self.device.write("DISP:TEXT \"%s\""%cmdstr);

    def disp_clr(self):
        self.device.write("DISP:TEXT:CLE");


def measure_current(plot=1, sample_rate=0.001,meastype='CURR',sample_num=512,maxvalue=0.3,labels='', hold=0, color='blue', title="", fw=0, fd="../rtc_data/", fn=""):
    import matplotlib.pyplot as plt
    import numpy as np
    mydm = dm.dm('GPIB2::23')
    I_sum=0;
    max_cur = 0
    min_cur = 2000                           #################/////
    mydm.start_rate(sample_num=sample_num,meastype=meastype,maxvalue=maxvalue,sample_rate=sample_rate)
    #mydm.start(sample_num=sample_num,meastype=meastype,maxvalue=maxvalue)
    res = mydm.getcurve()

    # A to mA
    for index, subres in enumerate(res):
        res[index] = subres*1000
        I_sum=I_sum+res[index]
        if res[index] > max_cur:
            max_cur = res[index]
        if res[index] < min_cur:             #################/////
            min_cur = res[index]
    result_average = I_sum/sample_num;

    print "max_current=%f"%max_cur
    print "min_current=%f"%min_cur           #################/////
    # plot
    if(plot):
        x = np.array(range(0, len(res)));
        y = np.array(res);
        if(hold):
            plt.hold;
        else:
            plt.figure(figsize=(8,8));
        plt.step(x,y,color,linewidth=2,label=labels+" max_vol: %f min_vol: %f"%(max_cur, min_cur));
        #plt.step(x,y,color,linewidth=2,label=labels+" average: %f"%(result_average));
        plt.legend();
        #plt.plot(x,z,"b--",label="$cos(x^2)$")
##      plt.xlabel("%s"%xlabel);
##      plt.ylabel("%s"%ylabel);
        plt.title(title);
##
##      lmt=getlmt(y);
##      plt.ylim(lmt[0],lmt[1]);
        #plt.legend();
        plt.xlabel("time unit: %dms"%(sample_rate*1000));
        if(meastype=='CURR'):
            plt.ylabel("current unit: 1mA");
        else:
            plt.ylabel("voltage unit: 1mV");
        plt.show();
        if(fw):
            f= open(fd+fn+'.txt', 'w')
            for index, content in enumerate(y):
                f.write("%f\n"%content)
    return result_average
