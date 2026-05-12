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


class FilterCondition:
    def __init__(self, expr):
        self.expr = expr
    
    def __repr__(self):
        return f"FilterCondition({self.expr})"


# 测试！
col = MagicColumn("id")
print(col == 5)   # FilterCondition(id = 5)   ← 不是 True！
print(col != 3)   # FilterCondition(id != 3)   ← 不是 False！
print(col > 10)   # FilterCondition(id > 10)   ← 不是 False！