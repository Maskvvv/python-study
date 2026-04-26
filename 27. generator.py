
# ============================================================
# Python 生成器（Generator）学习指南
# ============================================================

# ------------------------------------------------------------
# 1. 什么是生成器？
# ------------------------------------------------------------
# 生成器是一种特殊的迭代器，它不会一次性把所有结果存入内存，
# 而是每次只生成一个值，做到"按需计算、惰性求值"。
# 适合处理大量数据或无限序列，节省内存。

# ------------------------------------------------------------
# 2. 生成器表达式（最简单的生成器）
# ------------------------------------------------------------
# 把列表推导式的 [] 换成 () 就得到了生成器表达式

print("--- 生成器表达式 ---")

g = (x * x for x in range(5))
print(type(g))          # <class 'generator'>
print(next(g))          # 0
print(next(g))          # 1
print(next(g))          # 4

for val in g:
    print(val)          # 9, 16  (剩余的值)

# next() 超出范围会抛出 StopIteration
# for 循环会自动处理 StopIteration

# ------------------------------------------------------------
# 3. yield 关键字 —— 生成器函数
# ------------------------------------------------------------
# 含有 yield 的函数不再是普通函数，调用它不会执行函数体，
# 而是返回一个生成器对象。每次 next() 执行到 yield 暂停，
# 并返回 yield 后面的值；下次 next() 从暂停处继续。

print("\n--- yield 基础 ---")

def simple_gen():
    print("step 1")
    yield 10
    print("step 2")
    yield 20
    print("step 3")
    yield 30

g = simple_gen()
print(next(g))   # step 1 → 10
print(next(g))   # step 2 → 20
print(next(g))   # step 3 → 30

# ------------------------------------------------------------
# 4. 用生成器实现斐波那契数列
# ------------------------------------------------------------

print("\n--- 斐波那契生成器 ---")

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num, end=" ")
print()

# 对比：如果用列表返回，n 很大时会占用大量内存
# 生成器无论 n 多大，内存占用几乎不变

# ------------------------------------------------------------
# 5. 生成器方法：send()、throw()、close()
# ------------------------------------------------------------

print("\n--- send() 方法 ---")

# send() 可以向生成器内部传值，yield 表达式的返回值就是 send 传入的值
# 第一次必须 send(None) 或 next() 启动生成器

def echo_gen():
    while True:
        received = yield
        print(f"received: {received}")

g = echo_gen()
next(g)          # 启动生成器，执行到第一个 yield 暂停
g.send("hello")  # received: hello
g.send("world")  # received: world
g.close()        # 关闭生成器

# send() 带返回值的例子
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value

g = accumulator()
print(next(g))       # 0  （启动，yield 返回 total=0）
print(g.send(10))    # 10
print(g.send(20))    # 30
print(g.send(5))     # 35

# ------------------------------------------------------------
# 6. throw() 与 close()
# ------------------------------------------------------------

print("\n--- throw() 与 close() ---")

def risky_gen():
    try:
        yield 1
        yield 2
        yield 3
    except ValueError:
        print("ValueError caught inside generator!")
        yield 99

g = risky_gen()
print(next(g))           # 1
print(g.throw(ValueError))  # ValueError caught inside generator! → 99

# close() 会在生成器内部抛出 GeneratorExit
g2 = risky_gen()
print(next(g2))          # 1
g2.close()               # 关闭，后续 next() 会抛出 StopIteration

# ------------------------------------------------------------
# 7. yield from —— 委托给子生成器
# ------------------------------------------------------------

print("\n--- yield from ---")

# yield from 让生成器可以把部分操作委托给另一个可迭代对象/生成器

def sub_gen():
    yield 10
    yield 20

def main_gen():
    yield 1
    yield from sub_gen()   # 委托给 sub_gen
    yield 3

for v in main_gen():
    print(v, end=" ")      # 1 10 20 3
print()

# yield from 还能获取子生成器的返回值
def sub_gen_with_return():
    yield 100
    return "sub done"

def main_gen_with_return():
    result = yield from sub_gen_with_return()
    print(f"sub_gen returned: {result}")
    yield 200

for v in main_gen_with_return():
    print(v, end=" ")      # 100  sub_gen returned: sub done  200
print()

# ------------------------------------------------------------
# 8. 生成器管道（Pipeline）
# ------------------------------------------------------------

print("\n--- 生成器管道 ---")

# 多个生成器可以像管道一样串联，每一步惰性处理

def read_numbers():
    for i in range(1, 8):
        yield i

def filter_even(source):
    for n in source:
        if n % 2 == 0:
            yield n

def square(source):
    for n in source:
        yield n * n

pipeline = square(filter_even(read_numbers()))
print(list(pipeline))   # [4, 16, 36]

# ------------------------------------------------------------
# 9. 实战：用生成器读取大文件
# ------------------------------------------------------------

print("\n--- 大文件逐行读取示例 ---")

# 模拟一个逐行读取文件的生成器
def read_large_file(lines):
    for line in lines:
        yield line.strip()

mock_lines = ["line 1\n", "line 2\n", "line 3\n"]
for line in read_large_file(mock_lines):
    print(f"processed: {line}")

# 真实场景：
# with open("huge_file.txt") as f:
#     for line in f:          # 文件对象本身就是生成器
#         process(line)

# ------------------------------------------------------------
# 10. 生成器 vs 列表 对比
# ------------------------------------------------------------

print("\n--- 生成器 vs 列表 ---")

import sys

lst = [x * x for x in range(1000)]
gen = (x * x for x in range(1000))

print(f"列表占用内存: {sys.getsizeof(lst)} bytes")
print(f"生成器占用内存: {sys.getsizeof(gen)} bytes")

# 列表可以反复遍历，生成器只能遍历一次
# 列表支持索引/切片，生成器不支持
# 列表立即计算所有值，生成器惰性求值

# ------------------------------------------------------------
# 11. itertools 中的生成器工具
# ------------------------------------------------------------

print("\n--- itertools 生成器工具 ---")

from itertools import count, cycle, islice, chain

# count: 无限计数器
for i in islice(count(1), 5):
    print(i, end=" ")    # 1 2 3 4 5
print()

# cycle: 无限循环
for item in islice(cycle("ABC"), 7):
    print(item, end=" ")  # A B C A B C A
print()

# chain: 串联多个可迭代对象
for v in chain([1, 2], (3, 4), "ab"):
    print(v, end=" ")     # 1 2 3 4 a b
print()

# ------------------------------------------------------------
# 12. 总结
# ------------------------------------------------------------
# ✅ 生成器表达式: (expr for x in iterable)
# ✅ 生成器函数:   含 yield 的函数
# ✅ yield:        暂停并返回值，下次从暂停处继续
# ✅ send():       向生成器内部传值
# ✅ yield from:   委托子生成器
# ✅ 优势:         节省内存、惰性求值、可表示无限序列
# ✅ 注意:         生成器只能遍历一次，遍历后即耗尽
