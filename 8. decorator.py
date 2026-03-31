

def log(func):
    def wrapper(*args, **kwargs):
        """log decorator"""
        print('call %s():' % func.__name__)
        print('args =', *args)
        print('kwargs =', kwargs)
        return func(*args, **kwargs)
    return wrapper

@log
def now():
    print('2024-6-1')

print(now.__name__)
now()

now = log(now)
now()