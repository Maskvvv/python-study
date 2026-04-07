import psutil
import time

print("=" * 50)
print("Python psutil 模块演示 - 系统监控")
print("=" * 50)

# 1. CPU 信息
print("\n【1. CPU 信息】")
print(f"CPU 核心数 (逻辑): {psutil.cpu_count()}")
print(f"CPU 核心数 (物理): {psutil.cpu_count(logical=False)}")
print(f"CPU 使用率: {psutil.cpu_percent(interval=1)}%")
print(f"CPU 各核心使用率: {psutil.cpu_percent(interval=1, percpu=True)}")

cpu_freq = psutil.cpu_freq()
if cpu_freq:
    print(f"CPU 频率 - 当前: {cpu_freq.current}MHz, 最大: {cpu_freq.max}MHz")

cpu_stats = psutil.cpu_stats()
print(f"CPU 上下文切换: {cpu_stats.ctx_switches}")
print(f"CPU 中断次数: {cpu_stats.interrupts}")

# 2. 内存信息
print("\n【2. 内存信息】")
mem = psutil.virtual_memory()
print(f"总内存: {mem.total / (1024**3):.2f} GB")
print(f"可用内存: {mem.available / (1024**3):.2f} GB")
print(f"已用内存: {mem.used / (1024**3):.2f} GB")
print(f"内存使用率: {mem.percent}%")

swap = psutil.swap_memory()
print(f"交换分区总量: {swap.total / (1024**3):.2f} GB")
print(f"交换分区使用: {swap.used / (1024**3):.2f} GB")
print(f"交换分区使用率: {swap.percent}%")

# 3. 磁盘信息
print("\n【3. 磁盘信息】")
disk_usage = psutil.disk_usage('/')
print(f"磁盘总量: {disk_usage.total / (1024**3):.2f} GB")
print(f"磁盘已用: {disk_usage.used / (1024**3):.2f} GB")
print(f"磁盘空闲: {disk_usage.free / (1024**3):.2f} GB")
print(f"磁盘使用率: {disk_usage.percent}%")

print("\n磁盘分区列表:")
for partition in psutil.disk_partitions():
    print(f"  {partition.device} -> {partition.mountpoint} ({partition.fstype})")

print("\n磁盘 IO 统计:")
disk_io = psutil.disk_io_counters()
print(f"  读取: {disk_io.read_bytes / (1024**2):.2f} MB")
print(f"  写入: {disk_io.write_bytes / (1024**2):.2f} MB")

# 4. 网络信息
print("\n【4. 网络信息】")
print("网络接口:")
net_io = psutil.net_io_counters()
print(f"  发送: {net_io.bytes_sent / (1024**2):.2f} MB")
print(f"  接收: {net_io.bytes_recv / (1024**2):.2f} MB")

print("\n网络接口地址:")
for name, addrs in psutil.net_if_addrs().items():
    print(f"  {name}:")
    for addr in addrs:
        print(f"    {addr.family.name}: {addr.address}")

print("\n网络连接 (前10个):")
connections = psutil.net_connections(kind='inet')
for conn in connections[:10]:
    status = conn.status if conn.status else 'N/A'
    print(f"  {conn.laddr.ip}:{conn.laddr.port} -> {status}")

# 5. 进程信息
print("\n【5. 进程信息】")
print(f"当前进程 PID: {psutil.Process().pid}")
print(f"当前进程名称: {psutil.Process().name()}")

print("\n进程列表 (前10个):")
count = 0
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
    if count >= 10:
        break
    try:
        print(f"  PID: {proc.info['pid']:>6} | {proc.info['name']:<20} | CPU: {proc.info['cpu_percent']:>5}% | 内存: {proc.info['memory_percent']:.1f}%")
        count += 1
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# 6. 进程详情
print("\n【6. 当前进程详情】")
current_process = psutil.Process()
print(f"进程名: {current_process.name()}")
print(f"进程 PID: {current_process.pid}")
print(f"进程状态: {current_process.status()}")
print(f"创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_process.create_time()))}")
print(f"CPU 使用率: {current_process.cpu_percent()}%")
print(f"内存使用: {current_process.memory_info().rss / (1024**2):.2f} MB")
print(f"内存占比: {current_process.memory_percent():.2f}%")
print(f"线程数: {current_process.num_threads()}")
print(f"打开文件数: {len(current_process.open_files())}")

# 7. 系统启动时间
print("\n【7. 系统信息】")
boot_time = psutil.boot_time()
print(f"系统启动时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time))}")
uptime = time.time() - boot_time
hours = int(uptime // 3600)
minutes = int((uptime % 3600) // 60)
print(f"系统运行时长: {hours} 小时 {minutes} 分钟")

# 8. 用户信息
print("\n【8. 用户信息】")
for user in psutil.users():
    print(f"  用户: {user.name}, 终端: {user.terminal}, 登录时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.started))}")

# 9. 系统传感器 (Windows 可能不支持)
print("\n【9. 传感器信息】")
try:
    temps = psutil.sensors_temperatures()
    if temps:
        for name, entries in temps.items():
            print(f"  {name}:")
            for entry in entries:
                print(f"    {entry.label}: {entry.current}°C")
    else:
        print("  当前系统不支持温度传感器读取")
except AttributeError:
    print("  当前系统不支持传感器功能")

# 10. 电池信息
print("\n【10. 电池信息】")
try:
    battery = psutil.sensors_battery()
    if battery:
        print(f"  电量: {battery.percent}%")
        print(f"  电源连接: {'是' if battery.power_plugged else '否'}")
        if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
            print(f"  剩余时间: {battery.secsleft // 60} 分钟")
    else:
        print("  未检测到电池")
except AttributeError:
    print("  当前系统不支持电池信息读取")

# 11. 实时监控示例
print("\n【11. 实时监控示例 (5秒)】")
print("时间        CPU%   内存%   磁盘%")
print("-" * 40)
for i in range(5):
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    print(f"{i+1}秒:       {cpu:>5.1f}  {mem:>5.1f}  {disk:>5.1f}")

# 12. 进程管理操作
print("\n【12. 进程管理操作示例】")
print("""
# 获取进程
p = psutil.Process(pid)

# 进程操作
p.terminate()          # 终止进程
p.kill()               # 强制杀死进程
p.suspend()            # 挂起进程
p.resume()             # 恢复进程

# 查找进程
for proc in psutil.process_iter(['pid', 'name']):
    if 'python' in proc.info['name'].lower():
        print(proc.info)
""")

# 13. 常用监控脚本模板
print("\n【13. 常用监控脚本模板】")
print("""
import psutil
import time

def monitor(interval=1):
    while True:
        cpu = psutil.cpu_percent(interval=interval)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        print(f"CPU: {cpu}% | 内存: {mem}% | 磁盘: {disk}%")
        time.sleep(interval)

# monitor(2)  # 每2秒监控一次
""")

print("\n" + "=" * 50)
print("psutil 模块演示完成！🎉")
print("=" * 50)
print("\n💡 提示: psutil 是跨平台的系统监控库")
print("   安装命令: pip install psutil")
