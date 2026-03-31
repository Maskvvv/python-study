"""
Python 可变参数学习
=====================

可变参数允许函数接受任意数量的参数，非常灵活实用！
主要有两种形式：*args 和 **kwargs
"""

# ============================================
# 一、*args - 可变位置参数
# ============================================
print("=" * 50)
print("一、*args - 可变位置参数")
print("=" * 50)

def sum_all(*args):
    """接收任意数量的位置参数，求和"""
    total = 0
    for num in args:
        total += num
    return total

print(f"sum_all(1, 2, 3) = {sum_all(1, 2, 3)}")
print(f"sum_all(1, 2, 3, 4, 5) = {sum_all(1, 2, 3, 4, 5)}")
print(f"sum_all() = {sum_all()}")

print("\n*args 本质是一个元组(tuple):")
def show_args(*args):
    print(f"args的类型: {type(args)}")
    print(f"args的内容: {args}")

show_args("hello", "world", 123)


# ============================================
# 二、**kwargs - 可变关键字参数
# ============================================
print("\n" + "=" * 50)
print("二、**kwargs - 可变关键字参数")
print("=" * 50)

def print_info(**kwargs):
    """接收任意数量的关键字参数"""
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print("学生信息:")
print_info(name="小明", age=18, city="北京", score=95)

print("\n**kwargs 本质是一个字典(dict):")
def show_kwargs(**kwargs):
    print(f"kwargs的类型: {type(kwargs)}")
    print(f"kwargs的内容: {kwargs}")

show_kwargs(a=1, b=2, c=3)


# ============================================
# 三、混合使用参数
# ============================================
print("\n" + "=" * 50)
print("三、混合使用参数")
print("=" * 50)

def mixed_params(a, b, *args, **kwargs):
    """
    参数顺序规则:
    1. 普通位置参数
    2. 默认参数
    3. *args
    4. **kwargs
    """
    print(f"  普通参数 a = {a}")
    print(f"  普通参数 b = {b}")
    print(f"  *args = {args}")
    print(f"  **kwargs = {kwargs}")

print("调用 mixed_params(1, 2, 3, 4, name='test', age=20):")
mixed_params(1, 2, 3, 4, name="test", age=20)


# ============================================
# 四、解包参数
# ============================================
print("\n" + "=" * 50)
print("四、解包参数")
print("=" * 50)

def greet(name, age, city):
    print(f"  你好，{name}！你今年{age}岁，来自{city}")

print("使用 * 解包列表/元组:")
info_list = ["小红", 20, "上海"]
greet(*info_list)

print("\n使用 ** 解包字典:")
info_dict = {"name": "小刚", "age": 22, "city": "广州"}
greet(**info_dict)


# ============================================
# 五、实际应用场景
# ============================================
print("\n" + "=" * 50)
print("五、实际应用场景")
print("=" * 50)

print("\n1. 构建URL参数:")
def build_url(base, **params):
    """构建带参数的URL"""
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}?{query}"
    return base

url = build_url("https://api.example.com/search", q="python", page=1, size=10)
print(f"  {url}")

print("\n2. 计算平均值:")
def average(*numbers):
    """计算任意数量数字的平均值"""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

print(f"  average(1, 2, 3, 4, 5) = {average(1, 2, 3, 4, 5)}")
print(f"  average(10, 20) = {average(10, 20)}")

print("\n3. 日志记录函数:")
def log_message(level, *messages, **metadata):
    """灵活的日志函数"""
    msg = " ".join(str(m) for m in messages)
    print(f"  [{level}] {msg}")
    if metadata:
        print(f"  元数据: {metadata}")

log_message("INFO", "用户登录成功", "用户ID:", 12345, ip="192.168.1.1", device="mobile")


# ============================================
# 六、注意事项
# ============================================
print("\n" + "=" * 50)
print("六、注意事项")
print("=" * 50)

print("""
1. 参数顺序必须遵循：
   位置参数 -> 默认参数 -> *args -> **kwargs

2. *args 和 **kwargs 可以是任意名称，但约定俗成使用这两个名字

3. 一个函数只能有一个 *args 和一个 **kwargs

4. 使用解包时，元素数量要匹配函数参数数量
""")

print("\n恭喜你完成可变参数的学习！🎉")
