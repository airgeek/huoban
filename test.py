from retry import retry
import time
@retry(tries=5,timesout=10)
def ts():
	print('='*50)
	for i in range(12):
		print(i)
		time.sleep(1)
ts()