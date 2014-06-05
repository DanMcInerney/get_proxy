get_proxy
=========


Python class for returning a list of valid elite anonymity proxies with the fastest one first. Can be run on it's own, but was created with the intention of placing inside other scripts. Give the class the number of proxies you want returned as an argument.

Scrapes usually about ~700 unique proxies from:
* gatherproxy.com
* checkerproxy.net
* letushide.com

Tests each proxy against 2 HTTP links that confirm the IP, 1 HTTPS link that confirms IP, and 1 site which reflects the headers sent by the proxy to confirm the highest anonymity status.

Usage
------

```
P = find_http_proxy(5)
proxies = P.run()
```
Would create a list of the 5 fastest proxies within the variable



```
P = find_http_proxy(1)
resp = requests.get('http://danmcinerney.org', proxies={'http':'http://'+P.run()[0]})
```

Would create a response object that was fetched using the single fastest http proxy
this script could find.


### One liner to open Chrome using the fastest proxy found
```
google-chrome --proxy-server=`python -c 'import get_proxy; p = get_proxy.find_http_proxy(1); print p.run()[0]'`
```
Close out of any other instances of Chrome you have open. Navigate to your the directory of get_proxy.py then run this command to open a new Chrome window that is making all connections through the fastest proxy the script could find. No-hassle anonymity.
