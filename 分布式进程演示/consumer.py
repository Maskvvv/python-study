from multiprocessing.managers import BaseManager
import time

print("=" * 50)
print("分布式进程 - 消费者")
print("=" * 50)


class TaskManager(BaseManager):
    pass


TaskManager.register('get_task_queue')
TaskManager.register('get_result_queue')

print("正在连接服务端...")
manager = TaskManager(address=('127.0.0.1', 5000), authkey=b'my_secret_key')
manager.connect()
print("✓ 已连接到服务端")

task_queue = manager.get_task_queue()
result_queue = manager.get_result_queue()

print("\n开始处理任务...")
print("=" * 50)

processed = 0
while True:
    try:
        task = task_queue.get(timeout=3)
        print(f"  处理中: {task}")
        time.sleep(0.5)
        result = f'{task} ✓已完成'
        result_queue.put(result)
        processed += 1
    except:
        break

print("=" * 50)
print(f"\n✓ 共处理了 {processed} 个任务")

print("\n处理结果:")
while not result_queue.empty():
    print(f"  {result_queue.get()}")

print("\n✓ 消费者工作完成!")
