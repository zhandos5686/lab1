import re

def text_match(t):
    x = re.sub("[A-Z]", " ", t)
    return x

print(text_match("HappyBirthDay"))
print(text_match("NewYear"))
print(text_match("AxAr"))