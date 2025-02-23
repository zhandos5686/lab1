import re

def text_match(t):
    x = re.sub(r"\s|,|\.", ":", t)
    return x
    
print(text_match("as.adasd b"))
print(text_match("aB,adas ds"))
print(text_match(",ssadS sds"))