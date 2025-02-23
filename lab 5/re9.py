import re

def text_match(t):
    x = re.findall(r"[A-Z][a-z]+", t)
    
    return ' '.join(x)

print(text_match("HappyBirthDay"))
print(text_match("NewYear"))
print(text_match("AxAr"))