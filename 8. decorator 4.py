import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__} 执行耗时: {end - start:.4f} 秒')
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    print('任务完成')

@timer
def add(a, b):
    return a + b

slow_function()
print('add 结果:', add(3, 5))
