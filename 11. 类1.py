class Student(object):
    pass

def set_age(self, age):
    self.__age = age

def set_score(self, score):
    self.__score = score

Student.set_score = set_score

student = Student()



student.set_score(80)
print(student.__dict__)