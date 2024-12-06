#  -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bt__rf_test_tool_v1.2.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
reload(sys)
sys.setdefaultencoding('ISO-8859-1')
import random


from subprocess import Popen
from threading import Thread
import time
import subprocess
import threading
from PyQt4.QtCore import *
from bt_factory_test_tool_mainwindown import Ui_MainWindow
# from rftest.testcase.performance.bt_test_cmw import *
# from hal.common import *
# from baselib.instrument import *
from baselib.instrument import cmw_bt
from baselib.test_channel import com
from baselib.loglib.log_lib import *
import pyvisa
import visa

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

        self.setupfile = 'setup.txt'
        self.actionSave_as_setup.triggered.connect(self.save_as_setup)
        self.actionSave_setup.triggered.connect(self.save_setup)
        self.actionOpen_setup.triggered.connect(self.open_setup)

        self.emitting = EmittingStr(self)
        self.emitting.textWritten.connect(self.update_text)

        self.linkcmw_flag = False
        self.dut_mode_flag = False

        self.pushButton_linkcmw.clicked.connect(self.linkcmw)
        if self.groupBox_uartset.isChecked() == True:
            self.uart_comport_scan()
        self.pushButton_uart.clicked.connect(self.msg_uart)
        self.pushButton_inquiry.clicked.connect(self.inquiry)
        self.line_edit_event()

        self.testcount_total = 0
        self.testcount_pass = 0
        self.testcount_fail = 0

        self.pushButton_run.clicked.connect(self.test_item_select)
        self.pushButton_browse.clicked.connect(self.log_dic)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.itemDoubleClicked.connect(self.record_get)


    def log_dic(self):
        file_path = QFileDialog.getExistingDirectory(self,'file path','.\\report')
        self.lineEdit_browse.setText(file_path)
        self.filepath = str(self.lineEdit_browse.text())
        self.test_logdebug('{}'.format(self.filepath))

    def get_filename(self, folder, file_name, sub_folder=''):
        '''
        :folder: file store folder
        :file_name:  file name
        :sub_folder: if not need, it may be default ""
        '''

        if os.path.exists(folder) == False:
            os.mkdir(folder)

        filetime = time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()));
        # mac = self.read_mac()
        mac = ''

        gen_folder = '/%s'%(filetime[0:8])
        data_path2 = folder +'%s/'%(gen_folder)
        self.get_filename_data_path2 = data_path2
        if os.path.exists(data_path2) == False:
            os.mkdir(data_path2)

        fname = '%s'%(file_name)
        outfile_name = data_path2 + fname

        if sub_folder != '':
            gen_folder = '%s_%s'%(sub_folder,filetime[0:8])
            sub_path = data_path2+'%s/'%(gen_folder)
            if os.path.exists(sub_path) == False:
                os.mkdir(sub_path)

            outfile_name = sub_path + file_name

        return outfile_name

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
        QMessageBox.about(self,'info','debug')

    def line_edit_event(self):
        self.line_edit_range()
        # self.lineEdit_txlevel.editingFinished.connect(self.line_edit_range)

    def line_edit_range(self):
        self.lineEdit_txlevel.setValidator(QRegExpValidator(QRegExp("^(-([1-9][0-9]?|[1][0-1][0-9]?|120)?|0)$")))
        self.lineEdit_br_singlesens_txlevel.setValidator(
            QRegExpValidator(QRegExp("^(-([1-9][0-9]?|[1][0-1][0-9]?|120)?|0)$")))
        self.lineEdit_br_multsens_txlevel.setValidator(
            QRegExpValidator(QRegExp("^(-([1-9][0-9]?|[1][0-1][0-9]?|120)?|0)$")))
        self.lineEdit_br_maxinput_txpowerlevel.setValidator(
            QRegExpValidator(QRegExp("^(-([1-9][0-9]?|[1][0-1][0-9]?|120)?|0)$")))
        self.lineEdit_edr2sens_txlevel.setValidator(
            QRegExpValidator(QRegExp("^(-([1-9][0-9]?|[1][0-1][0-9]?|120)?|0)$")))
        self.lineEdit_edr3sens_txlevel.setValidator(
            QRegExpValidator(QRegExp("^(-([1-9][0-9]?|[1][0-1][0-9]?|120)?|0)$")))
        self.lineEdit_edr_maxinput_txpowerlevel.setValidator(
            QRegExpValidator(QRegExp("^(-([1-9][0-9]?|[1][0-1][0-9]?|120)?|0)$")))

        self.lineEdit_lctx.setValidator(QIntValidator(0,78))
        self.lineEdit_lcrx.setValidator(QIntValidator(0,78))
        self.lineEdit_mctx.setValidator(QIntValidator(0,78))
        self.lineEdit_mcrx.setValidator(QIntValidator(0,78))
        self.lineEdit_hctx.setValidator(QIntValidator(0,78))
        self.lineEdit_hcrx.setValidator(QIntValidator(0,78))

        self.lineEdit_lctx_r.setValidator(QIntValidator(0,78))
        self.lineEdit_lcrx_r.setValidator(QIntValidator(0,78))
        self.lineEdit_mctx_r.setValidator(QIntValidator(0,78))
        self.lineEdit_mcrx_r.setValidator(QIntValidator(0,78))
        self.lineEdit_hctx_r.setValidator(QIntValidator(0,78))
        self.lineEdit_hcrx_r.setValidator(QIntValidator(0,78))

        self.lineEdit_outputpower_numberofpacket.setValidator(QIntValidator(0, 100))
        self.lineEdit_powercontrol_numberofpacket.setValidator(QIntValidator(0, 100))
        self.lineEdit_icft_numberofpacket.setValidator(QIntValidator(0, 100))
        self.lineEdit_carrierdrift_numberofpacket.setValidator(QIntValidator(0, 100))
        self.lineEdit_mod_numberofpacket.setValidator(QIntValidator(0, 100))
        self.lineEdit_edrrelpower_numberofpacket.setValidator(QIntValidator(0, 100))
        self.lineEdit_edrfreq_numberofpacket.setValidator(QIntValidator(0, 100))
        self.lineEdit_edrdriff_numberofpacket.setValidator(QIntValidator(0, 100))

        self.lineEdit_singlesens_numberofpackets.setValidator(QIntValidator(1, 10000))
        self.lineEdit_multsens_numberofbit_2.setValidator(QIntValidator(1, 10000))
        self.lineEdit_brmaxinput_numberofbit.setValidator(QIntValidator(1, 10000))
        self.lineEdit_edresens_numberofbit.setValidator(QIntValidator(1, 10000))
        self.lineEdit_edrmaxinput_numberofbit.setValidator(QIntValidator(1, 10000))





    def link_instru(self,device_name='CMW'):
        device_list = []
        pyvisa.ResourceManager().close()
        rm = pyvisa.ResourceManager()
        res_list = rm.list_resources()
        self.test_logdebug(res_list)
        for res_name in res_list:
            if res_name.find("GPIB") != -1 or res_name.find("TCPIP0") != -1 or res_name.find("USB") != -1:
                self.test_logdebug(res_name)
                # self.device = rm.open_resource(res_name)
                # dev_name = self.device.ask("*IDN?")
                # logdebug(dev_name)
                # if dev_name.find(device_name) != -1:
                #     break
                try:
                    self.device = rm.open_resource(res_name)
                    dev_name = self.device.ask("*IDN?")
                    self.test_log(dev_name)
                    if dev_name.find(device_name) != -1:
                        device_list.append(self.device)
                        break
                except:
                    self.test_logerror('{} disconnect to instrument'.format(res_name))
                    return 'err'

    def linkcmw(self):
        res = self.link_instru(device_name='CMW')
        if res == 'err':
            QMessageBox.about(self, "error", 'Failed to connect instrument')
        else:
            res = self.device.ask('*IDN?')
            if res.find('CMW') != -1:
                QMessageBox.about(self, "pass", 'successed to connect instrument')
                dev_name = self.device.resource_name
                self.test_log('link instrument is {}'.format(dev_name))
                if dev_name.find('TCP') != -1:
                    self.comboBox_interfacetype.setEditText('LNA')
                    self.label_interfaceaddr.setText('IP ADDR/host name')
                    self.comboBox_interfaceaddr.setEditText('{}'.format(dev_name.split('::')[1]))
                elif dev_name.find('GPIB') != -1:
                    self.comboBox_interfacetype.setEditText('GPIB')
                    self.label_interfaceaddr.setText('GPIB ADDR')
                    self.comboBox_interfaceaddr.setEditText('{}'.format(dev_name.split('::')[1]))
                elif dev_name.find('USB') != -1:
                    self.comboBox_interfacetype.setEditText('USB')
                    self.label_interfaceaddr.setText('USB ADDR')
                    self.comboBox_interfaceaddr.setEditText('{}'.format(dev_name.split('::')[3]))
                # self.cb = cmw_bt.cmw_bt('CMW')
                self.csp = cmw_bt.combined_signal_path()
                self.linkcmw_flag = True
                self.test_log('linkcmw is {}'.format(self.linkcmw_flag))
            else:
                QMessageBox.critical(self, "error", 'Failed to connect instrument')

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
                else:
                    QMessageBox.critical(self, "error", 'The port is occupied')

            else:
                self.COM.deinit()
                self.pushButton_uart.setText('open')

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

    def inquiry(self):
        self.comboBox_bdaddr.clear()
        if self.linkcmw_flag == False:
            QMessageBox.critical(self, "error", 'Can not inquiry dut,Please connect the instrument first ')
        # elif self.dut_mode_flag:
        #     QMessageBox.critical(self, "error", 'Can not inquiry dut,Please check dut in test mode ')
        else:

            rate = 'BR'
            self.config_para_init()
            self.csp.reset()  # 复位cmw设置
            self.csp.clean()
            self.csp.signaling_switch(1)  # 1：仪器的蓝牙信令模式打开，0：关闭
            self.csp.rf_port(mode='signaling', rfport=self.rfport, atten=self.atten)  # 设置信令模式下 rfport和线损
            self.csp.sig_opmode(mode='RFT')
            self.csp.sig_std(std='CLAS')
            self.csp.hopping_en(en=1)
            self.csp.sig_btype(btype=rate)
            self.csp.config_sig_testmode(testmode='LOOP')
            self.csp.RF_Frequency_Settings_rx(mode='LOOP', ch_tx=0)
            self.csp.RF_Power_settings(rx_level=eval(str(self.lineEdit_txlevel.text())), tx_power=10, margin=8)
            self.csp.RF_Power_settings_autoranging()
            self.csp.config_connect_br_packet_pattern(pattern='PRBS9')  #设置BR包 payload 数据类型
            self.csp.config_connect_br_packet_ptype(ptype='DH1')    #设置BR包类型
            self.csp.config_paging_classic_NOResponses(1)   #设置stop inquire的条件，当inquire到的BD数量为设定值时则stop inquire
            self.csp.bt_connect_action(action='INQuire')    #开始inquire命令
            while 1:
                if self.csp.get_bt_connect_state() == 'SBY':
                    break
            target = self.csp.get_paging_classic_target()  # 返回inquire到的BD 列表
            self.test_logdebug('{}'.format(target))
            self.test_logdebug('{}'.format(target[1]))
            target_list = target.split(',')
            bd_list = []
            bd_num = eval(target_list[0])
            if bd_num != 0:
                for i in range(bd_num):
                    bd_list.append(target_list[i*2+4].replace('"',''))

            self.comboBox_bdaddr.addItems(bd_list)


    def config_para_init(self):
        self.filepath = str(self.lineEdit_browse.text())
        self.rfport = eval(str(self.comboBox_rfport.currentText()))
        # self.rxlevel = eval(str(self.lineEdit_txlevel.text()))
        if self.radioButton_hoppingoff.isChecked() == True:
            self.hopping_en = 0
        else:
            self.hopping_en = 1
        if self.radioButton_loopback.isChecked() == True:
            self.test_mode_in_tx = 'LOOP'
        else:
            self.test_mode_in_tx = 'TXTest'
        self.test_log('rfport is {}'.format(self.rfport))
        if self.checkBox_cableloss.isChecked() == True:
            try:
                self.atten = eval(str(self.lineEdit_cableloss.text()))

            except:
                self.test_logerror('Incorrect writing format')
                QMessageBox.critical(self,'error','Incorrect writing format,only 0--9 Arabic numerals')
        else:
            self.atten = 0
        self.test_log('cable loss is {}'.format(self.atten))
        self.test_lctx = eval(str(self.lineEdit_lctx.text()))
        self.test_mctx = eval(str(self.lineEdit_mctx.text()))
        self.test_hctx = eval(str(self.lineEdit_hctx.text()))
        self.test_lcrx = eval(str(self.lineEdit_lcrx.text()))
        self.test_mcrx = eval(str(self.lineEdit_mcrx.text()))
        self.test_hcrx = eval(str(self.lineEdit_hcrx.text()))

        self.test_lctx_r = eval(str(self.lineEdit_lctx_r.text()))
        self.test_mctx_r = eval(str(self.lineEdit_mctx_r.text()))
        self.test_hctx_r = eval(str(self.lineEdit_hctx_r.text()))
        self.test_lcrx_r = eval(str(self.lineEdit_lcrx_r.text()))
        self.test_mcrx_r = eval(str(self.lineEdit_mcrx_r.text()))
        self.test_hcrx_r = eval(str(self.lineEdit_hcrx_r.text()))

        self.test_chan_tx_list = [self.test_lctx,self.test_mctx,self.test_hctx]
        self.test_chan_tx_dic = {
            self.test_lctx :    self.test_lcrx,
            self.test_mctx :    self.test_mcrx,
            self.test_hctx :    self.test_hcrx
        }
        self.test_chan_rx_list = [self.test_lcrx_r,self.test_mcrx_r,self.test_hcrx_r]
        self.test_chan_rx_dic = {
            self.test_lcrx_r :    self.test_lctx_r,
            self.test_mcrx_r :    self.test_mctx_r,
            self.test_hcrx_r :    self.test_hctx_r
        }
        # rigtyperadiobuttons = self.groupbox7.findChildren(QtGui.QRadioButton)
        self.test001_ptype = [rb.text() for rb in self.groupBox_7.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        logdebug('test001_ptype is {}'.format(self.test001_ptype))
        self.test002_ptype = [rb.text() for rb in self.groupBox_10.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test003_ptype = [rb.text() for rb in self.groupBox_15.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test004_ptype = [rb.text() for rb in self.groupBox_14.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test005_ptype = [rb.text() for rb in self.groupBox_11.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test009_ptype_2 = [rb.text() for rb in self.groupBox_33.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test009_ptype_3 = [rb.text() for rb in self.groupBox_34.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test010_ptype_2 = [rb.text() for rb in self.groupBox_37.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test010_ptype_3 = [rb.text() for rb in self.groupBox_38.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test011_ptype_2 = [rb.text() for rb in self.groupBox_41.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]
        self.test011_ptype_3 = [rb.text() for rb in self.groupBox_42.findChildren(QtGui.QRadioButton) if rb.isChecked()][0]

    def config_classic_ber(self, rate='BR', tx_power=10):
        '''
        配置经典蓝牙连接CMW流程：
        复位仪器，打开信令模式，配置好RF参数和蓝牙包的参数，inquire EUT的BD，paging EUT并连接EUT。
        '''
        if rate not in ('BR','EDR'):
            raise StandardError('rate command wrong')
        self.config_para_init()
        self.csp.reset()    #复位cmw设置
        self.csp.clean()
        self.csp.signaling_switch(1)    #1：仪器的蓝牙信令模式打开，0：关闭
        self.csp.rf_port(mode='signaling', rfport=self.rfport, atten=self.atten)    #设置信令模式下 rfport和线损
        self.csp.sig_opmode(mode='RFT')
        self.csp.sig_std(std='CLAS')
        self.csp.sig_btype(btype=rate)
        self.csp.config_sig_testmode(testmode=self.test_mode_in_tx)
        self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_lctx,ch_rx=self.test_lcrx)
        self.csp.RF_Power_settings(rx_level=eval(str(self.lineEdit_txlevel.text())), tx_power=tx_power, margin=8)
        self.csp.RF_Power_settings_autoranging()
        # self.csp.config_rx_level(rxpwr=-50)
        if rate == 'BR':
            self.csp.config_connect_br_packet_pattern(pattern='PRBS9')  #设置BR包 payload 数据类型
            self.csp.config_connect_br_packet_ptype(ptype='DH1')    #设置BR包类型
            # self.csp.config_connect_br_packet_len(len=packet_len)   #设置BR包长
        else:
            self.csp.config_connect_edr_packet_pattern(pattern='PRBS9') #设置EDR包 payload 数据类型
            self.csp.config_connect_edr_packet_ptype(ptype='E21P')  #设置EDR的包类型，E21P：2-DH1，E31P：3-DH1
            # self.csp.config_connect_edr_packet_len(len=packet_len)  #设置EDR包长
        self.csp.config_paging_classic_NOResponses(1)   #设置stop inquire的条件，当inquire到的BD数量为设定值时则stop inquire
        self.csp.bt_connect_action(action='INQuire')    #开始inquire命令
        while 1:
            if self.csp.get_bt_connect_state() == 'SBY':
                break
            time.sleep(0.1)

        # target = self.csp.get_paging_classic_target()   #返回inquire到的BD 列表
        # self.csp.config_paging_classic_target(target=1) #设置inquire到的第一个BD用来paging
        target = self.csp.get_paging_classic_target()  # 返回inquire到的BD 列表
        self.test_logdebug('{}'.format(target))
        target_list = target.split(',')
        bd_list = []
        bd_num = eval(target_list[0])
        if bd_num != 0:
            for i in range(bd_num):
                bd_list.append(target_list[i * 2 + 4].replace('"', ''))
            self.csp.bt_connect_action(action='TMConnect')  #
            while 1:
                if self.csp.get_bt_connect_state() == 'TCON':
                    break
                time.sleep(0.1)
            self.test_log('bluetooth connect success')
        else:
            self.test_logerror('The device could not be found')
            return False

        # self.csp.bt_connect_action(action='STMode')
        # self.csp.config_rx_level(rxpwr=-51)
        # self.csp.bt_connect_action(action='TMConnect')
        # while 1:
        #     if self.csp.get_bt_connect_state() == 'TCON':
        #         break
        #     time.sleep(0.5)
    def set_loader(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_progress_bar)
        self.timer.start(10)

    def load_progress_bar(self):
        if self.pv >= self.item_num:
            self.timer.stop()
        else:
            self.progressBar.setValue(self.pv)

    def test_item_select(self):
        self.checkbox_list = [self.checkBox_test001.isChecked(),self.checkBox_test002.isChecked(),
                         self.checkBox_test003.isChecked(),self.checkBox_test004.isChecked(),
                         self.checkBox_test005.isChecked(), self.checkBox_test006.isChecked(),
                         self.checkBox_test007.isChecked(), self.checkBox_test008.isChecked(),
                         self.checkBox_test009.isChecked(), self.checkBox_test010.isChecked(),
                         self.checkBox_test011.isChecked(), self.checkBox_test012.isChecked(),
                         self.checkBox_test013.isChecked(), self.checkBox_test014.isChecked()
                         ]
        if self.checkbox_list.count(True)==0:
            QMessageBox.critical(self, "error", 'please select test item')
            return
        self.testcount_total += 1
        self.lineEdit_testcount_total.setText('{}'.format(self.testcount_total))
        self.label_runresult.setText('')
        self.label_fiallog.setText('')
        self.pushButton_run.setEnabled(False)
        self.textBrowser.clear()
        # self.config_para_init()
        res = self.config_classic_ber(rate='BR',tx_power=10)
        if res == False:
            self.label_runresult.setStyleSheet("color:red")
            self.label_runresult.setText('fail')
            self.label_fiallog.setStyleSheet("color:red")
            self.label_fiallog.setText('Unable to connect the CMW')
            self.testcount_fail += 1
            self.lineEdit_testcount_fail.setText('{}'.format(self.testcount_fail))
            return

        res_eutinfo = self.csp.retrieve_eut_information()
        self.test_logdebug('{}\n{}\n'.format(res_eutinfo[0],res_eutinfo[1]))
        res_eut_addr = res_eutinfo[1].replace('\n','').split('H')[1]
        wstr = ''
        for i in range(12-len(res_eut_addr)):
            wstr = wstr + '0'
        self.eut_addr = wstr + res_eut_addr
        logdebug(self.eut_addr)

        fname = self.get_filename(self.filepath,self.eut_addr)
        self.fw1=csvreport(fname,'{}\neut bdaddr is {}'.format(res_eutinfo[0],self.eut_addr))
        self.pv = 0

        self.item_num = 0

        for i in self.checkbox_list:
            if i == True:
                self.item_num = self.item_num + 1

        self.progressBar.setMaximum(self.item_num)
        self.progressBar.setValue(self.pv)
        # self.set_loader()
        self.test_logdebug('item value:  {}'.format(self.item_num))

        res = 'fail'
        if self.groupBox_brtestitem.isChecked() == True:
            if self.checkBox_test001.isChecked()==True :
                res = self.test001_BR_Output_Power()
                if res == 'fail':
                    self.test_fail(logstr='test001_BR_Output_Power', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test002.isChecked()==True:
                res = self.test002_BR_Power_Control()
                if res == 'fail':
                    self.test_fail(logstr='test002_BR_Power_Control', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test003.isChecked() == True:
                res = self.test003_BR_Modulation_Characteristics()
                if res == 'fail':
                    self.test_fail(logstr='test003_BR_Modulation_Characteristics', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test004.isChecked()==True:
                res = self.test004_BR_Initial_Carrier_Frequency_Tolerance()
                if res == 'fail':
                    self.test_fail(logstr='test004_BR_Initial_Carrier_Frequency_Tolerance', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test005.isChecked() == True:
                res = self.test005_BR_Carrier_Frequency_Drift()
                if res == 'fail':
                    self.test_fail(logstr='test005_BR_Carrier_Frequency_Drift', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test006.isChecked() == True:
                res = self.test006_BR_Sensitivity_single_slot_packets()
                if res == 'fail':
                    self.test_fail(logstr='test006_BR_Sensitivity_single_slot_packets', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test007.isChecked() == True:
                res = self.test007_BR_Sensitivity_multi_slot_packets()
                if res == 'fail':
                    self.test_fail(logstr='test007_BR_Sensitivity_multi_slot_packets', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test008.isChecked() == True:
                res = self.test008_BR_Maximum_Input_Level()
                if res == 'fail':
                    self.test_fail(logstr='test008_BR_Maximum_Input_Level', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
        if self.groupBox_edrtestitem.isChecked()==True:
            if self.checkBox_test009.isChecked() == True:
                res = self.test009_EDR_Relative_Transmit_Power()
                if res == 'fail':
                    self.test_fail(logstr='test009_EDR_Relative_Transmit_Power', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test010.isChecked() == True:
                res = self.test010_EDR_Modulation_Accuracy()
                if res == 'fail':
                    self.test_fail(logstr='test010_EDR_Modulation_Accuracy', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test011.isChecked() == True:
                res = self.test011_EDR_Differential_Phase_Encoding()
                if res == 'fail':
                    self.test_fail(logstr='test011_EDR_Differential_Phase_Encoding', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test012.isChecked() == True:
                res = self.test012_EDR_Sensitivity()
                if res == 'fail':
                    self.test_fail(logstr='test012_EDR_Sensitivity', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test013.isChecked() == True:
                res = self.test013_EDR_BER_Floor_Performance()
                if res == 'fail':
                    self.test_fail(logstr='test013_EDR_BER_Floor_Performance', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
            if self.checkBox_test014.isChecked() == True:
                res = self.test014_EDR_Maximum_Input_Level()
                if res == 'fail':
                    self.test_fail(logstr='test014_EDR_Maximum_Input_Level', resl=res)
                    return
                self.pv = self.pv + 1
                self.progressBar.setValue(self.pv)
        self.pushButton_run.setEnabled(True)
        self.label_runresult.setStyleSheet("color:green")
        self.label_runresult.setText('pass')
        self.testcount_pass += 1
        self.lineEdit_testcount_pass.setText('{}'.format(self.testcount_pass))
        self.report_rename(res)

    def test_fail(self, logstr='',resl=''):
        self.label_runresult.setStyleSheet("color:red")
        self.label_runresult.setText(resl)
        self.label_fiallog.setStyleSheet("color:red")
        self.label_fiallog.setText('{} fail'.format(logstr))
        self.testcount_fail += 1
        self.lineEdit_testcount_fail.setText('{}'.format(self.testcount_fail))
        self.pushButton_run.setEnabled(True)
        self.report_rename(resl)

    def report_rename(self, old_name=''):
        fn = list(self.fw1.filename)
        res = '_' + old_name
        fn.insert(len(fn)-4,res)
        fn1 = ''.join(fn)
        os.renames(self.fw1.filename,fn1)
        self.fw1.filename = fn1
        self.record_display(res=old_name)

    def record_display(self,res=''):
        wstr_bd = self.eut_addr
        wstr_time = self.fw1.logtime
        wstr_pf = res
        row = self.tableWidget.rowCount()
        items = [row,wstr_bd, wstr_time, wstr_pf]
        self.tableWidget.insertRow(row)

        self.mycheckbox = QCheckBox()
        self.mycheckbox.setChecked(True)

        newqwidget = QWidget()
        newlayout = QHBoxLayout()
        newlayout.setContentsMargins(0,0,0,0)
        newlayout.setAlignment(Qt.AlignCenter)
        newlayout.addWidget(self.mycheckbox)
        newqwidget.setLayout(newlayout)

        for j in range(len(items)):
            newitem = QTableWidgetItem(str(items[j]))
            newitem.setTextAlignment(Qt.AlignCenter)

            if items[j] == 'pass':
                self.tableWidget.setCellWidget(row, j, newqwidget)

            elif items[j] == 'fail':
                self.tableWidget.setCellWidget(row, j+1, newqwidget)

            else:
                self.tableWidget.setItem(row, j, newitem)

    def record_get(self,Item=None):
        row = Item.row()
        col = Item.column()
        logdebug('row = {}'.format(row))
        logdebug('col = {}'.format(col))
        del_row = int(self.tableWidget.rowCount())
        self.tableWidget.insertRow(del_row)
        bdad = self.tableWidget.item(row,1).text()
        logtime  = self.tableWidget.item(row,2).text()
        self.tableWidget.removeRow(del_row)
        record_filepath1 = self.get_filename_data_path2 + '/{}_{}_fail.csv'.format(bdad,logtime)
        record_filepath2 = self.get_filename_data_path2 + '/{}_{}_pass.csv'.format(bdad, logtime)
        logdebug(record_filepath1)
        if os.path.exists(record_filepath1):
            os.startfile(record_filepath1)
        if os.path.exists(record_filepath2):
            os.startfile(record_filepath2)

    def ptype_get(self,ptype_list=[1,2]):
        for i  in ptype_list:
            if i.isChecked() == True:
                res = str(self.i.text())
                self.test_log('ptype is {}'.format(res))
                return  res

    def test001_BR_Output_Power(self):
        self.test_log('\n****   test001_BR_Output_Power     ****\n')
        res_flag_list = []
        test_limit_txp_upper = eval(str(self.lineEdit_br_testlimit_maxpower.text()))
        test_limit_txp_lower = eval(str(self.lineEdit_br_testlimit_minpower.text()))
        test_limit_txp_peak = eval(str(self.lineEdit_br_testlimit_peakpower.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        # test001_ptype = 'DH1'
        test001_ptype_list = [self.radioButton_br_outputpower_dh1,self.radioButton_br_outputpower_dh3,self.radioButton_br_outputpower_dh5]
        # test001_ptype = self.ptype_get(test001_ptype_list)
        self.csp.config_connect_br_packet_ptype(ptype=self.test001_ptype)  # 设置BR包类型
        self.csp.config_connect_br_packet_pattern(pattern='PRBS9')  # 设置BR包 payload 数据类型
        test_count = eval(str(self.lineEdit_outputpower_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,nominal_pow(dBm),peak_pow(dBm)\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=chan_tx, ch_rx=self.test_chan_tx_dic[chan_tx])
            res1 = self.csp.get_power_measure_res()
            nominal_pow = eval(res1[2])
            peak_pow = eval(res1[3])

            if nominal_pow < test_limit_txp_upper and nominal_pow > test_limit_txp_lower and peak_pow < test_limit_txp_peak:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.fw1.write_data([chan_tx, nominal_pow, peak_pow, res_flag])
            self.test_log('channel {}   nominal_pow {}  peak_pow {}  {}\n'.format(chan_tx,nominal_pow,peak_pow,res_flag))
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test002_BR_Power_Control(self):
        self.test_log('\n****   test002_BR_Power_Control     ****\n')
        res_flag_list = []
        test_limit_pwrstep_max = eval(str(self.lineEdit_br_testlimit_powercontrol_maxstep.text()))
        test_limit_pwrstep_min = eval(str(self.lineEdit_br_testlimit_powercontrol_minstep.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        self.csp.config_connect_br_packet_ptype(ptype=self.test002_ptype)  # 设置BR包类型
        self.csp.config_connect_br_packet_pattern(pattern='PRBS9')  # 设置BR包 payload 数据类型
        test_count = eval(str(self.lineEdit_powercontrol_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,index,txpwr_step(dB)\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=chan_tx,
                                              ch_rx=self.test_chan_tx_dic[chan_tx])

            self.csp.config_power_control(para='MAX')
            res1 = self.csp.get_power_measure_res()
            nominal_pow_max = eval(res1[2])
            peak_pow = eval(res1[3])
            nominal_pow = nominal_pow_max
            for i in range(1,8):
                self.csp.config_power_control(para='DOWN')
                # self.csp.trigger_settings(source='power', threshold=-20-i, tout=1)
                res1 = self.csp.get_power_measure_res()
                nominal_pow_d = eval(res1[2])
                power_step  = nominal_pow - nominal_pow_d
                nominal_pow = nominal_pow_d
                if power_step < test_limit_pwrstep_max and power_step > test_limit_pwrstep_min :
                    res_flag = 'pass'
                else:
                    res_flag = 'fail'
                self.test_log('channel  {}  index   {}  nominal power   {}dBm  step   {}dB      {}\n'.format(chan_tx, i,
                                                                                                             nominal_pow,
                                                                                                             power_step,
                                                                                                             res_flag))

                self.fw1.write_data([chan_tx,i,power_step,res_flag])
                res_flag_list.append(res_flag)

            for i in range(1,8):
                self.csp.config_power_control(para='UP')
                # self.csp.trigger_settings(source='power', threshold=-20-i, tout=1)
                res1 = self.csp.get_power_measure_res()
                nominal_pow_u = eval(res1[2])
                power_step  = nominal_pow_u - nominal_pow
                nominal_pow = nominal_pow_u
                if power_step < test_limit_pwrstep_max and power_step > test_limit_pwrstep_min :
                    res_flag = 'pass'
                else:
                    res_flag = 'fail'
                self.test_log('channel  {}  index   {}  nominal power   {}dBm  step   {}dB      {}\n'.format(chan_tx,i,nominal_pow,power_step,res_flag))
                self.fw1.write_data([chan_tx, 8-i, power_step,res_flag])
            self.csp.config_power_control(para='MAX')
            res = self.csp.config_power_control_state()
            self.test_logdebug(res)

        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'


    def test003_BR_Modulation_Characteristics(self):
        self.test_log('\n****   test003_BR_Modulation_Characteristics     ****\n')
        res_flag_list = []
        test_limit_delta_f1_min = eval(str(self.lineEdit_br_testlimit_f1avgmin.text()))
        test_limit_delta_f1_max  = eval(str(self.lineEdit_br_testlimit_f1avgmax.text()))
        test_limit_delta_f2_99_min = eval(str(self.lineEdit_br_testlimit_f2maxmin.text()))
        test_limit_mod_ratio = eval(str(self.lineEdit_hctx_r_6.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        self.csp.config_connect_br_packet_ptype(ptype=self.test003_ptype)  # 设置BR包类型
        test_count = eval(str(self.lineEdit_mod_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,delta_f1_avg(KHz),delta_f2_avg(KHz),delta_f2_99(KHz),mod_ratio\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=chan_tx,
                                              ch_rx=self.test_chan_tx_dic[chan_tx])

            self.csp.config_connect_br_packet_pattern(pattern='P44')  # 设置BR包 payload 数据类型
            res = self.csp.get_modulation_measure_res()

            delta_f1_99 = eval(res[2]) / 1000.00
            freq_accuracy = eval(res[3]) / 1000.00
            freq_drift = eval(res[4]) / 1000.00
            drift_rate = eval(res[5])
            delta_f1_avg = eval(res[6]) / 1000.00
            delta_f1_min = eval(res[7]) / 1000.00
            delta_f1_max = eval(res[8]) / 1000.00


            self.csp.config_connect_br_packet_pattern(pattern='P11')  # 设置BR包 payload 数据类型
            res = self.csp.get_modulation_measure_res()

            delta_f2_99 = eval(res[2]) / 1000.00
            freq_accuracy = eval(res[3]) / 1000.00
            freq_drift = eval(res[4]) / 1000.00
            drift_rate = eval(res[5]) / 1000.00
            delta_f2_avg = eval(res[9]) / 1000.00
            delta_f2_min = eval(res[10]) / 1000.00
            delta_f2_max = eval(res[11]) / 1000.00
            mod_ratio = delta_f2_avg / delta_f1_avg
            if delta_f1_avg < test_limit_delta_f1_max and delta_f1_avg > test_limit_delta_f1_min and delta_f2_99 > test_limit_delta_f2_99_min and mod_ratio > test_limit_mod_ratio:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log('channel  {}  delta_f1_avg     {}KHz  delta_f2_avg     {}KHz   delta_f2_99     {}KHz   mod_ratio   {}     {}\n'.format(chan_tx,delta_f1_avg,delta_f2_avg,delta_f2_99,mod_ratio,res_flag))

            self.fw1.write_data([chan_tx,delta_f1_avg,delta_f2_avg,delta_f2_99,mod_ratio,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test004_BR_Initial_Carrier_Frequency_Tolerance(self):
        self.test_log('\n****   test004_BR_Initial_Carrier_Frequency_Tolerance     ****\n')
        res_flag_list = []
        test_limit_freq_accuracy = eval(str(self.lineEdit_br_testlimit_icftoffset.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        self.csp.config_connect_br_packet_ptype(ptype=self.test004_ptype)  # 设置BR包类型
        self.csp.config_connect_br_packet_pattern(pattern='P11')  # 设置BR包 payload 数据类型
        test_count = eval(str(self.lineEdit_icft_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,freq_accuracy(KHz)\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=chan_tx,
                                              ch_rx=self.test_chan_tx_dic[chan_tx])
            res = self.csp.get_modulation_measure_res()
            freq_accuracy = eval(res[3]) / 1000.00


            if abs(freq_accuracy) < test_limit_freq_accuracy :
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log('channel  {}  freq_accuracy    {}KHz      {}\n'.format(chan_tx, freq_accuracy, res_flag))
            self.fw1.write_data([chan_tx,freq_accuracy,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test005_BR_Carrier_Frequency_Drift(self):
        self.test_log('\n****   test005_BR_Carrier_Frequency_Drift     ****\n')
        res_flag_list = []
        test_limit_freq_drift1 = eval(str(self.lineEdit_br_testlimit_maxdh1drift.text()))
        test_limit_freq_drift3 = eval(str(self.lineEdit_br_testlimit_maxdh3drift.text()))
        test_limit_freq_drift5 = eval(str(self.lineEdit_br_testlimit_maxdh5drift.text()))
        test_limit_drift_rate1 = eval(str(self.lineEdit_br_testlimit_driftrate.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        self.csp.config_connect_br_packet_pattern(pattern='P11')  # 设置BR包 payload 数据类型
        test_count = eval(str(self.lineEdit_carrierdrift_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,freq_drift1(KHz),drift_rate1(KHz/us),freq_drift3(KHz),drift_rate3(KHz/us),freq_drift5(KHz),drift_rate5(KHz/us)\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=chan_tx,
                                              ch_rx=self.test_chan_tx_dic[chan_tx])
            self.csp.config_connect_br_packet_ptype(ptype='DH1')  # 设置BR包类型
            res = self.csp.get_modulation_measure_res()
            freq_drift1 = eval(res[4]) / 1000.00
            drift_rate1 = eval(res[5]) / 1000.00


            self.csp.config_connect_br_packet_ptype(ptype='DH3')  # 设置BR包类型
            res = self.csp.get_modulation_measure_res()
            freq_drift3 = eval(res[4]) / 1000.00
            drift_rate3 = eval(res[5]) / 1000.00


            self.csp.config_connect_br_packet_ptype(ptype='DH5')  # 设置BR包类型
            res = self.csp.get_modulation_measure_res()
            freq_drift5 = eval(res[4]) / 1000.00
            drift_rate5 = eval(res[5]) / 1000.00


            if abs(freq_drift1) < test_limit_freq_drift1 and  abs(freq_drift3) < test_limit_freq_drift3 and abs(freq_drift5) < test_limit_freq_drift5 and abs(drift_rate1) < test_limit_drift_rate1:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log('channel  {}  dh1 drift    {}KHz   dh3 drift   {}KHz   dh5 drift   {}KHz\ndh1 driftrate    {}KHz   dh3 driftrate   {}KHz   dh5 driftrate   {}KHz   {}\n'.format(chan_tx,freq_drift1,drift_rate1,freq_drift3,drift_rate3,freq_drift5,drift_rate5,res_flag))

            self.fw1.write_data([chan_tx,freq_drift1,drift_rate1,freq_drift3,drift_rate3,freq_drift5,drift_rate5,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test009_EDR_Relative_Transmit_Power(self):
        self.test_log('\n****   test009_EDR_Relative_Transmit_Power     ****\n')
        res_flag_list = []
        test_limit_dpsk_gfsk_diff_pwr_lower = eval(str(self.lineEdit_edr_testlimit_relpower_lower.text()))
        test_limit_dpsk_gfsk_diff_pwr_upper = eval(str(self.lineEdit_edr_testlimit_relpower_upper.text()))
        self.csp.mode_set(mode='EDR')
        self.csp.sig_btype(btype='EDR')
        self.csp.config_connect_edr_packet_pattern(pattern='PRBS9')  # 设置EDR包 payload 数据类型
        test_count = eval(str(self.lineEdit_edrrelpower_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,mod,nominal_pwr(dBm),gfsk_pwr(dBm),dpsk_pwr(dBm),dpsk_gfsk_diff_pwr(dB)\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=chan_tx,
                                              ch_rx=self.test_chan_tx_dic[chan_tx])
            self.csp.config_connect_edr_packet_ptype(ptype=self.dic_edr2_rate[self.test009_ptype_2])  # 设置EDR包类型
            res1 = self.csp.get_power_measure_res()
            logdebug('{}'.format(res1))
            res1 = [eval(i) for i in res1[0:]]
            nominal_pwr = res1[2]
            gfsk_pwr = res1[3]
            dpsk_pwr = res1[4]
            dpsk_gfsk_diff_pwr = res1[5]
            guard_period = res1[6]
            packet_timing = res1[7]
            peak_pwr = res1[8]

            if dpsk_gfsk_diff_pwr > test_limit_dpsk_gfsk_diff_pwr_lower and dpsk_gfsk_diff_pwr < test_limit_dpsk_gfsk_diff_pwr_upper:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel:{},  mod:{}, nominal_pwr(dBm):{},    gfsk_pwr(dBm):{},   dpsk_pwr(dBm):{},   dpsk_gfsk_diff_pwr(dB):{}     {}\n'.format(
                    chan_tx, 'EDR2', nominal_pwr, gfsk_pwr, dpsk_pwr, dpsk_gfsk_diff_pwr,res_flag))
            self.fw1.write_data([chan_tx,'EDR2',nominal_pwr,gfsk_pwr,dpsk_pwr,dpsk_gfsk_diff_pwr,res_flag])
            res_flag_list.append(res_flag)

            self.csp.config_connect_edr_packet_ptype(ptype=self.dic_edr3_rate[self.test009_ptype_3])  # 设置EDR包类型
            res1 = self.csp.get_power_measure_res()
            logdebug('{}'.format(res1))
            res1 = [eval(i) for i in res1[0:]]
            nominal_pwr = res1[2]
            gfsk_pwr = res1[3]
            dpsk_pwr = res1[4]
            dpsk_gfsk_diff_pwr = res1[5]
            guard_period = res1[6]
            packet_timing = res1[7]
            peak_pwr = res1[8]

            if dpsk_gfsk_diff_pwr > test_limit_dpsk_gfsk_diff_pwr_lower and dpsk_gfsk_diff_pwr < test_limit_dpsk_gfsk_diff_pwr_upper:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel:{},  mod:{}, nominal_pwr(dBm):{},    gfsk_pwr(dBm):{},   dpsk_pwr(dBm):{},   dpsk_gfsk_diff_pwr(dB):{}     {}\n'.format(
                    chan_tx, 'EDR3', nominal_pwr, gfsk_pwr, dpsk_pwr, dpsk_gfsk_diff_pwr,res_flag))
            self.fw1.write_data([chan_tx, 'EDR3',nominal_pwr, gfsk_pwr, dpsk_pwr, dpsk_gfsk_diff_pwr,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test010_EDR_Modulation_Accuracy(self):
        self.test_log('\n****   test010_EDR_Modulation_Accuracy     ****\n')
        res_flag_list = []
        test_limit_wi = eval(str(self.lineEdit_edr_testlimit_freqmod_wi.text()))
        test_limit_w0_wi = eval(str(self.lineEdit_edr_testlimit_freqmod_wiw0.text()))
        test_limit_w0_max = eval(str(self.lineEdit_edr_testlimit_freqmod_w0.text()))
        test_limit_edr2_DEVM_RMS = eval(str(self.lineEdit_edr_testlimit_freqmod_rmsdevmedr2.text()))
        test_limit_edr2_DEVM_peak = eval(str(self.lineEdit_edr_testlimit_freqmod_peakdevmedr2.text()))
        test_limit_edr2_DEVM_P99 = eval(str(self.lineEdit_edr_testlimit_freqmod_99devmedr2.text()))
        test_limit_edr3_DEVM_RMS = eval(str(self.lineEdit_edr_testlimit_freqmod_rmsdevmedr3.text()))
        test_limit_edr3_DEVM_peak = eval(str(self.lineEdit_edr_testlimit_freqmod_peakdevmedr3.text()))
        test_limit_edr3_DEVM_P99 = eval(str(self.lineEdit_edr_testlimit_freqmod_99devmedr3.text()))

        self.csp.mode_set(mode='EDR')
        self.csp.sig_btype(btype='EDR')
        self.csp.config_connect_edr_packet_pattern(pattern='PRBS9')  # 设置EDR包 payload 数据类型
        test_count = eval(str(self.lineEdit_edrfreq_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,mod,wi(Khz),w0_wi(Khz),w0_max(Khz),DEVM_RMS(%),DEVM_peak(%),DEVM_P99(%)\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=chan_tx,
                                              ch_rx=self.test_chan_tx_dic[chan_tx])
            self.csp.config_connect_edr_packet_ptype(ptype=self.dic_edr2_rate[self.test010_ptype_2])  # 设置EDR包类型
            for i in range(1):
                self.csp.config_power_control(para='DOWN')
            res = self.csp.get_modulation_measure_res()
            logdebug('{}'.format(res))
            res = [eval(i) for i in res[0:]]
            wi = res[2] / 1000
            w0_wi = res[3] / 1000
            w0_max = res[4] / 1000
            DEVM_RMS = res[5]*100.00
            DEVM_peak = res[6]*100.00
            DEVM_P99 = res[7]*100.00

            if abs(wi) < test_limit_wi and abs(w0_wi) < test_limit_w0_wi and abs(w0_max) < test_limit_w0_max and DEVM_RMS < test_limit_edr2_DEVM_RMS and DEVM_peak < test_limit_edr2_DEVM_peak and DEVM_P99 < test_limit_edr2_DEVM_P99:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel:{},  mod,wi(Khz):{}, w0_wi(Khz):{},  w0_max(Khz):{}, DEVM_RMS(%):{}, DEVM_peak(%):{},    DEVM_P99(%):{}    {}\n'.format(
                    chan_tx, 'EDR2', wi, w0_wi, w0_max, DEVM_RMS, DEVM_peak, DEVM_P99,res_flag))
            self.fw1.write_data([chan_tx,'EDR2',wi,w0_wi,w0_max,DEVM_RMS,DEVM_peak,DEVM_P99,res_flag])
            res_flag_list.append(res_flag)

            self.csp.config_connect_edr_packet_ptype(ptype=self.dic_edr3_rate[self.test010_ptype_3])  # 设置EDR包类型
            for i in range(1):
                self.csp.config_power_control(para='DOWN')
            res = self.csp.get_modulation_measure_res()
            logdebug('{}'.format(res))
            res = [eval(i) for i in res[0:]]
            wi = res[2] / 1000
            w0_wi = res[3] / 1000
            w0_max = res[4] / 1000
            DEVM_RMS = res[5]*100.00
            DEVM_peak = res[6]*100.00
            DEVM_P99 = res[7]*100.00

            if abs(wi) < test_limit_wi and abs(w0_wi) < test_limit_w0_wi and abs(w0_max) < test_limit_w0_max and DEVM_RMS < test_limit_edr3_DEVM_RMS and DEVM_peak < test_limit_edr3_DEVM_peak and DEVM_P99 < test_limit_edr3_DEVM_P99:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel:{},  mod,wi(Khz):{}, w0_wi(Khz):{},  w0_max(Khz):{}, DEVM_RMS(%):{}, DEVM_peak(%):{},    DEVM_P99(%):{}    {}\n'.format(
                    chan_tx, 'EDR3', wi, w0_wi, w0_max, DEVM_RMS, DEVM_peak, DEVM_P99,res_flag))
            res_flag_list.append(res_flag)
            self.fw1.write_data([chan_tx, 'EDR3', wi, w0_wi, w0_max, DEVM_RMS, DEVM_peak, DEVM_P99,res_flag])
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test011_EDR_Differential_Phase_Encoding(self):
        self.test_log('\n****   test011_EDR_Differential_Phase_Encoding     ****\n')
        res_flag_list = []
        test_limit_packet0error = eval(str(self.lineEdit_edr_testlimit_diffphase.text()))
        self.csp.mode_set(mode='EDR')
        self.csp.sig_btype(btype='EDR')
        self.csp.config_sig_testmode(testmode='TXTest')
        self.csp.config_connect_edr_packet_pattern(pattern='PRBS9')
        test_count = eval(str(self.lineEdit_edrdriff_numberofpacket.text()))
        self.csp.tx_measure_para(tout=5, repetition='SINGleshot', count=test_count)
        title = '\nchannel,mod,packet0error(%)\n'
        self.fw1.write_string(title)
        for chan_tx in self.test_chan_tx_list:
            self.csp.RF_Frequency_Settings_rx(mode='TXT', ch_tx=chan_tx,
                                              ch_rx=self.test_chan_tx_dic[chan_tx])
            self.csp.config_connect_edr_packet_ptype(ptype=self.dic_edr2_rate[self.test011_ptype_2])  # 设置EDR包类型
            res2 = self.csp.get_diff_phase_encoding_res()
            logdebug('{}'.format(res2))
            res2 = [eval(i) for i in res2[0:]]
            bit_error_rate = res2[2]
            packet0error = res2[3]
            if packet0error > test_limit_packet0error :
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel:{},  mod:{}, packet0error(%):{}  {}\n'.format(chan_tx, 'EDR2', packet0error, res_flag))
            self.fw1.write_data([chan_tx,'EDR2',packet0error,res_flag])
            res_flag_list.append(res_flag)

            self.csp.config_connect_edr_packet_ptype(ptype=self.dic_edr3_rate[self.test011_ptype_3])  # 设置EDR包类型
            res2 = self.csp.get_diff_phase_encoding_res()
            logdebug('{}'.format(res2))
            res2 = [eval(i) for i in res2[0:]]
            bit_error_rate = res2[2]
            packet0error = res2[3]

            if packet0error > test_limit_packet0error :
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel:{},  mod:{}, packet0error(%):{}  {}\n'.format(chan_tx, 'EDR3', packet0error, res_flag))
            self.fw1.write_data([chan_tx, 'EDR3', packet0error,res_flag])
            res_flag_list.append(res_flag)
        self.csp.config_sig_testmode(testmode=self.test_mode_in_tx)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test006_BR_Sensitivity_single_slot_packets(self):
        self.test_log('\n****   test006_BR_Sensitivity_single_slot_packets     ****\n')
        res_flag_list = []
        test_limit_ber = eval(str(self.lineEdit_br_testlimit_singlesens_ber.text()))
        test_limit_per = eval(str(self.lineEdit_br_testlimit_singlesens_per.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        self.csp.config_rxq_repetion(rep='SING')
        # self.lineEdit_txlevel.setText(str(self.lineEdit_br_singlesens_txlevel.text()))
        rx_level = eval(str(self.lineEdit_br_singlesens_txlevel.text()))
        self.csp.config_rx_level(rxpwr=rx_level)
        self.csp.config_rxq_br_packets(num=eval(str(self.lineEdit_singlesens_numberofpackets.text())))
        self.csp.config_connect_br_packet_pattern(pattern='PRBS9')
        self.csp.config_connect_br_packet_ptype(ptype='DH1')
        title = '\nBR_Sensitivity_single_slot\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        if self.radioButton_brsinglesens_dirtytx.isChecked() == True:
            self.csp.dirty_tx_settings(en=1,mode='BR')
        else:
            self.csp.dirty_tx_settings(en=0, mode='BR')
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber and per < test_limit_per:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log('channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}  {}\n'.format(chan_rx,ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx,rx_level,ber,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test007_BR_Sensitivity_multi_slot_packets(self):
        self.test_log('\n****   test007_BR_Sensitivity_multi_slot_packets     ****\n')
        res_flag_list = []
        test_limit_ber = eval(str(self.lineEdit_br_testlimit_multsens_ber_2.text()))
        test_limit_per = eval(str(self.lineEdit_br_testlimit_multsens_per.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        self.csp.config_rxq_repetion(rep='SING')
        rx_level = eval(str(self.lineEdit_br_multsens_txlevel.text()))
        self.csp.config_rx_level(rxpwr=rx_level)
        self.csp.config_rxq_br_packets(num=eval(str(self.lineEdit_multsens_numberofbit_2.text())))
        self.csp.config_connect_br_packet_pattern(pattern='PRBS9')
        self.csp.config_connect_br_packet_ptype(ptype='DH5')
        title = '\nBR_Sensitivity_multi_slot\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        if self.radioButton_brmultisens_dirtytx.isChecked() == True:
            self.csp.dirty_tx_settings(en=1,mode='BR')
        else:
            self.csp.dirty_tx_settings(en=0, mode='BR')
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber and per < test_limit_per:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log('channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}  {}\n'.format(chan_rx,ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, rx_level, ber,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test008_BR_Maximum_Input_Level(self):
        self.test_log('\n****   test008_BR_Maximum_Input_Level     ****\n')
        res_flag_list = []
        test_limit_ber = eval(str(self.lineEdit_br_testlimit_maxinput_ber.text()))
        test_limit_per = eval(str(self.lineEdit_br_testlimit_maxinput_per.text()))
        self.csp.mode_set(mode='BR')
        self.csp.sig_btype(btype='BR')
        self.csp.config_rxq_repetion(rep='SING')
        rx_level = eval(str(self.lineEdit_br_maxinput_txpowerlevel.text()))
        self.csp.config_rx_level(rxpwr=rx_level)
        self.csp.config_rxq_br_packets(num=eval(str(self.lineEdit_brmaxinput_numberofbit.text())))
        self.csp.config_connect_br_packet_pattern(pattern='PRBS9')
        self.csp.config_connect_br_packet_ptype(ptype='DH1')
        title = '\nBR_Maximum_Input_Level\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber and per < test_limit_per:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}    {}\n'.format(
                    chan_rx, ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, rx_level, ber,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'
    def test012_EDR_Sensitivity(self):
        self.test_log('\n****   test012_EDR_Sensitivity     ****\n')
        res_flag_list = []
        test_limit_ber = eval(str(self.lineEdit_edr_testlimit_sens_ber.text()))
        test_limit_per = eval(str(self.lineEdit_edr_testlimit_sens_per.text()))
        self.csp.mode_set(mode='EDR')
        self.csp.sig_btype(btype='EDR')
        self.csp.config_rxq_repetion(rep='SING')
        rx_level = eval(str(self.lineEdit_edr2sens_txlevel.text()))
        self.csp.config_rx_level(rxpwr=rx_level)
        self.csp.config_rxq_br_packets(num=eval(str(self.lineEdit_edresens_numberofbit.text())))
        self.csp.config_connect_edr_packet_pattern(pattern='PRBS9')  # 设置EDR包 payload 数据类型
        self.csp.config_connect_edr_packet_ptype(ptype='E21P')
        if self.radioButton_edrsens_dirtytx.isChecked() == True:
            self.csp.dirty_tx_settings(en=1,mode='EDR')
        else:
            self.csp.dirty_tx_settings(en=0, mode='EDR')
        title = '\nEDR2_Sensitivity\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber and per < test_limit_per:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}    {}\n'.format(
                    chan_rx, ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, rx_level, ber,res_flag])
            res_flag_list.append(res_flag)

        self.csp.config_connect_edr_packet_ptype(ptype='E31P')
        rx_level = eval(str(self.lineEdit_edr3sens_txlevel.text()))
        self.csp.config_rx_level(rxpwr=rx_level)
        title = '\nEDR3_Sensitivity\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber and per < test_limit_per:
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}    {}\n'.format(
                    chan_rx, ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, rx_level, ber,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test013_EDR_BER_Floor_Performance(self):
        self.test_log('\n****   test013_EDR_BER_Floor_Performance     ****\n')
        res_flag_list = []
        test_limit_ber = eval(str(self.lineEdit_edr_testlimit_berfloor_ber.text()))
        self.csp.mode_set(mode='EDR')
        self.csp.sig_btype(btype='EDR')
        self.csp.config_rx_level(rxpwr=-60)
        self.csp.config_rxq_repetion(rep='SING')
        self.csp.config_rxq_br_packets(num=1000)
        self.csp.config_connect_edr_packet_pattern(pattern='PRBS9')  # 设置EDR包 payload 数据类型
        self.csp.config_connect_edr_packet_ptype(ptype='E21P')
        title = '\nEDR2_BER_Floor_Performance\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber :
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}    {}\n'.format(
                    chan_rx, ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, -60, ber,res_flag])
            res_flag_list.append(res_flag)

        self.csp.config_connect_edr_packet_ptype(ptype='E31P')
        title = '\nEDR3_BER_Floor_Performance\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber :
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}    {}\n'.format(
                    chan_rx, ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, -60, ber,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'

    def test014_EDR_Maximum_Input_Level(self):
        self.test_log('\n****   test014_EDR_Maximum_Input_Level     ****\n')
        res_flag_list = []
        test_limit_ber = eval(str(self.lineEdit_edr_testlimit_maxinput_ber.text()))
        self.csp.mode_set(mode='EDR')
        self.csp.sig_btype(btype='EDR')
        self.csp.config_rxq_repetion(rep='SING')
        rx_level = eval(str(self.lineEdit_edr_maxinput_txpowerlevel.text()))
        self.csp.config_rx_level(rxpwr=rx_level)
        self.csp.config_rxq_br_packets(num=eval(str(self.lineEdit_edrmaxinput_numberofbit.text())))
        self.csp.config_connect_edr_packet_pattern(pattern='PRBS9')  # 设置EDR包 payload 数据类型
        self.csp.config_connect_edr_packet_ptype(ptype='E21P')
        title = '\nEDR2_Maximum_Input_Level\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber :
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}    {}\n'.format(
                    chan_rx, ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, rx_level, ber,res_flag])
            res_flag_list.append(res_flag)

        self.csp.config_connect_edr_packet_ptype(ptype='E31P')
        title = '\nEDR2_Maximum_Input_Level\nchannel,rx_level(dBm),ber(%)\n'
        self.fw1.write_string(title)
        for chan_rx in self.test_chan_rx_list:
            self.csp.RF_Frequency_Settings_rx(mode=self.test_mode_in_tx, ch_tx=self.test_chan_rx_dic[chan_rx],
                                              ch_rx=chan_rx)
            self.csp.ber_meas_state(state=0)

            while 1:
                state_res = self.csp.get_ber_meas_state()  # ber search 完成则退出循环
                # logdebug(state_res)
                if state_res == 'RDY':
                    loginfo('search complete')
                    break

            res = self.csp.meas_bt_ber_res(cmd_type='FETCH')
            ber = eval(res[1])
            per = eval(res[2])
            NAK = eval(res[5])
            hec_err = eval(res[6])
            crc_err = eval(res[7])
            packet_type_err = eval(res[8])
            pay_err = eval(res[9])
            if ber < test_limit_ber :
                res_flag = 'pass'
            else:
                res_flag = 'fail'
            self.test_log(
                'channel  {}  ber  {} per {}  NAK {}  hec_err {}  crc_err {}  packet_type_err {}  pay_err {}    {}\n'.format(
                    chan_rx, ber, per, NAK, hec_err, crc_err, packet_type_err, pay_err,res_flag))
            self.fw1.write_data([chan_rx, rx_level, ber,res_flag])
            res_flag_list.append(res_flag)
        for flag in res_flag_list:
            if flag == 'fail':
                return flag
        return 'pass'
    def save_as_setup(self):
        savefilename = QFileDialog.getSaveFileName(self,'save file','setup','file (*.txt)')
        logdebug('{}'.format(savefilename))
        if os.path.isfile(savefilename) == False:
            wf = open(savefilename, 'w')
            para_list = self.setup_get()
            for strm in para_list:
                wf.write(strm+'\n')
    def save_setup(self):
        savefilename = self.setupfile
        logdebug('{}'.format(savefilename))
        if os.path.isfile(savefilename) == False:
            wf = open(savefilename, 'w')
            para_list = self.setup_get()
            for strm in para_list:
                wf.write(strm+'\n')

    def open_setup(self):
        openfilename = QFileDialog.getOpenFileName(self, 'open file', 'setup', 'file (*.txt)')
        para_list = []
        self.setupfile = openfilename
        with open(openfilename) as fw:
            for line in fw:
                line = line.replace('\n', '')
                logdebug(line)
                para_list.append(line)
        self.setup_set(para_list=para_list)

    def setup_set(self,para_list=[]):
        self.radioButton_txmode.setChecked(bool(para_list[0]))
        self.radioButton_loopback.setChecked(bool(para_list[1]))
        self.radioButton_hoppingon.setChecked(bool(para_list[2]))
        self.radioButton_hoppingoff.setChecked(bool(para_list[3]))
        self.checkBox_cableloss.setChecked(bool(para_list[4]))
        self.lineEdit_cableloss.setText(para_list[5])
        self.lineEdit_txlevel.setText(para_list[6])
        self.comboBox_rfport.setCurrentIndex(eval(para_list[7]))
        self.lineEdit_lctx.setText(para_list[8])
        self.lineEdit_lcrx.setText(para_list[9])
        self.lineEdit_mctx.setText(para_list[10])
        self.lineEdit_mcrx.setText(para_list[11])
        self.lineEdit_hctx.setText(para_list[12])
        self.lineEdit_hcrx.setText(para_list[13])
        self.lineEdit_lctx_r.setText(para_list[14])
        self.lineEdit_lcrx_r.setText(para_list[15])
        self.lineEdit_mctx_r.setText(para_list[16])
        self.lineEdit_mcrx_r.setText(para_list[17])
        self.lineEdit_hctx_r.setText(para_list[18])
        self.lineEdit_hcrx_r.setText(para_list[19])
        self.lineEdit_outputpower_numberofpacket.setText(para_list[20])
        self.lineEdit_br_testlimit_maxpower.setText(para_list[21])
        self.lineEdit_br_testlimit_minpower.setText(para_list[22])
        self.lineEdit_br_testlimit_peakpower.setText(para_list[23])
        self.lineEdit_powercontrol_numberofpacket.setText(para_list[24])
        self.lineEdit_br_testlimit_powercontrol_maxstep.setText(para_list[25])
        self.lineEdit_br_testlimit_powercontrol_minstep.setText(para_list[26])
        self.lineEdit_icft_numberofpacket.setText(para_list[27])
        self.lineEdit_br_testlimit_icftoffset.setText(para_list[28])
        self.lineEdit_carrierdrift_numberofpacket.setText(para_list[29])
        self.lineEdit_br_testlimit_maxdh1drift.setText(para_list[30])
        self.lineEdit_br_testlimit_maxdh3drift.setText(para_list[31])
        self.lineEdit_br_testlimit_maxdh5drift.setText(para_list[32])
        self.lineEdit_br_testlimit_driftrate.setText(para_list[33])
        self.lineEdit_mod_numberofpacket.setText(para_list[34])
        self.lineEdit_br_testlimit_f1avgmin.setText(para_list[35])
        self.lineEdit_br_testlimit_f1avgmax.setText(para_list[36])
        self.lineEdit_br_testlimit_f2maxmin.setText(para_list[37])
        self.lineEdit_hctx_r_6.setText(para_list[38])
        self.lineEdit_br_singlesens_txlevel.setText(para_list[39])
        self.lineEdit_singlesens_numberofpackets.setText(para_list[40])
        self.lineEdit_br_testlimit_singlesens_ber.setText(para_list[41])
        self.lineEdit_br_testlimit_singlesens_per.setText(para_list[42])
        self.lineEdit_br_multsens_txlevel.setText(para_list[43])
        self.lineEdit_multsens_numberofbit_2.setText(para_list[44])
        self.lineEdit_br_testlimit_multsens_ber_2.setText(para_list[45])
        self.lineEdit_br_testlimit_multsens_per.setText(para_list[46])
        self.lineEdit_br_maxinput_txpowerlevel.setText(para_list[47])
        self.lineEdit_brmaxinput_numberofbit.setText(para_list[48])
        self.lineEdit_br_testlimit_maxinput_ber.setText(para_list[49])
        self.lineEdit_br_testlimit_maxinput_per.setText(para_list[50])
        self.lineEdit_edrrelpower_numberofpacket.setText(para_list[51])
        self.lineEdit_edr_testlimit_relpower_lower.setText(para_list[52])
        self.lineEdit_edr_testlimit_relpower_upper.setText(para_list[53])
        self.lineEdit_edrfreq_numberofpacket.setText(para_list[54])
        self.lineEdit_edr_testlimit_freqmod_wi.setText(para_list[55])
        self.lineEdit_edr_testlimit_freqmod_wiw0.setText(para_list[56])
        self.lineEdit_edr_testlimit_freqmod_w0.setText(para_list[57])
        self.lineEdit_edr_testlimit_freqmod_rmsdevmedr2.setText(para_list[58])
        self.lineEdit_edr_testlimit_freqmod_rmsdevmedr3.setText(para_list[59])
        self.lineEdit_edr_testlimit_freqmod_peakdevmedr2.setText(para_list[60])
        self.lineEdit_edr_testlimit_freqmod_peakdevmedr3.setText(para_list[61])
        self.lineEdit_edr_testlimit_freqmod_99devmedr2.setText(para_list[62])
        self.lineEdit_edr_testlimit_freqmod_99devmedr3.setText(para_list[63])
        self.lineEdit_edrdriff_numberofpacket.setText(para_list[64])
        self.lineEdit_edr_testlimit_diffphase.setText(para_list[65])
        self.lineEdit_edr2sens_txlevel.setText(para_list[66])
        self.lineEdit_edr3sens_txlevel.setText(para_list[67])
        self.lineEdit_edresens_numberofbit.setText(para_list[68])
        self.lineEdit_edr_testlimit_sens_ber.setText(para_list[69])
        self.lineEdit_edr_testlimit_sens_per.setText(para_list[70])
        self.lineEdit_edr_testlimit_berfloor_ber.setText(para_list[71])
        self.lineEdit_edr_maxinput_txpowerlevel.setText(para_list[72])
        self.lineEdit_edrmaxinput_numberofbit.setText(para_list[73])
        self.lineEdit_edr_testlimit_maxinput_ber.setText(para_list[74])
        self.lineEdit_browse.setText(para_list[75])
        self.radioButton_brsinglesens_dirtytx.setChecked(bool(para_list[76]))
        self.radioButton_brmultisens_dirtytx.setChecked(bool(para_list[77]))
        self.radioButton_edrsens_dirtytx.setChecked(bool(para_list[78]))


    def setup_get(self):
        para1 = str(self.radioButton_txmode.isChecked())
        para2 = str(self.radioButton_loopback.isChecked())
        para3 = str(self.radioButton_hoppingon.isChecked())
        para4 = str(self.radioButton_hoppingoff.isChecked())
        para5 = str(self.checkBox_cableloss.isChecked())
        para6 = str(self.lineEdit_cableloss.text())
        para7 = str(self.lineEdit_txlevel.text())
        para8 = str(self.comboBox_rfport.currentIndex())
        para9 = str(self.lineEdit_lctx.text())
        para10 = str(self.lineEdit_lcrx.text())
        para11 = str(self.lineEdit_mctx.text())
        para12 = str(self.lineEdit_mcrx.text())
        para13 = str(self.lineEdit_hctx.text())
        para14 = str(self.lineEdit_hcrx.text())
        para15 = str(self.lineEdit_lctx_r.text())
        para16 = str(self.lineEdit_lcrx_r.text())
        para17 = str(self.lineEdit_mctx_r.text())
        para18 = str(self.lineEdit_mcrx_r.text())
        para19 = str(self.lineEdit_hctx_r.text())
        para20 = str(self.lineEdit_hcrx_r.text())
        para21 = str(self.lineEdit_outputpower_numberofpacket.text())
        para22 = str(self.lineEdit_br_testlimit_maxpower.text())
        para23 = str(self.lineEdit_br_testlimit_minpower.text())
        para24 = str(self.lineEdit_br_testlimit_peakpower.text())
        para25 = str(self.lineEdit_powercontrol_numberofpacket.text())
        para26 = str(self.lineEdit_br_testlimit_powercontrol_maxstep.text())
        para27 = str(self.lineEdit_br_testlimit_powercontrol_minstep.text())
        para28 = str(self.lineEdit_icft_numberofpacket.text())
        para29 = str(self.lineEdit_br_testlimit_icftoffset.text())
        para30 = str(self.lineEdit_carrierdrift_numberofpacket.text())
        para31 = str(self.lineEdit_br_testlimit_maxdh1drift.text())
        para32 = str(self.lineEdit_br_testlimit_maxdh3drift.text())
        para33 = str(self.lineEdit_br_testlimit_maxdh5drift.text())
        para34 = str(self.lineEdit_br_testlimit_driftrate.text())
        para35 = str(self.lineEdit_mod_numberofpacket.text())
        para36 = str(self.lineEdit_br_testlimit_f1avgmin.text())
        para37 = str(self.lineEdit_br_testlimit_f1avgmax.text())
        para38 = str(self.lineEdit_br_testlimit_f2maxmin.text())
        para39 = str(self.lineEdit_hctx_r_6.text())
        para40 = str(self.lineEdit_br_singlesens_txlevel.text())
        para41 = str(self.lineEdit_singlesens_numberofpackets.text())
        para42 = str(self.lineEdit_br_testlimit_singlesens_ber.text())
        para43 = str(self.lineEdit_br_testlimit_singlesens_per.text())
        para44 = str(self.lineEdit_br_multsens_txlevel.text())
        para45 = str(self.lineEdit_multsens_numberofbit_2.text())
        para46 = str(self.lineEdit_br_testlimit_multsens_ber_2.text())
        para47 = str(self.lineEdit_br_testlimit_multsens_per.text())
        para48 = str(self.lineEdit_br_maxinput_txpowerlevel.text())
        para49 = str(self.lineEdit_brmaxinput_numberofbit.text())
        para50 = str(self.lineEdit_br_testlimit_maxinput_ber.text())
        para51 = str(self.lineEdit_br_testlimit_maxinput_per.text())
        para52 = str(self.lineEdit_edrrelpower_numberofpacket.text())
        para53 = str(self.lineEdit_edr_testlimit_relpower_lower.text())
        para54 = str(self.lineEdit_edr_testlimit_relpower_upper.text())
        para55 = str(self.lineEdit_edrfreq_numberofpacket.text())
        para56 = str(self.lineEdit_edr_testlimit_freqmod_wi.text())
        para57 = str(self.lineEdit_edr_testlimit_freqmod_wiw0.text())
        para58 = str(self.lineEdit_edr_testlimit_freqmod_w0.text())
        para59 = str(self.lineEdit_edr_testlimit_freqmod_rmsdevmedr2.text())
        para60 = str(self.lineEdit_edr_testlimit_freqmod_rmsdevmedr3.text())
        para61 = str(self.lineEdit_edr_testlimit_freqmod_peakdevmedr2.text())
        para62 = str(self.lineEdit_edr_testlimit_freqmod_peakdevmedr3.text())
        para63 = str(self.lineEdit_edr_testlimit_freqmod_99devmedr2.text())
        para64 = str(self.lineEdit_edr_testlimit_freqmod_99devmedr3.text())
        para65 = str(self.lineEdit_edrdriff_numberofpacket.text())
        para66 = str(self.lineEdit_edr_testlimit_diffphase.text())
        para67 = str(self.lineEdit_edr2sens_txlevel.text())
        para68 = str(self.lineEdit_edr3sens_txlevel.text())
        para69 = str(self.lineEdit_edresens_numberofbit.text())
        para70 = str(self.lineEdit_edr_testlimit_sens_ber.text())
        para71 = str(self.lineEdit_edr_testlimit_sens_per.text())
        para72 = str(self.lineEdit_edr_testlimit_berfloor_ber.text())
        para73 = str(self.lineEdit_edr_maxinput_txpowerlevel.text())
        para74 = str(self.lineEdit_edrmaxinput_numberofbit.text())
        para75 = str(self.lineEdit_edr_testlimit_maxinput_ber.text())
        para76 = str(self.lineEdit_browse.text())
        para77 = str(self.radioButton_brsinglesens_dirtytx.isChecked())
        para78 = str(self.radioButton_brmultisens_dirtytx.isChecked())
        para79 = str(self.radioButton_edrsens_dirtytx.isChecked())
        return [para1, para2, para3, para4, para5, para6, para7, para8, para9, para10,
                para11, para12, para13, para14, para15, para16, para17, para18, para19, para20,
                para21, para22, para23, para24, para25, para26, para27, para28, para29, para30,
                para31, para32, para33, para34, para35, para36, para37, para38, para39, para40,
                para41, para42, para43, para44, para45, para46, para47, para48, para49, para50,
                para51, para52, para53, para54, para55, para56, para57, para58, para59, para60,
                para61, para62, para63, para64, para65, para66, para67, para68, para69, para70,
                para71, para72, para73, para74, para75, para76, para77, para78, para79
                ]

class func_ui(Ui_MainWindow):
    driver_thread = []  # type: Thread
    data = []  # type: Popen
    driver_show = []

    def __init__(self, MainWindow):
        self.payload_len_dict = {
            1: 27,
            2: 54,
            3: 83,
            4: 183,
            5: 367,
            6: 552,
            7: 339,
            8: 679,
            9: 1021
            }
        self.pattern_br_dict = {
            '00000000' : 4 ,
            '11111111' : 3,
            '10101010' : 2,
            '11110000' : 1,
            'PRBS9' : 7
            }
        self.pattern_le_dict = {
            '00000000' : 5 ,
            '11111111' : 4,
            '10101010' : 2,
            '11110000' : 1,
            'PRBS9' : 0
            }
        ##mianwindown init
        self.setupUi(MainWindow)
class csvreport(object):
    '''
    用于生成 CSV 格式 的 表格
    '''

    def __init__(self, csvname, title, no_time=0):
        '''
        :csvname:
              input csv name is path+name
        :title:
                it may be string ['str1, str2, str3, ...\n']
        :output CSV name is csvname+localtime.csv
        '''
        self.logtime = time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
        if no_time==1:
            self.logtime = self.logtime[0:8]

        self.filename = '%s_%s.csv'%(csvname, self.logtime)
##        self.filename = './rftest/rfdata/test_phase_case/test_phase_case_CHIP722_A_20190507.csv'

        if os.path.isfile(self.filename) == False:
            self.wf = open(self.filename, 'w')
            self.wf.write(title)
        else:
            self.wf = open(self.filename, 'a')
        self.wf.close()


    def get_type(self, data, float_num=2):
        if type(data) == int:
            ostr = str(data)+','
        elif type(data) == str:
            ostr = data+','
        else:
            if float_num==2:
                ostr = '%2.2f,'%data
            else:
                ostr = '%2.4f,'%data
        return ostr

    def write_data(self, data_list, float_num=2):
        '''
        csv write data line
        :data_list:
            it may be string and int type, like ['str', 'str', int, int, ...]
        '''
        self.wf = open(self.filename, 'a')
        wstr = ''
        for data in data_list:
##            print data
##            print type(data)
            if type(data) == list:
                for dl in data:
                    wstr += self.get_type(dl,float_num)
            else:
                wstr += self.get_type(data, float_num)

        wstr += '\n'
        self.wf.write(wstr)
        self.wf.close()

    def write_string(self, string):
        '''
        csv write data line
        :string:
        '''
        self.wf = open(self.filename, 'a')
        self.wf.write(string)
        self.wf.close()

    def close(self):
        '''
        释放 csv 文件
        '''
        self.wf.close()


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