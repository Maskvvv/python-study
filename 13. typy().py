def fn(self, name='world'): # 先定义函数
    print('Hello, %s.' % name)


# Hello = type('Hello', (object,), dict(hello=fn))
Hello = type('Hello', (object,), {"hello": fn})
h = Hello()
h.hello()