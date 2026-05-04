# ============================================================
# Python Pydantic 模块学习指南
# ============================================================

# ------------------------------------------------------------
# 1. 什么是 Pydantic？
# ------------------------------------------------------------
# Pydantic 是 Python 中最流行的数据验证库，使用 Python 类型注解来：
#   - 声明数据的"形状"（schema）
#   - 自动验证传入的数据是否符合预期类型
#   - 自动将数据转换（coerce）为目标类型
#   - 生成清晰的错误信息
#   - 序列化模型为 JSON / dict
#
# 为什么用 Pydantic？
#   - FastAPI 的核心依赖，几乎所有 FastAPI 项目都在用
#   - 比 dataclass 更强大：自动验证 + 转换 + 序列化
#   - 性能极高：核心用 Rust 编写（pydantic-core）
#   - IDE 支持极好：基于类型注解，补全和检查都很棒

print("=" * 50)
print("Python Pydantic 模块演示")
print("=" * 50)

# ------------------------------------------------------------
# 2. 最基本的模型
# ------------------------------------------------------------
# BaseModel 是 Pydantic 的核心基类
# 只需定义带类型注解的属性，就自动拥有了验证能力

print("\n【2. 基本 Model】")

from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str


user = User(name="小明", age=18, email="xiaoming@example.com")
print(f"  user.name  = {user.name}")
print(f"  user.age   = {user.age}")
print(f"  user.email = {user.email}")
print(f"  user.model_dump() = {user.model_dump()}")

print("[OK] 基本 Model 演示完成")

# ------------------------------------------------------------
# 3. 自动类型转换（Coercion）
# ------------------------------------------------------------
# Pydantic 会尽可能将输入数据转换为目标类型
# 比如字符串 "18" 传给 int 字段，会自动转为 18
# 这在处理表单数据、API 请求时非常实用

print("\n【3. 自动类型转换】")

user2 = User(name="小红", age="20", email="hong@example.com")
print(f'  传入 age="20" (str)，实际 user2.age = {user2.age} (type={type(user2.age).__name__})')

print("[OK] 自动类型转换演示完成")

# ------------------------------------------------------------
# 4. 验证失败与错误信息
# ------------------------------------------------------------
# 当数据无法转换或不符合约束时，Pydantic 会抛出 ValidationError
# 错误信息非常详细，指出了哪个字段、什么问题、输入了什么

print("\n【4. 验证失败与错误信息】")

from pydantic import ValidationError

try:
    User(name="小刚", age="不是数字", email="gang@example.com")
except ValidationError as e:
    print(f"  验证失败！错误信息：")
    for error in e.errors():
        print(f"    字段: {'.'.join(str(x) for x in error['loc'])}")
        print(f"    错误: {error['msg']}")
        print(f"    输入: {error['input']}")
        print()

print("[OK] 验证失败演示完成")

# ------------------------------------------------------------
# 5. 可选字段与默认值
# ------------------------------------------------------------
# Optional[str] = None  → 字段可以不传，默认为 None
# str = "默认值"        → 字段可以不传，默认为指定值
# 不设默认值            → 字段必传，否则报错

print("\n【5. 可选字段与默认值】")

from typing import Optional


class UserProfile(BaseModel):
    name: str
    age: int = 0
    bio: Optional[str] = None
    is_active: bool = True


profile1 = UserProfile(name="小华")
print(f"  只传 name: {profile1.model_dump()}")

profile2 = UserProfile(name="小华", age=25, bio="热爱编程", is_active=False)
print(f"  全部传入: {profile2.model_dump()}")

print("[OK] 可选字段与默认值演示完成")

# ------------------------------------------------------------
# 6. 字段验证器 Field
# ------------------------------------------------------------
# Field() 可以为字段添加约束和元数据：
#   - gt / ge / lt / le  → 数值大小限制
#   - min_length / max_length → 字符串长度限制
#   - pattern → 正则表达式验证
#   - description → 字段描述（用于生成文档）

print("\n【6. Field 字段约束】")

from pydantic import Field


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="商品名称")
    price: float = Field(gt=0, description="商品价格，必须大于0")
    stock: int = Field(ge=0, description="库存数量，不能为负数")


product = Product(name="Python编程书", price=59.9, stock=100)
print(f"  合法商品: {product.model_dump()}")

try:
    Product(name="", price=-10, stock=-5)
except ValidationError as e:
    print(f"  非法商品验证失败：")
    for error in e.errors():
        print(f"    {'.'.join(str(x) for x in error['loc'])}: {error['msg']}")

print("[OK] Field 字段约束演示完成")

# ------------------------------------------------------------
# 7. 模型嵌套
# ------------------------------------------------------------
# Pydantic 模型可以嵌套使用，构建复杂的数据结构
# 内嵌模型同样会自动验证

print("\n【7. 模型嵌套】")


class Address(BaseModel):
    city: str
    street: str
    zip_code: str


class Employee(BaseModel):
    name: str
    age: int
    address: Address


emp = Employee(
    name="张三",
    age=30,
    address={"city": "北京", "street": "长安街1号", "zip_code": "100000"},
)
print(f"  嵌套模型: {emp.model_dump()}")
print(f"  直接访问内嵌字段: emp.address.city = {emp.address.city}")

print("[OK] 模型嵌套演示完成")

# ------------------------------------------------------------
# 8. 列表与字典类型
# ------------------------------------------------------------
# Pydantic 支持 list[T]、dict[K, V] 等泛型类型
# 列表中的每个元素都会被逐一验证

print("\n【8. 列表与字典类型】")


class Classroom(BaseModel):
    name: str
    students: list[str]
    scores: dict[str, float]


cls = Classroom(
    name="三年二班",
    students=["小明", "小红", "小刚"],
    scores={"小明": 95.5, "小红": 88.0, "小刚": 72.5},
)
print(f"  班级: {cls.name}")
print(f"  学生: {cls.students}")
print(f"  成绩: {cls.scores}")

print("[OK] 列表与字典类型演示完成")

# ------------------------------------------------------------
# 9. model_validator 模型级验证器
# ------------------------------------------------------------
# 当验证逻辑涉及多个字段之间的关系时，使用 model_validator
# mode='after' 表示在所有字段验证通过之后执行

print("\n【9. model_validator 模型级验证】")

from pydantic import model_validator


class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def check_date_order(self):
        if self.start_date > self.end_date:
            raise ValueError("开始日期不能晚于结束日期")
        return self


valid_range = DateRange(start_date="2024-01-01", end_date="2024-12-31")
print(f"  合法日期范围: {valid_range.start_date} ~ {valid_range.end_date}")

try:
    DateRange(start_date="2024-12-31", end_date="2024-01-01")
except ValidationError as e:
    print(f"  非法日期范围: {e.errors()[0]['msg']}")

print("[OK] model_validator 演示完成")

# ------------------------------------------------------------
# 10. field_validator 字段验证器
# ------------------------------------------------------------
# field_validator 用于对单个字段进行自定义验证
# 比 Field() 的约束更灵活，可以写任意验证逻辑

print("\n【10. field_validator 字段验证器】")

from pydantic import field_validator


class PasswordForm(BaseModel):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("密码长度至少8位")
        if not any(c.isupper() for c in v):
            raise ValueError("密码必须包含大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v


try:
    PasswordForm(username="admin", password="123")
except ValidationError as e:
    print(f"  弱密码验证失败: {e.errors()[0]['msg']}")

strong = PasswordForm(username="admin", password="Secure123")
print(f"  强密码验证通过: username={strong.username}")

print("[OK] field_validator 演示完成")

# ------------------------------------------------------------
# 11. 序列化 model_dump / model_dump_json
# ------------------------------------------------------------
# model_dump()       → 转为 dict
# model_dump_json()  → 转为 JSON 字符串
# 还可以用 exclude / include 控制输出哪些字段

print("\n【11. 序列化】")

import json


class Article(BaseModel):
    title: str
    content: str
    author: str
    views: int = 0


article = Article(title="Pydantic入门", content="Pydantic真好用！", author="小明", views=100)

print(f"  model_dump()         = {article.model_dump()}")
print(f"  model_dump(exclude)  = {article.model_dump(exclude={'views'})}")
print(f"  model_dump_json()    = {article.model_dump_json()}")
print(f"  JSON 格式化输出:")
print(f"    {json.dumps(article.model_dump(), ensure_ascii=False, indent=2)}")

print("[OK] 序列化演示完成")

# ------------------------------------------------------------
# 12. 从 JSON / dict 创建模型
# ------------------------------------------------------------
# model_validate()       → 从 dict 创建（验证）
# model_validate_json()  → 从 JSON 字符串创建

print("\n【12. 从 dict / JSON 创建模型】")

data = {"title": "从字典创建", "content": "内容", "author": "小红"}
article_from_dict = Article.model_validate(data)
print(f"  从 dict 创建: {article_from_dict.title}")

json_str = '{"title": "从JSON创建", "content": "内容", "author": "小刚"}'
article_from_json = Article.model_validate_json(json_str)
print(f"  从 JSON 创建: {article_from_json.title}")

print("[OK] 从 dict / JSON 创建模型演示完成")

# ------------------------------------------------------------
# 13. model_config 配置
# ------------------------------------------------------------
# ConfigDict 可以配置模型的行为，常用选项：
#   - str_strip_whitespace  → 自动去除字符串首尾空格
#   - extra='forbid'        → 禁止传入未定义的字段
#   - extra='ignore'        → 忽略未定义的字段

print("\n【13. model_config 配置】")

from pydantic import ConfigDict


class StrictUser(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str
    age: int


strict = StrictUser(name="  小明  ", age=18)
print(f"  str_strip_whitespace: name='{strict.name}' (空格被自动去除)")

try:
    StrictUser(name="小明", age=18, unknown_field="???")
except ValidationError as e:
    print(f"  extra='forbid': 未知字段被拒绝: {e.errors()[0]['msg']}")

print("[OK] model_config 配置演示完成")

# ------------------------------------------------------------
# 14. 枚举类型 Enum
# ------------------------------------------------------------
# Pydantic 原生支持 Python 的 Enum 类型

print("\n【14. 枚举类型】")

from enum import Enum


class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Car(BaseModel):
    brand: str
    color: Color


car = Car(brand="特斯拉", color="red")
print(f"  car.color = {car.color} (value={car.color.value})")

try:
    Car(brand="比亚迪", color="yellow")
except ValidationError as e:
    print(f"  无效颜色: {e.errors()[0]['msg']}")

print("[OK] 枚举类型演示完成")

# ------------------------------------------------------------
# 15. 自定义类型与 BeforeValidator
# ------------------------------------------------------------
# BeforeValidator 可以在 Pydantic 标准验证之前对数据进行预处理
# 比如将字符串 "yes"/"no" 转为 True/False

print("\n【15. BeforeValidator 自定义类型】")

from typing import Annotated
from pydantic import BeforeValidator


def normalize_bool(v):
    if isinstance(v, str):
        if v.lower() in ("yes", "y", "1", "true"):
            return True
        if v.lower() in ("no", "n", "0", "false"):
            return False
    return v


FlexibleBool = Annotated[bool, BeforeValidator(normalize_bool)]


class Survey(BaseModel):
    question: str
    answer: FlexibleBool


s1 = Survey(question="你喜欢Python吗？", answer="yes")
s2 = Survey(question="你用过Pydantic吗？", answer="no")
print(f"  answer='yes' → {s1.answer}")
print(f"  answer='no'  → {s2.answer}")

print("[OK] BeforeValidator 演示完成")

# ------------------------------------------------------------
# 16. 继承与扩展
# ------------------------------------------------------------
# Pydantic 模型支持继承，子类会继承父类的所有字段
# 可以在子类中添加新字段或覆盖父类字段

print("\n【16. 继承与扩展】")


class BaseItem(BaseModel):
    name: str
    price: float


class DigitalItem(BaseItem):
    download_url: str
    file_size_mb: float


digital = DigitalItem(name="电子书", price=29.9, download_url="https://example.com/book.pdf", file_size_mb=5.2)
print(f"  数字商品: {digital.model_dump()}")

print("[OK] 继承与扩展演示完成")

# ------------------------------------------------------------
# 17. computed_field 计算字段
# ------------------------------------------------------------
# computed_field 装饰器可以将 @property 标记为模型字段
# 在 model_dump() 和 model_dump_json() 时也会被包含

print("\n【17. computed_field 计算字段】")

from pydantic import computed_field


class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height


rect = Rectangle(width=3, height=4)
print(f"  面积: {rect.area}")
print(f"  model_dump() 包含计算字段: {rect.model_dump()}")

print("[OK] computed_field 演示完成")

# ------------------------------------------------------------
# 18. 别名 Alias
# ------------------------------------------------------------
# 当外部数据的字段名与 Python 属性名不一致时（如 JSON 用 camelCase），
# 可以用 Field(alias=...) 来映射

print("\n【18. 别名 Alias】")


class APIUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_name: str = Field(alias="userName")
    user_age: int = Field(alias="userAge")


api_user = APIUser(userName="小明", userAge=18)
print(f"  用别名创建: user_name={api_user.user_name}, user_age={api_user.user_age}")
print(f"  也可以用属性名创建: {APIUser(user_name='小红', user_age=20).model_dump()}")
print(f"  序列化时用 by_alias=True: {api_user.model_dump(by_alias=True)}")

print("[OK] 别名 Alias 演示完成")

# ------------------------------------------------------------
# 19. 实战：API 请求/响应模型
# ------------------------------------------------------------
# Pydantic 在 FastAPI 等框架中最常见的用法：
# 定义请求体和响应体的数据模型

print("\n【19. 实战：API 请求/响应模型】")

from datetime import datetime
from uuid import uuid4


class CreatePostRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    tags: list[str] = []


class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]
    created_at: str
    author: str


def create_post(request: CreatePostRequest, author: str) -> PostResponse:
    post = PostResponse(
        id=str(uuid4())[:8],
        title=request.title,
        content=request.content,
        tags=request.tags,
        created_at=datetime.now().isoformat(),
        author=author,
    )
    return post


new_post = create_post(
    CreatePostRequest(title="Pydantic实战", content="Pydantic让数据验证变得简单！", tags=["python", "pydantic"]),
    author="小明",
)
print(f"  创建文章成功！")
print(f"  ID: {new_post.id}")
print(f"  标题: {new_post.title}")
print(f"  标签: {new_post.tags}")
print(f"  时间: {new_post.created_at}")

print("[OK] API 请求/响应模型演示完成")

# ------------------------------------------------------------
# 总结
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("Pydantic 学习总结")
print("=" * 50)
print("""
  核心概念：
    BaseModel        → 所有模型的基类
    Field()          → 字段约束与元数据
    ValidationError  → 验证失败时抛出的异常

  验证器：
    field_validator   → 单字段自定义验证
    model_validator   → 多字段联合验证
    BeforeValidator   → 预处理（在标准验证之前）

  序列化：
    model_dump()          → 转 dict
    model_dump_json()     → 转 JSON 字符串
    model_validate()      → 从 dict 创建
    model_validate_json() → 从 JSON 字符串创建

  配置：
    ConfigDict        → 模型行为配置
    computed_field    → 计算属性字段
    Field(alias=...)  → 字段别名

  适用场景：
    [v] API 请求/响应数据验证（FastAPI 核心）
    [v] 配置文件解析与验证
    [v] 数据清洗与转换
    [v] 替代 dataclass（需要验证时）
""")
