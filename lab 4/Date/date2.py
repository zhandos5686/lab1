from datetime import datetime, timedelta

t = datetime.today()
y = t - timedelta(days=1)
tw = t + timedelta(days=1)

print("Yesterday:", y.strftime("%Y-%m-%d"))
print("Today:", t.strftime("%Y-%m-%d"))
print("Tomorrow:", tw.strftime("%Y-%m-%d"))