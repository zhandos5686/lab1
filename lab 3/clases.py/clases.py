class io():
    def getString():
        return input()
    def printString(s: str):
        print(s.upper())

# a = io.getString()
# io.printString(a)

class Shape():
    def area(self):
        return 0
    
class Square(Shape):
    def __init__(self, length):
        self.length = length

    def area(self):
        return self.length ** 2
    
# print(Shape().area())
# print(Square(2).area())

class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width
    
# print(Rectangle(2, 3).area())

class Point():
    def __init__(self, x, y, /):
        self.x = x
        self.y = y

    def show(self):
        print(f"({self.x}, {self.y})")

    def move(self, x, y, /):
        self.x += x
        self.y += y

    def dist(self, point):
        return (((point.x - self.x) ** 2 
                 + (point.y - self.y) ** 2)) ** 0.5
    
"""
p1 = Point(0, 0)
p2 = Point(1, 1)
p1.move(5, 4)
print(p1.dist(p2))
p1.show()
p2.show()
"""

class Account():
    def __init__(self, owner: str, balance = 0):
        self.owner = owner
        self.balance = balance

    def deposit(self, credit: int):
        self.balance += credit
        print(f"Deposit {credit}. Balance: {self.balance}")

    def withdraw(self, credit: int):
        if (self.balance < credit):
            print("Not enough credits!")
            return
        self.balance -= credit
        print(f"Withdraw {credit}. Balance: {self.balance}")

"""
acc = Account("Zhandos")
acc.deposit(100)
acc.withdraw(120)
acc.withdraw(100)
"""

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

import random
numbers = [random.randint(1, 1000) for _ in range(100)]
prime = list(filter(lambda x: is_prime(x), numbers))