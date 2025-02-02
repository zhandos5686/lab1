def spy_game(nums):
    counter = 0
    for i in range(len(nums)):
        if nums[i]==0:
            counter+=1
        if counter == 1 and nums[i]==7:
            counter = 0
        if counter == 2 and nums[i]==7:
            return True
    return False 

ist = list(map(int, input().split()))
print(spy_game(ist))