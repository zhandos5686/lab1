import re 
txt = "absda0"
x = re.search(r"^ab|^a", txt)

if x:
  print("YES! We have a match!")
else:
  print("No match")