# ============================================================
# Python 上下文管理器（Context Manager）学习指南
# ============================================================

# ------------------------------------------------------------
# 1. 什么是上下文管理器？
# ------------------------------------------------------------
# 上下文管理器是 Python 中用于管理"资源获取与释放"的机制。
# 最常见的用法就是 with 语句，它确保资源在使用后能被正确清理，
# 即使发生了异常也不会遗漏清理工作。
#
# 典型场景：文件操作、数据库连接、线程锁、网络连接等。
# 核心思想：不管中间是否出错，"进入"和"退出"总是成对出现。

print("=" * 50)
print("Python 上下文管理器（Context Manager）演示")
print("=" * 50)

# ------------------------------------------------------------
# 2. 最常见的例子：with open()
# ------------------------------------------------------------
# 不用 with 的写法（容易忘记关闭文件）：
#   f = open("test.txt", "w")
#   f.write("hello")
#   f.close()          # 如果 write 抛异常，close 就不会执行！
#
# 用 with 的写法（自动关闭，即使出错也会关闭）：

print("\n【2. with open() -- 最常见的上下文管理器】")

import os

test_file = os.path.join(os.path.dirname(__file__), "_context_test.txt")

with open(test_file, "w", encoding="utf-8") as f:
    f.write("上下文管理器真方便！")
    print(f"  文件是否关闭？写入中: {f.closed}")  # False

print(f"  文件是否关闭？离开with后: {f.closed}")  # True

if os.path.exists(test_file):
    os.remove(test_file)

print("[OK] with open() 演示完成")

# ------------------------------------------------------------
# 3. 自定义上下文管理器 -- 类实现（__enter__ / __exit__）
# ------------------------------------------------------------
# 只需定义两个魔法方法：
#   __enter__(self)  -- 进入 with 时调用，返回值赋给 as 变量
#   __exit__(self, exc_type, exc_val, exc_tb) -- 离开 with 时调用
#       exc_type/exc_val/exc_tb 是异常信息，如果正常退出则全为 None
#       返回 True 表示异常已被处理，不再向外传播
#       返回 False（默认）表示异常继续传播

print("\n【3. 类实现上下文管理器】")


class Timer:
    """计时器上下文管理器，自动测量 with 块的执行时间"""

    def __enter__(self):
        import time
        self.start = time.perf_counter()
        print("  [Timer] 计时开始...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end = time.perf_counter()
        print(f"  [Timer] 计时结束，耗时: {self.end - self.start:.6f} 秒")
        if exc_type is not None:
            print(f"  [!] 捕获到异常: {exc_type.__name__}: {exc_val}")
        return False


with Timer():
    total = sum(range(10_000_00))

print("[OK] 类实现上下文管理器演示完成")

# ------------------------------------------------------------
# 4. __exit__ 处理异常
# ------------------------------------------------------------
# __exit__ 返回 True 时，with 块内的异常会被"吞掉"，不再传播

print("\n【4. __exit__ 处理异常】")


class SafeDivide:
    """安全除法：捕获除零异常，返回 None 而不是崩溃"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ZeroDivisionError:
            print(f"  [SafeDivide] 拦截了异常: {exc_val}，返回 None 代替")
            return True
        return False

    def divide(self, a, b):
        return a / b


with SafeDivide() as sd:
    result = sd.divide(10, 0)
    print(f"  10 / 0 = {result}")

print("[OK] 异常处理演示完成")

# ------------------------------------------------------------
# 5. 自定义上下文管理器 -- 生成器实现（@contextmanager）
# ------------------------------------------------------------
# 用 contextlib.contextmanager 装饰器，把生成器函数变成上下文管理器
# yield 之前 = __enter__，yield 之后 = __exit__
# yield 的值 = as 变量接收的值

print("\n【5. @contextmanager 生成器实现】")

from contextlib import contextmanager


@contextmanager
def tag(name):
    """HTML 标签上下文管理器"""
    print(f"  <{name}>", end=" ")
    yield name
    print(f"</{name}>")


with tag("title"):
    print("Hello Context Manager!", end=" ")

print()
print("[OK] @contextmanager 演示完成")

# ------------------------------------------------------------
# 6. @contextmanager 中处理异常
# ------------------------------------------------------------
# 在 yield 外面加 try/except 即可捕获 with 块内的异常

print("\n【6. @contextmanager 异常处理】")


@contextmanager
def safe_operation(name):
    print(f"  >> 开始操作: {name}")
    try:
        yield
    except Exception as e:
        print(f"  [!] 操作 [{name}] 出错: {e}")
    finally:
        print(f"  [OK] 操作 [{name}] 清理完成")


with safe_operation("危险计算"):
    result = 1 / 0

print("[OK] @contextmanager 异常处理演示完成")

# ------------------------------------------------------------
# 7. contextlib 实用工具
# ------------------------------------------------------------

print("\n【7. contextlib 实用工具】")

# --- 7a. closing() ---
# 把只有 close() 方法的对象变成上下文管理器
from contextlib import closing
from urllib.request import urlopen

print("  --- closing() ---")
print("  closing() 可以把任何有 close() 方法的对象变成上下文管理器")
print("  例如: with closing(urlopen(url)) as page: ...")

# --- 7b. suppress() ---
# 静默忽略指定异常，比 try/except pass 更优雅
from contextlib import suppress

print("  --- suppress() ---")
with suppress(FileNotFoundError):
    os.remove("不存在的文件.txt")
print("  suppress(FileNotFoundError) 静默忽略了文件不存在的异常")

# --- 7c. redirect_stdout / redirect_stderr ---
# 临时重定向标准输出
from contextlib import redirect_stdout
import io

print("  --- redirect_stdout() ---")
buffer = io.StringIO()
with redirect_stdout(buffer):
    print("这行文字被重定向到 buffer 了，不会显示在屏幕上")

captured = buffer.getvalue()
print(f"  从 buffer 中取回: '{captured.strip()}'")

# --- 7d. ExitStack ---
# 动态管理可变数量的上下文管理器
from contextlib import ExitStack

print("  --- ExitStack ---")
with ExitStack() as stack:
    files = [stack.enter_context(open(os.path.join(os.path.dirname(__file__), f"_test_{i}.txt"), "w"))
             for i in range(3)]
    for i, f in enumerate(files):
        f.write(f"文件 {i} 的内容")
    print(f"  同时打开了 {len(files)} 个文件")

for i in range(3):
    path = os.path.join(os.path.dirname(__file__), f"_test_{i}.txt")
    if os.path.exists(path):
        os.remove(path)

print("[OK] contextlib 工具演示完成")

# ------------------------------------------------------------
# 8. 异步上下文管理器（async with）
# ------------------------------------------------------------
# 定义 __aenter__ 和 __aexit__ 即可支持 async with

print("\n【8. 异步上下文管理器】")

import asyncio


class AsyncTimer:
    """异步计时器上下文管理器"""

    async def __aenter__(self):
        self.start = asyncio.get_event_loop().time()
        print("  [AsyncTimer] 异步计时开始...")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end = asyncio.get_event_loop().time()
        print(f"  [AsyncTimer] 异步计时结束，耗时: {self.end - self.start:.6f} 秒")


async def demo_async_context():
    async with AsyncTimer():
        await asyncio.sleep(0.1)


asyncio.run(demo_async_context())
print("[OK] 异步上下文管理器演示完成")

# ------------------------------------------------------------
# 9. 实战示例：数据库连接模拟
# ------------------------------------------------------------

print("\n【9. 实战示例：模拟数据库连接】")


class DatabaseConnection:
    """模拟数据库连接的上下文管理器"""

    def __init__(self, db_name):
        self.db_name = db_name
        self.connected = False

    def __enter__(self):
        print(f"  [DB] 连接数据库 [{self.db_name}]...")
        self.connected = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"  [DB] 断开数据库 [{self.db_name}] 连接")
        self.connected = False
        if exc_type is not None:
            print(f"  [!] 事务回滚（因为异常: {exc_type.__name__}）")
        else:
            print(f"  [OK] 事务提交")
        return False

    def execute(self, sql):
        if not self.connected:
            raise RuntimeError("数据库未连接！")
        print(f"  [SQL] 执行: {sql}")


with DatabaseConnection("mydb") as db:
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("SELECT * FROM users")

print("[OK] 数据库连接模拟演示完成")

# ------------------------------------------------------------
# 10. 实战示例：临时切换工作目录
# ------------------------------------------------------------

print("\n【10. 实战示例：临时切换工作目录】")


@contextmanager
def working_directory(path):
    """临时切换工作目录，退出后自动恢复"""
    old_dir = os.getcwd()
    os.chdir(path)
    print(f"  [CWD] 切换到: {os.getcwd()}")
    try:
        yield
    finally:
        os.chdir(old_dir)
        print(f"  [CWD] 恢复到: {os.getcwd()}")


with working_directory(os.path.dirname(__file__)):
    print(f"  当前目录: {os.getcwd()}")

print("[OK] 临时切换目录演示完成")

# ------------------------------------------------------------
# 总结
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("上下文管理器总结")
print("=" * 50)
print("""
  1. 核心作用：确保资源的获取与释放成对出现，即使发生异常
  2. 类实现：定义 __enter__ 和 __exit__ 方法
  3. 生成器实现：用 @contextmanager 装饰器 + yield
  4. 异步版本：定义 __aenter__ 和 __aexit__，用 async with
  5. contextlib 工具箱：
     - closing()         -> 包装有 close() 方法的对象
     - suppress()        -> 静默忽略指定异常
     - redirect_stdout() -> 临时重定向输出
     - ExitStack         -> 动态管理多个上下文管理器
  6. 最佳实践：
     - 任何需要"配对操作"（打开/关闭、获取/释放、加锁/解锁）
       都应该考虑用上下文管理器
     - 优先使用 with 语句管理资源，不要手动 close()
""")
