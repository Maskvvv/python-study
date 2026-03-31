"""
Python @property 装饰器学习
============================

@property 可以把一个方法变成属性调用，实现 getter/setter/deleter
让代码更优雅、更安全！
"""

# ============================================
# 一、为什么需要 @property？
# ============================================
print("=" * 50)
print("一、为什么需要 @property？")
print("=" * 50)

print("""
问题场景：
- 想要控制属性的访问（只读、验证等）
- 不想直接暴露属性，但又想用点号访问
- 需要在设置属性时进行验证

@property 的作用：
- 将方法伪装成属性
- 可以实现 getter、setter、deleter
- 代码更优雅，调用更自然
""")


# ============================================
# 二、基本用法 - 只读属性
# ============================================
print("\n" + "=" * 50)
print("二、基本用法 - 只读属性")
print("=" * 50)

class Circle:
    """圆形类 - 演示只读属性"""
    
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        """getter: 获取半径"""
        return self._radius
    
    @property
    def area(self):
        """只读属性: 计算面积（没有setter）"""
        return 3.14159 * self._radius ** 2
    
    @property
    def circumference(self):
        """只读属性: 计算周长"""
        return 2 * 3.14159 * self._radius

circle = Circle(5)
print(f"半径: {circle.radius}")
print(f"面积: {circle.area:.2f}")
print(f"周长: {circle.circumference:.2f}")

print("\n尝试修改只读属性会报错（已注释）:")
print("  circle.area = 100  # AttributeError: can't set attribute")


# ============================================
# 三、完整用法 - getter/setter/deleter
# ============================================
print("\n" + "=" * 50)
print("三、完整用法 - getter/setter/deleter")
print("=" * 50)

class Person:
    """人类 - 演示完整的 property"""
    
    def __init__(self, name, age):
        self._name = name
        self._age = age
    
    @property
    def name(self):
        """getter: 获取名字"""
        print("  [获取名字]")
        return self._name
    
    @name.setter
    def name(self, value):
        """setter: 设置名字"""
        print(f"  [设置名字: {value}]")
        if not isinstance(value, str):
            raise ValueError("名字必须是字符串")
        if len(value) < 2:
            raise ValueError("名字至少2个字符")
        self._name = value
    
    @property
    def age(self):
        """getter: 获取年龄"""
        return self._age
    
    @age.setter
    def age(self, value):
        """setter: 设置年龄（带验证）"""
        if not isinstance(value, int):
            raise ValueError("年龄必须是整数")
        if value < 0 or value > 150:
            raise ValueError("年龄必须在0-150之间")
        self._age = value
    
    @age.deleter
    def age(self):
        """deleter: 删除年龄"""
        print("  [删除年龄]")
        self._age = 0

person = Person("小明", 18)
print(f"姓名: {person.name}")
print(f"年龄: {person.age}")

print("\n修改属性:")
person.name = "小红"
person.age = 20
print(f"新姓名: {person.name}")
print(f"新年龄: {person.age}")

print("\n删除年龄:")
del person.age
print(f"删除后年龄: {person.age}")


# ============================================
# 四、实际应用场景
# ============================================
print("\n" + "=" * 50)
print("四、实际应用场景")
print("=" * 50)

print("\n1. 温度转换器:")
class Celsius:
    """摄氏温度类 - 自动转换华氏温度"""
    
    def __init__(self, temperature=0):
        self._temperature = temperature
    
    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, value):
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度(-273.15°C)")
        self._temperature = value
    
    @property
    def fahrenheit(self):
        """只读: 自动计算华氏温度"""
        return self._temperature * 1.8 + 32

temp = Celsius(25)
print(f"  摄氏: {temp.temperature}°C")
print(f"  华氏: {temp.fahrenheit}°F")

temp.temperature = 100
print(f"  修改后摄氏: {temp.temperature}°C")
print(f"  修改后华氏: {temp.fahrenheit}°F")

print("\n2. 商品价格（带验证）:")
class Product:
    """商品类 - 价格验证"""
    
    def __init__(self, name, price):
        self.name = name
        self._price = 0
        self.price = price
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("价格不能为负数")
        self._price = value
    
    @property
    def price_display(self):
        """只读: 格式化显示价格"""
        return f"¥{self._price:.2f}"

product = Product("苹果", 9.9)
print(f"  商品: {product.name}")
print(f"  价格: {product.price_display}")

product.price = 12.5
print(f"  新价格: {product.price_display}")

print("\n3. 延迟计算属性:")
class Rectangle:
    """矩形类 - 延迟计算面积"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._area = None
    
    @property
    def area(self):
        """延迟计算: 只有访问时才计算"""
        if self._area is None:
            print("  [计算面积...]")
            self._area = self.width * self.height
        return self._area

rect = Rectangle(5, 3)
print(f"  第一次访问面积: {rect.area}")
print(f"  第二次访问面积: {rect.area} (使用缓存)")


# ============================================
# 五、property() 函数写法（了解即可）
# ============================================
print("\n" + "=" * 50)
print("五、property() 函数写法（了解即可）")
print("=" * 50)

class OldStyle:
    """传统写法 - 不推荐"""
    
    def __init__(self, value):
        self._value = value
    
    def get_value(self):
        return self._value
    
    def set_value(self, value):
        self._value = value
    
    def del_value(self):
        del self._value
    
    value = property(get_value, set_value, del_value, "这是value属性")

obj = OldStyle(100)
print(f"  传统写法获取: {obj.value}")
obj.value = 200
print(f"  传统写法修改: {obj.value}")


# ============================================
# 六、注意事项
# ============================================
print("\n" + "=" * 50)
print("六、注意事项")
print("=" * 50)

print("""
1. @property 必须先定义 getter，才能定义 setter/deleter

2. setter/deleter 的方法名必须与 property 名相同

3. 只读属性：只定义 getter，不定义 setter

4. 内部变量命名约定：
   - 使用 _name 表示"受保护的"内部变量
   - 不要与 property 同名，否则会无限递归

5. 性能考虑：
   - 简单属性访问不需要 @property
   - 需要计算/验证时才使用

6. 继承时：
   - 子类可以覆盖 property
   - 使用 super() 调用父类的 property
""")

print("\n恭喜你完成 @property 的学习！🎉")
