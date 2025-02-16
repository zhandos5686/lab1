def sq(n):
    for i in range(n + 1):
        yield i ** 2

n = 10
for x in sq(n):
    print(x, end=" ")
