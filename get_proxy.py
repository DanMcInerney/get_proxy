#!/usr/bin/env python2

''' Python class for returning a list of valid elite anonymity proxies with the fastest
one first. Can be run on it's own, but was created with the intention of placing inside
other scripts. Give the class the number of proxies you want returned as an argument.

Example:

P = find_http_proxy(1)
res = requests.get('http://danmcinerney.org', proxies={'http':'http://'+P.run()})

Would create a response object that was fetched using the single fastest http proxy
this script could find amongst the 600+ it tests in parallel'''

from gevent import monkey
monkey.patch_all()

import requests
import ast
import gevent
import sys, re, time, os, argparse
import socket
from BeautifulSoup import BeautifulSoup

class find_http_proxy:
    ''' Will only gather L1 (elite anonymity) proxies
    which should not give out your IP or advertise
    that you are using a proxy at all '''

    def __init__(self, num_of_proxies):
        ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'
        self.proxy_list = []
        self.headers = {'User-Agent':ua}
        self.show_num = num_of_proxies
        self.externalip = self.external_ip()
        self.final_proxies = []

    def external_ip(self):
        ''' Get the accurate, non-proxied IP '''
        resp = requests.get('http://myip.dnsdynamic.org/', headers=self.headers)
        ip = resp.text
        return ip

    def run(self):
        ''' Gets raw high anonymity (L1) proxy data then calls make_proxy_list()
        Currently parses data from gatherproxy.com and letushide.com '''

        letushide_list = self.letushide_resp()
        gatherproxy_list = self.gatherproxy_resp()
        checkerproxy_list = self.checkerproxy_resp()

        self.proxy_list.append(letushide_list)
        self.proxy_list.append(gatherproxy_list)
        self.proxy_list.append(checkerproxy_list)

        # Flatten list of lists (1 master list containing 1 list of ips per proxy website)
        self.proxy_list = [ips for proxy_site in self.proxy_list for ips in proxy_site]
        self.proxy_list = list(set(self.proxy_list)) # Remove duplicates

        return self.proxy_checker()

    def checkerproxy_resp(self):
        ''' Make the request to checkerproxy and create a master list from that site '''
        cp_ips = []
        try:
            url = 'http://checkerproxy.net/all_proxy'
            r = requests.get(url, headers=self.headers)
            html = r.text
        except Exception:
            checkerproxy_list = []
            return checkerproxy_list

        checkerproxy_list = self.parse_checkerproxy(html)
        return checkerproxy_list

    def parse_checkerproxy(self, html):
        ''' Only get elite proxies from checkerproxy '''
        ips = []
        soup = BeautifulSoup(html)
        for tr in soup.findAll('tr'):
            if len(tr) == 19:
                ip_found = False
                elite = False
                ip_port = None
                tds = tr.findAll('td')
                for td in tds:
                    if ':' in td.text:
                        ip_found = True
                        ip_port_re = re.match('(\d{1,3}\.){3}\d{1,3}:\d{1,5}', td.text)
                        if ip_port_re:
                            ip_port = ip_port_re.group()
                        if not ip_port:
                            ip_found = False
                    if 'Elite' in td.text:
                        elite = True
                    if ip_found == True and elite == True:
                        ips.append(str(ip_port))
                        break
        return ips

    def letushide_resp(self):
        ''' Make the request to the proxy site and create a master list from that site '''
        letushide_ips = []
        for i in xrange(1,20): # can search maximum of 20 pages
            try:
                url = 'http://letushide.com/filter/http,hap,all/%s/list_of_free_HTTP_High_Anonymity_proxy_servers' % str(i)
                r = requests.get(url, headers=self.headers)
                html = r.text
                ips = self.parse_letushide(html)

                # Check html for a link to the next page
                if '/filter/http,hap,all/%s/list_of_free_HTTP_High_Anonymity_proxy_servers' % str(i+1) in html:
                    pass
                else:
                    letushide_ips.append(ips)
                    break
                letushide_ips.append(ips)
            except:
                break

        # Flatten list of lists (1 list containing 1 list of ips for each page)
        letushide_list = [item for sublist in letushide_ips for item in sublist]
        return letushide_list

    def parse_letushide(self, html):
        ''' Parse out list of IP:port strings from the html '''
        # \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}  -  matches IP addresses
        # </a></td><td>  -  is in between the IP and the port
        # .*?<  -  match all text (.) for as many characters as possible (*) but don't be greedy (?) and stop at the next greater than (<)
        raw_ips = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}</a></td><td>.*?<', html)
        ips = []
        for ip in raw_ips:
            ip = ip.replace('</a></td><td>', ':')
            ip = ip.strip('<')
            ips.append(str(ip))
        return ips

    def gatherproxy_resp(self):
        url = 'http://gatherproxy.com/proxylist/anonymity/?t=Elite'
        try:
            r = requests.get(url, headers = self.headers)
            lines = r.text.splitlines()
        except:
            gatherproxy_list = []
            return gatherproxy_list

        gatherproxy_list = self.parse_gp(lines)
        return gatherproxy_list

    def parse_gp(self, lines):
        ''' Parse the raw scraped data '''
        gatherproxy_list = []
        for l in lines:
            if 'proxy_ip' in l.lower():
                l = l.replace('gp.insertPrx(', '')
                l = l.replace(');', '')
                l = l.replace('null', 'None')
                l = l.strip()
                l = ast.literal_eval(l)

                proxy = '%s:%s' % (l["PROXY_IP"], l["PROXY_PORT"])
                gatherproxy_list.append(str(proxy))
        return gatherproxy_list

    def proxy_checker(self):
        ''' Concurrency stuff here '''
        jobs = [gevent.spawn(self.proxy_checker_resp, proxy) for proxy in self.proxy_list]
        try:
            while 1:
                gevent.sleep(1)
                if len(self.final_proxies) >= self.show_num:
                    gevent.killall(jobs)
                    break
        except KeyboardInterrupt:
            sys.exit('[-] Ctrl-C caught, exiting')

        return self.final_proxies[:self.show_num]

    def proxy_checker_resp(self, proxy):
        ''' Run 4 web tests on each proxy IP:port and collect the results '''
        proxyip = str(proxy.split(':', 1)[0])

        results = []
        urls = ['http://danmcinerney.org/ip.php',
                'http://myip.dnsdynamic.org',
                'https://www.astrill.com/what-is-my-ip-address.php',
                'http://danmcinerney.org/headers.php']

        for url in urls:
            try:
                check = requests.get(url,
                                    headers = self.headers,
                                    proxies = {'http':'http://'+proxy,
                                               'https':'http://'+proxy},
                                    timeout = 15)

                html = check.text
                error = self.html_handler(html, url)
                results.append((error, proxy, url))

            except Exception as e:
                error = True
                results.append((error, proxy, url))

        proxy = self.proxy_tests(results)
        if proxy:
            self.final_proxies.append(proxy)

    def html_handler(self, html, url):
        ''' Check the html for errors and if none are found return time to load page '''

        html_lines = html.splitlines()
        leng = len(html_lines)
        error = False

        # Both of these urls just return the ip and nothing else
        if url in ['http://danmcinerney.org/ip.php', 'http://myip.dnsdynamic.org']:
            if leng == 1:  # Should return 1 line of html
                if self.externalip in html:
                    error = True
            else:
                error = True
            return error

        # This is the SSL page
        elif 'astrill' in url:
            soup = BeautifulSoup(html)
            ip = soup.find("td", { "colspan": 2 }).text # the ip is the only on with colspan = 2
            if self.externalip in ip:
                error = True
            return error

        # This is the header checking page
        elif '/headers' in url:
            # check for proxy headers
            proxy_headers = ['via: ', 'forwarded: ', 'x-forwarded-for', 'client-ip']
            if leng > 15: # 15 is arbitrary, I just don't think you'll ever see more than 15 headers
                error = True
            else:
                for l in html_lines:
                    for h in proxy_headers:
                        if h in l.lower():
                            error = True
                            return error
            return error

    def proxy_tests(self, results):
        ''' Sees if the proxy passes all the tests and limits the results '''
        for r in results:
            error = r[0]
            if error == True:
               return
            proxy = r[1]

        return proxy

# How to run:
#print 'Fetching the fastest 4 proxies...'
#P = find_http_proxy(4)
#prox = P.run()
#print 'Fastest L1 proxies:', prox
