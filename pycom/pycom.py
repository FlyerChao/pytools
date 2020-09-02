# coding:utf-8
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from mainwindow import Ui_MainWindow
import sys
import os
import cgitb
import threading
import io
# from queue import Queue
# 导入time模块
import time
#from datetime import datetime
import serial
import serial.tools.list_ports
# from pyico import *
import yaml

window_out_s = ""
global fp
fp = ""
global logfile_flag;
logfile_flag = 0

# 继承QThread
class LoopThread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    loop_signal = pyqtSignal(str)

    def __init__(self, serial_num):
        super(LoopThread, self).__init__()
        self.serial_num = serial_num
        self.terminated = False

    def __del__(self):
        self.wait()

    def run(self):
        global logfile_flag;
        global fp
        print("begin read serial")
        while not self.terminated:
            if mainWindow.haveserial() == True:
                b = Server2IoTextHandleBean()
                if self.serial_num.is_open is True:
                    b.text_bin = super(io.IOBase, self.serial_num).readline()
                    if len(b.text_bin) != 0:
                        out_s = b.text_bin.decode('utf-8', errors='ignore')

                        ct = time.time()
                        local_time = time.localtime(ct)
                        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                        data_secs = (ct - int(ct)) * 1000
                        time_stamp = "[%s.%03d]" % (data_head, data_secs)

                        file_head = time.strftime("%Y%m%d_%H%M%S", local_time)
                        file_name = "%s.log" % (file_head)

                        window_out_s = time_stamp + ': ' + out_s;

                        if logfile_flag == 1:
                            if fp != "":
                                fp.write(window_out_s.replace('\r',''))
                                fp.flush()
                        self.loop_signal.emit(window_out_s)  # 注意这里与_signal = pyqtSignal(str)中的类型相同
            else:
                # print("will be end loop")
                self.terminated = None
        print("end read serial")

    def finished(self):
        self.terminated = True

    def quit(self):
        self.terminated = True

class TextHandleBean:

    def __init__(self):
        self.direction = None
        self.text_bin = None
        self.text_raw = None
        self.text_format = None

class Server2IoTextHandleBean(TextHandleBean):

    def __init__(self):
        super().__init__()
        self.direction = '<<'

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    sigSet_textedit = pyqtSignal(str)  ####信号定义
    logfile_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # 设置应用程序的窗口图标
        root = QFileInfo(__file__).absolutePath()
        self.setWindowIcon(QIcon(root+'/lmedia1.ico'))

        #串口无效
        self.ser = None
        self.send_num = 0
        self.receive_num = 0
        #记录最后发送的回车字符的变量
        self.rcv_enter = ''

        # #显示发送与接收的字符数量
        # dis = '发送：'+ '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
        # self.statusBar.showMessage(dis)

        #刷新一下串口的列表
        self.refresh()

        #波特率
        self.comboBox_2.addItem('115200')
        self.comboBox_2.addItem('57600')
        self.comboBox_2.addItem('56000')
        self.comboBox_2.addItem('38400')
        self.comboBox_2.addItem('19200')
        self.comboBox_2.addItem('14400')
        self.comboBox_2.addItem('9600')
        self.comboBox_2.addItem('4800')
        self.comboBox_2.addItem('2400')
        self.comboBox_2.addItem('1200')

        #数据位
        self.comboBox_3.addItem('8')
        self.comboBox_3.addItem('7')
        self.comboBox_3.addItem('6')
        self.comboBox_3.addItem('5')

        #停止位
        self.comboBox_4.addItem('1')
        self.comboBox_4.addItem('1.5')
        self.comboBox_4.addItem('2')

        #校验位
        self.comboBox_5.addItem('NONE')
        self.comboBox_5.addItem('ODD')
        self.comboBox_5.addItem('EVEN')

        #对testEdit进行事件过滤
        self.textbrowser.installEventFilter(self)

        #实例化一个定时器
        # self.timer = QTimer(self)

        self.timer_send= QTimer(self)

        self.sigSet_textedit.connect(self.set_textedit)####信号槽连接
        # #定时器调用读取串口接收数据
        # self.timer.timeout.connect(self.recv)

        #定时发送
        self.timer_send.timeout.connect(self.send)

        #发送数据按钮
        # self.pushButton.clicked.connect(self.send)
        self.pushButton.clicked.connect(lambda:self.send(0))
        self.pushButton_2cmd.clicked.connect(lambda: self.send(1))
        self.pushButton_3cmd.clicked.connect(lambda:self.send(2))

        #打开关闭串口按钮
        self.pushButton_2.clicked.connect(self.open_close)

        #刷新串口外设按钮
        self.pushButton_4.clicked.connect(self.refresh)

        #清除窗口
        self.pushButton_3.clicked.connect(self.clear)

        #定时发送
        self.checkBox_4.clicked.connect(self.send_timer_box)

        #比较文件中的比较内容，然后发送对应的内容
        self.checkBox_cmp.clicked.connect(self.send_cmp_box)
        self.cmp_str_flag = False

        #波特率修改
        self.comboBox_2.activated.connect(self.baud_modify)

        #串口号修改
        self.comboBox.activated.connect(self.com_modify)

        #开始保存文件
        # checkBox_savefile
        self.checkBox_savefile.stateChanged.connect(self.save_file)

        self._thread = None

        #执行一下打开串口
        # self.open_close(False)
        self.pushButton_2.setChecked(False)

        #读取循环发送列表的计数器
        self.sendcount = 1
        self.intervalseconds = 1
         #实例化一个定时器
        self.loop_send_timer = QTimer(self)
        # #定时器调用读取串口接收数据
        self.loop_send_timer.timeout.connect(self.fun_timer)

    def send_bytes(self, send_str):
        if self.ser != None:
            #发送数据
            input_s = send_str + '\r'
            input_s = input_s.encode('utf-8')
            try:
                num = self.ser.write(input_s)
            except:
                #串口拔出错误，关闭定时器
                self.ser.close()
                self.ser = None

    def save_file(self):
        global logfile_flag
        global fp
        if self.checkBox_savefile.checkState():
            print("begin log file")
            ct = time.time()
            local_time = time.localtime(ct)
            data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            data_secs = (ct - int(ct)) * 1000
            time_stamp = "[%s.%03d]" % (data_head, data_secs)

            file_head = time.strftime("%Y%m%d_%H%M%S", local_time)
            file_name = "%s.log" % (file_head)

            logfile_flag = 1
            if fp == "":
                fp = open(file_name, "w+")
        else:
            print("close log file")
            logfile_flag = 0
            if fp != "":
                fp.close()
            fp = ""

    # 获取是否存在串口
    def haveserial(self):
        # 查询可用的串口
        if self.thread is None:
            return False

        plist = list(serial.tools.list_ports.comports())
        if len(plist) <= 0:
            print("No used com!")
            return False
        else:
            # print("have com can be used")
            return True

    #刷新一下串口
    def refresh(self):
        #查询可用的串口
        plist=list(serial.tools.list_ports.comports())

        if len(plist) <= 0:
            print("No used com!");
            self.statusBar.showMessage('没有可用的串口')
            return False
        else:
            #把所有的可用的串口输出到comboBox中去
            self.comboBox.clear()

            for i in range(0, len(plist)):
                plist_0 = list(plist[i])
                self.comboBox.addItem(str(plist_0[0]))
            return True

    #事件过滤
    def eventFilter(self, obj, event):
        #处理textEdit的键盘按下事件
        if event.type() == event.KeyPress:

            if self.ser != None:
                if event.key() == QtCore.Qt.Key_Up:

                    #up 0x1b5b41 向上箭头
                    send_list = []
                    send_list.append(0x1b)
                    send_list.append(0x5b)
                    send_list.append(0x41)
                    input_s = bytes(send_list)

                    num = self.ser.write(input_s)
                elif event.key() == QtCore.Qt.Key_Down:
                    #down 0x1b5b42 向下箭头
                    send_list = []
                    send_list.append(0x1b)
                    send_list.append(0x5b)
                    send_list.append(0x42)
                    input_s = bytes(send_list)

                    num = self.ser.write(input_s)
                else:
                    #获取按键对应的字符
                    char = event.text()
                    num = self.ser.write(char.encode('utf-8'))
                # self.send_num = self.send_num + num
                # dis = '发送：'+ '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
                # self.statusBar.showMessage(dis)
            else:
                pass
            return True
        else:
            return False

    #重载窗口关闭事件
    def closeEvent(self,e):
        print("closeEvent")
        #关闭定时器，停止读取接收数据
        self.timer_send.stop()
        self.loop_stop()
        #关闭串口
        if self.ser != None:
            self.ser.close()

    #定时发送数据
    def send_timer_box(self):
        if self.ser != None:
            if self.checkBox_4.checkState():
                try:
                    with open("com_config.yaml") as fd:
                        self.dict_str = yaml.unsafe_load(fd)
                    print("=======com_config.yaml==============",time.strftime('%Y-%m-%d %H:%M:%S'))
                    for command1 in self.dict_str:
                        print(command1['command'])
                    if self.loop_send_timer.isActive() != True:
                            self.loop_send_timer.start(1000)  # 1s
                except expression as identifier:
                    pass
            else:
                if self.loop_send_timer.isActive() == True:
                        self.loop_send_timer.stop()  # 1s

    def send_cmp_box(self):
        print("read compare config")
        if self.ser != None:
            if self.checkBox_cmp.checkState():
                try:
                    with open("compare_config.yaml") as fd:
                        self.cmp_str = yaml.unsafe_load(fd)
                    print("=======compare_config.yaml==============", time.strftime('%Y-%m-%d %H:%M:%S'))
                    print(self.cmp_str)
                    for command1 in self.cmp_str:
                        print("compare command is :", command1['compare_str'])
                    self.cmp_str_flag = True
                except expression as identifier:
                    pass
            else:
                print("do nothing")
                self.cmp_str_flag = False

    #清除窗口操作
    def clear(self):
        self.textbrowser.clear()
        self.send_num = 0
        self.receive_num = 0

    #串口发送数据处理
    def send(self, button_num):
        if self.ser != None:
            if button_num == 0:
                input_s = self.lineEdit.text()
            elif button_num == 1:
                input_s = self.lineEdit_2cmd.text()
            elif button_num == 2:
                input_s = self.lineEdit_3cmd.text()
            if input_s != "":
                #发送字符
                if (self.checkBox.checkState() == False):
                    input_s = input_s + '\r'
                    input_s = input_s.encode('utf-8')
                    print("input_s is ", input_s)
                else:
                    #发送十六进制数据
                    input_s = input_s.strip() #删除前后的空格
                    send_list=[]
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)

                        except ValueError:
                            print('input hex data!')
                            QMessageBox.critical(self, 'pycom','请输入十六进制数据，以空格分开!')
                            return None

                        input_s = input_s[2:]
                        input_s = input_s.strip()

                        #添加到发送列表中
                        send_list.append(num)
                    input_s = bytes(send_list)
                print(input_s)
                #发送数据
                try:
                    num = self.ser.write(input_s)
                except:

                    #串口拔出错误，关闭定时器
                    self.ser.close()
                    self.ser = None

                    #设置为打开按钮状态
                    self.pushButton_2.setChecked(False)
                    self.pushButton_2.setText("打开串口")
                    print('serial error send!')
                    return None

            else:
                print('none data input!')
        else:
            #停止发送定时器
            self.timer_send.stop()
            QMessageBox.critical(self, 'pycom','请打开串口')

    #波特率修改
    def baud_modify(self):
        if self.ser != None:
            self.ser.baudrate = int(self.comboBox_2.currentText())

    #串口号修改
    def com_modify(self):
        if self.ser != None:
            self.ser.port = self.comboBox.currentText()

    def set_textedit(self, log):
        #先把光标移到到最后
        cursor = self.textbrowser.textCursor()
        if(cursor != cursor.End):
            cursor.movePosition(cursor.End)
            self.textbrowser.setTextCursor(cursor)

        #获取到text光标
        textCursor = self.textbrowser.textCursor()
        #滚动到底部
        textCursor.movePosition(textCursor.End)
        #设置光标到text中去
        self.textbrowser.setTextCursor(textCursor)

        #把字符串显示到窗口中去
        self.textbrowser.insertPlainText(log)

        #获取到text光标
        textCursor = self.textbrowser.textCursor()
        #滚动到底部
        textCursor.movePosition(textCursor.End)
        #设置光标到text中去
        self.textbrowser.setTextCursor(textCursor)

        if self.cmp_str_flag == True:
            for cmd_str in self.cmp_str:
                if str(log).find(cmd_str['compare_str']) != -1:
                    send_cmd_str_temp = '\r'+'\n'+cmd_str['send_cmd']+'\r'+'\n'
                    self.send_bytes(send_str=send_cmd_str_temp)
        #获取到text光标
        textCursor = self.textbrowser.textCursor()
        #滚动到底部
        textCursor.movePosition(textCursor.End)
        #设置光标到text中去
        self.textbrowser.setTextCursor(textCursor)

    def loop_start(self):
        # 创建线程
        self.thread = LoopThread(serial_num = self.ser)
        # 连接信号
        self.thread.loop_signal.connect(self.set_textedit)  # 进程连接回传到GUI的事件
        # 开始线程
        self.thread.start()

    def loop_stop(self):
        if self.thread is not None:
            self.terminated = True
            # if threading.current_thread() != self.thread :
            #     self.thread.stop()
            self.thread = None
            print("loop_stop tread")
            if self.ser is not None:
                self.ser.cancel_read()

    #打开关闭串口
    def open_close(self, btn_sta):
        if btn_sta == True:
            try:
                #输入参数'COM13',115200
                self.ser = serial.Serial(self.comboBox.currentText(), int(self.comboBox_2.currentText()), timeout=0.1)
            except:
                QMessageBox.critical(self, 'pycom','没有可用的串口或当前串口被占用')
                return None
            #字符间隔超时时间设置
            self.ser.interCharTimeout = 0.001
            #1ms的测试周期
            self.loop_start()
            # self.timer.start(1)
            self.pushButton_2.setText("关闭串口")
            print('open')
        else:
            #关闭定时器，停止读取接收数据
            if self.loop_send_timer.isActive() == True:
                self.loop_send_timer.stop()
            self.loop_stop()
            try:
                #关闭串口
                self.ser.close()
            except:
                QMessageBox.critical(self, 'pycom','关闭串口失败')
                return None
            time.sleep(0.5)
            self.ser = None
            self.pushButton_2.setText("打开串口")
            print('close!')

    def fun_timer(self):
        for command_dic in self.dict_str:
            if self.intervalseconds != 0 :
                if (self.intervalseconds % int(command_dic['interval'])) == 0:
                    if self.sendcount != 0 and command_dic['count'] != 0:
                        if command_dic['count'] == -1:
                            self.send_bytes(send_str=command_dic['command'])
                        elif self.sendcount <= ( int(command_dic['count']) * int(command_dic['interval'])):
                            self.send_bytes(send_str=command_dic['command'])
        self.intervalseconds = self.intervalseconds + 1
        self.sendcount = self.sendcount + 1

if __name__ == "__main__":
    try:
        print("*** start at %s ***" % (time.ctime(time.time())))
        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("============, error:%s" % (e))
    finally:
        print("*** end at %s ***" % (time.ctime(time.time())))
