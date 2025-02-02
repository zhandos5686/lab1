def uni(x):
    uni_list = []
    for i in lst:
        if i not in uni_list:
            uni_list.append(i)
    return uni_list

lst = input().split()
print(" ".join(uni(lst)))