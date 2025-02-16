import math
def pa(s, l):
    return (s * (l ** 2)) / (4 * math.tan(math.pi / s))

s, l = 4, 25
print(round(pa(s, l), 2))


