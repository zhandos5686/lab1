def has_33(arr):
    for i in range(len(arr)-1):
        if arr[i]== "3" and arr[i+1] == "3":
            print("True")
            return 1
    print("False")
    return 0

ist = input().split()
print(ist)
has_33(ist)