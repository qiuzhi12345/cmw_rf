# -- coding: utf-8 --

#Filename: usb.py
import os
import logging
import time
import platform
import sys
import inspect
import numpy as np
if platform.platform().find("Win") != -1:
    import ctypes

class _eaglelog(object):
    log = None
    logf = None
    def __init__(self):
        self.LOGPATH = "./log/"

        if platform.platform().find("Win") != -1:
            self.FOREGROUND_WHITE = 0x0007
            self.FOREGROUND_BLUE = 0x09 # text color contains blue.
            self.FOREGROUND_GREEN= 0x0A # text color contains green.
            self.FOREGROUND_RED  = 0x0C # text color contains red.
            self.FOREGROUND_YELLOW = 0x0E
            self.STD_OUTPUT_HANDLE= -11
            self.std_out_handle = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        else:
            self.FOREGROUND_WHITE = 37
            self.FOREGROUND_BLUE = 34 # text color contains blue.
            self.FOREGROUND_GREEN= 32 # text color contains green.
            self.FOREGROUND_RED  = 31 # text color contains red.
            self.FOREGROUND_YELLOW = 33

    def __set_color(self, color):
        global std_out_handle
        if platform.platform().find("Win") != -1:
            bool = ctypes.windll.kernel32.SetConsoleTextAttribute(self.std_out_handle, color)
            return bool
        else:
            sys.stdout.write("\033[1;%dm"%color)
            sys.stdout.flush()

    def __clear_color(self):
        global std_out_handle
        if platform.platform().find("Win") != -1:
            bool = ctypes.windll.kernel32.SetConsoleTextAttribute(self.std_out_handle, self.FOREGROUND_WHITE)
            return bool
        else:
            sys.stdout.write("\033[0m")
            sys.stdout.flush()


    def loglevelinit(self):
        '''
        初始化 log system
        '''
        N = "N"
        D = "D"
        I = "I"
        W = "W"
        E = "E"
        R = "R"
        logging.addLevelName(0,  N)
        logging.addLevelName(10, D)
        logging.addLevelName(20, I)
        logging.addLevelName(30, W)
        logging.addLevelName(40, E)
        logging.addLevelName(50, R)

    def loggetlevel(self):
        '''
        获取 当前 log 级别：
        '''
        loglvl=_eaglelog.log.getEffectiveLevel();
        return logging.getLevelName(loglvl);

    def logsetlevel(self, infolvl):
        '''
        获取 当前 log 级别：
        '''
        if    infolvl=='DEBUG' or infolvl=='D' :
            _eaglelog.log.setLevel(logging.DEBUG);
        elif  infolvl=='INFO'  or infolvl=='I':
            _eaglelog.log.setLevel(logging.INFO);
        elif  infolvl=='WARN' or infolvl=='WARNING'  or infolvl=='W':
            _eaglelog.log.setLevel(logging.WARN);
        elif  infolvl=='ERROR' or infolvl=='E':
            _eaglelog.log.setLevel(logging.ERROR);
        elif  infolvl=='RES' or infolvl=='R':
            _eaglelog.log.setLevel(logging.CRITICAL);
        else:
            print 'Error in level,try again...';



    def logdebug(self, info):
        '''
        输出 DEBUG 级别 log
        '''
        if _eaglelog.logf != None:
            _eaglelog.logf.debug(info);
        self.__set_color(self.FOREGROUND_BLUE)
        _eaglelog.log.debug(info);
        self.__clear_color()
    def loginfo(self, info):
        '''
        输出 infor 级别 log
        '''
        if _eaglelog.logf != None:
            _eaglelog.logf.info(info);
       #set_color(FOREGROUND_BLUE)
        _eaglelog.log.info(info);
        #__clear_color()
    def logwarn(self, info):
        '''
        输出 warn 级别 log
        '''
        if _eaglelog.logf != None:
            _eaglelog.logf.warn(info);
        self.__set_color(self.FOREGROUND_YELLOW)
        _eaglelog.log.warn(info);
        self.__clear_color()
    def logerror(self, info):
        '''
        输出 error 级别 log
        '''
        if _eaglelog.logf != None:
            _eaglelog.logf.error(info);
        self.__set_color(self.FOREGROUND_RED)
        _eaglelog.log.error(info);
        self.__clear_color()
    def logres(self, info):
        '''
        输出 result 级别 log
        '''
        if _eaglelog.logf != None:
            _eaglelog.logf.critical(info);
        self.__set_color(self.FOREGROUND_RED)
        _eaglelog.log.critical(info);
        self.__clear_color()

    def log2f_init(self, logname,filetype='csv'):
        '''
        输出log 至 文件

        :filetype:
            log 文件后缀
        :return:
            log 文件名字
        '''
        #add log file record method

        if _eaglelog.logf == None:
            _eaglelog.logf=logging.getLogger('eaglef');
            logtime= time.strftime('_%Y_%m_%d_%H_%M_%S',time.localtime());
            filename='./log/'+logname+logtime+'.'+filetype;
            formatter = logging.Formatter('[%(asctime)s %(funcName)s %(levelname)-8s]: %(message)s')
            self.logfile=logging.FileHandler(filename,'w');
            self.logfile.setFormatter(formatter);
            _eaglelog.logf.addHandler(self.logfile);
            _eaglelog.logf.setLevel(logging.DEBUG);
            return filename;


    def log2f_deinit(self):
        '''
        关闭输出 log 文件
        '''
        self.logfile.flush();
        self.logfile.close();
        _eaglelog.logf.removeHandler(self.logfile);

    def log_init(self):
        """
        logsystem 初始化
        """
        # try:
        if _eaglelog.log == None:
            _eaglelog.log=logging.getLogger('eagle');
            self.loglevelinit()
            formatter = logging.Formatter('[%(levelname)-1s]: %(message)s')
            console=logging.StreamHandler();
            console.formatter = formatter
            _eaglelog.log.addHandler(console);
            _eaglelog.log.setLevel(logging.DEBUG);
            print 'Load Log system, Log level:',self.loggetlevel();
        # except:
        #     print 'Fail to load LOG SYSTEM!!!!!';


def _infor(info):
    res = ''
    for index, i in enumerate(info):
        if index == len(info) - 1:
            res = res + str(i)
        else:
            res = res + str(i) + " "
    return res

global _loginst
_loginst = _eaglelog()
_loginst.log_init()

def logdebug(*info):
    '''
    打印 DEBUG 级别 log
    '''
    out = _infor(info)
    _loginst.logdebug(out)
def loginfo(*info):
    '''
    打印 INFO 级别 log
    '''
    out = _infor(info)
    _loginst.loginfo(out)
def logwarn(*info):
    '''
    打印 WARN 级别 log
    '''
    out = _infor(info)
    _loginst.logwarn(out)
def logerror(*info):
    '''
    打印 ERROR 级别 log
    '''
    out = _infor(info)
    _loginst.logerror(out)
def logres(*info):
    '''
    打印 RESULT 级别 log
    '''
    out = _infor(info)
    _loginst.logres(out)



def logpass():
    '''
    打印 PASS log, 级别为 RESULT

    :return:
        True
    '''
    testcase = inspect.stack()[1][3]
    _loginst.logres("%s: PASS"%testcase)
    return True
def logfail():
    '''
    打印 Fail log, 级别为 RESULT

    :return:
        False
    '''
    testcase = inspect.stack()[1][3]
    _loginst.logres("%s: FAIL"%testcase)
    return False

def logresck(res):
    if res:
        testcase = inspect.stack()[1][3]
        _loginst.logres("%s: PASS"%testcase)
        return True
    else:
        testcase = inspect.stack()[1][3]
        _loginst.logres("%s: FAIL"%testcase)
        return False

def log2f_init(logname,filetype='csv'):
    '''
    打印log 的同时，存入log 文件中

    :filetype:
        log 文件后缀
    :return:
        log 文件名字
    '''
    return _loginst.log2f_init(logname,filetype)
def log2f_deinit():
    '''
    关闭输出 log 文件
    '''
    _loginst.log2f_deinit()
def logsetlevel(infolvl):
    '''
    设置 log 输出 level包括

    - DEBUG (D)
    - INFO  (I)
    - WARN  (W)
    - ERROR (E)
    - RES   (R)
    '''

    _loginst.logsetlevel(infolvl)
def loggetlevel():
    '''
    获取当前 log level
    :return:

    '''
    return _loginst.loggetlevel()

def logcolor(log_str, c_u = 'y'):
    '''colorize string for print

    :param log_str: contents to be printed
    :param color:
            - Y   YELLOW
            - Gr  GREY
            - B   BLUE
            - C   CYAN
            - G   GREEN
            - R   RED
            - M   Megenta
            - GY  
            - GB
    :return: a string patterned with selected color
    '''
    c_l = {'Gr':30,
           'R' :31,
           'G' :32,
           'Y' :33,
           'B' :34,
           'M' :35,
           'C' :36,
           'W' :37,
           'GY':'30;43',
           'GB':'30;44'
           }

    color_index = c_l.get(c_u.upper(),37) #returns white if not found 
    prefix = '\033[1;%r'%color_index
    endfix = '\033[1;m'
    context_colored = prefix +'m'+log_str+endfix
    return context_colored 
