from datetime import datetime

c = datetime.now().replace(microsecond=0)
print(c)