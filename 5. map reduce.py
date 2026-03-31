def f(x):
    return x * x

r = map(f, [1, 2, 3, 4, 5, 6, 7, 8, 9])
print(list(r))


def fn(x, y):
    return x * 10 + y

from functools import reduce

def fn1(x, y):
    print(x, y)
    return x * 10 + y

print(reduce(fn1, [1, 3, 5, 7, 9]))
