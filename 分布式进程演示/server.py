from multiprocessing.managers import BaseManager
import queue

print("=" * 50)
print("分布式进程 - 服务端")
print("=" * 50)


class TaskManager(BaseManager):
    pass


task_queue = queue.Queue()
result_queue = queue.Queue()

TaskManager.register('get_task_queue', callable=lambda: task_queue)
TaskManager.register('get_result_queue', callable=lambda: result_queue)

manager = TaskManager(address=('127.0.0.1', 5000), authkey=b'my_secret_key')

print("正在启动服务端...")
manager.start()
print("✓ 服务端已启动，监听地址: 127.0.0.1:5000")
print("✓ 等待生产者和消费者连接...")
print("=" * 50)
print("提示: 先运行 producer.py 发送任务")
print("      再运行 consumer.py 处理任务")
print("      按回车键关闭服务端")
print("=" * 50)

input()

print("正在关闭服务端...")
manager.shutdown()
print("✓ 服务端已关闭")
