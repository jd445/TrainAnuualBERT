import psutil
from datetime import datetime
import time
import signal
import subprocess
def get_process_name(process):
    try:
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

def kill_process(process):
    try:
        subprocess.run("kill -9 " + str(process.pid), shell= True)
    except:
        return None
    

def kill_longTime_lxml(process):
    current_time = datetime.now()

    # 计算时间差
    time_difference = current_time - datetime.fromtimestamp(process.create_time())

    if time_difference.total_seconds() > 150:
        # 检查进程状态是否为 running
        if process.status() == 'running':
            # 杀死进程
            kill_process(process)
            print(f"已终止进程 {process.pid}，因为它已经运行超过300秒。")
def monitor_latexml_processes():
    all_processes = psutil.process_iter(['pid', 'name'])

    # 筛选正在运行的latexml进程
    try:
        latexml_processes = [proc for proc in all_processes if proc.name() == 'latexml' and get_process_name(proc) != None]
    
        # 遍历筛选出的latexml进程，检查运行时间并终止超时进程
        for process in latexml_processes:
            kill_longTime_lxml(process)
    except:
        None

while True:
    print("10s")
    monitor_latexml_processes()
    time.sleep(10)  # 每隔10秒执行一次