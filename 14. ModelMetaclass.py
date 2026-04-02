"""
Python ModelMetaclass 元类学习
================================

元类是"创建类的类"，是 Python 中非常强大的高级特性！
理解元类，就能理解 Django ORM、SQLAlchemy 等框架的魔法 ✨
"""

# ============================================
# 一、Python 类的本质
# ============================================
print("=" * 50)
print("一、Python 类的本质")
print("=" * 50)

print("""
在 Python 中：
- 一切皆对象，类也是对象！
- 类是 type 的实例
- type 是所有类的元类（metaclass）
""")

class SimpleClass:
    pass

obj = SimpleClass()

print(f"obj 是 SimpleClass 的实例: {type(obj).__name__}")
print(f"SimpleClass 是 type 的实例: {type(SimpleClass).__name__}")
print(f"type 是 type 的实例: {type(type).__name__}")

print("\n类的继承链:")
print(f"  obj -> SimpleClass -> type -> object")


# ============================================
# 二、type() 函数动态创建类
# ============================================
print("\n" + "=" * 50)
print("二、type() 函数动态创建类")
print("=" * 50)

print("\n方式1: 普通的类定义")
class Dog1:
    species = "犬科"
    
    def __init__(self, name):
        self.name = name
    
    def bark(self):
        return f"{self.name}: 汪汪！"

dog1 = Dog1("旺财")
print(f"  {dog1.bark()}")

print("\n方式2: 使用 type() 动态创建类")
def dog_init(self, name):
    self.name = name

def dog_bark(self):
    return f"{self.name}: 汪汪！"

Dog2 = type(
    "Dog2",                          # 类名
    (),                              # 继承的父类（元组）
    {                                # 属性和方法（字典）
        "species": "犬科",
        "__init__": dog_init,
        "bark": dog_bark
    }
)

dog2 = Dog2("小黑")
print(f"  {dog2.bark()}")

print("\ntype() 的三种用法:")
print("  1. type(obj)      - 获取对象的类型")
print("  2. type(name, bases, dict) - 动态创建新类")


# ============================================
# 三、什么是元类？
# ============================================
print("\n" + "=" * 50)
print("三、什么是元类？")
print("=" * 50)

print("""
元类（Metaclass）的定义：
- 元类是创建类的"模板"
- 类创建实例对象，元类创建类对象
- 默认的元类是 type

为什么需要元类？
- 在类创建时自动修改类
- 实现ORM映射（如 Django Model）
- 自动添加方法或属性
- 接口检查、注册类等
""")


# ============================================
# 四、自定义元类
# ============================================
print("\n" + "=" * 50)
print("四、自定义元类")
print("=" * 50)

print("\n简单示例: 自动添加类属性")

class AutoNameMeta(type):
    """自动为类添加 __created_by__ 属性的元类"""
    
    def __new__(mcs, name, bases, namespace):
        print(f"  [元类] 正在创建类: {name}")
        namespace["__created_by__"] = "AutoNameMeta"
        namespace["__class_name__"] = name
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

class Animal(metaclass=AutoNameMeta):
    pass

class Cat(Animal):
    def meow(self):
        return "喵喵~"

print(f"\nAnimal.__created_by__ = {Animal.__created_by__}")
print(f"Cat.__class_name__ = {Cat.__class_name__}")
print(f"Cat().meow() = {Cat().meow()}")


# ============================================
# 五、ModelMetaclass 实现原理
# ============================================
print("\n" + "=" * 50)
print("五、ModelMetaclass 实现原理")
print("=" * 50)

print("\n模拟 Django ORM 的简化版 ModelMetaclass:")

class ModelMetaclass(type):
    """
    模型元类 - 模拟 Django ORM 的核心机制
    
    功能:
    1. 收集字段定义
    2. 创建字段映射
    3. 添加便捷方法
    """
    
    def __new__(mcs, name, bases, namespace):
        if name == "Model":
            return super().__new__(mcs, name, bases, namespace)
        
        print(f"\n  [ModelMetaclass] 创建模型: {name}")
        
        fields = {}
        for key, value in list(namespace.items()):
            if not key.startswith("_") and not callable(value):
                fields[key] = value
                print(f"    发现字段: {key} = {value}")
        
        namespace["_fields"] = fields
        namespace["_table_name"] = name.lower()
        
        cls = super().__new__(mcs, name, bases, namespace)
        return cls


class Model(metaclass=ModelMetaclass):
    """基础模型类"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._fields:
                setattr(self, key, value)
    
    def save(self):
        fields = []
        values = []
        for field in self._fields:
            fields.append(field)
            values.append(getattr(self, field, None))
        print(f"    [SQL] INSERT INTO {self._table_name} ({', '.join(fields)}) VALUES ({', '.join(repr(v) for v in values)})")
    
    def __repr__(self):
        attrs = ", ".join(f"{k}={getattr(self, k, None)!r}" for k in self._fields)
        return f"{self.__class__.__name__}({attrs})"


class User(Model):
    """用户模型 - 自动被元类处理"""
    id = None
    name = None
    email = None
    age = None


class Product(Model):
    """商品模型"""
    id = None
    name = None
    price = None

print("\n使用模型:")
user = User(name="小明", email="xiaoming@example.com", age=18)
print(f"  创建用户: {user}")
user.save()

product = Product(name="iPhone", price=6999)
print(f"  创建商品: {product}")
product.save()


# ============================================
# 六、元类的其他应用场景
# ============================================
print("\n" + "=" * 50)
print("六、元类的其他应用场景")
print("=" * 50)

print("\n1. 单例模式:")
class SingletonMeta(type):
    """单例元类"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        print("    初始化数据库连接...")

db1 = Database()
db2 = Database()
print(f"  db1 is db2: {db1 is db2}")

print("\n2. 抽象基类（强制子类实现方法）:")
class AbstractMeta(type):
    """抽象类元类 - 检查子类是否实现了必需方法"""
    
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:
            required = getattr(bases[0], "_abstract_methods", [])
            for method in required:
                if method not in namespace:
                    raise TypeError(f"{name} 必须实现 {method} 方法")
        return cls

class Shape(metaclass=AbstractMeta):
    _abstract_methods = ["area", "perimeter"]

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

rect = Rectangle(4, 5)
print(f"  Rectangle(4, 5).area() = {rect.area()}")

print("\n3. 类注册器:")
class RegistryMeta(type):
    """注册器元类 - 自动注册子类"""
    registry = {}
    
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "Plugin":
            mcs.registry[name.lower()] = cls
            print(f"    注册插件: {name}")
        return cls

class Plugin(metaclass=RegistryMeta):
    pass

class AudioPlugin(Plugin):
    pass

class VideoPlugin(Plugin):
    pass

print(f"  已注册插件: {list(Plugin.registry.keys())}")


# ============================================
# 七、元类 vs 其他技术
# ============================================
print("\n" + "=" * 50)
print("七、元类 vs 其他技术")
print("=" * 50)

print("""
┌─────────────┬────────────────────────────────────┐
│   技术      │           适用场景                  │
├─────────────┼────────────────────────────────────┤
│ 装饰器      │ 修改函数/类，简单直接               │
│ __init_subclass__ │ Python 3.6+，替代简单元类    │
│ 类装饰器    │ 修改已定义的类                      │
│ 元类        │ 控制类的创建过程，最强大            │
└─────────────┴────────────────────────────────────┘

Python 之禅: "元类就是深度的魔法，99%的用户应该根本不必为此操心。"
""")


# ============================================
# 八、__init_subclass__ 替代方案
# ============================================
print("\n" + "=" * 50)
print("八、__init_subclass__ 替代方案（Python 3.6+）")
print("=" * 50)

print("\n使用 __init_subclass__ 可以实现类似效果，更简单:")

class BaseModel:
    """使用 __init_subclass__ 的基类"""
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._fields = {
            k: v for k, v in cls.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }
        print(f"  [__init_subclass__] 处理类: {cls.__name__}, 字段: {list(cls._fields.keys())}")

class Article(BaseModel):
    title = None
    content = None
    author = None

print(f"Article._fields = {Article._fields}")


# ============================================
# 九、注意事项
# ============================================
print("\n" + "=" * 50)
print("九、注意事项")
print("=" * 50)

print("""
1. 元类会继承：
   - 子类会继承父类的元类
   - 多重继承时要注意元类冲突

2. __new__ vs __init__：
   - __new__: 创建类对象，返回类
   - __init__: 初始化类对象，不返回

3. 命名约定：
   - 元类名通常以 Meta 结尾
   - 元类参数通常用 mcs 而非 cls

4. 不要滥用：
   - 能用装饰器/继承解决的，不用元类
   - 元类增加代码复杂度

5. 调试困难：
   - 元类在类定义时就执行
   - 出错时堆栈跟踪可能很复杂
""")

print("\n恭喜你完成 ModelMetaclass 的学习！🎉")
print("现在你理解了 Django ORM 等框架的核心魔法！✨")
