import asyncio
import time

print("=" * 50)
print("Python asyncio 异步编程演示 - async/await")
print("=" * 50)


# ============================================================
# 1. 基础：定义和运行协程
# ============================================================
print("\n【1. 基础：定义和运行协程】")


async def hello():
    print("  Hello")
    await asyncio.sleep(1)
    print("  World")


asyncio.run(hello())
print("[OK] 协程基础演示完成")

# ============================================================
# 2. async/await 语法
# ============================================================
print("\n【2. async/await 语法】")


async def countdown(name, n):
    for i in range(n, 0, -1):
        print(f"  {name}: {i}")
        await asyncio.sleep(0.5)
    print(f"  {name} 完成!")


asyncio.run(countdown("倒计时", 3))
print("[OK] async/await 语法演示完成")

# ============================================================
# 3. 并发执行多个协程 - gather
# ============================================================
print("\n【3. 并发执行多个协程 - gather】")


async def task(name, seconds):
    print(f"  {name} 开始 (耗时 {seconds}s)")
    await asyncio.sleep(seconds)
    print(f"  {name} 完成")
    return f"{name}的结果"


async def demo_gather():
    start = time.perf_counter()
    results = await asyncio.gather(
        task("任务A", 2),
        task("任务B", 1),
        task("任务C", 3),
    )
    elapsed = time.perf_counter() - start
    print(f"  所有任务完成，总耗时: {elapsed:.1f}s (并发执行，约等于最长的3秒)")
    print(f"  结果: {results}")


asyncio.run(demo_gather())
print("[OK] gather 并发演示完成")

# ============================================================
# 4. 创建任务 - create_task
# ============================================================
print("\n【4. 创建任务 - create_task】")


async def demo_create_task():
    task1 = asyncio.create_task(task("后台任务1", 2))
    task2 = asyncio.create_task(task("后台任务2", 1))

    print("  任务已创建，可以做其他事情...")
    await asyncio.sleep(0.5)
    print("  其他事情做完了，等待任务完成")

    result1 = await task1
    result2 = await task2
    print(f"  结果: {result1}, {result2}")


asyncio.run(demo_create_task())
print("[OK] create_task 演示完成")

# ============================================================
# 5. 等待任务 - wait
# ============================================================
print("\n【5. 等待任务 - wait】")


async def demo_wait():
    tasks = [
        asyncio.create_task(task(f"任务{i}", i * 0.5 + 0.5))
        for i in range(1, 5)
    ]

    done, pending = await asyncio.wait(
        tasks,
        timeout=2.0,
    )

    print(f"  已完成: {len(done)} 个")
    print(f"  未完成: {len(pending)} 个")

    for p in pending:
        p.cancel()
        try:
            await p
        except asyncio.CancelledError:
            pass


asyncio.run(demo_wait())
print("[OK] wait 演示完成")

# ============================================================
# 6. 超时控制 - wait_for
# ============================================================
print("\n【6. 超时控制 - wait_for】")


async def slow_operation():
    await asyncio.sleep(5)
    return "慢操作完成"


async def demo_wait_for():
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=1.0)
        print(f"  结果: {result}")
    except asyncio.TimeoutError:
        print("  操作超时! 1秒内未完成")


asyncio.run(demo_wait_for())
print("[OK] wait_for 超时控制演示完成")

# ============================================================
# 7. 异步锁 - Lock
# ============================================================
print("\n【7. 异步锁 - Lock】")
counter = 0
async_lock = asyncio.Lock()


async def increment_with_async_lock(name):
    global counter
    for _ in range(10000):
        async with async_lock:
            counter += 1
    print(f"  {name} 完成")


async def demo_async_lock():
    global counter
    counter = 0
    tasks = [
        asyncio.create_task(increment_with_async_lock(f"协程{i}"))
        for i in range(5)
    ]
    await asyncio.gather(*tasks)
    print(f"  使用异步锁 - 计数器结果: {counter} (期望: 50000)")


asyncio.run(demo_async_lock())
print("[OK] 异步锁演示完成")

# ============================================================
# 8. 异步事件 - Event
# ============================================================
print("\n【8. 异步事件 - Event】")


async def demo_async_event():
    event = asyncio.Event()

    async def waiter(name):
        print(f"  {name} 等待事件...")
        await event.wait()
        print(f"  {name} 收到事件，继续执行!")

    async def setter():
        await asyncio.sleep(1)
        print("  设置事件!")
        event.set()

    await asyncio.gather(
        waiter("W1"),
        waiter("W2"),
        setter(),
    )


asyncio.run(demo_async_event())
print("[OK] 异步 Event 演示完成")

# ============================================================
# 9. 异步条件变量 - Condition
# ============================================================
print("\n【9. 异步条件变量 - Condition】")


async def demo_async_condition():
    condition = asyncio.Condition()
    shared_data = []

    async def producer():
        async with condition:
            shared_data.append("数据")
            print("  生产者: 添加数据")
            condition.notify()

    async def consumer():
        async with condition:
            while not shared_data:
                print("  消费者: 等待数据...")
                await condition.wait()
            data = shared_data.pop()
            print(f"  消费者: 消费 {data}")

    await asyncio.gather(
        asyncio.create_task(consumer()),
        asyncio.create_task(asyncio.sleep(0.5)),
    )
    await producer()
    await asyncio.sleep(0.1)


asyncio.run(demo_async_condition())
print("[OK] 异步 Condition 演示完成")

# ============================================================
# 10. 异步信号量 - Semaphore
# ============================================================
print("\n【10. 异步信号量 - Semaphore】")


async def demo_async_semaphore():
    semaphore = asyncio.Semaphore(2)

    async def limited_worker(name):
        async with semaphore:
            print(f"  {name} 获得信号量, 开始工作")
            await asyncio.sleep(0.5)
            print(f"  {name} 释放信号量")

    tasks = [asyncio.create_task(limited_worker(f"T{i}")) for i in range(5)]
    await asyncio.gather(*tasks)


asyncio.run(demo_async_semaphore())
print("[OK] 异步 Semaphore 演示完成 (最多2个协程同时执行)")

# ============================================================
# 11. 异步队列 - Queue
# ============================================================
print("\n【11. 异步队列 - Queue】")


async def demo_async_queue():
    queue = asyncio.Queue()

    async def producer(name, items):
        for item in items:
            await queue.put(item)
            print(f"  生产者 {name}: 放入 {item}")
            await asyncio.sleep(0.1)

    async def consumer(name, count):
        for _ in range(count):
            item = await queue.get()
            print(f"  消费者 {name}: 取出 {item}")
            queue.task_done()

    await asyncio.gather(
        producer("P1", ["苹果", "香蕉"]),
        producer("P2", ["橙子", "葡萄"]),
        consumer("C1", 4),
    )


asyncio.run(demo_async_queue())
print("[OK] 异步 Queue 演示完成")

# ============================================================
# 12. 异步上下文管理器
# ============================================================
print("\n【12. 异步上下文管理器】")


class AsyncContextManager:
    async def __aenter__(self):
        print("  异步进入上下文")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("  异步退出上下文")
        await asyncio.sleep(0.1)


async def demo_async_context():
    async with AsyncContextManager() as cm:
        print("  在异步上下文中执行操作")


asyncio.run(demo_async_context())
print("[OK] 异步上下文管理器演示完成")

# ============================================================
# 13. 异步迭代器
# ============================================================
print("\n【13. 异步迭代器】")


class AsyncRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __aiter__(self):
        self.current = self.start
        return self

    async def __anext__(self):
        if self.current >= self.end:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        value = self.current
        self.current += 1
        return value


async def demo_async_iterator():
    async for num in AsyncRange(1, 5):
        print(f"  异步迭代: {num}")


asyncio.run(demo_async_iterator())
print("[OK] 异步迭代器演示完成")

# ============================================================
# 14. 异步生成器
# ============================================================
print("\n【14. 异步生成器】")


async def async_fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        await asyncio.sleep(0.05)
        yield a
        a, b = b, a + b


async def demo_async_generator():
    print("  斐波那契数列:", end=" ")
    async for num in async_fibonacci(10):
        print(num, end=" ")
    print()


asyncio.run(demo_async_generator())
print("[OK] 异步生成器演示完成")

# ============================================================
# 15. 模拟异步IO操作 - 网络请求
# ============================================================
print("\n【15. 模拟异步IO操作 - 网络请求】")


async def fetch_url(url, delay):
    print(f"  开始请求: {url}")
    await asyncio.sleep(delay)
    print(f"  完成请求: {url} (模拟耗时 {delay}s)")
    return f"{url} 的响应数据"


async def demo_async_io():
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch_url("https://api.example.com/users", 2),
        fetch_url("https://api.example.com/posts", 1.5),
        fetch_url("https://api.example.com/comments", 1),
    )
    elapsed = time.perf_counter() - start
    print(f"  3个请求总耗时: {elapsed:.1f}s (并发，约等于最长的2秒)")
    print(f"  如果串行执行需要: 4.5s")


asyncio.run(demo_async_io())
print("[OK] 模拟异步IO演示完成")

# ============================================================
# 16. TaskGroup (Python 3.11+)
# ============================================================
print("\n【16. TaskGroup (Python 3.11+)】")


async def demo_task_group():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(task("Group任务1", 1))
        t2 = tg.create_task(task("Group任务2", 0.5))
        t3 = tg.create_task(task("Group任务3", 0.8))
    print(f"  TaskGroup 结果: {t1.result()}, {t2.result()}, {t3.result()}")


asyncio.run(demo_task_group())
print("[OK] TaskGroup 演示完成")

# ============================================================
# 17. 异步子进程
# ============================================================
print("\n【17. 异步子进程】")


async def demo_async_subprocess():
    proc = await asyncio.create_subprocess_exec(
        "python", "-c", "print('Hello from subprocess!')",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    print(f"  子进程输出: {stdout.decode().strip()}")
    print(f"  返回码: {proc.returncode}")


asyncio.run(demo_async_subprocess())
print("[OK] 异步子进程演示完成")

# ============================================================
# 18. 取消任务
# ============================================================
print("\n【18. 取消任务】")


async def long_task():
    try:
        print("  长任务开始...")
        await asyncio.sleep(10)
        print("  长任务完成 (不应该看到这行)")
    except asyncio.CancelledError:
        print("  长任务被取消!")
        raise


async def demo_cancel():
    t = asyncio.create_task(long_task())
    await asyncio.sleep(0.5)
    t.cancel()
    try:
        await t
    except asyncio.CancelledError:
        print("  主协程: 确认任务已取消")


asyncio.run(demo_cancel())
print("[OK] 取消任务演示完成")

# ============================================================
# 19. 异步超时 (Python 3.11+)
# ============================================================
print("\n【19. 异步超时 - timeout (Python 3.11+)】")


async def demo_timeout():
    try:
        async with asyncio.timeout(1.0):
            await asyncio.sleep(5)
    except TimeoutError:
        print("  timeout 上下文管理器: 操作超时!")


asyncio.run(demo_timeout())
print("[OK] asyncio.timeout 演示完成")

# ============================================================
# 20. 回调函数
# ============================================================
print("\n【20. 回调函数】")


async def demo_callback():
    def on_done(t):
        print(f"  回调: 任务完成，结果 = {t.result()}")

    t = asyncio.create_task(task("回调任务", 0.5))
    t.add_done_callback(on_done)
    await t


asyncio.run(demo_callback())
print("[OK] 回调函数演示完成")

# ============================================================
# 21. asyncio 与多线程对比
# ============================================================
print("\n【21. asyncio vs 多线程 对比】")
print("  +--------------+------------------+------------------+")
print("  |     特性      |     多线程        |    asyncio       |")
print("  +--------------+------------------+------------------+")
print("  |   并发模型    |   操作系统调度     |   事件循环调度    |")
print("  |   切换开销    |   较大            |   极小            |")
print("  |   数据安全    |   需要加锁        |   单线程无需加锁  |")
print("  |   适用场景    |   CPU密集+IO密集  |   IO密集型        |")
print("  |   调试难度    |   较难            |   较易            |")
print("  |   代码风格    |   同步写法        |   async/await     |")
print("  +--------------+------------------+------------------+")

# ============================================================
# 22. 实战：异步并发下载模拟
# ============================================================
print("\n【22. 实战：异步并发下载模拟】")


async def download_file(filename, size_mb, speed_mbps):
    print(f"  开始下载: {filename} ({size_mb}MB)")
    downloaded = 0
    chunk = speed_mbps * 0.2
    while downloaded < size_mb:
        await asyncio.sleep(0.2)
        downloaded = min(downloaded + chunk, size_mb)
        progress = int(downloaded / size_mb * 20)
        bar = "#" * progress + "-" * (20 - progress)
        print(f"\r  {filename}: [{bar}] {downloaded:.1f}/{size_mb}MB", end="", flush=True)
    print(f"\r  {filename}: [{'#' * 20}] 下载完成!        ")


async def demo_concurrent_download():
    start = time.perf_counter()
    await asyncio.gather(
        download_file("video.mp4", 10, 8),
        download_file("music.mp3", 5, 6),
        download_file("photo.jpg", 3, 4),
    )
    elapsed = time.perf_counter() - start
    print(f"  并发下载总耗时: {elapsed:.1f}s")


asyncio.run(demo_concurrent_download())
print("[OK] 异步并发下载演示完成")

# ============================================================
# 23. 实战：异步生产者-消费者模式
# ============================================================
print("\n【23. 实战：异步生产者-消费者模式】")


async def demo_producer_consumer():
    queue = asyncio.Queue(maxsize=5)

    async def producer(pid):
        for i in range(3):
            item = f"P{pid}-物品{i}"
            await queue.put(item)
            print(f"  [生产] 生产者{pid}: 生产 {item} (队列: {queue.qsize()})")
            await asyncio.sleep(0.3)

    async def consumer(cid):
        for _ in range(6):
            item = await queue.get()
            print(f"  [消费] 消费者{cid}: 消费 {item}")
            await asyncio.sleep(0.5)
            queue.task_done()

    producers = [asyncio.create_task(producer(i)) for i in range(2)]
    consumers = [asyncio.create_task(consumer(i)) for i in range(1)]

    await asyncio.gather(*producers)
    await queue.join()
    for c in consumers:
        c.cancel()
        try:
            await c
        except asyncio.CancelledError:
            pass


asyncio.run(demo_producer_consumer())
print("[OK] 异步生产者-消费者演示完成")

# ============================================================
# 24. asyncio.run() 的注意事项
# ============================================================
print("\n【24. asyncio.run() 注意事项】")
print("  1. asyncio.run() 每次调用会创建新的事件循环，结束时关闭")
print("  2. 不能在已有事件循环中调用 asyncio.run()")
print("  3. 在 Jupyter/IPython 中直接使用 await，不要用 asyncio.run()")
print("  4. asyncio.run() 会自动取消未完成的任务")
print("  5. 推荐使用 asyncio.run() 而非手动管理事件循环")

# ============================================================
# 25. 常用 asyncio 函数速查
# ============================================================
print("\n【25. 常用 asyncio 函数速查】")
print("  +------------------------+--------------------------------------+")
print("  |        函数             |             说明                     |")
print("  +------------------------+--------------------------------------+")
print("  | asyncio.run()          | 运行协程，创建并关闭事件循环          |")
print("  | asyncio.create_task()  | 创建并调度 Task                      |")
print("  | asyncio.gather()       | 并发执行多个协程，收集结果            |")
print("  | asyncio.wait()         | 等待多个任务，支持超时和条件          |")
print("  | asyncio.wait_for()     | 等待单个协程，支持超时                |")
print("  | asyncio.sleep()        | 异步等待(非阻塞)                     |")
print("  | asyncio.Queue()        | 异步队列                             |")
print("  | asyncio.Lock()         | 异步锁                               |")
print("  | asyncio.Event()        | 异步事件                             |")
print("  | asyncio.Condition()    | 异步条件变量                         |")
print("  | asyncio.Semaphore()    | 异步信号量                           |")
print("  | asyncio.timeout()      | 异步超时上下文 (3.11+)               |")
print("  | asyncio.TaskGroup()    | 任务组 (3.11+)                       |")
print("  +------------------------+--------------------------------------+")

print("\n" + "=" * 50)
print("asyncio 异步编程演示完成!")
print("=" * 50)
