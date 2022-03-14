import requests
from multiprocessing import Pool
from time import time



url_list = ["https://python.org", "https://realpython.com", "https://google.com"]
content_list = list()

def get_content(url):
    res = requests.get(url)
    content_list.append(res.content)


start = time()
# for url in url_list:
#     get_content(url)

with Pool(processes=len(url_list)) as pool:
    pool.map(get_content, url_list)
print("len: ", len(content_list))
print("duration : ", time()-start)