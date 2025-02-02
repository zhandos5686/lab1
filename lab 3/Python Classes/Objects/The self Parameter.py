class Person:
  def __init__(mysillyobject, name, age):
    mysillyobject.name = name
    mysillyobject.age = age

  def myfunc(abc):
    print("Hello my name is " + abc.name)

p1 = Person("John", 36)
p1.myfunc()

#Modify Object Properties
p1.age = 40

#Delete Object Properties
del p1.age

#Delete Objects
del p1

#The pass Statement
class Person:
  pass