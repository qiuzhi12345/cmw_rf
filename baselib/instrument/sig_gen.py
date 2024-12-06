from visa import *
import time
import re

class dm(GpibInstrument):
    prim_addr = -1;
    op_statlst=['OPEN',    #just open, not initialize for test
		'CLOSE',   #shutdown,need reopen again
		'RUN',     #begin measure
		'RDY',     #stop running,data is ready
		'ERROR',   #instrument is in error state, need reset
		'LOSE'];   #can't contact with it
    op_stat='LOSE';
    def __init__(self,name='',timeout = 10):
        '''name: dm1 or dm2,please check tag on dm instruments
        '''
	try:
	    instr_lst0 = get_instruments_list();
	    instr_lst= [];
	    for i in range(0, len(instr_lst0)):
		if re.findall(r'GPIB', instr_lst0[i],re.M)!=[]:
		    instr_lst.append(instr_lst0[i]);
	    if len(instr_lst) == 0:
		print 'Find no instrument on GPIB Bus!';
		return;
	    self.prim_addr='';
	    for i in range(0, len(instr_lst)):
		instr = instrument(instr_lst[i]);
		answer = instr.ask('*IDN?');
		if answer.find('HEWLETT-PACKARD,34401A,0,10-5-2')!=-1:
                    if name in ['dm1','DM1','Dm1'] and instr_lst[i]=='GPIB0::6':
                          self.prim_addr=instr_lst[i];
                          print 'Find DM1, Address is %s'%instr_lst[i];
		          break;
                    elif name in ['dm2','DM2','Dm2'] and instr_lst[i]=='GPIB0::22':
                          self.prim_addr=instr_lst[i];
                          print 'Find DM2, Address is %s'%instr_lst[i];
		          break;
                    elif name =='':
                        print 'Find DM, Address is %s'%instr_lst[i];
                        self.prim_addr=instr_lst[i];
		        break;
	    if self.prim_addr == '':
                print 'Sorry, find no DM name:%s exist!'%name;
		return;
	    GpibInstrument.__init__(self,self.prim_addr);
	    print 'Open DM Successfully!';
	    self.op_stat = 'OPEN';
	    self.timeout = timeout;
	except:
	    print 'Fail to operate GPIB bus!'
	    return;
	print 'Initialize DM OK!'
    def get_result(self,name ,data_type = 'AVER'):
	if name == 'IDC':
	    return '%4.4f'%(float(self.ask("MEAS:CURR:DC? MAX")));
	elif name == 'VDC':
	    return '%4.4f'%(float(self.ask("MEAS:VOLT:DC? MAX")));
	elif name == 'IAC':
	    return '%4.4f'%(float(self.ask("MEAS:CURR:AC? MAX")));
	elif name == 'VAC':
	    return '%4.4f'%(float(self.ask("MEAS:VOLT:AC? MAX")));
	else:
	    return 'DATA NAME ERROR';

    def isbusy(self,timeout=10):
	for i in range(0,timeout):
	    if '1'==self.ask('*OPC?'):
	        return False;
    	    time.sleep(1);
	return True;

    def reset(self):
        self.write("*RST");
        self.write("*CLS");
	if False== self.isbusy():
	    print 'DM reset ok!'
	    return True;
        else:
            print 'DM reset timeout %d sec!'%timeout;
	    return False;


    def start(self,meastype='CURR',maxvalue=0.3,res=1E-3,sample_num=512):
        self.write("CONF:%s:DC DEF,DEF"%meastype);
        self.write("%s:DC:RANG %f"%(meastype,maxvalue));
        self.write("%s:DC:RES %f"%(meastype,res));
        self.write("%s:DC:NPLC MIN"%meastype);
        self.write("ZERO:AUTO OFF");
        self.write("DET:BAND MAX");
        self.write("TRIG:SOUR BUS");
        self.write("TRIG:DEL:AUTO OFF");
        self.write("TRIG:DEL 0");
        self.write("SAMP:COUN %d"%sample_num);
        self.write("TRIG:COUN 1");
        self.write("INIT");

    def getcurve(self):
        self.write("*TRG");
        result=self.ask("FETC?");
	result_lst=result.split(',');
        curve=[float(data) for data in result_lst];
        return curve;

    def display(self,cmdstr="READY"):
        self.write("DISP ON");
        self.write("DISP:TEXT \"%s\""%cmdstr);

    def disp_clr(self):
        self.write("DISP:TEXT:CLE");


