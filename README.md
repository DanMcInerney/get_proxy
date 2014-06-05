get_proxy
=========


Python class for returning a list of valid elite anonymity proxies with the fastest
one first. Can be run on it's own, but was created with the intention of placing inside
other scripts. Give the class the number of proxies you want returned as an argument.

Scrapes usually about ~700 unique proxies from:
* gatherproxy.com
* checkerproxy.com
* letushide.com

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
