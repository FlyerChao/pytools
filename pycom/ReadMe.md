# 使用说明

[toc]

## 1. 开发工具

python3.8 + pyqt5 + yaml

## 2. 基本功能介绍

本工具实现串口的基本功能。

![1673513364008](image/ReadMe/Snipaste_2023-01-16_14-30-25.png)

| 功能项       | 描述                                                                                               | 备注 |
| ------------ | -------------------------------------------------------------------------------------------------- | ---- |
| 串口号       | 扫描到当前的PC上的串口号                                                                           |      |
| 刷新串口设备 | 重新获取串口号                                                                                     |      |
| 保存文件     | 当每次勾选的时候会新建一个保存文件，在当前的目录下创建日志文件<br />日志名称为《年月日时分秒.log》 |      |
| 自动滚屏     | 当勾选后，会自动滚屏，否则不会自动滚屏 |      |
| 波特率       | 选择当前的默认的波特率（目前最大到115200）                                                         |      |
| 定时发送     | 定时发送一些命令                                                                                   |      |
| 比较发送     | 监控收到的命令，当收到特定的命令后发送特定的操作                              |      |
| 顺序发送     |  顺序发送定义的命令，只执行一次                            |      |
| 数据位       | 串口的数据位设置                                                                                   |      |
| 停止位       | 串口的停止位设置                                                                                   |      |
| 发送命令     | 可以设定3个发送命令                                                                                |      |
| 校验位       | 串口的校验位设置                                                                                   |      |
| HEX发送      | 发送栏中的命令以hex的方式发送                                                                      |      |

主界面的缓存大小是1w行。

## 3. 定时发送配置文件（com_config.yaml)

```yaml
- command: 'test1'
  interval: 5
  count: -1
- command: 'test2'
  interval: 10
  count: 5
- command: 'test3'
  interval: 7
  count: 4
```

配置文件采用yaml的格式（==格式一定要符合要求==），发送的命令根据需求修改，无上限设置

| 命令字   | 说明             | 备注             |
| -------- | ---------------- | ---------------- |
| command  | 需要发送的命令字 |                  |
| interval | 间隔发送的时间   | 秒               |
| count    | 发送的次数       | ==-1：一直发送== |

## 4. 比较发送（compare_config.yaml)

```yaml
- compare_str: ' LEN  : 3 DATA : OK'
  send_cmd: 'lastgasp'
- compare_str: '==== +CEREG: +CEREG: 0,1'
  send_cmd: 'lastgasp'
```

配置文件采用yaml的格式（==格式一定要符合要求==），发送的命令根据需求修改，无上限设置

| 命令字      | 说明             | 备注                   |
| ----------- | ---------------- | ---------------------- |
| compare_str | 需要对比的字符串 | ==需要用单引号括起来== |
| send_cmd    | 需要发送的命令字 |                        |

## 5. 顺序发送（sequence_config.yaml)

```yaml
- command: "[AUTO,ON]"
  timedelay: 10
- command: "[AUTO,ON]"
  timedelay: 9
- command: "[AUTO,ON]"
  timedelay: 8
```

配置文件采用yaml的格式（==格式一定要符合要求==），发送的命令根据需求修改，无上限设置

| 命令字      | 说明             | 备注                   |
| ----------- | ---------------- | ---------------------- |
| compare_str | 需要对比的字符串 | ==需要用引号括起来== |
| timedelay  | 发送命令后的等待时间 |               |

## 6. 颜色配置（color.yaml)

```yaml
- compare_str: 'INFO: '
  color: 9
- compare_str: 'DEBUG:'
  color: 2
- compare_str: '=>ERROR:'
  color: 7
- compare_str: 'WARNNING:'
  color: 10
```

配置文件采用yaml的格式（==格式一定要符合要求==），发送的命令根据需求修改，无上限设置

| 命令字      | 说明             | 备注                   |
| ----------- | ---------------- | ---------------------- |
| compare_str | 需要对比的字符串 | ==需要用引号括起来== |
| color | 查找到字符串后设置的颜色，填写枚举对应的数字 |  |

颜色配置如下枚举
``` python
class GlobalColor(int):
        color0 = 0... # type: Qt.GlobalColor
        color1 = 1... # type: Qt.GlobalColor
        black = 2... # type: Qt.GlobalColor
        white = 3... # type: Qt.GlobalColor
        darkGray = 4... # type: Qt.GlobalColor
        gray = 5... # type: Qt.GlobalColor
        lightGray = 6... # type: Qt.GlobalColor
        red = 7... # type: Qt.GlobalColor
        green = 8... # type: Qt.GlobalColor
        blue = 9... # type: Qt.GlobalColor
        cyan = 10... # type: Qt.GlobalColor
        magenta = 11... # type: Qt.GlobalColor
        yellow = 12... # type: Qt.GlobalColor
        darkRed = 13... # type: Qt.GlobalColor
        darkGreen = 14... # type: Qt.GlobalColor
        darkBlue = 15... # type: Qt.GlobalColor
        darkCyan = 16... # type: Qt.GlobalColor
        darkMagenta = 17... # type: Qt.GlobalColor
        darkYellow = 18... # type: Qt.GlobalColor
        transparent = 19... # type: Qt.GlobalColor
```
![20191107163337482](image/ReadMe/20191107163337482.png)
