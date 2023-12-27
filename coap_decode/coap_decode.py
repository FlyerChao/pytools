import fileinput
import os
import string

# 1.Read file by each line
# 2.Find key word "coap receive dump" to find coap data
# 3.Find 1st keyword "=========== " to find pre line to real data
# 4.Find 2rd keyword "=========== "
FIRST_STR = "coap receive"
SECOND_STR = "================"
THIRD_STR = " ]:"
TEMP_FILE_NAME = "temp.txt"

MESSAGE_TYPES = ["Confirmable", "NON-confirmable", "ACKnowledgement", "Reset"]
RESPONSE_CLASSES = ["Request", "class1", "CLASS2", "class3", "CLASS4", "CLASS5"]

CLASS0_DES = ["EMPTY", "GET", "POST", "PUT", "DELETE"]
CLASS2_DES = ["Created", "Deleted", "Valid", "Changed", "Content", "Continue"]
CLASS4_DES = ["Bad Request", "Unauthorized", "Bad Option", "Forbidden", "Not Found",
                "Method Not Allowed", "Not Acceptable", "", "Request Entity Incomplete",
                "", "", "", "Precondition Failed", "Request Entity Too Large", "",
                "Unsupported Content-Format"]
CLASS5_DES = ["Internal Server Error", "Not Implemented", "Bad Gateway", "Service Unavailable",
                "Gateway timeout", "Proxying Not supported"]

# OPTION_NAMES = ["", "If-Match", "", "Uri-Host", "ETag", "If-None-Match", "", "Uri-Port",
#                 "Location-Path", "", "", "", "Content-Format", "", "Max-Age",
#                 "Uri-Query", "", "Accept"]
OPTION_NAMES = {}
CONTENT_FORMATS = []

def init_option_names():
    OPTION_NAMES[1] = "If-Match"
    OPTION_NAMES[3] = "Uri-Host"
    OPTION_NAMES[11] = "Uri-Path"
    OPTION_NAMES[23] = "Block2"
    OPTION_NAMES[27] = "Block1"
    # OPTION_NAMES.insert(20, "Location-Query")
    # OPTION_NAMES.insert(23, "")
    # OPTION_NAMES.insert(27, "")
    # OPTION_NAMES.insert(28, "Size2")
    # OPTION_NAMES.insert(35, "Proxy-Uri")
    # OPTION_NAMES.insert(39, "Proxy-Scheme")
    # OPTION_NAMES.insert(60, "Size1")

def init_content_formats():
    CONTENT_FORMATS.insert(0, "text/plain;charset=utf-8")
    CONTENT_FORMATS.insert(40, "application/link-format")
    CONTENT_FORMATS.insert(41, "application/xml")
    CONTENT_FORMATS.insert(42, "application/octet-stream")
    CONTENT_FORMATS.insert(47, "application/exi")
    CONTENT_FORMATS.insert(50, "application/exi")
    CONTENT_FORMATS.insert(60, "application/cbor")

def read_file(local_path):
    fd = open(TEMP_FILE_NAME, "w")
    case_count = 0
    for line in fileinput.input(local_path):
        if case_count  == 0:
            if line.find(FIRST_STR) != -1:
                case_count = 1
                continue

        if case_count == 1:
            if line.find(SECOND_STR) != -1:
                case_count = 2
                continue

        if case_count == 2:
            if line.find(SECOND_STR) != -1:
                case_count = 3
                continue
            if line.find(THIRD_STR) != -1:
                tmp_str = line.split(THIRD_STR)
                fd.write(tmp_str[1].strip('\n'))
                continue

        if case_count == 3:
            if line.find(SECOND_STR) != -1:
                fd.write('\n')
                break;
    fd.close()

def str2hex(s):
    odata = 0;
    su =s.upper()
    for c in su:
        tmp=ord(c)
        if tmp <= ord('9') :
            odata = odata << 4
            odata += tmp - ord('0')
        elif ord('A') <= tmp <= ord('F'):
            odata = odata << 4
            odata += tmp - ord('A') + 10
    return odata

def analay_coap(local_path):
    count = 0
    i = 0
    coap_message_data = []
    token_array = []
    print("analay_coap111, loacal_path is:",local_path)
    print("===============================")
    for line in fileinput.input(local_path):
        print("analay_coap")
        data_array = line.split(' ')
        while "" in data_array:
            data_array.remove("")
    for aaa in data_array:
        bbb = str2hex(aaa)
        coap_message_data.append(bbb)
        # print str2hex(aaa)
    print (coap_message_data, "length",len(coap_message_data))
    # for i in range(len(coap_message_data)):
    #     print( '%#x'%coap_message_data[i])

    VER = coap_message_data[0] >> 6;
    print ("VER =%x" % VER)
    message_index = coap_message_data[0] >> 4 & 0x03;
    print( "Message types =%s" % MESSAGE_TYPES[message_index])
    TKL = coap_message_data[0] & 0x0f
    print ("Token length =%x" % TKL)

    method_code = coap_message_data[1] >> 5;
    # print "Method codes =", METHOD_CODES[method_code]

    description = coap_message_data[1] & 0x1f;
    if method_code == 0:
        print ("description =%s" % CLASS0_DES[description])
    if method_code == 2:
        if description == 31:
            description = 5
        print ("description = %s" % CLASS2_DES[description - 1])
    if method_code == 4:
        print ("description =%s" % CLASS4_DES[description])

    message_id = coap_message_data[2] * 16 + coap_message_data[3]
    print ("Message ID =%x" % message_id)

    if coap_message_data[1] == 0:#empty ack
        return

    if TKL > 0:
        for i in range(TKL):
            token_array.append(coap_message_data[4 + i])
            print( 'Token is: %#x'%token_array[i])

    option_index = 4 + TKL

    list_s = [];
    i = 0
    option_flag = 0
    option_length_flag = 0
    option_data = 0
    option_delta_base = 0
    block_flag = 0
    coap_count = 0
    option_delta_count = 0
    option_length_count = 0
    block_data = 0
    has_payload = 0
    for data_temp in coap_message_data[option_index:]:
        coap_count += 1
        if option_flag == 0:
            if data_temp == 255:
                has_payload = 1
                break
            option_data = data_temp

            if option_delta_count == 0 and option_length_count == 0:
                option_delta_base += option_data >> 4
                option_length = option_data & 0x0f

            if option_delta_count == 0:
                if option_delta_base > 12:
                    option_delta_count = (option_data >> 4) - 12
            else:
                option_delta_base += option_data
                option_delta_count -= 1

            if option_length_count == 0:
                if option_length > 12:
                    option_length_count = option_length - 12
            else:
                if option_delta_count == 0:
                    option_length += option_data
                option_length_count -= 1

            if option_delta_count == 0 and option_length_count == 0:
                option_flag = 1
        else:
            if id(i) < id(option_length):
                list_s.append(chr(data_temp))
                i = i + 1
            if id(i) == id(option_length):
                option_flag = 0
                i = 0
                if option_delta_base == 23 or option_delta_base == 27:
                    block_flag = 1
        if block_flag == 1:
            block_szx = 0
            for data in list_s:
                block_data = block_data*256 + ord(data)
            block_szx = block_data & 0x07
            block_data = block_data >> 3
            block_m = block_data & 0x01
            block_data = block_data >> 1
            block_number = block_data
            if True == OPTION_NAMES.__contains__(option_delta_base):
                print(">> ",OPTION_NAMES[option_delta_base])
            print("bock num=%d, M=%d, size=%d" %(block_number, block_m, block_szx))
            list_s.clear()
            option_flag = 0
            block_flag = 0
            block_data = 0
            i = 0
        if option_flag == 0:
            if True == OPTION_NAMES.__contains__(option_delta_base):
                print(">> ",OPTION_NAMES[option_delta_base], ":", str(list_s))
            list_s.clear()
    if has_payload == 1:
        print("payload:",coap_message_data[option_index+coap_count:])
    # for c in coap_message_data[option_index+coap_count:]:
    #     print(chr(c))
    # option_length = coap_message_data[option_index] & 0x0f
    # print ("option length = %x, %x" % (option_length, coap_message_data[option_index]))
    # if option_length == 1:
    #     option_data = coap_message_data[option_index]
    # else:
    #     option_data = coap_message_data[option_index+1:option_index+option_length]
    # print("option_index:",option_index,"option_data is:", option_data)

    # option_delta = coap_message_data[option_index] >> 4 & 0x0f
    # if option_delta < 13:
    #     print ("only option delta:", option_delta)
    #     print ("option no =", OPTION_NAMES[option_delta])
    # else:
    #     print ("need to check details")
    #     return

    # if method_code != 0:
    #     playload_marker_index = option_index + option_length + 1
    #     print ("playload_marker_index =", playload_marker_index)
    #     if playload_marker_index >= len(coap_message_data):
    #         print ("NO PLAYLOAD")
    #         return
    #     if coap_message_data[playload_marker_index] != 0xff:
    #         print( "===== COAP ERROR CHECK ====")
    #         return
    #     print( "payload_marker =", coap_message_data[playload_marker_index])
    # else:
    #     playload_marker_index = option_index

    # payload = coap_message_data[playload_marker_index+1:]
    # print ("payload =", payload)

    # list_s = [];
    # for i in range(len(payload)):
    #     list_s.append(chr(payload[i]))
    # print (str(list_s))

if __name__ == "__main__":
    init_option_names()
    init_content_formats()

    # for temp in OPTION_NAMES:
    #     print(temp,OPTION_NAMES[temp])
    read_file("test.txt")
    analay_coap(TEMP_FILE_NAME)
