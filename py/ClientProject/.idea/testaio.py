import time, requests
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
def ppc(r, *args, **kwargs):
    print(args, kwargs)
    print(r.status_code)
    print(r.headers)
    print(r.request.headers)
    print(r.elapsed.microseconds/1000000)
t1 = time.time()
session = FuturesSession(executor=ThreadPoolExecutor(max_workers=10))
session.headers={'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
# first request is started in background
future_one = session.get('http://esf.lf.fang.com/chushou/3_172211861.htm', hooks=dict(response=ppc))
# second requests is started immediately
future_two = session.get('http://fz.58.com/ershoufang/24377806264508x.shtml?psid=103838084190136523699058400&entinfo=24377806264508_0', hooks=dict(response=ppc))
# wait for the first request to complete, if it hasn't already
#
# response_one = future_one.result()
# print('response one status: {0}'.format(response_one.status_code))
# print(response_one.elapsed.microseconds/1000000)
# wait for the second request to complete, if it hasn't already
#response_two = future_two.result()
# print('response two status: {0}'.format(response_two.status_code))
# print(response_two.elapsed.microseconds/1000000)
t2 = time.time()
print('向服务器传递数据耗时:%f' % (t2-t1))