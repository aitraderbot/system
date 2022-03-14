import requests
from multiprocessing import Pool
from time import time


x = "15.0023456"
count = 1
while True:

    y = x[:-count]
    if y == "15.00":
        valid = True
        break
    else:
        count += 1
        continue

print(valid)
