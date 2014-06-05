get_proxy
=========


Python class for returning a list of valid elite anonymity proxies with the fastest
one first. Can be run on it's own, but was created with the intention of placing inside
other scripts. Give the class the number of proxies you want returned as an argument.

Example:

P = find_http_proxy(1)
res = requests.get('http://danmcinerney.org', proxies={'http':'http://'+P.run()})

Would create a response object that was fetched using the single fastest http proxy
this script could find amongst the 600+ it tests in parallel
