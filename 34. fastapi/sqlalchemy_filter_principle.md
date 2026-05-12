# SQLAlchemy filter 条件表达式的实现原理 —— Python 运算符重载的魔法 ✨

当你在 SQLAlchemy 中写下：

```python
db.query(TodoModel).filter(TodoModel.id == 5).first()
```

你有没有想过：`TodoModel.id == 5` 为什么不是返回 `True/False`，而是能被 `filter()` 识别并翻译成 SQL 的 `WHERE` 子句？

答案就是：**Python 的运算符重载（Operator Overloading）**。

---

## 一、从 Python 的运算符说起

Python 中，每个运算符背后都对应一个"双下划线方法"（魔术方法）：

| 运算符 | 对应方法 | 含义 |
|--------|---------|------|
| `a == b` | `a.__eq__(b)` | 等于 |
| `a != b` | `a.__ne__(b)` | 不等于 |
| `a > b` | `a.__gt__(b)` | 大于 |
| `a < b` | `a.__lt__(b)` | 小于 |
| `a >= b` | `a.__ge__(b)` | 大于等于 |
| `a <= b` | `a.__le__(b)` | 小于等于 |

正常情况下，`__eq__` 返回 `True` 或 `False`。但 Python **并不强制要求返回 bool** —— 你可以返回任何对象！这就是 SQLAlchemy 的切入点。

---

## 二、手写一个迷你版：理解核心原理

### 2.1 FilterCondition —— 过滤条件对象

```python
class FilterCondition:
    """存储一个比较表达式"""

    def __init__(self, operator: str, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __and__(self, other):
        """重载 & 运算符，实现条件组合：cond1 & cond2"""
        return FilterCondition("AND", self, other)

    def __or__(self, other):
        """重载 | 运算符，实现条件组合：cond1 | cond2"""
        return FilterCondition("OR", self, other)

    def to_sql(self) -> str:
        """把条件对象翻译成 SQL 字符串"""
        if isinstance(self.left, FilterCondition):
            left_sql = f"({self.left.to_sql()})"
        elif isinstance(self.left, Column):
            left_sql = self.left.name
        else:
            left_sql = repr(self.left)

        if isinstance(self.right, FilterCondition):
            right_sql = f"({self.right.to_sql()})"
        else:
            right_sql = repr(self.right)

        return f"{left_sql} {self.operator} {right_sql}"
```

### 2.2 Column —— 重载所有比较运算符

```python
class Column:
    """模拟 SQLAlchemy 的 Column"""

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return FilterCondition("=", self, other)

    def __ne__(self, other):
        return FilterCondition("!=", self, other)

    def __gt__(self, other):
        return FilterCondition(">", self, other)

    def __lt__(self, other):
        return FilterCondition("<", self, other)

    def __ge__(self, other):
        return FilterCondition(">=", self, other)

    def __le__(self, other):
        return FilterCondition("<=", self, other)

    def contains(self, keyword):
        """模拟 LIKE 查询"""
        return FilterCondition("LIKE", self, f"%{keyword}%")
```

---

## 三、见证魔法时刻

```python
id_col = Column("id")
title_col = Column("title")
completed_col = Column("completed")

# 单条件查询
cond1 = id_col == 5
print(cond1.to_sql())          # id = 5
print(type(id_col == 5))       # <class 'FilterCondition'>  不是 bool！

# 多条件组合
cond2 = (id_col > 3) & (completed_col == True)
print(cond2.to_sql())          # (id > 3) AND (completed = True)

# LIKE 查询
cond3 = title_col.contains("FastAPI")
print(cond3.to_sql())          # title LIKE '%FastAPI%'

# 复杂组合
cond4 = (id_col > 0) & (title_col.contains("Python") | completed_col == True)
print(cond4.to_sql())          # (id > 0) AND ((title LIKE '%Python%') OR (completed = True))
```

看到没？`id_col == 5` 没有返回 `True/False`，而是返回了一个 `FilterCondition` 对象！这就是 SQLAlchemy 的核心思路。

---

## 四、SQLAlchemy 真实实现的关键细节

### 4.1 InstrumentedAttribute —— 双重身份

`TodoModel.id` 不是普通的 `Column`，而是 `InstrumentedAttribute`，它同时具有双重身份：

| 访问方式 | 得到什么 | 用途 |
|---------|---------|------|
| `TodoModel.id`（类访问） | 列描述对象 | 构建查询条件 |
| `todo.id`（实例访问） | 实际值（如 `5`） | 读取数据 |

### 4.2 防止误用：`__bool__` 报错

SQLAlchemy 的条件对象重载了 `__bool__`，直接当 bool 用会抛异常：

```python
if TodoModel.id == 5:   # ❌ TypeError: Boolean value of this clause is not defined
    pass
```

这是为了防止你把"条件表达式"当成"判断语句"来用 —— 它只是**描述条件**，不是在做判断！

### 4.3 延迟执行（Lazy Evaluation）

```
构建条件 → 不执行 SQL
调用 .first() / .all() / .count() → 才真正执行 SQL
```

这让你可以灵活地组合条件，最后一步才查询：

```python
query = db.query(TodoModel)

if keyword:
    query = query.filter(TodoModel.title.contains(keyword))

if only_completed:
    query = query.filter(TodoModel.completed == True)

# 上面只是拼接条件，没有执行 SQL
results = query.all()   # 这里才真正查询数据库
```

### 4.4 参数绑定（防 SQL 注入）

SQLAlchemy **不会**直接把值拼进 SQL 字符串，而是用参数化查询：

```python
db.query(TodoModel).filter(TodoModel.id == 5)
```

生成的 SQL：

```sql
SELECT * FROM todos WHERE id = ?    -- 参数: (5,)
```

而不是：

```sql
SELECT * FROM todos WHERE id = 5    -- 字符串拼接，有注入风险！
```

这样就杜绝了 SQL 注入的风险。

---

## 五、完整流程图

```
你写的 Python 代码              SQLAlchemy 内部                   最终 SQL
────────────────────────────────────────────────────────────────────────────

TodoModel.id == 5
       │
       ▼
Column.__eq__(5)
       │
       ▼
BinaryExpression(op="=", left="id", right=5)     →   WHERE id = ?
                                                        参数: (5,)

.filter(expr)
       │
       ▼
把表达式对象收集到查询中
       │
       ▼
.first() / .all()
       │
       ▼
编译所有表达式 → 生成完整 SQL → 发给数据库执行
```

---

## 六、总结

| 概念 | 说明 |
|------|------|
| **运算符重载** | Python 允许自定义 `==`、`>` 等运算符的返回值 |
| **`__eq__` 返回对象** | SQLAlchemy 让 `==` 返回 `BinaryExpression` 而非 `bool` |
| **链式调用** | `.filter()` 接收表达式对象，翻译成 `WHERE` 子句 |
| **延迟执行** | 条件只是"描述"，`.first()`/`.all()` 时才真正执行 SQL |
| **参数绑定** | 值通过参数传递，防止 SQL 注入 |
| **`__bool__` 报错** | 防止把条件表达式误当成 `if` 判断来用 |

这就是 SQLAlchemy 的优雅之处：**用 Python 的语法写 SQL 条件，既直观又安全** 🎀
