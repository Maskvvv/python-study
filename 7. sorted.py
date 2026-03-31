sorted([36, 5, -12, 9, -21])
print(sorted([36, 5, -12, 9, -21]))

sorted([36, 5, -12, 9, -21], key=abs)
print(sorted([36, 5, -12, 9, -21], key=abs))

sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower)
print(sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower))

sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower, reverse=True)
print(sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower, reverse=True))