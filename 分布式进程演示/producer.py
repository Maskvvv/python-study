from multiprocessing.managers import BaseManager
import time

print("=" * 50)
print("分布式进程 - 生产者")
print("=" * 50)


class TaskManager(BaseManager):
    pass


TaskManager.register('get_task_queue')

print("正在连接服务端...")
manager = TaskManager(address=('127.0.0.1', 5000), authkey=b'my_secret_key')
manager.connect()
print("✓ 已连接到服务端")

task_queue = manager.get_task_queue()

print("\n开始发送任务...")
for i in range(1, 11):
    task = f'任务-{i}'
    task_queue.put(task)
    print(f"  发送: {task}")
    time.sleep(0.2)

print("\n✓ 所有任务已发送完成!")
print("=" * 50)
print("提示: 现在可以运行 consumer.py 来处理任务")
