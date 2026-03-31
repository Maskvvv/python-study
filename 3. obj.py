def person(name, age, *, city, job):
 print(name, age, city, job)


def person1(name, age, *args, city, job):
    print(name, age, args, city, job)

person('张三', 18, "北京", "销售")
