# ============================================================
# Python @dataclass 学习指南
# ============================================================

# ------------------------------------------------------------
# 1. 什么是 dataclass？
# ------------------------------------------------------------
# dataclass 是 Python 3.7+ 引入的一个装饰器，来自 dataclasses 模块
# 它可以自动为我们生成那些"又长又无聊"的特殊方法：
#   - __init__   → 构造函数
#   - __repr__   → 打印/调试时的字符串表示
#   - __eq__     → 相等比较 (==)
#   - __hash__   → 哈希值（当 frozen=True 时自动生成）
#   - __lt__ 等  → 比较操作（当 order=True 时自动生成）
#
# 为什么用 dataclass？
#   - 少写大量样板代码，让类定义更简洁
#   - 比 __init__ 手写更不容易出错
#   - 比 namedtuple 更灵活（支持默认值、方法、继承）
#   - 比 Pydantic 更轻量（不需要额外安装，但无验证功能）
#   - Python 标准库自带，零依赖！

print("=" * 50)
print("Python @dataclass 演示")
print("=" * 50)

# ------------------------------------------------------------
# 2. 最基本的用法：对比普通类 vs dataclass
# ------------------------------------------------------------
# 先看普通类要写多少代码……

print("\n【2. 普通类 vs dataclass】")


class UserOldStyle:
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self):
        return f"UserOldStyle(name={self.name!r}, age={self.age!r}, email={self.email!r})"

    def __eq__(self, other):
        if not isinstance(other, UserOldStyle):
            return NotImplemented
        return (self.name, self.age, self.email) == (other.name, other.age, other.email)


# 再看 dataclass —— 一行装饰器搞定！

from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
    email: str


user1 = User(name="小明", age=18, email="xiaoming@example.com")
print(f"  自动 __init__: {user1}")
print(f"  自动 __eq__:   {User('小明', 18, 'a@b.com') == User('小明', 18, 'a@b.com')}")
print(f"  普通类对比:     {UserOldStyle('小明', 18, 'a@b.com') == UserOldStyle('小明', 18, 'a@b.com')}")

print("[OK] 普通类 vs dataclass 演示完成")

# ------------------------------------------------------------
# 3. 默认值
# ------------------------------------------------------------
# 和普通函数参数一样，有默认值的字段必须放在没有默认值的字段后面
# 注意：默认值不能是可变对象（如 list、dict），必须用 field(default_factory=...)

print("\n【3. 默认值】")


@dataclass
class Product:
    name: str
    price: float = 0.0
    in_stock: bool = True


p1 = Product(name="键盘")
print(f"  只传 name: {p1}")

p2 = Product(name="鼠标", price=99.9, in_stock=False)
print(f"  全部传入: {p2}")

print("[OK] 默认值演示完成")

# ------------------------------------------------------------
# 4. field() 函数详解
# ------------------------------------------------------------
# field() 是 dataclass 中最灵活的工具，可以精细控制每个字段：
#   - default          → 默认值
#   - default_factory  → 默认值工厂（用于可变默认值）
#   - repr             → 是否出现在 __repr__ 中
#   - compare          → 是否参与 __eq__ 和比较
#   - hash             → 是否参与 __hash__
#   - metadata         → 自定义元数据
#   - kw_only          → 是否只能通过关键字参数传入

print("\n【4. field() 函数详解】")

from dataclasses import field


@dataclass
class Student:
    name: str
    scores: list[float] = field(default_factory=list)
    _internal_id: int = field(default=0, repr=False)
    nickname: str = field(default="", compare=False)


s1 = Student(name="小明")
print(f"  默认 scores: {s1.scores}")
print(f"  _internal_id 不出现在 repr 中: {s1}")

s2 = Student(name="小红", scores=[90, 85, 92], nickname="红红")
s3 = Student(name="小刚", scores=[88, 79], nickname="刚子")
print(f"  nickname 不参与比较: s2 == s3 → {s2 == s3}")
print(f"  （只比较 name 和 scores，nickname 被忽略）")

s1.scores.append(100)
s2.scores.append(95)
print(f"  每个实例的 scores 是独立的: s1.scores={s1.scores}, s2.scores={s2.scores}")

print("[OK] field() 函数详解演示完成")

# ------------------------------------------------------------
# 5. 可变默认值的陷阱 (WARNING)
# ------------------------------------------------------------
# Python 中类属性的默认值是共享的！
# 如果直接写 tags: list = []，所有实例会共享同一个列表！
# dataclass 会检测到这种情况并抛出 TypeError
# 正确做法：使用 field(default_factory=list)

print("\n【5. 可变默认值的陷阱】")

# 错误写法（dataclass 会阻止你）：
# @dataclass
# class BadExample:
#     items: list = []  # TypeError: mutable default <class 'list'> for field items is not allowed

# 正确写法：


@dataclass
class GoodExample:
    items: list[str] = field(default_factory=list)


a = GoodExample()
b = GoodExample()
a.items.append("A的物品")
b.items.append("B的物品")
print(f"  a.items = {a.items}")
print(f"  b.items = {b.items}")
print(f"  互不影响!")

print("[OK] 可变默认值的陷阱演示完成")

# ------------------------------------------------------------
# 6. __post_init__ 初始化后钩子
# ------------------------------------------------------------
# __post_init__ 在 __init__ 执行完毕后自动调用
# 常用于：
#   - 根据其他字段计算派生属性
#   - 执行初始化后的验证逻辑
#   - 初始化不能作为字段的复杂对象

print("\n【6. __post_init__】")


@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)
    perimeter: float = field(init=False)

    def __post_init__(self):
        self.area = self.width * self.height
        self.perimeter = 2 * (self.width + self.height)


rect = Rectangle(width=3, height=4)
print(f"  矩形: {rect.width} x {rect.height}")
print(f"  面积: {rect.area}")
print(f"  周长: {rect.perimeter}")

print("[OK] __post_init__ 演示完成")

# ------------------------------------------------------------
# 7. init=False —— 不在构造函数中的字段
# ------------------------------------------------------------
# field(init=False) 的字段不会出现在 __init__ 参数中
# 通常配合 __post_init__ 或直接赋默认值使用

print("\n【7. init=False 字段】")


@dataclass
class Counter:
    name: str
    count: int = field(init=False, default=0)

    def increment(self):
        self.count += 1


counter = Counter(name="访问计数")
print(f"  创建时: {counter}")
counter.increment()
counter.increment()
counter.increment()
print(f"  三次 increment 后: {counter}")

print("[OK] init=False 字段演示完成")

# ------------------------------------------------------------
# 8. frozen=True —— 不可变 dataclass
# ------------------------------------------------------------
# frozen=True 让实例变成不可变的（像 namedtuple 一样）
# 尝试修改属性会抛出 FrozenInstanceError
# frozen 的 dataclass 是可哈希的，可以作为 dict 的 key 或放入 set

print("\n【8. frozen=True 不可变 dataclass】")


@dataclass(frozen=True)
class Point:
    x: float
    y: float


p = Point(x=1.0, y=2.0)
print(f"  Point: {p}")
print(f"  可哈希: hash(p) = {hash(p)}")
print(f"  可作为 dict key: {{{p}: '原点'}}")

try:
    p.x = 999
except Exception as e:
    print(f"  尝试修改 frozen 实例: {type(e).__name__}: {e}")

points_set = {Point(1, 2), Point(3, 4), Point(1, 2)}
print(f"  放入 set 自动去重: {points_set}")

print("[OK] frozen=True 演示完成")

# ------------------------------------------------------------
# 9. order=True —— 自动生成比较方法
# ------------------------------------------------------------
# order=True 会自动生成 __lt__, __le__, __gt__, __ge__
# 比较按照字段定义的顺序逐个比较
# 注意：order=True 和 frozen=True 经常搭配使用

print("\n【9. order=True 自动比较】")


@dataclass(order=True)
class Score:
    math: int
    english: int
    chinese: int


s1 = Score(math=90, english=80, chinese=85)
s2 = Score(math=90, english=85, chinese=70)
s3 = Score(math=85, english=90, chinese=95)

print(f"  s1: {s1}")
print(f"  s2: {s2}")
print(f"  s3: {s3}")
print(f"  s1 < s2: {s1 < s2}  (先比 math，相同再比 english)")
print(f"  排序: {sorted([s1, s2, s3])}")

print("[OK] order=True 演示完成")

# ------------------------------------------------------------
# 10. 继承
# ------------------------------------------------------------
# dataclass 支持继承，子类会继承父类的所有字段
# 注意：父类字段排在子类字段前面
# 有默认值的字段不能出现在没有默认值的字段前面（跨继承也适用）

print("\n【10. 继承】")


@dataclass
class Animal:
    name: str
    age: int


@dataclass
class Dog(Animal):
    breed: str
    is_good_boy: bool = True


dog = Dog(name="旺财", age=3, breed="柴犬")
print(f"  继承: {dog}")
print(f"  父类字段: name={dog.name}, age={dog.age}")
print(f"  子类字段: breed={dog.breed}, is_good_boy={dog.is_good_boy}")

print("[OK] 继承演示完成")

# ------------------------------------------------------------
# 11. 添加方法
# ------------------------------------------------------------
# dataclass 就是一个普通的类，可以随意添加方法

print("\n【11. 添加方法】")


@dataclass
class BankAccount:
    owner: str
    balance: float = 0.0

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("存款金额必须大于0")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("余额不足")
        self.balance -= amount
        return self.balance

    def __str__(self):
        return f"{self.owner} 的账户余额: {self.balance:.2f}元"


acc = BankAccount(owner="小明", balance=1000)
print(f"  {acc}")
acc.deposit(500)
print(f"  存入500后: {acc}")
acc.withdraw(200)
print(f"  取出200后: {acc}")
print(f"  repr: {acc!r}")

print("[OK] 添加方法演示完成")

# ------------------------------------------------------------
# 12. dataclass 转换工具
# ------------------------------------------------------------
# dataclasses 模块提供了几个实用的转换函数：
#   - asdict()      → 转为字典（递归）
#   - astuple()     → 转为元组（递归）
#   - replace()     → 创建副本并修改部分字段

print("\n【12. 转换工具】")

from dataclasses import asdict, astuple, replace


@dataclass
class Book:
    title: str
    author: str
    price: float


book = Book(title="Python编程", author="小明", price=59.9)

print(f"  asdict():  {asdict(book)}")
print(f"  astuple(): {astuple(book)}")

book2 = replace(book, price=49.9, title="Python编程（第2版）")
print(f"  replace() 修改价格和标题: {book2}")
print(f"  原始 book 不受影响: {book}")

print("[OK] 转换工具演示完成")

# ------------------------------------------------------------
# 13. kw_only —— 强制关键字参数
# ------------------------------------------------------------
# kw_only=True 让所有字段只能通过关键字参数传入
# 也可以在 field() 中对单个字段设置 kw_only

print("\n【13. kw_only 关键字参数】")


@dataclass(kw_only=True)
class Config:
    host: str
    port: int = 8080
    debug: bool = False


# cfg = Config("localhost")  # TypeError: 必须用关键字参数
cfg = Config(host="localhost")
print(f"  必须用关键字: {cfg}")

# 单个字段 kw_only


@dataclass
class MixedConfig:
    name: str
    host: str = field(kw_only=True)
    port: int = field(kw_only=True, default=3306)


mc = MixedConfig("数据库", host="localhost")
print(f"  混合模式: {mc}")

print("[OK] kw_only 演示完成")

# ------------------------------------------------------------
# 14. slots=True —— 节省内存
# ------------------------------------------------------------
# Python 3.10+ 支持 slots=True
# 使用 __slots__ 代替 __dict__ 存储属性
# 好处：内存占用更小，属性访问更快
# 限制：不能动态添加新属性

print("\n【14. slots=True】")


@dataclass(slots=True)
class FastPoint:
    x: float
    y: float


fp = FastPoint(x=1.0, y=2.0)
print(f"  slots 实例: {fp}")

try:
    fp.z = 3.0
except AttributeError as e:
    print(f"  不能动态添加属性: {e}")

print("[OK] slots=True 演示完成")

# ------------------------------------------------------------
# 15. match_args —— 位置模式匹配
# ------------------------------------------------------------
# Python 3.10+ 的 match/case 语法支持
# match_args=True（默认）会生成 __match_args__ 元组
# 使得 dataclass 可以在 match 语句中按位置匹配

print("\n【15. match_args 与模式匹配】")


@dataclass
class Command:
    action: str
    target: str


cmd = Command(action="delete", target="temp_file")

match cmd:
    case Command(action="create", target=t):
        print(f"  创建: {t}")
    case Command(action="delete", target=t):
        print(f"  删除: {t}")
    case _:
        print(f"  未知命令")

print("[OK] match_args 演示完成")

# ------------------------------------------------------------
# 16. 嵌套 dataclass
# ------------------------------------------------------------
# dataclass 可以嵌套使用，asdict/astuple 会递归处理

print("\n【16. 嵌套 dataclass】")


@dataclass
class Address:
    city: str
    street: str


@dataclass
class Person:
    name: str
    age: int
    address: Address


addr = Address(city="北京", street="长安街1号")
person = Person(name="张三", age=30, address=addr)
print(f"  嵌套: {person}")
print(f"  asdict 递归: {asdict(person)}")
print(f"  访问内嵌字段: {person.address.city}")

print("[OK] 嵌套 dataclass 演示完成")

# ------------------------------------------------------------
# 17. dataclass vs Pydantic vs namedtuple vs 普通类
# ------------------------------------------------------------
# 选择指南：

print("\n【17. dataclass vs 其他方案对比】")

from collections import namedtuple

# namedtuple
PointNT = namedtuple("PointNT", ["x", "y"])
pnt = PointNT(x=1, y=2)

# dataclass
@dataclass(frozen=True)
class PointDC:
    x: float
    y: float

pdc = PointDC(x=1, y=2)

# Pydantic
from pydantic import BaseModel


class PointPydantic(BaseModel):
    x: float
    y: float


ppyd = PointPydantic(x=1, y=2)

print(f"  namedtuple: {pnt}")
print(f"  dataclass:  {pdc}")
print(f"  Pydantic:   {ppyd}")

print("""
  对比表：
  +--------------+-----------+-----------+-----------+-----------+
  | 特性         | namedtuple| dataclass | Pydantic  | 普通类    |
  +--------------+-----------+-----------+-----------+-----------+
  | 样板代码     | 极少      | 很少      | 很少      | 很多      |
  | 不可变       | 默认不可变| frozen=T  | frozen=T  | 需手写    |
  | 默认值       | 不支持    | 支持      | 支持      | 支持      |
  | 方法         | 不支持    | 支持      | 支持      | 支持      |
  | 类型验证     | 无        | 无        | 有!       | 需手写    |
  | 自动转换     | 无        | 无        | 有!       | 无        |
  | 序列化       | _asdict() | asdict()  | model_dump| 需手写    |
  | 额外依赖     | 无(标准库)| 无(标准库)| 需安装    | 无        |
  | 性能         | 最快      | 快        | 较快(Rust)| 取决于实现|
  +--------------+-----------+-----------+-----------+-----------+

  选择建议：
    - 只需要简单的不可变数据容器 -> namedtuple
    - 需要默认值、方法、继承，不需要验证 -> dataclass (推荐)
    - 需要数据验证、自动转换、序列化 -> Pydantic
    - 需要完全控制所有行为 -> 普通类
""")

print("[OK] 对比演示完成")

# ------------------------------------------------------------
# 18. 实战：用 dataclass 构建配置系统
# ------------------------------------------------------------

print("\n【18. 实战：配置系统】")


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "mydb"
    user: str = "admin"
    password: str = ""
    max_connections: int = field(default=10, repr=False)


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False


@dataclass
class AppConfig:
    app_name: str = "MyApp"
    version: str = "1.0.0"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    def __post_init__(self):
        if self.server.debug:
            print(f"  [DEBUG] 调试模式已启用")


default_config = AppConfig()
print(f"  默认配置:")
print(f"    数据库: {default_config.database}")
print(f"    服务器: {default_config.server}")

custom_config = AppConfig(
    app_name="生产环境",
    database=DatabaseConfig(host="db.example.com", password="secret123"),
    server=ServerConfig(port=443),
)
print(f"  自定义配置:")
print(f"    应用: {custom_config.app_name}")
print(f"    数据库: {custom_config.database}")
print(f"    服务器: {custom_config.server}")

print("[OK] 配置系统实战演示完成")

# ------------------------------------------------------------
# 19. dataclass 参数一览表
# ------------------------------------------------------------
print("\n【19. @dataclass 参数一览】")
print("""
  @dataclass(
      init=True,          # 是否生成 __init__
      repr=True,          # 是否生成 __repr__
      eq=True,            # 是否生成 __eq__
      order=False,        # 是否生成 __lt__, __le__, __gt__, __ge__
      unsafe_hash=False,  # 是否生成 __hash__（即使实例可变）
      frozen=False,       # 是否让实例不可变
      match_args=True,    # 是否生成 __match_args__（3.10+）
      kw_only=False,      # 是否强制所有字段用关键字参数（3.10+）
      slots=False,        # 是否使用 __slots__（3.10+）
      weakref_slot=False, # 是否添加 __weakref__ 槽位（3.11+）
  )
""")

# ------------------------------------------------------------
# 总结
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("@dataclass 学习总结")
print("=" * 50)
print("""
  核心概念：
    @dataclass         → 装饰器，自动生成特殊方法
    field()            → 精细控制单个字段
    __post_init__      → 初始化后钩子

  常用参数：
    frozen=True        → 不可变 + 可哈希
    order=True         → 自动比较方法
    slots=True         → 节省内存（3.10+）
    kw_only=True       → 强制关键字参数（3.10+）

  转换工具：
    asdict(obj)        → 转字典（递归）
    astuple(obj)       → 转元组（递归）
    replace(obj, ...)  → 创建修改副本

  field() 常用参数：
    default            → 默认值
    default_factory    → 可变默认值的工厂函数
    init=False         → 不在构造函数中
    repr=False         → 不在 __repr__ 中
    compare=False      → 不参与比较
    hash=False         → 不参与哈希
    kw_only=True       → 只能关键字传入

  适用场景：
    [v] 数据容器类（替代手写 __init__）
    [v] 配置类
    [v] 值对象（frozen=True）
    [v] 不需要验证的简单数据模型
    [v] 作为 Pydantic 的轻量替代（无验证需求时）
""")
