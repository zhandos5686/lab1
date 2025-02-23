import re

def text_match(t):
    x = re.search("^a+[A-Za-z]+b$", t)
    if x:
        return("YES! We have a match!")
    else:
        return("No match")
    
print(text_match("assadasdb"))
print(text_match("aBsadasds"))
print(text_match("assadSsds"))