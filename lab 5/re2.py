import re 
txt = "abbsda0"
x = re.search(r"^abbb|^abb", txt)

if x:
  print("YES! We have a match!")
else:
  print("No match")