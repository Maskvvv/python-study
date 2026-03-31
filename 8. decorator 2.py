def log(func):
    def wrapper(*args, **kwargs):
        print(f'调用 {func.__name__}()')
        print(f'args = {args}')
        print(f'kwargs = {kwargs}')
        return func(*args, **kwargs)
    return wrapper

@log
def process_data(data_dict1, data_dict2, name=1):
    print(f'处理 {name} 的数据: {data_dict1}')
    print(f'处理 {name} 的数据: {data_dict2}')

# 调用
process_data({'a': 1, 'b': 2}, {'c': 3, 'd': 4}, name='小明')
# calculate([1, 2, 3], factor=10)