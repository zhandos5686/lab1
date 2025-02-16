def cd(n):
    while n >= 0:
        yield n
        n -= 1

n = 5
for x in cd(n):
    print(x, end=" ")
