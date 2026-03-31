import os
list = [d for d in os.listdir('.')]

print(list)

print(os.listdir('.'))

l = range(10)
print(l[0:5])
print([i for i in l])

# 生成器
g = (x * x for x in range(10))
for n in g:
    print(n)


