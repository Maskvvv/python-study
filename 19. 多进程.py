import multiprocessing
import time
import os

print("=" * 50)
print("Python 多进程演示 - multiprocessing 模块")
print("=" * 50)


def worker(name, seconds):
    print(f"进程 {name} 开始, PID: {os.getpid()}")
    time.sleep(seconds)
    print(f"进程 {name} 结束, 耗时 {seconds} 秒")
    return f"{name} 完成"


def worker_with_queue(queue, data):
    result = data * 2
    queue.put(result)
    print(f"进程 PID {os.getpid()} 将结果放入队列: {result}")


def worker_with_shared_value(value):
    for _ in range(1000):
        with value.get_lock():
            value.value += 1


# 1. 创建单个进程
print("\n【1. 创建单个进程 - Process】")
p = multiprocessing.Process(target=worker, args=('A', 1))
p.start()
p.join()
print("✓ 单个进程执行完成")

# 2. 创建多个进程
print("\n【2. 创建多个进程】")
processes = []
for i in range(3):
    p = multiprocessing.Process(target=worker, args=(f'P{i}', 1))
    processes.append(p)
    p.start()

for p in processes:
    p.join()
print("✓ 所有进程执行完成")

# 3. 使用 Pool 进程池
print("\n【3. 使用进程池 - Pool】")


def square(x):
    time.sleep(0.1)
    return x * x


with multiprocessing.Pool(processes=4) as pool:
    results = pool.map(square, [1, 2, 3, 4, 5])
    print(f"Pool.map 结果: {results}")

    results = pool.map_async(square, [6, 7, 8])
    print(f"Pool.map_async 结果: {results.get()}")

    result = pool.apply(square, (10,))
    print(f"Pool.apply 结果: {result}")

    results = [pool.apply_async(square, (i,)) for i in range(11, 14)]
    print(f"Pool.apply_async 结果: {[r.get() for r in results]}")

print("✓ 进程池执行完成")

# 4. 进程间通信 - Queue
print("\n【4. 进程间通信 - Queue】")
queue = multiprocessing.Queue()
p1 = multiprocessing.Process(target=worker_with_queue, args=(queue, 10))
p2 = multiprocessing.Process(target=worker_with_queue, args=(queue, 20))

p1.start()
p2.start()
p1.join()
p2.join()

while not queue.empty():
    print(f"从队列获取: {queue.get()}")
print("✓ Queue 通信完成")

# 5. 进程间通信 - Pipe
print("\n【5. 进程间通信 - Pipe】")


def pipe_sender(conn):
    conn.send("来自发送进程的消息!")
    conn.close()


def pipe_receiver(conn):
    msg = conn.recv()
    print(f"接收进程收到: {msg}")
    conn.close()


parent_conn, child_conn = multiprocessing.Pipe()
p1 = multiprocessing.Process(target=pipe_sender, args=(child_conn,))
p2 = multiprocessing.Process(target=pipe_receiver, args=(parent_conn,))

p1.start()
p2.start()
p1.join()
p2.join()
print("✓ Pipe 通信完成")

# 6. 共享内存 - Value 和 Array
print("\n【6. 共享内存 - Value】")
shared_value = multiprocessing.Value('i', 0)

processes = []
for _ in range(4):
    p = multiprocessing.Process(target=worker_with_shared_value, args=(shared_value,))
    processes.append(p)
    p.start()

for p in processes:
    p.join()

print(f"共享值最终结果: {shared_value.value}")
print("✓ 共享内存演示完成")

# 7. 共享内存 - Array
print("\n【7. 共享内存 - Array】")


def modify_array(arr):
    for i in range(len(arr)):
        arr[i] = arr[i] * 2


shared_array = multiprocessing.Array('i', [1, 2, 3, 4, 5])
p = multiprocessing.Process(target=modify_array, args=(shared_array,))
p.start()
p.join()
print(f"共享数组结果: {list(shared_array)}")
print("✓ 共享数组演示完成")

# 8. 进程锁 - Lock
print("\n【8. 进程锁 - Lock】")


def worker_with_lock(lock, num):
    with lock:
        print(f"进程 {num} 获得锁, PID: {os.getpid()}")
        time.sleep(0.5)
        print(f"进程 {num} 释放锁")


lock = multiprocessing.Lock()
processes = []
for i in range(3):
    p = multiprocessing.Process(target=worker_with_lock, args=(lock, i))
    processes.append(p)
    p.start()

for p in processes:
    p.join()
print("✓ 进程锁演示完成")

# 9. 获取当前进程信息
print("\n【9. 当前进程信息】")
current_process = multiprocessing.current_process()
print(f"当前进程名: {current_process.name}")
print(f"当前进程 PID: {os.getpid()}")
print(f"CPU 核心数: {multiprocessing.cpu_count()}")

# 10. 进程状态
print("\n【10. 进程状态检查】")
p = multiprocessing.Process(target=worker, args=('Status-Test', 0.5))
print(f"创建后状态 - is_alive: {p.is_alive()}")
p.start()
print(f"启动后状态 - is_alive: {p.is_alive()}")
p.join()
print(f"结束后状态 - is_alive: {p.is_alive()}")

print("\n" + "=" * 50)
print("多进程演示完成！🎉")
print("=" * 50)
