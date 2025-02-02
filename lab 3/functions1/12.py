def histogram(x):
    for i in range(len(x)):
        print("*"*x[i])

ist = list(map(int, input().split()))

histogram(ist)