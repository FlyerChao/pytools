# coding:utf-8
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtCore import QStringListModel, Qt
from serial.tools import miniterm
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
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
import datetime
import queue
import codecs

window_out_s = ""
global fp
fp = ""
global logfile_flag;
logfile_flag = 0
global g_mainWindow
global edit_flag
global queue_buf
history_cmd_file_name='history_cmd.yaml'

def fuzzyfinder_test(input, collection, accessor=lambda x: x):
    """
    Args:
        input (str): A partial string which is typically entered by a user.
        collection (iterable): A collection of strings which will be filtered
                            based on the `input`.
        accessor (function): If the `collection` is not an iterable of strings,
                            then use the accessor to fetch the string that
                            will be used for fuzzy matching.

    Returns:
        suggestions (generator): A generator object that produces a list of
            suggestions narrowed down from `collection` using the `input`.
    """
    suggestions = []
    input = str(input) if not isinstance(input, str) else input
    pat = '.*?'.join(map(re.escape, input))
    pat = '(?=({0}))'.format(pat)   # lookahead regex to manage overlapping matches
    regex = re.compile(pat, re.IGNORECASE)
    for item in collection:
        r = list(regex.finditer(accessor(item)))
        if r:
            best = min(r, key=lambda x: len(x.group(1)))   # find shortest match
            suggestions.append((len(best.group(1)), best.start(), accessor(item), item))

    return (z[-1] for z in sorted(suggestions))

# 继承QThread
class LoopThread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    loop_signal = pyqtSignal(str)

    def __init__(self, serial_num):
        super(LoopThread, self).__init__()
        self.serial_num = serial_num
        self.terminated = False
        self.buffer = ''
        self.queue = queue.Queue(maxsize=1048576)

    def __del__(self):
        self.wait()

    def run(self):
        global logfile_flag;
        global fp
        global queue_buf
        print("begin read serial")
        while not self.terminated:
            if g_mainWindow.haveserial() == True:
                if self.serial_num.is_open is True:
                    try:
                        self.buffer += queue_buf.get()
                        while '\n' in self.buffer: #split data line by line and store it in var
                            var, self.buffer = self.buffer.split('\n', 1)
                            self.queue.put(var) #put received line in the queue
                            if self.queue.empty() is True:
                                continue
                            temp_xx = self.queue.get()
                            out_s = str(temp_xx.replace('\0',''))
                            time_stamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]')
                            out_temp = out_s.replace('\r','')
                            window_out_s = time_stamp + ': ' + out_temp.replace('\n','') + "\n"
                            window_out_ss = time_stamp + ': ' + out_temp.replace('\n','')
                            # window_out_s = '<font color=\"#0000FF\">' + window_out_s + '</font>'

                            if logfile_flag == 1:
                                if fp is not None:
                                    fp.write(window_out_s)
                                    fp.flush()
                            self.loop_signal.emit(window_out_ss)  # 注意这里与_signal = pyqtSignal(str)中的类型相同
                            window_out_s = ""

                    except Exception as e:
                        print("============, error:%s" % (e))
                        #串口拔出错误，关闭定时器
                        print("uart eject")
                        self.ser = None
                        g_mainWindow.open_close(False)
                        # MainWindow.findChildren.pushButton_2.setText("打开串口")
                        #刷新一下串口的列表
                        g_mainWindow.refresh()
                        self.finished()
            else:
                # print("will be end loop")
                self.terminated = None
        print("end read serial")

    def finished(self):
        self.terminated = True

    def quit(self):
        self.terminated = True

# 继承QThread
class LoopThread_SendCmd(QtCore.QThread):
    #  通过类成员对象定义信号对象
    loop_signal = pyqtSignal(str)

    def __init__(self, serial_num, dic_str):
        super(LoopThread_SendCmd, self).__init__()
        self.serial_num = serial_num
        self.terminated = False
        self.dic_str = dic_str
        self.buffer = ''
        self.queue = queue.Queue(maxsize=1048576)

    def __del__(self):
        self.wait()

    def run(self):
        global g_mainWindow
        print("begin send sequence serial")
        for command1 in self.dic_str:
            print(command1['command'])
            # g_mainWindow.send_bytes(command1['command'])
            self.sleep(1)
            # time.sleep(5)
        # print(self.dic_str)
        # g_mainWindow.send_bytes(self.dic_str)
        print("end send sequence serial")

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

codecs.register(lambda c: hexlify_codec.getregentry() if c == 'hexlify' else None)
try:
    raw_input
except NameError:
    # pylint: disable=redefined-builtin,invalid-name
    raw_input = input   # in python3 it's "raw"
    unichr = chr

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Transform(object):
    """do-nothing: forward all data unchanged"""
    def rx(self, text):
        """text received from serial port"""
        return text

    def tx(self, text):
        """text to be sent to serial port"""
        return text

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text


class CRLF(Transform):
    """ENTER sends CR+LF"""

    def tx(self, text):
        return text.replace('\n', '\r\n')


class CR(Transform):
    """ENTER sends CR"""

    def rx(self, text):
        return text.replace('\r', '\n')

    def tx(self, text):
        return text.replace('\n', '\r')


class LF(Transform):
    """ENTER sends LF"""


class NoTerminal(Transform):
    """remove typical terminal control codes from input"""

    REPLACEMENT_MAP = dict((x, 0x2400 + x) for x in range(32) if unichr(x) not in '\r\n\b\t')
    REPLACEMENT_MAP.update(
        {
            0x7F: 0x2421,  # DEL
            0x9B: 0x2425,  # CSI
        })

    def rx(self, text):
        return text.translate(self.REPLACEMENT_MAP)

    echo = rx


class NoControls(NoTerminal):
    """Remove all control codes, incl. CR+LF"""

    REPLACEMENT_MAP = dict((x, 0x2400 + x) for x in range(32))
    REPLACEMENT_MAP.update(
        {
            0x20: 0x2423,  # visual space
            0x7F: 0x2421,  # DEL
            0x9B: 0x2425,  # CSI
        })


class Printable(Transform):
    """Show decimal code for all non-ASCII characters and replace most control codes"""

    def rx(self, text):
        r = []
        for c in text:
            if ' ' <= c < '\x7f' or c in '\r\n\b\t':
                r.append(c)
            elif c < ' ':
                r.append(unichr(0x2400 + ord(c)))
            else:
                r.extend(unichr(0x2080 + ord(d) - 48) for d in '{:d}'.format(ord(c)))
                r.append(' ')
        return ''.join(r)

    echo = rx


class Colorize(Transform):
    """Apply different colors for received and echo"""

    def __init__(self):
        # XXX make it configurable, use colorama?
        self.input_color = '\x1b[37m'
        self.echo_color = '\x1b[31m'

    def rx(self, text):
        return self.input_color + text

    def echo(self, text):
        return self.echo_color + text


class DebugIO(Transform):
    """Print what is sent and received"""

    def rx(self, text):
        sys.stderr.write(' [RX:{!r}] '.format(text))
        sys.stderr.flush()
        return text

    def tx(self, text):
        sys.stderr.write(' [TX:{!r}] '.format(text))
        sys.stderr.flush()
        return text

# other ideas:
# - add date/time for each newline
# - insert newline after: a) timeout b) packet end character

EOL_TRANSFORMATIONS = {
    'crlf': CRLF,
    'cr': CR,
    'lf': LF,
}

TRANSFORMATIONS = {
    'direct': Transform,    # no transformation
    'default': NoTerminal,
    'nocontrol': NoControls,
    'printable': Printable,
    'colorize': Colorize,
    'debug': DebugIO,
}

class Miniterm(object):
    """\
    Terminal application. Copy data from serial port to console and vice versa.
    Handle special keys from the console to show menu etc.
    """

    def __init__(self, serial_instance, echo=False, eol='crlf', filters=()):
        # self.console = Console()
        self.serial = serial_instance
        self.echo = echo
        self.raw = False
        self.input_encoding = 'UTF-8'
        self.output_encoding = 'UTF-8'
        self.eol = eol
        self.filters = filters
        self.update_transformations()
        # self.exit_character = unichr(0x1d)  # GS/CTRL+]
        # self.menu_character = unichr(0x14)  # Menu: CTRL+T
        self.alive = None
        self._reader_alive = None
        self.receiver_thread = None
        self.rx_decoder = None
        self.tx_decoder = None
        self.set_rx_encoding("UTF-8")

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        if hasattr(self.serial, 'cancel_read'):
            self.serial.cancel_read()
        self.receiver_thread.join()

    def start(self):
        """start worker threads"""
        self.alive = True
        self._start_reader()
        # enter console->serial loop
        # self.transmitter_thread = threading.Thread(target=self.writer, name='tx')
        # self.transmitter_thread.daemon = True
        # self.transmitter_thread.start()
        # self.console.setup()

    def stop(self):
        """set flag to stop worker threads"""
        self.alive = False

    def join(self, transmit_only=False):
        """wait for worker threads to terminate"""
        self.transmitter_thread.join()
        if not transmit_only:
            if hasattr(self.serial, 'cancel_read'):
                self.serial.cancel_read()
            self.receiver_thread.join()

    def close(self):
        self.serial.close()

    def update_transformations(self):
        """take list of transformation classes and instantiate them for rx and tx"""
        transformations = [EOL_TRANSFORMATIONS[self.eol]] + [TRANSFORMATIONS[f]
                                                             for f in self.filters]
        self.tx_transformations = [t() for t in transformations]
        self.rx_transformations = list(reversed(self.tx_transformations))

    def set_rx_encoding(self, encoding, errors='replace'):
        """set encoding for received data"""
        self.input_encoding = encoding
        self.rx_decoder = codecs.getincrementaldecoder(encoding)(errors)

    def set_tx_encoding(self, encoding, errors='replace'):
        """set encoding for transmitted data"""
        self.output_encoding = encoding
        self.tx_encoder = codecs.getincrementalencoder(encoding)(errors)

    def dump_port_settings(self):
        """Write current settings to sys.stderr"""
        sys.stderr.write("\n--- Settings: {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits}\n".format(
            p=self.serial))
        sys.stderr.write('--- RTS: {:8}  DTR: {:8}  BREAK: {:8}\n'.format(
            ('active' if self.serial.rts else 'inactive'),
            ('active' if self.serial.dtr else 'inactive'),
            ('active' if self.serial.break_condition else 'inactive')))
        try:
            sys.stderr.write('--- CTS: {:8}  DSR: {:8}  RI: {:8}  CD: {:8}\n'.format(
                ('active' if self.serial.cts else 'inactive'),
                ('active' if self.serial.dsr else 'inactive'),
                ('active' if self.serial.ri else 'inactive'),
                ('active' if self.serial.cd else 'inactive')))
        except serial.SerialException:
            # on RFC 2217 ports, it can happen if no modem state notification was
            # yet received. ignore this error.
            pass
        sys.stderr.write('--- software flow control: {}\n'.format('active' if self.serial.xonxoff else 'inactive'))
        sys.stderr.write('--- hardware flow control: {}\n'.format('active' if self.serial.rtscts else 'inactive'))
        sys.stderr.write('--- serial input encoding: {}\n'.format(self.input_encoding))
        sys.stderr.write('--- serial output encoding: {}\n'.format(self.output_encoding))
        sys.stderr.write('--- EOL: {}\n'.format(self.eol.upper()))
        sys.stderr.write('--- filters: {}\n'.format(' '.join(self.filters)))

    def reader(self):
        """loop and copy serial->console"""
        global queue_buf
        try:
            while self.alive and self._reader_alive:
                # read all that is there or wait for one byte
                data = self.serial.read(self.serial.in_waiting or 1)
                if data:
                    if self.raw:
                        # self.console.write_bytes(data)
                        # print("0000"+data)
                        queue_buf.put(data)
                    else:
                        text = self.rx_decoder.decode(data)
                        for transformation in self.rx_transformations:
                            text = transformation.rx(text)
                        # self.console.write(text)
                        # print("0000"+text)
                        queue_buf.put(text)
        except serial.SerialException:
            self.alive = False
            # self.console.cancel()
            raise       # XXX handle instead of re-raise?

# class Sequence_Cmd_Thread(object):
#     def __init__(self, dict_list) -> None:
#         self.thread_id = None
#         self.dict_list = dict_list
#         # self.event = threading.Event()
#     def create(self):
#         self.thread_id = threading.Thread(target=self.run)
#     def start(self):
#         self.thread_id.daemon = True
#         self.thread_id.start()
#     def run(self):
#         # print(self.dict_list)
#         for command in self.dict_list:
#             print(command['command'])
#             time.sleep(1)
#             # self.event.wait(timeout=1)
#             # threading.Event.wait(self,timeout=0.1)
#     def stop(self):
#         self.thread_id.join()

class Sequence_Cmd_Thread(QtCore.QThread):
    cmd_signal = pyqtSignal(str)

    def __init__(self, dict_list, pushButton_sequence_cmd):
        super(Sequence_Cmd_Thread, self).__init__()
        self.dict_list = dict_list
        self.pushButton_sequence_cmd = pushButton_sequence_cmd

    def __del__(self):
        self.wait()

    def run(self):
        print("run Sequence_Cmd_Thread start")
        for command in self.dict_list:
            print("***at %s ***" % (time.ctime(time.time())))
            print(command['command'])
            self.cmd_signal.emit(command['command'])
            time.sleep(command['timedelay'])
        print("run Sequence_Cmd_Thread stop")
        self.pushButton_sequence_cmd.setText("顺序发送")

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    sigSet_textedit = pyqtSignal(str)  ####信号定义
    logfile_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # 设置应用程序的窗口图标

        # root = QFileInfo(__file__).absolutePath()
        # print("path is : ", root)
        self.setWindowIcon(QIcon('lmedia1.ico'))
        # if sys.platform == "win32":
        #     print('try find windows icon')
        #     self.setWindowIcon(QIcon('/lmedia1.ico'))
        # else:
        #     self.setWindowIcon(QIcon(root+'/lmedia1.ico'))

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
        self.comboBox_2.addItem('1200')
        self.comboBox_2.addItem('2400')
        self.comboBox_2.addItem('4800')
        self.comboBox_2.addItem('9600')
        self.comboBox_2.addItem('14400')
        self.comboBox_2.addItem('19200')
        self.comboBox_2.addItem('38400')
        self.comboBox_2.addItem('56000')
        self.comboBox_2.addItem('57600')
        self.comboBox_2.addItem('230400')
        self.comboBox_2.addItem('460800')
        self.comboBox_2.addItem('500000')
        self.comboBox_2.addItem('576000')
        self.comboBox_2.addItem('921600')
        self.comboBox_2.addItem('1000000')
        self.comboBox_2.addItem('1152000')
        self.comboBox_2.addItem('1500000')
        self.comboBox_2.addItem('2000000')
        self.comboBox_2.addItem('2500000')
        self.comboBox_2.addItem('3000000')
        self.comboBox_2.addItem('3500000')
        self.comboBox_2.addItem('4000000')

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

        self.lineEdit.textChanged.connect(lambda:self.line_edit_get(0))
        self.lineEdit_2cmd.textChanged.connect(lambda:self.line_edit_get(1))
        self.lineEdit_3cmd.textChanged.connect(lambda:self.line_edit_get(2))
        # listview
        self.slm = QStringListModel()
        self.qlist = []
        self.slm.setStringList(self.qlist)
        self.listView.setModel(self.slm)
        self.listView.clicked.connect(self.clicked_)

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

        #比较文件中的比较内容，然后发送对应的内容
        self.pushButton_sequence_cmd.clicked.connect(self.click_sequence)

        #波特率修改
        self.comboBox_2.activated.connect(self.baud_modify)

        #串口号修改
        self.comboBox.activated.connect(self.com_modify)

        #开始保存文件
        # checkBox_savefile
        self.checkBox_savefile.stateChanged.connect(self.save_file)

        if self.checkBox_savefile.checkState():
            self.save_file()

        self.click_sequence_flag = 0

        #开始自动滚屏
        self.checkBox_autoscroll.stateChanged.connect(self.auto_scroll_to_end)

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

        self.load_color_file_flag = False
        self.load_color_file()

    def click_sequence(self):
        try:
            if self.click_sequence_flag == 0:
                self.pushButton_sequence_cmd.setText("正在发送")
                self.click_sequence_flag = 1

                with open("sequence_config.yaml") as fd:
                    sequence_cmd_list = yaml.unsafe_load(fd)
                print(sequence_cmd_list)
                self.thread_sequence = Sequence_Cmd_Thread(dict_list=sequence_cmd_list,
                                                            pushButton_sequence_cmd=self.pushButton_sequence_cmd)
                self.thread_sequence.cmd_signal.connect(self.call_back)
                self.thread_sequence.start()
                print("run Sequence_Cmd_Thread 111111")


            elif self.click_sequence_flag == 1:
                self.pushButton_sequence_cmd.setText("顺序发送")
                self.click_sequence_flag = 0
                self.thread_sequence.exit()
                self.thread_sequence.terminate()

        except:
            pass

    def load_color_file(self):
        with open("color.yaml") as fd:
                self.color_str = yaml.unsafe_load(fd)
                self.load_color_file_flag = True
        # print("=======compare_config.yaml==============", time.strftime('%Y-%m-%d %H:%M:%S'))
        # print(self.cmp_str)
        # for command1 in self.cmp_str:
        #     print("compare command is :", command1['compare_str'])
        # self.cmp_str_flag = True

    def call_back(self, msg):
        print("call back msg:"+str(msg))
        self.send_bytes(str(msg))

    def clicked_(self, qModelIndex):
        global edit_flag
        text_str = str(self.list_text[qModelIndex.row()])
        # print("选择结果" + text_str)
        edit_num = edit_flag
        if edit_num == 0:
            self.lineEdit.setText(text_str)
        elif edit_num == 1:
            self.lineEdit_2cmd.setText(text_str)
        elif edit_num == 2:
            self.lineEdit_3cmd.setText(text_str)

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

    def auto_scroll_to_end(self):
        #获取到text光标
        textCursor = self.textbrowser.textCursor()
        #滚动到底部
        textCursor.movePosition(textCursor.End)
        #设置光标到text中去
        self.textbrowser.setTextCursor(textCursor)

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
            file_name_str = self.comboBox.currentText()
            # file_name = "%s_%s.log" %(self.comboBox.currentText(), file_head)
            file_name = "%s_%s.log" %(file_name_str.replace('/','_'), file_head)

            logfile_flag = 1
            if fp == "":
                fp = open(file_name, "w+", encoding="utf-8")
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
        if self.ser != None:
            plist = list(serial.tools.list_ports.comports())
            if len(plist) <= 0:
                #串口拔出错误，关闭定时器
                self.ser.close()
                self.ser = None
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
                            self.loop_send_timer.start(100)  # 100ms
                except expression as identifier:
                    pass
            else:
                if self.loop_send_timer.isActive() == True:
                        self.loop_send_timer.stop()  # 100ms

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

    # def send_sequence_cmd_box(self):
    #     if self.ser != None:
    #         print("click button")
    #         self.send_sequence_class.start()
    #         self.send_sequence_class.stop()
    #         pass
            # if self.checkBox_sequence_cmd.checkState():
            #     print("read sequence config")
            #     # try:
            #         # for command1 in sequence_cmd_list:
            #         # print("compare command is :", command1['command'])

            #     self.send_sequence_class.start()
            #     self.send_sequence_class.stop()
            #     # # 创建线程
            #     # cmd_thread = LoopThread_SendCmd(serial_num = self.ser, dic_str=sequence_cmd_list)
            #     # # 开始线程
            #     # cmd_thread.start()
            #     # cmd_thread.exit()
            #     self.checkBox_sequence_cmd.setCheckState(0)
            #         # cmd_thread.stop()
            #         # self.send_bytes(command1["command"])
            #         # time.sleep(5)
            #     # except expression as identifier:
            #     #     pass
            # else:
            #     print("do nothing, close fd")

    #清除窗口操作
    def clear(self):
        self.textbrowser.clear()
        self.send_num = 0
        self.receive_num = 0

    #获取输入数据
    def line_edit_get(self, edit_num):
        global edit_flag
        edit_flag = edit_num
        collection = []
        if edit_num == 0:
            # print("edit1: ", self.lineEdit.text())
            str_temp = self.lineEdit.text()
        elif edit_num == 1:
            # print("edit2: ", self.lineEdit_2cmd.text())
            str_temp = self.lineEdit_2cmd.text()
        elif edit_num == 2:
            # print("edit3: ", self.lineEdit_3cmd.text())
            str_temp = self.lineEdit_3cmd.text()
        try:
            with open(history_cmd_file_name) as fd:
                cmd_str = yaml.unsafe_load(fd)
            for command in cmd_str:
                # print("history command is :", command['cmd_str'])
                collection.append(command['cmd_str'])
            # print("collection type is", type(collection))
            # print( "collection data is :",collection)
            # print(list(fuzzyfinder_test(str_temp,collection)))
            self.list_text = list(fuzzyfinder_test(str_temp,collection))
            self.slm.setStringList(self.list_text)
            fd.close()
        except Exception as e:
            print("=====line_edit_get=====, error:%s" % (e))
            pass

    #串口发送数据处理
    def send(self, button_num):
        cmd_list = {}
        collection = []
        collection_tmp = []
        tmp_dict = {}
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
                    # print("input_s is ", input_s)
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
                # print(input_s)
                #发送数据
                try:
                    num = self.ser.write(input_s)
                    with open(history_cmd_file_name) as fd:
                        cmd_list = yaml.unsafe_load(fd)
                    fd.close()
                    for command in cmd_list:
                        collection.append(command['cmd_str'])
                        collection_tmp.append(command['cmd_str'])
                    collection_tmp.append(input_s.decode('utf-8').replace('\n', '').replace('\r', ''))
                    set_collection = list(set(collection_tmp))
                    if len(set_collection)==len(cmd_list):
                        print("存在重复的，不需要写入文件")
                    else:
                        print("有新增项")
                        tmp_dict['cmd_str']=input_s.decode('utf-8').replace('\n', '').replace('\r', '')
                        cmd_list.append(tmp_dict)
                        with open(history_cmd_file_name,"w",encoding="utf-8") as fd:
                            yaml.dump(cmd_list,fd)
                        fd.close()

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
        # #先把光标移到到最后
        # cursor = self.textbrowser.textCursor()
        # if(cursor != cursor.End):
        #     cursor.movePosition(cursor.End)
        #     self.textbrowser.setTextCursor(cursor)

        if self.checkBox_autoscroll.checkState():
            #获取到text光标
            textCursor = self.textbrowser.textCursor()
            #滚动到底部
            textCursor.movePosition(textCursor.End)
            #设置光标到text中去
            self.textbrowser.setTextCursor(textCursor)

        # #把字符串显示到窗口中去
        if self.load_color_file_flag == True:
            for command in self.color_str:
                # print("compare command is :", command['compare_str'])
                if log.find(command['compare_str']) >= 1:
                    # print("aaaaaaaaaaaaa", command['color'])
                    aaaa = Qt.GlobalColor(command['color'])
                    self.textbrowser.setTextColor(aaaa)
                    break
        else:
            if log.find("INFO: ") >= 1:
                self.textbrowser.setTextColor(Qt.GlobalColor.blue)
            elif log.find("DEBUG:") >= 1:
                self.textbrowser.setTextColor(Qt.GlobalColor.black)
            elif log.find("=>ERROR:") >= 1:
                self.textbrowser.setTextColor(Qt.GlobalColor.red)
            elif log.find("WARNNING:") >= 1:
                self.textbrowser.setTextColor(Qt.GlobalColor.darkYellow)

        # print("Qt.GlobalColor.blue", Qt.GlobalColor.blue)
        # print("type Qt.GlobalColor.blue", type(Qt.GlobalColor.blue))
        # aaaa = Qt.GlobalColor(command['color'])

        # if log.find("INFO: ") >= 1:
        #     self.textbrowser.setTextColor(aaaa)
        # elif log.find("DEBUG:") >= 1:
        #     self.textbrowser.setTextColor(Qt.GlobalColor.black)
        # elif log.find("=>ERROR:") >= 1:
        #     self.textbrowser.setTextColor(Qt.GlobalColor.red)
        # elif log.find("WARNNING:") >= 1:
        #     self.textbrowser.setTextColor(Qt.GlobalColor.darkYellow)

        # self.textbrowser.insertPlainText(log)
        self.textbrowser.append(log)
        self.textbrowser.setTextColor(Qt.GlobalColor.black)

        if self.checkBox_autoscroll.checkState():
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
        # #获取到text光标
        # textCursor = self.textbrowser.textCursor()
        # #滚动到底部
        # textCursor.movePosition(textCursor.End)
        # #设置光标到text中去
        # self.textbrowser.setTextCursor(textCursor)

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
                # self.ser = serial.Serial(self.comboBox.currentText(), int(self.comboBox_2.currentText()), timeout=0.1)
                self.ser = serial.Serial(self.comboBox.currentText(), int(self.comboBox_2.currentText()), timeout=1)
                self.miniterm = Miniterm(serial_instance=self.ser)
            except Exception as e:
                print("============, error:%s" % (e))
                QMessageBox.critical(self, 'pycom','没有可用的串口或当前串口被占用')
                return None
            #字符间隔超时时间设置
            # self.ser.interCharTimeout = 0.001
            self.ser.interCharTimeout = 0.1
            #1ms的测试周期
            self.miniterm.start()
            self.loop_start()
            # self.timer.start(1)
            self.pushButton_2.setText("关闭串口")
            print('open')
        else:
            #关闭定时器，停止读取接收数据
            if self.loop_send_timer.isActive() == True:
                self.loop_send_timer.stop()
            self.loop_stop()
            self.miniterm.stop()
            try:
                #关闭串口
                self.ser.close()
            except:
                # QMessageBox.critical(self, 'pycom','关闭串口失败')
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
                        # time.sleep(0.1)
        self.intervalseconds = self.intervalseconds + 1
        self.sendcount = self.sendcount + 1

# 删除list字典的重复项
def deleteDuplicate(li):
    new_l = []
    seen = set()
    for d in li:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)
        else:
            print("duplicate is:",d)
    return new_l

if __name__ == "__main__":
    try:
        # cgitb.enable(format='text')
        print("*** start at %s ***" % (time.ctime(time.time())))
        queue_buf = queue.Queue(maxsize=1048576)

        with open(history_cmd_file_name) as fd:
            cmd_str = yaml.unsafe_load(fd)
        fd.close()

        cmd_temp = deleteDuplicate(cmd_str)
        with open(history_cmd_file_name,"w",encoding="utf-8") as fd:
            yaml.dump(cmd_temp,fd)
        fd.close()

        app = QtWidgets.QApplication(sys.argv)
        g_mainWindow = MainWindow()
        g_mainWindow.show()
        sys.exit(app.exec_())
    except Exception as exp:
        print("============, error:%s" % (exp))
        with open("crash_log.txt","w",encoding="utf-8") as fd:
            fd.write( exp )
        fd.close()
    finally:
        print("*** end at %s ***" % (time.ctime(time.time())))
