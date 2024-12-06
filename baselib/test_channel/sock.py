#Filename:sock.py
import socket
import time;
import re;
from baselib.loglib.log_lib import *

global sock;
global sockstat;
global IQ_ID;
##IQ_ID = 0;

def close():
    global sock;

    try:
      sock.settimeout(3); #wait for 10 seconds to get reply from server
      sock.send('shutdown');
      lastwords=sock.recv(1024);
    except:
      lastwords='Get Server response timeout!';

    logwarn(lastwords);
    loginfo('Close Sock OK!');
    sock.close();

def open(sername='chopin',Servport=34000):
    global sock;
    global sockstat;
    global IQ_ID;
    loginfo("connect to server ...");

    try:
      sockstat=True;
      step=1; #flag which step in current state for exception
      servport=Servport;
      sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
      sock.settimeout(10);

      step=2;
      seraddr=socket.gethostbyname(sername);
      sock.connect((seraddr,servport));
      loginfo('Available Contact with Server '+sock.getpeername()[0]);
      time.sleep(1);

      step=3;
      sock.send('login');
      line='';

      while re.findall(r'(?:wt200ExitLog|IQxelExitLog|IQviewExitLog|ExitLog)$',line,re.M)==[]:
          line=sock.recv(1024);
          loginfo(line);
##      print '5555',re.findall(r'(?:wt200ExitLog|IQxelExitLog)$',line)
      IQ_value=re.findall(r'(?:wt200ExitLog|IQxelExitLog|IQviewExitLog)$',line)
      if IQ_value == ['IQxelExitLog']:
          IQ_ID = 1;              # IQ_ID=1  IQxel
          print 'IQ_ID',IQ_ID
      elif IQ_value ==['wt200ExitLog']:
          IQ_ID = 2;              # IQ_ID=2  wt200
          print 'IQ_ID=',IQ_ID
      elif IQ_value ==['IQviewExitLog']:
          IQ_ID = 3;              # IQ_ID=3  IQview
          print 'IQ_ID=',IQ_ID
      return"****open server success****"
    except:
        sockstat=False;
        if step==1:
           logerror('Fail to connect with server!');
        elif step==2:
           logerror('Can not find Server which name is:'+sername);
        else:
           logerror('Get Server Login response timeout!');

        return (sockstat,step)

    sock.settimeout(None); #default timeout

def req(cmdstr,timeout=30):
    global sock;
    global sockstat;

    if sockstat==False:
       logerror('Sock is not open!');
       return '';
    #match word and data including float or integer
    matchstr = re.findall(r'^[-*\w+\.*\w*\s+,*]+$',cmdstr,re.M);
    if matchstr==[]:
       logwarn('Cmd syntax is error!');
       return '';

    line='';
    try:
       sock.settimeout(timeout);
       sock.send(cmdstr);
       line=sock.recv(32*1024);
       logdebug(line);
       sock.settimeout(None);
    except:
       logerror('Fail to send command to server!');

    return line;

def getstat():
    global sockstat;
    return sockstat;

def get_IQ_ID():
    global IQ_ID;
    return IQ_ID;