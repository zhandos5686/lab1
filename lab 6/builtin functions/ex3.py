def polindrom(soilem,teris_soilem):
    for i in soilem:
        for j in teris_soilem:
            if i!=j:
                return False
                break
            return True    
sentence=str(input("enter sentence:"))
soilem_reverse=''.join(reversed(sentence))
print(polindrom(sentence,soilem_reverse))
def is_palindrome(s):
    return all(map(lambda x: x[0] == x[1], zip(s, reversed(s))))
print(is_palindrome(sentence))
