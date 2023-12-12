# 导入matplotlib.pyplot模块
import re

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.dates as mdates


def draw_chart(mem_time: list, mem: list, cpu_time: list, cpu_apk: list, cpu_core: list, png_name: str):
    # 绘制堆积面积图
    plt.figure(figsize=(20, 6))
    font = FontProperties(fname="simhei.ttf", size=14)
    plt.stackplot(cpu_time, cpu_core, cpu_apk, labels=['cpu_core', 'cpu_apk'], colors=['#A9B2C3', '#A4C639'])
    # 设置图形标题和坐标轴标签
    plt.title('软件运行时cpu和内存占用率', fontproperties=font)
    plt.xlabel('Time')
    plt.ylabel('cpu')
    # 显示制堆面积图例
    plt.legend(loc='upper left')
    # 创建次坐标轴
    ax2 = plt.twinx()
    ax2.set_ylim(0, max(mem) + 50)
    # 在次坐标轴上绘制折线图
    ax2.plot(mem_time, mem, 'b-', label='memory')
    # 设置次坐标轴的标签和颜色
    ax2.set_ylabel('memory')
    ax2.tick_params(axis='y', colors='b')
    # 获取当前轴
    ax = plt.gca()
    # 设置主要日期格式化程序
    formatter = mdates.DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(formatter)
    # 显示折现图例
    ax2.legend(loc='best')
    # 显示图形
    # plt.show()
    plt.savefig(png_name)


def load_cpu_data(cpu_file: str,cpu_number:int=1) -> (list, list, list):
    with open(cpu_file, "r") as f:
        # 创建两个空列表，用于存储时间和占用率
        time = []
        cpu_apk = []
        cpu_core = []
        # 遍历文件的每一行
        for line in f:
            # 去掉行尾的换行符
            line = line.strip()
            # 用逗号分隔时间和占用率
            try:
                t, u = line.split("      ")
                # 将时间和占用率转换为浮点数，并添加到对应的列表中
                pattern = r"\d+\.\d+%|\d+%"
                _, pre_cpu_apk, pre_cpu_core = re.findall(pattern, u)
                time.append(mdates.datestr2num(t))
                cpu_apk.append(float(pre_cpu_apk.replace("%", ""))/cpu_number)
                cpu_core.append(float(pre_cpu_core.replace("%", ""))/cpu_number)
            except ValueError as err:
                print('cpu info wrong:%s' % line)
    # 返回时间和占用率的列表
    return time, cpu_apk, cpu_core


def load_mem_data(mem_file: str) -> (list, list):
    with open(mem_file, "r") as f:
        # 创建两个空列表，用于存储时间和占用率
        time = []
        mem = []
        # 遍历文件的每一行
        for line in f:
            # 去掉行尾的换行符
            line = line.strip()
            # 用逗号分隔时间和占用率
            t, u = line.split("      ")
            time.append(mdates.datestr2num(t))
            mem.append(float(u) / 1024)
    # 返回时间和占用率的列表
    return time, mem
