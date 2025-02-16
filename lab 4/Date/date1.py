from datetime import datetime, timedelta

ct = datetime.today()
nw = ct - timedelta(days=5)
print( nw.strftime("%Y-%m-%d"))