import sys
from baselib.loglib.log_lib import *
import socket
from baselib.test_channel import (sock,server)
import time
import re
import subprocess

class instru_server(object):

    def __init__(self,instru_name="wt200",ipaddr="192.168.100.251"):
        self.instru_name=instru_name
        if re.findall('iqx',self.instru_name,flags=re.IGNORECASE)!=[]:
            server_name="iqxel_serv.py"
            serv_port=34000
            ipaddr="192.168.100.252"
        elif re.findall('iqv',self.instru_name,flags=re.IGNORECASE)!=[]:
            server_name="iqv_serv.py"
            serv_port=34020
            ipaddr="192.168.100.254"
        elif re.findall('wt',self.instru_name,flags=re.IGNORECASE)!=[]:
            server_name="wt200_serv.py"
            serv_port=34010
        else:
            logerror("instru_server is not exist")
        loginfo(server_name)
        addrlist=socket.gethostbyname_ex(socket.gethostname())[2]
        addr=""
        for i in range(0,len(addrlist)):
            if re.match(r'^192\.168\.100\.',addrlist[i],re.M)!=None:
                addr=addrlist[i];
                break
        if addr=="":
            logerror("192.168.100.xxx serverIP is not exist")
            sys.exit(1)
        logsetlevel("RES")
        sockstat=sock.open(addr,serv_port)
        logsetlevel("INFO")
        if sockstat==None:
            loginfo("succeed to connect with server!")
        elif sockstat[0]==False:
            if sockstat[1]==3:
                sock.open(addr,serv_port)
                sock.req("open %s"%ipaddr)
                #sock.req("init")
            else:
                chlid=subprocess.Popen(['ipython','-i','./baselib/instrument/tester_serv/%s'%(server_name),ipaddr],shell=False,creationflags=subprocess.CREATE_NEW_CONSOLE)

                while True:
                    logsetlevel("RES")
                    result=sock.open(addr,serv_port)
                    logsetlevel("INFO")
                    if result=="****open server success****":
                        break


