def line(x):
    list = x.split(" ")
    return list[::-1]
x = input(" ")
result = " ".join(line(x))
print(result)