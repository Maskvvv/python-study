import multiprocessing
from multiprocessing.managers import BaseManager
import time
import random
import queue

print("=" * 50)
print("Python 分布式进程演示 - multiprocessing.managers")
print("=" * 50)

# ============================================================
# 分布式进程核心概念：
# 通过网络在不同机器/进程间共享数据
# 使用 BaseManager 创建可远程访问的共享对象
# ============================================================


# 1. 基础：创建自定义 Manager
print("\n【1. 自定义 Manager 类】")


class QueueManager(BaseManager):
    pass


print("✓ 定义了 QueueManager 类，继承自 BaseManager")

# 2. 注册共享类型
print("\n【2. 注册共享类型】")
QueueManager.register('get_queue', callable=lambda: queue.Queue())
QueueManager.register('get_dict', callable=lambda: {})
QueueManager.register('get_list', callable=lambda: [])
print("✓ 注册了 Queue、Dict、List 三种共享类型")

# 3. 创建服务端
print("\n【3. 创建服务端模式】")
print("""
服务端代码示例:
----------------
from multiprocessing.managers import BaseManager
import queue

class QueueManager(BaseManager):
    pass

QueueManager.register('get_queue', callable=lambda: queue.Queue())

# 创建管理器并启动服务
manager = QueueManager(address=('127.0.0.1', 5000), authkey=b'secret')
manager.start()

# 获取共享对象
shared_queue = manager.get_queue()
shared_queue.put('来自服务端的数据')

print('服务端运行中...')
input('按回车键退出...')
manager.shutdown()
""")

# 4. 创建客户端
print("\n【4. 创建客户端模式】")
print("""
客户端代码示例:
----------------
from multiprocessing.managers import BaseManager

class QueueManager(BaseManager):
    pass

QueueManager.register('get_queue')

# 连接到服务端
manager = QueueManager(address=('127.0.0.1', 5000), authkey=b'secret')
manager.connect()

# 获取共享对象
shared_queue = manager.get_queue()
data = shared_queue.get()
print(f'收到数据: {data}')
""")

# 5. 本地模拟演示（单进程内）
print("\n【5. 本地模拟演示】")


class DemoManager(BaseManager):
    pass


shared_queue = queue.Queue()
shared_dict = {}
shared_list = []

DemoManager.register('get_queue', callable=lambda: shared_queue)
DemoManager.register('get_dict', callable=lambda: shared_dict)
DemoManager.register('get_list', callable=lambda: shared_list)

manager = DemoManager()
manager.start()

proxy_queue = manager.get_queue()
proxy_dict = manager.get_dict()
proxy_list = manager.get_list()

proxy_queue.put("Hello")
proxy_queue.put("World")
proxy_dict['name'] = 'Python'
proxy_dict['version'] = '3.12'
proxy_list.extend([1, 2, 3, 4, 5])

print(f"队列内容: {list(proxy_queue.queue)}")
print(f"字典内容: {dict(proxy_dict)}")
print(f"列表内容: {list(proxy_list)}")

manager.shutdown()
print("✓ 本地模拟演示完成")

# 6. 完整示例：生产者-消费者模式
print("\n【6. 完整示例：分布式生产者-消费者】")
print("=" * 50)
print("""
===== 服务端代码 (server.py) =====
import queue
from multiprocessing.managers import BaseManager

class TaskManager(BaseManager):
    pass

task_queue = queue.Queue()
result_queue = queue.Queue()

TaskManager.register('get_task_queue', callable=lambda: task_queue)
TaskManager.register('get_result_queue', callable=lambda: result_queue)

manager = TaskManager(address=('0.0.0.0', 5000), authkey=b'my_secret_key')
print('服务端启动，等待连接...')
server = manager.get_server()
server.serve_forever()

===== 生产者代码 (producer.py) =====
from multiprocessing.managers import BaseManager

class TaskManager(BaseManager):
    pass

TaskManager.register('get_task_queue')

manager = TaskManager(address=('127.0.0.1', 5000), authkey=b'my_secret_key')
manager.connect()
task_queue = manager.get_task_queue()

for i in range(10):
    task_queue.put(f'任务-{i}')
    print(f'发送: 任务-{i}')

===== 消费者代码 (consumer.py) =====
from multiprocessing.managers import BaseManager

class TaskManager(BaseManager):
    pass

TaskManager.register('get_task_queue')
TaskManager.register('get_result_queue')

manager = TaskManager(address=('127.0.0.1', 5000), authkey=b'my_secret_key')
manager.connect()
task_queue = manager.get_task_queue()
result_queue = manager.get_result_queue()

while True:
    try:
        task = task_queue.get(timeout=5)
        print(f'处理: {task}')
        result_queue.put(f'{task} 已完成')
    except:
        print('队列为空，退出')
        break
""")

# 7. 使用上下文管理器
print("\n【7. 使用上下文管理器（推荐）】")
print("""
# 服务端
with BaseManager(address=('', 5000), authkey=b'key') as manager:
    manager.register('get_data', callable=lambda: {'status': 'ok'})
    manager.start()
    print('服务运行中...')
    input()

# 客户端
with BaseManager(address=('127.0.0.1', 5000), authkey=b'key') as manager:
    manager.register('get_data')
    manager.connect()
    data = manager.get_data()
    print(data)
""")

# 8. 安全注意事项
print("\n【8. 安全注意事项】")
print("""
⚠️ 重要安全提示:
1. authkey 必须保密，用于身份验证
2. 生产环境建议使用 SSL/TLS 加密
3. address 绑定 '0.0.0.0' 允许外部访问
4. address 绑定 '127.0.0.1' 仅限本地访问
5. 使用防火墙限制访问端口
""")

# 9. 常见共享类型
print("\n【9. 常见共享类型】")
print("""
类型          | 说明
-------------|------------------
Queue        | 线程安全的队列
dict         | 共享字典
list         | 共享列表
Value        | 共享值
Array        | 共享数组
Namespace    | 共享命名空间
""")

# 10. 性能优化建议
print("\n【10. 性能优化建议】")
print("""
1. 减少网络传输：批量处理数据
2. 使用连接池：复用连接
3. 异步操作：避免阻塞
4. 数据压缩：大数据传输时压缩
5. 本地缓存：频繁读取的数据缓存
""")

print("\n" + "=" * 50)
print("分布式进程演示完成！🎉")
print("=" * 50)
print("\n💡 提示: 分布式进程需要分别运行服务端和客户端代码")
print("   请将上面的代码保存为独立文件后运行测试")
