#Filename:server.py
import socket
import time
import re;
import sys;
sys.path.append('.\\');
import com;

global serv;

def serverOpen(addr='127.0.0.1',port=34000):
    global serv;
    try:
      serv=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
      #get IP address of host
      pcname=socket.gethostname();
      print 'Server Name:',pcname;
      addrlist=socket.gethostbyname_ex(pcname)[2];

      addrmatchnum=0;
      print 'No.  Address';
      for i in range(0,len(addrlist)):
          print i,'  ',addrlist[i];
          if addr=='IQview':
             if re.match(r'^192\.168\.100\.',addrlist[i],re.M)!=None:
                addr=addrlist[i];
                addrmatchnum+=1;
          elif addr=='IQxel':
             if re.match(r'^192\.168\.100\.',addrlist[i],re.M)!=None:
                addr=addrlist[i];
                addrmatchnum+=1;
          elif addr == 'WT2000':
             if re.match(r'^192\.168\.100\.',addrlist[i],re.M)!=None:
                addr=addrlist[i];
                addrmatchnum+=1;
          elif addr == 'wt200':
             if re.match(r'^192\.168\.100\.',addrlist[i],re.M)!=None:
                addr=addrlist[i];
                addrmatchnum+=1;
##          else:
##             if re.match(r'^192\.168\.0\.',addrlist[i],re.M)!=None:
##                addr=addrlist[i];
##                addrmatchnum+=1;


      #select IP address if host has multi address
      if addrmatchnum >1:
          addrno=-1;
          while addrno<0 or addrno>=len(addrlist):
              addrno=int(raw_input('please select No. of IP address:'));
              addr=addrlist[addrno];
      elif addrmatchnum==0:
          print 'find no suitable IP address for server!';
          return None;
      else:
          addr=addr;

      print 'Selected IP Address:',addr,' Port:',port;
      serv.bind((addr,port));
    except:
      print 'Fail to setup Server on address:',addr;
      return None;

    try:
      print "The Server is running";
      print "Waiting for client to connect...\n";
      serv.listen(1);
      que,vec=serv.accept();
      print "the socket is connected!";
      print "connect with",vec;
      return que;
    except:
      print 'Listen no socket to connect!';
      return None;

def readln(que,comport=6):
    cmdln=que.recv(1024);
    if cmdln=="login":
       print "client login!";
       PrintLog(que);

       #open serial port of server
       comstat=com.open(comport);
       if comstat==True:
          que.sendall('Com on Server side is Ready!\n');
          que.sendall('ExitLog');
          return True;
       else:
          que.sendall('Fail to open Com%d on Server side!\n'%comport);
          que.sendall('ExitLog');
          return False;
    elif cmdln=='shutdown':
          return False;
    else:
       print "Command From Client:",cmdln;
       try:
          cmd_lst=cmdln.split(',');
          if len(cmd_lst)==1:
             reply=com.req(cmd_lst[0]);
          else:
             reply=com.req(cmd_lst[0],int(cmd_lst[1]));
          que.sendall(reply);
          return True;
       except:
          print 'Server Com fail to operate!';
          input('Press Ctrl+C terminate process...');
          return False;

def PrintLog(que):
     servaddr= que.getsockname();
     ln1= "****************************************\n";
     ln2= "*                                      *\n";
     ln3= "*     Welcom From Remote Server!       *\n";
     ln4= "*     Address:"+servaddr[0]+" Port:"+str(servaddr[1])+" *\n";
     ln5= "*                                      *\n";
     ln6= "****************************************\n";

     prnstr=ln1+ln2+ln3+ln4+ln5+ln6;
     que.sendall(prnstr);

#main process run:
if __name__ == '__main__':
    que= serverOpen();
    if que!=None:
       #wait for disconnect....
       while True:
          sockstat=readln(que,6);
          if sockstat==False:
             break;

       #close com
       com.close();
       print "close server!";
       que.sendall('GoodByte from Server!');

       #delay 1 second,then close socket
       time.sleep(1);
       serv.close();
    else:
       print 'Fail to open Server!';
       try:
         input('Press Ctrl+C terminate process...');
       except:
         print '\nexit abnormal';
