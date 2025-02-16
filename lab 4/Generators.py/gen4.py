def sqr(a, b):
    for i in range(a, b + 1):
        yield i ** 2

a, b = 3, 7
for x in sqr(a, b):
    print(x)
