import threading
import time
from concurrent.futures import ThreadPoolExecutor

print("=" * 50)
print("Python 多线程演示 - threading 模块")
print("=" * 50)


def worker(name, seconds):
    print(f"  线程 {name} 开始, TID: {threading.get_ident()}")
    time.sleep(seconds)
    print(f"  线程 {name} 结束, 耗时 {seconds} 秒")


# 1. 创建单个线程
print("\n【1. 创建单个线程 - Thread】")
t = threading.Thread(target=worker, args=('A', 1))
t.start()
t.join()
print("✓ 单个线程执行完成")

# 2. 创建多个线程
print("\n【2. 创建多个线程】")
threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(f'T{i}', 0.5))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
print("✓ 所有线程执行完成")

# 3. 线程锁 - Lock
print("\n【3. 线程锁 - Lock】")
counter = 0
lock = threading.Lock()


def increment_with_lock():
    global counter
    for _ in range(10000):
        with lock:
            counter += 1


threads = []
for _ in range(5):
    t = threading.Thread(target=increment_with_lock)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
print(f"使用锁 - 计数器结果: {counter} (期望: 50000)")

counter = 0


def increment_without_lock():
    global counter
    for _ in range(10000):
        counter += 1


threads = []
for _ in range(5):
    t = threading.Thread(target=increment_without_lock)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
print(f"不使用锁 - 计数器结果: {counter} (期望: 50000, 可能不准确)")
print("✓ 线程锁演示完成")

# 4. 可重入锁 - RLock
print("\n【4. 可重入锁 - RLock】")
rlock = threading.RLock()


def recursive_function(n):
    with rlock:
        print(f"  递归层级: {n}")
        if n > 0:
            recursive_function(n - 1)


t = threading.Thread(target=recursive_function, args=(3,))
t.start()
t.join()
print("✓ RLock 演示完成")

# 5. 事件 - Event
print("\n【5. 事件 - Event】")
event = threading.Event()


def waiter(name):
    print(f"  {name} 等待事件...")
    event.wait()
    print(f"  {name} 收到事件，继续执行!")


def setter():
    time.sleep(1)
    print("  设置事件!")
    event.set()


threads = [
    threading.Thread(target=waiter, args=('W1',)),
    threading.Thread(target=waiter, args=('W2',)),
    threading.Thread(target=setter)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("✓ Event 演示完成")

# 6. 条件变量 - Condition
print("\n【6. 条件变量 - Condition】")
condition = threading.Condition()
shared_data = []


def producer():
    with condition:
        shared_data.append('数据')
        print("  生产者: 添加数据")
        condition.notify()


def consumer():
    with condition:
        while not shared_data:
            print("  消费者: 等待数据...")
            condition.wait()
        data = shared_data.pop()
        print(f"  消费者: 消费 {data}")


t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=producer)
t1.start()
time.sleep(0.5)
t2.start()
t1.join()
t2.join()
print("✓ Condition 演示完成")

# 7. 信号量 - Semaphore
print("\n【7. 信号量 - Semaphore】")
semaphore = threading.Semaphore(2)


def limited_worker(name):
    with semaphore:
        print(f"  {name} 获得信号量, 开始工作")
        time.sleep(0.5)
        print(f"  {name} 释放信号量")


threads = [threading.Thread(target=limited_worker, args=(f'T{i}',)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("✓ Semaphore 演示完成 (最多2个线程同时执行)")

# 8. 线程屏障 - Barrier
print("\n【8. 线程屏障 - Barrier】")
barrier = threading.Barrier(3)


def barrier_worker(name):
    print(f"  {name} 到达屏障, 等待其他线程...")
    barrier.wait()
    print(f"  {name} 通过屏障!")


threads = [threading.Thread(target=barrier_worker, args=(f'T{i}',)) for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("✓ Barrier 演示完成")

# 9. 定时器 - Timer
print("\n【9. 定时器 - Timer】")
timer = threading.Timer(1.0, lambda: print("  定时器触发!"))
print("  启动定时器 (1秒后执行)")
timer.start()
timer.join()
print("✓ Timer 演示完成")

# 10. 守护线程 - Daemon
print("\n【10. 守护线程 - Daemon】")


def daemon_worker():
    while True:
        print("  守护线程运行中...")
        time.sleep(0.3)


def normal_worker():
    time.sleep(0.8)
    print("  普通线程完成")


d = threading.Thread(target=daemon_worker, daemon=True)
n = threading.Thread(target=normal_worker)
d.start()
n.start()
n.join()
print("✓ 守护线程演示完成 (主线程结束后守护线程自动终止)")

# 11. 线程本地存储 - local
print("\n【11. 线程本地存储 - local】")
local_data = threading.local()


def local_worker(name):
    local_data.value = name
    time.sleep(0.1)
    print(f"  线程 {threading.current_thread().name}: local_data = {local_data.value}")


threads = [threading.Thread(target=local_worker, args=(f'数据{i}',), name=f'Thread-{i}') for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("✓ 线程本地存储演示完成 (每个线程有独立的副本)")

# 12. 线程池 - ThreadPoolExecutor
print("\n【12. 线程池 - ThreadPoolExecutor】")


def task(n):
    time.sleep(0.2)
    return n * n


with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(task, [1, 2, 3, 4, 5]))
    future = executor.submit(task, 6)
    print(f"  线程池执行结果: {results}")
    print(f"  提交任务6的结果: {future.result()}")
print("✓ 线程池演示完成")

# 13. 当前线程信息
print("\n【13. 当前线程信息】")
print(f"当前线程: {threading.current_thread().name}")
print(f"主线程: {threading.main_thread().name}")
print(f"活跃线程数: {threading.active_count()}")
print(f"活跃线程列表: {[t.name for t in threading.enumerate()]}")

# 14. 自定义线程类
print("\n【14. 自定义线程类】")


class MyThread(threading.Thread):
    def __init__(self, name):
        super().__init__(name=name)
        self.result = None

    def run(self):
        print(f"  自定义线程 {self.name} 开始执行")
        time.sleep(0.5)
        self.result = f"{self.name} 的结果"
        print(f"  自定义线程 {self.name} 执行完成")


my_thread = MyThread("CustomThread")
my_thread.start()
my_thread.join()
print(f"  获取结果: {my_thread.result}")
print("✓ 自定义线程类演示完成")

print("\n" + "=" * 50)
print("多线程演示完成！🎉")
print("=" * 50)
