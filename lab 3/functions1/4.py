primes = list(map(int, input()))
def prime(x):
    newlist = []
    for num in x:
        if num < 2:
            continue
        divisor = 0
        for j in range(1, num + 1): 
            if num % j == 0:
                divisor += 1
        if divisor == 2: 
            newlist.append(num)
    return newlist

print(prime(primes))
