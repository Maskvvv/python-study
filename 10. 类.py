class Student(object):
    def __init__(self, name, age):
        self.__name = name
        self.__age = age
    def get_name(self):
        return self.__name
    def get_age(self):
        return self.__age
    
    def print_info(self):
        print(f'姓名: {self.__name}, 年龄: {self.__age}')



bart = Student('Bart Simpson', 10)

print(bart.get_name())
print(bart.get_age())
bart.print_info()
