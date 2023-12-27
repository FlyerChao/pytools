# RO_CODE（Read-Only Code）：这是单片机的程序代码区域，通常包含不可修改的二进制代码。
# RO_CODE区域主要用于存储程序指令，包括各种函数、子程序等。
# 这些指令在单片机出厂时已经固化在RO_CODE区域中，用户无法修改。

# RO_DATA（Read-Only Data）：这是单片机的只读数据存储器区域。
# 它通常用于存储一些不可修改的常量或固件数据，例如预设的标志位、固定的表项数据等。
# 这些数据一般在单片机出厂时已经预先写入，用户无法修改。
# 1）只读全局变量
# 定义全局变量const char a[100]=”abcdefg”将生成大小为100个字节的只读数据区，并使用字符串“abcdefg”初始化。如果定义为const char a[]=”abcdefg”,没有指定大小，将根据“abcdefgh”字串的长度，生成8个字节的只读数据段。
# 2）只读局部变量
# 例如：在函数内部定义的变量const char b[100]=”9876543210”;其初始化的过程和全局变量。
# 3）程序中使用的常量
# 例如：在程序中使用printf("information\n”),其中包含了字串常量，编译器会自动把常量“information \n”放入只读数据区。

# RW_DATA（Read-Write Data）：这是单片机的可读可写数据存储器区域。
# 它通常用于存储用户可以读取和修改的数据，例如变量的值、状态信息等。
# RW_DATA区域可以根据用户的需要随时进行读写操作。
# 1）已初始化全局变量
# 例如：在函数外部，定义全局的变量char a[100]=”abcdefg”
# 2）已初始化局部静态变量
# 例如：在函数中定义static char b[100]=”9876543210”。函数中由static定义并且已经初始化的数据和数组将被编译为读写数据段。
# 说明：
# 读写数据区的特点是必须在程序中经过初始化，如果只有定义，没有初始值，则不会生成读写数据区，而会定义为未初始化数据区(BSS)。
# 如果全局变量（函数外部定义的变量）加入static修饰符，写成static char a[100]的形式，这表示只能在文件内部使用，而不能被其他文件使用。

# RO-data：它指程序中用到的只读数据，因而程序不能被修改的内容，这些数据被存储在ROM区。 RO-data区典型：
# 例1、C语言中const关键字定义的变量。
# 例2、C语言中定义的全局常量。
# 例3、C语言中定义的字符串。

# RW-data：即可读写数据区域，一定是初始化为“非0值”的可读写数据，而且应用程序可以修改其内容，这些数据被存储在RAM区
# RW-data区典型：
# 例1、C语言中定义的全局变量，且初始化为“非0值”。
# 例2、C语言中定义的静态变量。且初始化为“非0值”。

# import json
import re
import time
# import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
# import numpy as np
# import os
# import threading
from datetime import datetime
import tkinter as tk
import sys
import inspect

g_analyze_flag = -1

start_time = time.time()

# skip_tap_count = 0
skip_tap_list = []
g_draw_path_str = ''
# 全局绘图的对象
g_fig= None
g_ax = None
g_click_flag = False

# 全局的退出的标记
g_exit_flag = False

## 画弹出提示框的window的对象
g_window_root = None

def popup_window():
    global g_window_root
    global g_fig
    global g_exit_flag

    g_exit_flag = False

    g_window_root.destroy()
    plt.close(g_fig)
    print("Function name:", inspect.currentframe().f_code.co_name,", Line number:", inspect.currentframe().f_lineno)
    g_exit_flag = True


def draw_button_msg(input_text='输入要显示的字符'):
    global g_window_root

    g_window_root = tk.Tk()
    g_window_root.title("主窗口")
    popup_button = tk.Button(g_window_root, text=input_text, command=popup_window, background='#cc1111')
    popup_button.pack()
    g_window_root.mainloop()


class Node():
    # def __init__(self, deep_path = '.', ro_code = 0, ro_data = 0, rw_data = 0, children=None, parent = None):
    def __init__(self, deep_path = '.', parent_node = None, children = None, ro_code = 0, ro_data = 0, rw_data = 0):
        self.deep_path = deep_path
        self.ro_code = ro_code
        self.ro_data = ro_data
        self.rw_data = rw_data
        self.sum = 0
        self.parent_node = parent_node
        self.l_children = children or []
        # self.parent = parent
    def add_children(self, node):
        self.l_children.append(node)
    def update_node_data(self, ro_code =0, ro_data = 0, rw_data = 0):
        self.ro_code = ro_code
        self.ro_data = ro_data
        self.rw_data = rw_data
        self.sum = ro_code + ro_data + rw_data

scr=Node(deep_path="root", ro_code=0,ro_data=0,rw_data=0)

# scr1=Node(deep_path="scr1", parent_node=scr, ro_code=1,ro_data=1,rw_data=1)
# scr2=Node(deep_path="scr2", parent_node=scr, ro_code=2,ro_data=2,rw_data=2)
# scr3=Node(deep_path="scr3", parent_node=scr, ro_code=3,ro_data=3,rw_data=3)

# scr11=Node(deep_path="scr11", parent_node=scr1, ro_code=11,ro_data=11,rw_data=11)
# scr12=Node(deep_path="scr12", parent_node=scr1, ro_code=12,ro_data=12,rw_data=12)
# scr13=Node(deep_path="scr13", parent_node=scr2, ro_code=13,ro_data=13,rw_data=13)
# scr14=Node(deep_path="scr14", parent_node=scr2, ro_code=14,ro_data=14,rw_data=14)
# scr1.add_children(scr11)
# scr1.add_children(scr12)
# # scr1.add_children(scr13)
# # scr1.add_children(scr14)
# scr2.add_children(scr13)
# scr2.add_children(scr14)

# scr21=Node(deep_path="scr21", parent_node=scr11, ro_code=21,ro_data=21,rw_data=21)
# scr22=Node(deep_path="scr22", parent_node=scr13, ro_code=22,ro_data=22,rw_data=22)
# scr11.add_children(scr21)
# scr13.add_children(scr22)

# scr31=Node(deep_path="scr31", parent_node=scr11, ro_code=31,ro_data=31,rw_data=31)
# scr32=Node(deep_path="scr32", parent_node=scr22, ro_code=32,ro_data=32,rw_data=32)
# scr11.add_children(scr31)
# scr22.add_children(scr32)

# input_dict = {
#     "deep1": [ scr1, scr2, scr3],
#     "deep2": [scr11, scr12, scr13, scr14]
# }

module_summary_dict = {}

# new_dict = {"deep3": [scr21, scr22]}

# input_dict.update(new_dict)
# input_dict["deep3"].append(scr11)
# print(input_dict.keys())

# print(len(input_dict["scr1"]))
# print(input_dict["scr1"][0].deep_path)

# for current_node in input_dict["src2"]:
#     print(current_node.deep_path)
parents_count = 0

# 获取由多少个父节点
def get_how_many_parents(current_node):
    global parents_count

    if current_node.parent_node != None:
        parents_count = parents_count + 1
        get_how_many_parents(current_node.parent_node)
    return parents_count

# parents_count = 0
# print("scr31 has ", get_how_many_parents(scr31) - 1, " parents")
# parents_count = 0
# print("scr32 has ", get_how_many_parents(scr32) - 1, " parents")

# 打印节点内容，包含子node
def print_node(current_node):
    global parents_count

    skip_tap_count = 0
    parents_count = 0
    skip_tap_count = get_how_many_parents(current_node) - 1

    for j in range(skip_tap_count):
        print("\t",end="")
    print("{")

    for j in range(skip_tap_count):
        print("\t",end="")
    print(f"    {current_node.deep_path}: {current_node.ro_code}, {current_node.ro_data}, {current_node.rw_data}")

    for j in range(skip_tap_count):
        print("\t",end="")
    print("}")

    if len(current_node.l_children) != 0:
        skip_tap_count = skip_tap_count + 1
        skip_tap_list.append(skip_tap_count)
        # print("skip_tap_count is ", skip_tap_count)
        for next_node in current_node.l_children:
            print_node(next_node)
    else:
        # print("-------------> no child")
        if len(skip_tap_list) != 0:
            skip_tap_count = skip_tap_list.pop()

# 因为是树状结构，所以只是从第一级开始展示即可
def print_dict_tree(dictionary):
    for current_node in dictionary["deep1"]:
        print_node(current_node)

# def pretty_print_dict(dictionary):
#     i = 0
#     for current_key in dictionary.keys():
#         print(current_key)
#         for current_node in dictionary[current_key]:
#                 # print("find the node in deep:", current_node.deep_path)
#                 for j in range(i):
#                     print("\t",end="")
#                 print("{")
#                 for j in range(i):
#                     print("\t",end="")
#                 print(f"    {current_node.deep_path}: {current_node.ro_code}, {current_node.ro_data}, {current_node.rw_data}")
#                 for j in range(i):
#                     print("\t",end="")
#                 print("}")
#         i = i+1


# pretty_print_dict(input_dict)
#
def find_node_in_parents_node(parent_node, child_node):
    for node in parent_node.l_children:
        if node.deep_path == child_node.deep_path:
            return node
    return None

# 匹配node在节点中存在于哪个字典中
def find_node_in_dict(current_dict, new_node):
    for current_key in current_dict.keys():
        for current_node in current_dict[current_key]:
            if new_node.deep_path == current_node.deep_path:
                print("find the node in deep:", current_node.deep_path)
                return current_node
    print("don't find the node")
    return None

# 根据deep的key来查找node的path是否存在
# 存在返回1，不存在返回0
def find_node_base_deep(current_dict, deep_key, check_node):
    if len(current_dict) != 0:
        for current_node in current_dict[deep_key]:
            if check_node.deep_path == current_node.deep_path:
                # print("find the node {check_node.path} in {deep_key}")
                return current_node
    return None

def update_node_dict_by_deep(current_dict, deep_key, new_node):
    if deep_key in current_dict.keys():
        current_dict[deep_key].append(new_node)
    else:
        new_dict = {deep_key: [new_node]}
        current_dict.update(new_dict)


# test_path1 = "a\\b\\c\\d\\e\\f"
# test_path2 = "a\\b\\g\\h"
# test_path3 = "i\\g\\h"

# path_list = test_path1.split('\\')

# print(path_list)
last_node = None
def parse_path_update_dict(path_list, dictionary):
    global last_node
    need_update = 0
    i = 1
    for name in path_list:
        # print(i, name)
        deep_key="deep"+str(i)
        if i == 1:
            node = Node(deep_path=name, parent_node=scr, ro_code=0, ro_data=0, rw_data=0)
            # check_node in deep1, fetch the node in deep1
            if find_node_base_deep(dictionary, "deep1", node) == None:
                # print("need update 1111 ")
                need_update = 1
            else:
                node = find_node_base_deep(dictionary, "deep1", node)
        else:
            node = Node(deep_path=name, parent_node=last_node, ro_code=0, ro_data=0, rw_data=0)
            if find_node_in_parents_node(last_node, node) == None:
                last_node.l_children.append(node)
                need_update = 1
            else:
                node = find_node_in_parents_node(last_node, node)
                need_update = 0
                # print("need update 222 ")
        last_node = node
        if need_update == 1:
            update_node_dict_by_deep(dictionary, deep_key,node)
        i = i+1
        need_update = 0

def parse_path_get_node(full_path_name, dictionary):
    i = 0

    path_line = full_path_name.strip('\n').replace(":","").replace(" ","")
    path_line = path_line.strip('\\')
    path_line = re.sub(r'\[.*?\]', '', path_line)
    path_list = path_line.split('\\')

    # print("parse_path_get_node: ", path_list)

    for name in path_list:
        # print(i, name)
        deep_key="deep"+str(i)
        if i == 0:
            node = Node(deep_path=name, parent_node=scr, ro_code=0, ro_data=0, rw_data=0)
            # check_node in deep1, fetch the node in deep1
            if find_node_base_deep(dictionary, "deep1", node) == None:
                return None
            else:
                node = find_node_base_deep(dictionary, "deep1", node)
        else:
            node = Node(deep_path=name, parent_node=last_node, ro_code=0, ro_data=0, rw_data=0)
            if find_node_in_parents_node(last_node, node) == None:
                return None
            else:
                node = find_node_in_parents_node(last_node, node)
        last_node = node
        i = i+1
    # print("i is ", i, "len(path_list) is ", len(path_list))

    if i > len(path_list):
        return None

    if len(last_node.l_children) != 0:
        # print("last_node's name: ", last_node.deep_path)
        return last_node
    else:
        return None

# parse_path_update_dict(test_path1.split('\\'), input_dict)
# parse_path_update_dict(test_path2.split('\\'), input_dict)
# parse_path_update_dict(test_path3.split('\\'), input_dict)

# print_dict_tree(input_dict)

def string2int(s):
    if s.strip() == "":
        return 0
    else:
        return int(s)

def ergodic_file(file_name="module_summary_new.txt"):
    global g_analyze_flag

    with open(file_name, 'r') as module_summ_file:
        for line in module_summ_file:
            if "\\Obj\\" in line:
                floder_list = line.split("\\Obj\\")
                path_line = floder_list[1].strip('\n').replace(":","").replace(" ","")
                path_line = re.sub(r'\[.*?\]', '', path_line)
                # print(path_line)
                # parse_path_update_dict(floder_list[1].strip('\n').split('\\'), module_summary_dict)
                parse_path_update_dict(path_line.split('\\'), module_summary_dict)

            if "    Total: " in line:
                #针对MG12的文件的分析截取
                if g_analyze_flag == 1:
                    ro_code = line[37:45].strip(' ').strip("'").strip("\r").strip("\n").replace("'","")
                    ro_data = line[46:54].strip(' ').strip("'").strip("\r").strip("\n").replace("'","")
                    rw_data = line[55:64].strip(' ').strip("'").strip("\r").strip("\n").replace("'","")

                #针对MG24的文件的分析截取
                if g_analyze_flag == 2:
                    ro_code = line[37:45].strip(' ').strip("'").strip("\r").strip("\n").replace("'","")
                    ro_data = line[57:63].strip(' ').strip("'").strip("\r").strip("\n").replace("'","")
                    rw_data = line[64:72].strip(' ').strip("'").strip("\r").strip("\n").replace("'","")

                ro_code = string2int(ro_code)
                ro_data = string2int(ro_data)
                rw_data = string2int(rw_data)
                if last_node != None:
                    last_node.update_node_data(ro_code=ro_code,ro_data=ro_data, rw_data=rw_data)
                # print("ro_code: ",ro_code,"\tro_data: ", ro_data,"\trw_data: ", rw_data)

g_ro_code = 0
g_ro_data = 0
g_rw_data = 0

def update_node_data(current_node):
    global g_ro_code
    global g_ro_data
    global g_rw_data

    if len(current_node.l_children) != 0:
        for next_node in current_node.l_children:
            # print(current_node.deep_path, g_ro_code, g_ro_data, g_rw_data)
            g_ro_code = g_ro_code + next_node.ro_code
            g_ro_data = g_ro_data + next_node.ro_data
            g_rw_data = g_rw_data + next_node.rw_data
            update_node_data(next_node)
    else:
        # if current_node.ro_code != 0 or current_node.ro_data != 0 or current_node.rw_data != 0:
        if g_ro_code == 0 and g_ro_data == 0 and g_rw_data == 0:
            g_ro_code = g_ro_code + current_node.ro_code
            g_ro_data = g_ro_data + current_node.ro_data
            g_rw_data = g_rw_data + current_node.rw_data

def update_all_data(dictionary):
    global g_ro_code
    global g_ro_data
    global g_rw_data

    for key in dictionary.keys():
        for current_node in dictionary[key]:
            g_ro_code = 0
            g_ro_data = 0
            g_rw_data = 0
            update_node_data(current_node)
            current_node.update_node_data( ro_code=g_ro_code, ro_data=g_ro_data, rw_data=g_rw_data)

# print_dict_tree(module_summary_dict)

cust_labels = ['ro_code', 'ro_data', 'rw_data']
color_list = ['#aa5522', '#11aa55', '#5555cc']
# cust_paths_list = []

# print("-------------------------------------")
# print("name \t\t\t ro_code \t\t r0_data \t\t rw_data")
# for current_node in module_summary_dict["deep1"]:
#     print(current_node.deep_path,'\t\t\t', current_node.ro_code, '\t',current_node.ro_data, '\t',current_node.rw_data, '\t',current_node.sum)
#     cust_paths_list.append(current_node.deep_path)
# print("-------------------------------------")

def draw_deep_bar(cust_deep='deep1'):
    i = 0
    global g_fig
    global g_ax
    global cust_labels
    global g_exit_flag
    # global cust_paths_list
    cust_paths_list = []

    global color_list
    global module_summary_dict
    global g_draw_path_str

    g_exit_flag = False

    if cust_deep == "deep1":
        g_draw_path_str = '\\'
    #     print("g_draw_path_str 11 is ", g_draw_path_str)
    # else:
    #     print("---------------------")

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体设置-黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

    fig, ax = plt.subplots()

    g_fig = fig
    g_ax = ax

    # print("-------------------------------------")
    # print("name \t\t\t ro_code \t\t r0_data \t\t rw_data")
    for current_node in module_summary_dict[cust_deep]:
        # print(current_node.deep_path,'\t\t\t', current_node.ro_code, '\t',current_node.ro_data, '\t',current_node.rw_data, '\t',current_node.sum)
        cust_paths_list.append(current_node.deep_path)
        if i == 0:
            ax.bar(i, current_node.ro_code, 0.3, bottom=0, facecolor= color_list[0], align='edge',label=cust_labels[0])
            plt.text(i,current_node.ro_code/2,str(current_node.ro_code),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.ro_data, 0.3, bottom=current_node.ro_code, facecolor= color_list[1], align='edge',label=cust_labels[1])
            plt.text(i,current_node.ro_code+current_node.ro_data/2,str(current_node.ro_data),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.rw_data, 0.3, bottom=(current_node.ro_code+current_node.ro_data), facecolor= color_list[2], align='edge',label=cust_labels[2])
            plt.text(i,current_node.ro_code+current_node.ro_data+current_node.rw_data/2,str(current_node.rw_data),fontsize=9,verticalalignment='center')
            i = i + 1
        else:
            ax.bar(i, current_node.ro_code, 0.3, bottom=0, facecolor= color_list[0], align='edge')
            plt.text(i,current_node.ro_code/2,str(current_node.ro_code),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.ro_data, 0.3, bottom=current_node.ro_code, facecolor= color_list[1], align='edge')
            plt.text(i,current_node.ro_code+current_node.ro_data/2,str(current_node.ro_data),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.rw_data, 0.3, bottom=(current_node.ro_code+current_node.ro_data), facecolor= color_list[2], align='edge')
            plt.text(i,current_node.ro_code+current_node.ro_data+current_node.rw_data/2,str(current_node.rw_data),fontsize=9,verticalalignment='center')
            i = i + 1
    # print("-------------------------------------")

    plt.xticks(range(len(cust_paths_list)),cust_paths_list)
    # ax.set_ylabel('Y轴标题/个')
    # ax.set_xlabel('X轴标题/个')

    plt.title("当前目录的分区")
    plt.legend()	#打开图例
    # plt.grid(True)	#打开网格

    bswitch_list = []
    for i in range(len(cust_paths_list)):
        # print("i is ", i)
        axswitch = fig.add_axes([(i+1)/((len(cust_paths_list)) +1), 0.01, 0.01, 0.05])
        bswitch = Button(axswitch, cust_paths_list[i])
        bswitch_list.append(bswitch)

    i = 0
    for bt_switch in bswitch_list:
        input_path = str(cust_paths_list[i])
        # print("----> i is ", i, "text is :", input_path)
        # bt_switch.on_clicked(lambda x: fn_click(x, text=bt_switch.label._text))
        bt_switch.on_clicked(lambda x, y=input_path: fn_click(x, y))
        i = i + 1

    #保存图片
    # fig.tight_layout()
    # plt.savefig("测试数据.png",dpi=300)
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.show()
    print("Function name:", inspect.currentframe().f_code.co_name,"Line number:", inspect.currentframe().f_lineno)
    plt.close(g_fig)
    g_exit_flag = True

def fn_click(event, text=''):
    global g_draw_path_str
    global g_fig
    global g_ax
    global g_click_flag
    global g_exit_flag

    # print("input text is ", text)
    # print(event.name, event.button)

    ## 检查输入的路径是否还有子节点，如果存在继续执行，否则返回，不关闭当前的图像
    g_exit_flag = False

    if len(g_draw_path_str) != 0:
        g_draw_path_str = g_draw_path_str + text + '\\'
        # print("g_draw_path_str+text is ", g_draw_path_str)
    # else:
        # print("xxxxxx g_draw_path_str is ", g_draw_path_str)

    if '上一级' in g_draw_path_str:
        g_draw_path_str = g_draw_path_str.replace("上一级\\","")
        g_draw_path_str = g_draw_path_str.strip('\\')
        split_temp_list = g_draw_path_str.split('\\')
        # print("split_temp_list is : ", split_temp_list)
        if len(split_temp_list) > 1:
            g_draw_path_str = ''
            i = 0
            for temp_str in split_temp_list:
                if i == len(split_temp_list) -1:
                    break
                g_draw_path_str = g_draw_path_str + temp_str + '\\'
                i = i + 1
            print("new g_draw_path_str is ", g_draw_path_str)
        else:
            g_draw_path_str='Obj'
            print("new g_draw_path_str is ", g_draw_path_str)

    if g_draw_path_str != 'Obj':
        if None == parse_path_get_node(g_draw_path_str, module_summary_dict):
            draw_button_msg("不存在子目录了，请重新运行代码")
            # g_exit_flag = True
            return
    plt.close(g_fig)
    print("Function name:", inspect.currentframe().f_code.co_name,", Line number:", inspect.currentframe().f_lineno)

    # time.sleep(10)
    g_click_flag = True
    # draw_by_path(g_draw_path_str)
    # g_event.set()

def draw_by_path(draw_path=None):
    i = 0
    global cust_labels
    # global cust_paths_list
    cust_paths_list = []

    global color_list
    global module_summary_dict
    global g_draw_path_str
    global g_fig
    global g_ax
    global g_exit_flag

    g_exit_flag = False

    if draw_path == "Obj":
        draw_deep_bar('deep1')
        return

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体设置-黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

    fig, ax = plt.subplots()

    g_fig = fig
    g_ax = ax

    if draw_path == None:
        print("请输入正确的路径，已obj之后的目录开始")
        return

    print("将要展示的是", draw_path, "的内容")
    if len(g_draw_path_str) == 0:
        g_draw_path_str = g_draw_path_str + draw_path + '\\'
        print("g_draw_path_str is ", g_draw_path_str)
    # draw_path = g_draw_path_str

    path_line = draw_path.strip('\n').replace(":","").replace(" ","")
    path_line = path_line.strip('\\')
    path_line = re.sub(r'\[.*?\]', '', path_line)
    path_list = path_line.split('\\')
    # print(path_list)

    for i in range(len(path_list)):
        if i == 0:
            node = Node(deep_path=path_list[0], parent_node=scr, ro_code=0, ro_data=0, rw_data=0)
            if find_node_base_deep(module_summary_dict, "deep1", node) == None:
                print("无法找到对应的正确路径")
                print("请输入正确的路径，已obj之后的目录开始")
                return
            else:
                parent_node = find_node_base_deep(module_summary_dict, "deep1", node)
        else:
            node = Node(deep_path=path_list[i], parent_node=parent_node, ro_code=0, ro_data=0, rw_data=0)
            parent_node = find_node_in_parents_node(parent_node, node)

    if len(parent_node.l_children) == 0:
        print("不存在子节点，需要打印当前的数据")

    # print("-------------------------------------")
    # print("name \t\t\t ro_code \t\t r0_data \t\t rw_data")
    i = 0
    for current_node in parent_node.l_children:
        # print(current_node.deep_path,'\t\t\t', current_node.ro_code, '\t',current_node.ro_data, '\t',current_node.rw_data, '\t',current_node.sum)
        cust_paths_list.append(current_node.deep_path)

        if i == 0:
            ax.bar(i, current_node.ro_code, 0.3, bottom=0, facecolor= color_list[0], align='edge',label=cust_labels[0])
            plt.text(i,current_node.ro_code/2,str(current_node.ro_code),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.ro_data, 0.3, bottom=current_node.ro_code, facecolor= color_list[1], align='edge',label=cust_labels[1])
            plt.text(i,current_node.ro_code+current_node.ro_data/2,str(current_node.ro_data),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.rw_data, 0.3, bottom=(current_node.ro_code+current_node.ro_data), facecolor= color_list[2], align='edge',label=cust_labels[2])
            plt.text(i,current_node.ro_code+current_node.ro_data+current_node.rw_data/2,str(current_node.rw_data),fontsize=9,verticalalignment='center')
            i = i + 1
        else:
            ax.bar(i, current_node.ro_code, 0.3, bottom=0, facecolor= color_list[0], align='edge')
            plt.text(i,current_node.ro_code/2,str(current_node.ro_code),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.ro_data, 0.3, bottom=current_node.ro_code, facecolor= color_list[1], align='edge')
            plt.text(i,current_node.ro_code+current_node.ro_data/2,str(current_node.ro_data),fontsize=9,verticalalignment='center')
            ax.bar(i, current_node.rw_data, 0.3, bottom=(current_node.ro_code+current_node.ro_data), facecolor= color_list[2], align='edge')
            plt.text(i,current_node.ro_code+current_node.ro_data+current_node.rw_data/2,str(current_node.rw_data),fontsize=9,verticalalignment='center')
            i = i + 1

    # print("-------------------------------------",cust_paths_list)

    plt.xticks(range(len(cust_paths_list)),cust_paths_list)
    # ax.set_ylabel('Y轴标题/个')
    # ax.set_xlabel('X轴标题/个')

    title_str = "目录"+ draw_path+"的分区"
    plt.title(title_str)
    plt.legend()	#打开图例
    # plt.grid(True)	#打开网格

    # loc, lables_list = plt.xticks()
    # print(type(loc[0]), type(lables_list[0]))

    bswitch_list = []

    axswitch = fig.add_axes([0.08, 0.89, 0.09, 0.05])
    bswitch = Button(axswitch, "上一级")
    bswitch_list.append(bswitch)

    for i in range(len(cust_paths_list)):
        # print("cust_paths_list i is ", i)
        axswitch = fig.add_axes([(i+1)/((len(cust_paths_list)) +1), 0.01, 0.01, 0.05])
        bswitch = Button(axswitch, cust_paths_list[i])
        bswitch_list.append(bswitch)

    i = 0
    for bt_switch in bswitch_list:
        # print("bt_switch i is ", i)
        if i == 0:
            input_path = "上一级"
            # bswitch.on_clicked(lambda x, y="上一级": fn_click(x, y))
        else:
            input_path = str(cust_paths_list[i-1])
            # print("----> i is ", i, "text is :", input_path)
            # bt_switch.on_clicked(lambda x: fn_click(x, text=bt_switch.label._text))
        bt_switch.on_clicked(lambda x, y=input_path: fn_click(x, y))
        i = i + 1

    #保存图片
    # fig.tight_layout()
    # plt.savefig("测试数据.png",dpi=300)
    # print(plt.get_backend())
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.show()
    print("Function name:", inspect.currentframe().f_code.co_name,", Line number:", inspect.currentframe().f_lineno)
    plt.close(g_fig)
    # g_exit_flag = True

# draw_deep_bar('deep1')

SPLIT_MATCH_LINE = '*******************************************************************************'
SPLIT_FILE_NAME = ["RUNTIME.txt","HEAP_SELECTION.txt",
                   "PLACEMENT_SUMMARY.txt","INIT_TABLE.txt",
                   "MODULE_SUMMARY.txt","ENTRY_LIST.txt"]

SPLIT_MATCH_MODULE_LIST = [":\\Users\\", "Total: "]
SPLIT_MATCH_NEW_FILE = ["module_summary_new.txt"]

# LIST_SPLIT_FILE_NAME = list(SPLIT_FILE_NAME)
def split_file(file_name, split_mat_line, split_file_new_name):
    start_wr_flag = 0
    i = 0
    fd_w = 0
    # 打开原始文件和目标文件
    with open(file_name, 'r') as source_file:
        # 按行读取原始文件
        # open('target.txt', 'w') as target_file
        for line in source_file:
            # 如果该行以默认匹配字符串开始
            if line.startswith(split_mat_line):
                start_wr_flag = 1
                if fd_w != 0: #有文件已经打开
                    fd_w.close()
                    fd_w = 0
                    i = i + 1
                if fd_w == 0:
                    # local_name = SPLIT_FILE_NAME[int(i)]
                    # fd_w = open(LIST_SPLIT_FILE_NAME[i],'w')
                    fd_w = open(split_file_new_name[i],'w')

            if start_wr_flag == 1:
                # 将该行写入目标文件
                fd_w.write(line)
    fd_w.close()

def split_file_aa(file_name, split_match_line, split_file_new_name):
    start_wr_flag = 0
    i = 0
    match_word_start_flag = 0
    # last_match_word_flag = 0
    fd_w = 0
    # 打开原始文件和目标文件
    with open(file_name, 'r') as source_file:
        # 按行读取原始文件
        # open('target.txt', 'w') as target_file
        for line in source_file:
            # 如果该行以默认匹配字符串开始
            for match_word in split_match_line:
                if match_word in line:
                    if match_word == split_match_line[0]:
                        match_word_start_flag = 1

                    if match_word_start_flag == 1:
                        start_wr_flag = 1
                    # if fd_w != 0: #有文件已经打开
                    #     fd_w.close()
                    #     fd_w = 0
                    #     i = i + 1
                    if fd_w == 0:
                        # local_name = SPLIT_FILE_NAME[int(i)]
                        # fd_w = open(LIST_SPLIT_FILE_NAME[i],'w')
                        fd_w = open(split_file_new_name[i],'w')
                # else:
                #     start_wr_flag = 0
                    if start_wr_flag == 1:
                        # 将该行写入目标文件
                        # fd_w.write(line.replace('\'',''))
                        fd_w.write(line)

                    if match_word == split_match_line[-1]:
                        # print(match_word, line)
                        match_word_start_flag = 0
                        start_wr_flag = 0
    fd_w.close()

def check_input_arg(argv):
    if len(argv) > 1:
        if argv[1] == 'mg12':
            return 1
        if argv[1] == 'mg24':
            return 2

    print("请输入正确的参数:mg12 或者 mg24")
    return -1

if __name__ == "__main__":
    exit_count = 0

    g_analyze_flag = check_input_arg(sys.argv)
    if g_analyze_flag < 0:
        quit()

    split_file('Newolc.map', SPLIT_MATCH_LINE, SPLIT_FILE_NAME)
    split_file_aa(SPLIT_FILE_NAME[4], SPLIT_MATCH_MODULE_LIST, SPLIT_MATCH_NEW_FILE)

    ergodic_file()
    update_all_data(module_summary_dict)

    #绘制开始的图像
    draw_by_path('Obj')

    while True:
        if g_click_flag == True:
            g_click_flag = False
            # 获取当前时间
            now = datetime.now()
            # 打印当前时间（只有日期和时间）
            print("当前时间为：", now.strftime("%Y-%m-%d %H:%M:%S"))
            draw_by_path(g_draw_path_str)
        time.sleep(0.01)
        if g_exit_flag == True:
            if exit_count > 2:
                break
            exit_count = exit_count + 1
        else:
            exit_count = 0

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"程序执行时间: {execution_time}秒")

