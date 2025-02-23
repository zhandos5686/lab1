import re

def text_match(t):
    x = re.search("[A-Z]+[a-z]", t)
    if x:
        return("YES! We have a match!")
    else:
        return("No match")
    
print(text_match("assad_asds"))
print(text_match("aBsad_asds"))
print(text_match("assad_Ssds"))