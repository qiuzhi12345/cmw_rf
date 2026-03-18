#  -*- coding: utf-8 -*-
from imp import reload

# Form implementation generated from reading ui file 'bt__rf_test_tool_v1.2.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui,Qt
from PyQt4.QtCore import QRegExp, QTimer
from PyQt4.QtGui import QMainWindow, QFileDialog, QApplication, QAbstractItemView, QRegExpValidator, QIntValidator, QMessageBox

import sys
reload(sys)
sys.setdefaultencoding('ISO-8859-1')
# import random
# import exceptions

from subprocess import Popen
from threading import Thread
# import time
# import subprocess
# import threading

from rftest_tool import Ui_MainWindow
# from rftest.testcase.performance.bt_test_cmw import *
from common import MEM_TS
# from baselib.instrument import *
# from baselib.instrument import cmw_bt
from baselib.test_channel import com
from baselib.loglib.log_lib import *
import pyvisa
# import visa

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)



class EmittingStr(QtCore.QThread):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    # def __init__(self, parent=None):
    #     super(EmittingStr, self).__init__(parent)

    def __init__(self,  data):
        # self._data = data
        # super(EmittingStr, self).__init__(data)
        # self.show_win = show_win
        super(EmittingStr, self).__init__()

    def write(self,data):

        self.textWritten.emit("{} :".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+'{}'.format(data))

class MyWindow(QMainWindow,Ui_MainWindow):

    def __init__(self, parent = None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)

        self.dic_edr2_rate = {
            'DH1':    'E21P',
            'DH3':    'E23P',
            'DH5':    'E25P'
            }
        self.dic_edr3_rate = {
            'DH1':    'E31P',
            'DH3':    'E33P',
            'DH5':    'E35P'
            }

        self.dic_pwr_level = {
            '12':  63,
            '10':  42,
            '8':   31,
            '6':   24,
            '4':   18,
            '2':   14,
            '0':   11,
            '-2':  9,
            '-4':  7,
            'min':  0
         }
        self.dic_pattern = {
            '11110000':  1,
            '10101010':  2,
            '11111111':  4,
            '00000000':  5,
            '00001111':  6,
            '01010101':  7,
            'prbs9':  0,
            'prbs15':  3
        }

        self.emitting = EmittingStr(self)
        self.emitting.textWritten.connect(self.update_text)

        self.pushButton_uart_refrash.clicked.connect(self.uart_comport_scan)
        # if self.groupBox_uartset.isChecked() == True:
        #     self.uart_comport_scan()
        self.pushButton_uart.clicked.connect(self.msg_uart)
        self.line_edit_event()

        self.comboBox_txmode.currentIndexChanged.connect(self.line_edit_event)
        self.comboBox_rxmode.currentIndexChanged.connect(self.line_edit_event)
        self.pushButton_txon.clicked.connect(self.txon)
        self.pushButton_rxon.clicked.connect(self.rxon)
        self.pushButton_txoff.clicked.connect(self.cmdstop)
        self.pushButton_rxoff.clicked.connect(self.rxoff)

        self.pushButton_rd.clicked.connect(self.reg_rd)
        self.pushButton_rdbit.clicked.connect(self.reg_rdbit)
        self.pushButton_wr.clicked.connect(self.reg_wr)
        self.pushButton_wrbit.clicked.connect(self.reg_wrbit)

        self.pushButton_signaltest_enter.clicked.connect(self.signaltest_enter)
        self.pushButton_signaltest_exit.clicked.connect(self.signaltest_exit)

    def reg_rd(self):
        regaddr = str(self.lineEdit_regaddr.text())
        self.test_logdebug("regaddr:{}".format(regaddr))
        regaddr =eval(regaddr)
        self.mem = MEM_TS(self.COM)
        result = self.mem.rd(regaddr)
        self.lineEdit_regvalue.setText(str(hex(result)))

    def reg_rdbit(self):
        regaddr = str(self.lineEdit_regaddr.text())
        msb = int(self.lineEdit_msb.text())
        lsb = int(self.lineEdit_lsb.text())
        self.test_logdebug("regaddr:{}".format(regaddr))
        regaddr =eval(regaddr)
        self.mem = MEM_TS(self.COM)
        result = self.mem.rdm(regaddr,msb,lsb)
        self.lineEdit_regvalue.setText(str(hex(result)))

    def reg_wr(self):
        regaddr = str(self.lineEdit_regaddr.text())
        regvalue = str(self.lineEdit_regvalue.text())

        self.test_logdebug("regaddr:{}  regvalue:{}".format(regaddr,regvalue))
        regaddr =eval(regaddr)
        regvalue =eval(regvalue)
        self.mem = MEM_TS(self.COM)
        self.mem.wr(regaddr,regvalue)

    def reg_wrbit(self):
        regaddr = str(self.lineEdit_regaddr.text())
        regvalue = str(self.lineEdit_regvalue.text())
        msb = int(self.lineEdit_msb.text())
        lsb = int(self.lineEdit_lsb.text())
        self.test_logdebug("regaddr:{}  regvalue:{}".format(regaddr,regvalue))
        regaddr =eval(regaddr)
        regvalue =eval(regvalue)
        self.mem = MEM_TS(self.COM)
        self.mem.wrm(regaddr,msb,lsb,regvalue)

    def signaltest_enter(self):
        self.cmdstop()
        cmdstr = 'cli_btdut'
        for i in range(4):
            time.sleep(0.1)
            res = self.COM.req_com(cmdstr, endstr='TS', wr_end='\r\n', timeout=1)
            self.test_logdebug(res)
            if len(res) != 0:
                if res[1].find('enter DUT mode') != -1:
                    self.lineEdit_signaltest.setText('enter DUT mode success')
                    self.groupBox_txmode.setEnabled(False)
                    self.groupBox_rxmode.setEnabled(False)
                    break
    def signaltest_exit(self):
        cmdstr = 'cli_testend'
        for i in range(4):
            time.sleep(0.1)
            res = self.COM.req_com(cmdstr, endstr='TS', wr_end='\r\n', timeout=1)
            self.test_logdebug(res)
            if len(res) != 0:
                if res[0].find('bttestend') != -1:
                    self.lineEdit_signaltest.setText('exit')
                    self.groupBox_txmode.setEnabled(True)
                    self.groupBox_rxmode.setEnabled(True)
                    break
    def txon(self):
        self.mem = MEM_TS(self.COM)
        txmode = str(self.comboBox_txmode.currentText())
        chan = int(self.lineEdit_channel.text())
        pattern = str(self.comboBox_tx_pattern.currentText())
        s_pwr_level = str(self.comboBox_tx_pwr_level.currentText())
        pattern = self.dic_pattern[pattern]
        pwr_level = self.dic_pwr_level[s_pwr_level]
        self.mem.wrm(0x50421004,22,22,1)
        self.mem.wrm(0x5042100c,31,26,pwr_level)
        self.test_logdebug("txmode:{} chan:{} pattern:{}  pwr_level:{}".format(txmode,chan,pattern,pwr_level))
        if txmode == 'txtone':
            self.txtone(2402+chan,  pwr_level)
        elif txmode == 'br':
            self.BR_TX(chan=chan, len=27, ptype=pattern, rate=1)
        elif txmode == 'edr_2m':
            self.BR_TX(chan=chan, len=54, ptype=pattern, rate=4)
        elif txmode == 'edr_3m':
            self.BR_TX(chan=chan, len=83, ptype=pattern, rate=7)
        elif txmode == 'le_1m':
            self.LE_TX(chan=chan, len=37, ptype=pattern, phy=1)
        elif txmode == 'le_2m':
            self.LE_TX(chan=chan, len=37, ptype=pattern, phy=2)

    def rxon(self):
        self.mem = MEM_TS(self.COM)
        rxmode = str(self.comboBox_rxmode.currentText())
        chan = str(self.lineEdit_channel_rx.text())
        if rxmode == 'br':
            self.BR_RX(chan=chan, len=27, ptype=0, rate=1, ltaddr=1, uap=0x04, lap=0x010203)
        elif rxmode == 'edr_2m':
            self.BR_RX(chan=chan, len=54, ptype=0, rate=4, ltaddr=1, uap=0x04, lap=0x010203)
        elif rxmode == 'edr_3m':
            self.BR_RX(chan=chan, len=83, ptype=0, rate=7, ltaddr=1, uap=0x04, lap=0x010203)
        elif rxmode == 'le_1m':
            self.LE_RX(chan=chan, len=37, ptype=0, phy=1)
        elif rxmode == 'le_2m':
            self.LE_RX(chan=chan, len=37, ptype=0, phy=2)
    def rxoff(self):
        self.mem = MEM_TS(self.COM.ComPort)
        rxmode = self.comboBox_rxmode.currentText()
        res = self.cmdstop()
        if rxmode == 'le_1m':
            if res.find('bleRxCount=') != -1:
                blerxcount = int(res[res.find('bleRxCount=')+11:res.find('\n')])
                self.test_logdebug("blerxcount:{}".format(blerxcount))

                self.lineEdit.text(blerxcount)

    def cmdstop(self):
        cmdstr = 'cli_testend'
        for i in range(10):
            time.sleep(0.1)
            res = self.COM.req_com(cmdstr, endstr='TS', wr_end='\r\n', timeout=1)
            self.test_logdebug(res)
            if len(res) != 0:
                if res[0] != 'cmd   head error! Send Again!   \n':
                    break
        return res
    def LE_TX(self, chan=0, len=37, ptype=2, phy=2):
        '''
        chan:   0--39
        len:    1--255
        ptype:       * 0x00 PRBS9 sequence "11111111100000111101" (in transmission order) as described in [Vol 6] Part F, Section 4.1.5
                     * 0x01 Repeated "11110000" (in transmission order) sequence as described in [Vol 6] Part F, Section 4.1.5
                     * 0x02 Repeated "10101010" (in transmission order) sequence as described in [Vol 6] Part F, Section 4.1.5
                     * 0x03 PRBS15 sequence as described in [Vol 6] Part F, Section 4.1.5
                     * 0x04 Repeated "11111111" (in transmission order) sequence
                     * 0x05 Repeated "00000000" (in transmission order) sequence
                     * 0x06 Repeated "00001111" (in transmission order) sequence
                     * 0x07 Repeated "01010101" (in transmission order) sequence
        phy:    1 ->1M; 2 ->2M; 3->coded S=8; 4->coded S=2
        '''
        if chan < 0 or chan > 39:
            self.test_logerror(' le channel is out of range')
            return False
        if len < 1 or len > 255:
            self.test_logerror('le packet lenght is out of range')
            return False
        self.cmdstop()
        for i in range(5):
            res = self.COM.req_com("cli_bletx ch=%d len=%d pay=%d phy=%d" %(chan, len, ptype, phy), wr_end='\r\n', timeout=5)
            if res.find("bletx ch=%d len=%d pay=%d phy=%d" %(chan, len, ptype, phy)) != -1:
                self.test_logdebug('le tx ok')
                break
            i = i+1
            self.cmdstop()
            self.test_logerror('cmd return error')

    def BR_TX(self, chan=0, len=37, ptype=2, rate=2):
        '''
        chan:       0--78
        len:        1--1021
                    lenMax: (DH1)->27;    (2-DH1)->54;  (3-DH1)->83
                    (DH3)->183;   (2-DH3)->367; (3-DH3)->552
                    (DH5)->339;   (2-DH5)->679; (3-DH5)->1021
        ptype:       * 0x00 PRBS9 sequence "11111111100000111101" (in transmission order) as described in [Vol 6] Part F, Section 4.1.5
                     * 0x01 Repeated "11110000" (in transmission order) sequence as described in [Vol 6] Part F, Section 4.1.5
                     * 0x02 Repeated "10101010" (in transmission order) sequence as described in [Vol 6] Part F, Section 4.1.5
                     * 0x03 PRBS15 sequence as described in [Vol 6] Part F, Section 4.1.5
                     * 0x04 Repeated "11111111" (in transmission order) sequence
                     * 0x05 Repeated "00000000" (in transmission order) sequence
                     * 0x06 Repeated "00001111" (in transmission order) sequence
                     * 0x07 Repeated "01010101" (in transmission order) sequence
        type:       1 ->(DH1);    2 ->(2-DH1);  3->(3-DH1);
                    4 ->(DH3);    5 ->(2-DH3);  6->(3-DH3);
                    7 ->(DH5);    8 ->(2-DH5);  9->(3-DH5);
        '''
        self.cmdstop()
        if chan < 0 or chan > 78:
            self.test_logerror(' BT channel is out of range')
            return False
        if len < 1 or len > 1021:
            self.test_logerror('BT packet lenght is out of range')
            return False
        for i in range(3):
            res = self.COM.req_com("cli_bttx ch=%d len=%d pay=%d type=%d ltaddr=1 uap=0x00 lap=0x123456 pkt_num=0" %(chan, len, ptype, rate), wr_end='\r\n', timeout=5)
            self.test_logdebug(res)
            if res.find("bttx ch={} len={} pay={} type=".format(chan, len, ptype)) != -1 or res.find("bttx pkt_num:") != -1:
                self.test_logdebug('bt tx ok')
                break
            i = i+1
            self.cmdstop()
            self.test_logerror('cmd return error')

    def BR_RX(self, chan=0, len=27, ptype=5, rate=1, ltaddr=1, uap=0x48, lap=0x000080):
        if chan < 0 or chan > 78:
            self.test_logerror(' BT channel is out of range')
            return False
        if len < 1 or len > 1021:
            self.test_logerror('BT packet length is out of range')
            return False
        if ptype < 1 or ptype > 6:
            self.test_logerror('BT packet paytype is out of range')
            return False
        self.COM.req_com("cli_btrx ch={} len={} pay={} type={} ltaddr={} uap={} lap={}".format(chan, len, ptype, rate, ltaddr, hex(uap), hex(lap)), wr_end='\r\n', timeout=5)

    def LE_RX(self, chan=0, phy=1, mod=0, countMode=0):
        if chan < 0 or chan > 39:
            self.test_logerror(' channel is out of range')
            return False
        self.COM.req_com("cli_blerx ch={} phy={} modu={} countMode={}".format(chan, phy, mod, countMode), wr_end='\r\n', timeout=5)

    def txtone(self, chan, pwr_level):
        # if chan < 0 or chan > 39:
        #     logerror(' channel is out of range')
        #     return False
        self.cmdstop()
        self.COM.req_com("cli_txtone freq={} pa={} txm=255".format(chan, pwr_level), wr_end='\r\n', timeout=5)


    def update_text(self,message):

        self.textBrowser.append(self.fontcolor+message)
        self.CURSOR = self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.CURSOR.End)
        QApplication.processEvents()

    def test_logdebug(self,msg):
        self.fontcolor = "<font color='blue'>"
        logdebug(msg)
        self.emitting.write(msg)
    def test_log(self,msg):
        self.fontcolor = "<font color='black'>"
        loginfo(msg)
        self.emitting.write(msg)
    def test_logerror(self,msg):
        self.fontcolor = "<font color='red'>"
        logerror(msg)
        self.emitting.write(msg)

    def msg_debug(self):
        QtGui.QMessageBox.about(self,'info','debug')

    def line_edit_event(self):
        self.line_edit_range()
        # self.lineEdit_txlevel.editingFinished.connect(self.line_edit_range)

    def line_edit_range(self):
        if str(self.comboBox_txmode.currentText()).find('le') != -1:
            self.lineEdit_channel.setValidator(QIntValidator(0,39))
        else:
            self.lineEdit_channel.setValidator(QIntValidator(0,78))
        if str(self.comboBox_rxmode.currentText()).find('le') != -1:
            self.lineEdit_channel_rx.setValidator(QIntValidator(0,39))
        else:
            self.lineEdit_channel_rx.setValidator(QIntValidator(0,78))

    def msg_uart(self):
        self.test_logdebug('uart comport index:{}'.format(self.comboBox_uartcomport.currentIndex()))
        if self.comboBox_uartcomport.currentIndex() == -1 or self.comboBox_uartbd.currentIndex() == -1:
            QMessageBox.about(self, "worning", 'Please select comport and baudrate')
        else:
            self.test_logdebug('pushButton_uart.text:{}'.format(self.pushButton_uart.text()))
            self.uart_setting()
            if self.pushButton_uart.text() == 'open':
                if self.COM.isopen == True:
                    self.pushButton_uart.setText('close')
                    self.groupBox_txmode.setEnabled(True)
                    self.groupBox_rxmode.setEnabled(True)
                    self.groupBox_reg.setEnabled(True)
                    self.groupBox_signaltest.setEnabled(True)
                else:
                    QMessageBox.critical(self, "error", 'The port is occupied')

            else:
                self.COM.deinit()
                self.pushButton_uart.setText('open')
                self.groupBox_txmode.setEnabled(False)
                self.groupBox_rxmode.setEnabled(False)
                self.groupBox_reg.setEnabled(False)
                self.groupBox_signaltest.setEnabled(False)

    def uart_comport_scan(self):
        uart_comport_list = []
        rm = pyvisa.ResourceManager()
        res_list = rm.list_resources()
        self.test_logdebug(res_list)
        for res_name in res_list:
            if res_name.find('ASRL') != -1:
                uart_comport = res_name.split('::')[0].split('RL')[1]
                self.test_log(' uart comport {} invailable'.format(uart_comport))
                self.comboBox_uartcomport.addItem(uart_comport)
    def uart_setting(self):
        self.test_logdebug('uartcomport currenttext is {}'.format(self.comboBox_uartcomport.currentText()))
        uartcomport = str(self.comboBox_uartcomport.currentText())
        uartbaudrate = str(self.comboBox_uartbd.currentText())
        self.COM = com.COM(eval(uartcomport), bdw=eval(uartbaudrate))
        self.test_log('open uart comport {} success,baudrate is {}'.format(uartcomport,uartbaudrate))



class func_ui(Ui_MainWindow):
    driver_thread = []  # type: Thread
    data = []  # type: Popen
    driver_show = []

    def __init__(self, MainWindow):

        ##mianwindown init
        self.setupUi(MainWindow)


if __name__=='__main__':

    app = QtGui.QApplication(sys.argv)
    main = QtGui.QMainWindow()
    # win_main = Ui_MainWindow()
    # win_main.setupUi(main)
    # win_emit = EmittingStr(main)
    # ui = func_ui(main)
    win = MyWindow()
    # win.showMaximized()

    win.show()
    # win_main.test_mode.currentIndexChanged.connect(win_main.test_mode_change)
    # win_main.uart_com_num.activated.connect(win_main.uart_com_change)
    # win_main.uart_com_num.activated.connect(win_emit.uart_com_change)
    # main.show()
    sys.exit(app.exec_())