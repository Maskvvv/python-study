from multiprocessing.managers import BaseManager
import queue

print("=" * 50)
print("分布式进程 - 简化演示（单文件版）")
print("=" * 50)
print("此演示在同一进程中模拟服务端和客户端")
print("=" * 50)


class SimpleManager(BaseManager):
    pass


shared_queue = queue.Queue()
shared_dict = {}

SimpleManager.register('get_queue', callable=lambda: shared_queue)
SimpleManager.register('get_dict', callable=lambda: shared_dict)

manager = SimpleManager()
manager.start()

proxy_queue = manager.get_queue()
proxy_dict = manager.get_dict()

print("\n【1. 测试共享队列】")
print("  放入数据...")
for i in range(1, 6):
    proxy_queue.put(f"数据-{i}")
    print(f"    put: 数据-{i}")

print("  取出数据...")
while not proxy_queue.empty():
    data = proxy_queue.get()
    print(f"    get: {data}")

print("\n【2. 测试共享字典】")
proxy_dict['name'] = 'Python'
proxy_dict['version'] = '3.12'
proxy_dict['type'] = '编程语言'

print("  字典内容:")
for key, value in proxy_dict.items():
    print(f"    {key}: {value}")

print("\n【3. 测试远程访问特性】")
print(f"  队列类型: {type(proxy_queue)}")
print(f"  字典类型: {type(proxy_dict)}")
print("  (注意: 这些是代理对象，不是原始对象)")

manager.shutdown()

print("\n" + "=" * 50)
print("简化演示完成！🎉")
print("=" * 50)
