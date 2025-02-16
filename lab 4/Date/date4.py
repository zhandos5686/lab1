from datetime import datetime

d1 = datetime(2024, 2, 10, 12, 0, 0)  
d2 = datetime(2024, 2, 16, 14, 30, 0)

s = abs((d2 - d1).total_seconds())
print(s)