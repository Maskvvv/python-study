def is_odd(n: int) -> bool:
    return n % 2 == 1

print(filter(is_odd, [1, 2, 4, 5, 6, 9, 10, 15]))
print(list(filter(is_odd, [1, 2, 4, 5, 6, 9, 10, 15])))


print(list(filter(lambda x: x % 2 == 1, [1, 2, 4, 5, 6, 9, 10, 15])))
