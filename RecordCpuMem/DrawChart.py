import datetime
import os
import subprocess
import threading
import time

from main import load_cpu_data, load_mem_data, draw_chart

RUNNING = True


def yaki_shell(_cmd) -> str or None:
    cmd = 'adb shell %s' % _cmd
    ret = subprocess.run(args=cmd, shell=True, capture_output=True, encoding='utf-8')
    if ret.returncode == 0:
        return ret.stdout
    else:
        print('cmd err:%s\r\nreturn code:%s\r\nstderr:%s\r\nstdout:%s' % (cmd, ret.returncode, ret.stderr, ret.stdout))
        return None


def get_pss() -> str:
    p = yaki_shell('dumpsys meminfo com.astrob.turbodog |findstr PSS')
    pss = ''
    if p:
        try:
            pss = p.strip().split()[2]  # PSS数值
        except Exception as err:
            print('pss format is wrong:%s\r\npss str:%s' % (err, p))
    return pss


def get_cpu() -> str:
    p = yaki_shell('dumpsys cpuinfo |findstr com.astrob.turbodog')
    cpu = ''
    if p:
        try:
            cpu = p.strip()  # cpu数值
        except Exception as err:
            print('cpu format is wrong:%s\r\ncpu str:%s' % (err, p))
    return cpu


def write_log(pss_f_name: str, cpu_f_name: str, interval_time: int = 5):
    with open(pss_f_name, "w+", encoding="utf-8") as f_pss:
        with open(cpu_f_name, "w+", encoding="utf-8") as f_cpu:
            while RUNNING:
                start_time = time.time()
                mem_info = get_pss()
                cpu_info = get_cpu()
                current_time = str(datetime.datetime.now())  # 当前输出文本的时间节点
                f_pss.write(current_time + '      ')
                f_pss.write(mem_info + '\n')
                f_pss.flush()
                f_cpu.write(current_time + '      ')
                f_cpu.write(cpu_info + '\n')
                f_cpu.flush()
                sleep_time = interval_time - (time.time() - start_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)


if __name__ == '__main__':
    time_now = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))
    pss_file_name = os.path.join(os.path.abspath('.'), f'TB9_{time_now}_Pss.log')
    cpu_file_name = os.path.join(os.path.abspath('.'), f'TB9_{time_now}_cpu.log')
    try:
        t = threading.Thread(target=write_log, args=(pss_file_name, cpu_file_name,1))
        t.setDaemon(True)
        t.start()
        # do something in there
        time.sleep(6000)
    except KeyboardInterrupt:
        print('正在停止！')
    RUNNING = False
    time.sleep(6)
    # draw chart
    cpu_time, cpu_apk, cpu_core = load_cpu_data(cpu_file_name,cpu_number=6)
    mem_time, mem = load_mem_data(pss_file_name)
    draw_chart(mem_time, mem, cpu_time, cpu_apk, cpu_core, f"TB9_{time_now}.png")


