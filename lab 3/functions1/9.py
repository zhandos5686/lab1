import math

def volume(r):
    v = (4/3)*math.pi*pow(r, 3)
    return v

print(volume(float(input())))