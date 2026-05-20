class MagicColumn:
    def __init__(self, name):
        self.name = name
    
    # 重载 == 运算符，不返回 bool，返回一个"条件对象"
    def __eq__(self, other):
        return FilterCondition(f"{self.name} = {other}")
    
    # 重载 != 运算符
    def __ne__(self, other):
        return FilterCondition(f"{self.name} != {other}")
    
    # 重载 > 运算符
    def __gt__(self, other):
        return FilterCondition(f"{self.name} > {other}")
    
    # 重载 < 运算符
    def __lt__(self, other):
        return FilterCondition(f"{self.name} < {other}")
    
    # 重载 | 运算符（管道符/按位或）
    def __or__(self, other):
        if isinstance(other, FilterCondition):
            return FilterCondition(f"{self.name} OR ({other.expr})")
        return FilterCondition(f"{self.name} | {other}")


class FilterCondition:
    def __init__(self, expr):
        self.expr = expr
    
    def __repr__(self):
        return f"FilterCondition({self.expr})"
    
    # 重载 | 运算符，实现条件的 OR 组合
    def __or__(self, other):
        if isinstance(other, FilterCondition):
            return FilterCondition(f"({self.expr}) OR ({other.expr})")
        return FilterCondition(f"({self.expr}) | {other}")


# 测试！
col = MagicColumn("id")
print(col == 5)   # FilterCondition(id = 5)   ← 不是 True！
print(col != 3)   # FilterCondition(id != 3)   ← 不是 False！
print(col > 10)   # FilterCondition(id > 10)   ← 不是 False！

# 管道符 | 测试
print("\n===== 管道符 | 演示 =====")
print(col | "active")                    # MagicColumn 直接用 |
print((col == 5) | (col > 10))           # 两个条件组合（OR）
print((col == 5) | (col != 3))           # 用括号明确优先级
print((col == 5) | (col > 10) | (col < 1))  # 多个条件链式 OR