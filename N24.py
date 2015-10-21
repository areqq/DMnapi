#!/usr/bin/python -u
# -*- coding: UTF-8 -*-

import re, urllib2, socket, zipfile
from StringIO import StringIO

def parse_n24(lines):
    id = 0
    res = {}
    for l in lines:
        try:
            l = l.strip()
            l = re.sub('^[ \t]+','', l)

            if l.startswith('<id>'):
                id = int(re.match(r"<id>(\d+)</id>", l).groups(0)[0])
                res[id] = dict( id = id, title = '?', season = '?', episode = '?', imdb = '?', language = 'pl', size = 0, fps = '?',
                year = '?', release = '?' )
            elif l.startswith('<title>'):
                res[id]['title'] = re.match(r"<title>(.+)</title>", l).groups(0)[0]
            elif l.startswith('<season>'):
                res[id]['season'] = re.match(r"<season>(.*)</season>", l).groups(0)[0]
            elif l.startswith('<episode>'):
                res[id]['episode'] = re.match(r"<episode>(.*)</episode>", l).groups(0)[0]
            elif l.startswith('<imdb>'):
                res[id]['imdb'] = re.match(r"<imdb>(.*)</imdb>", l).groups(0)[0]
            elif l.startswith('<language>'):
                res[id]['language'] = re.match(r"<language>(.+)</language>", l).groups(0)[0]
            elif l.startswith('<size>'):
                res[id]['size'] = int(re.match(r"<size>(\d+)[|<]", l).groups(0)[0])
            elif l.startswith('<fps>'):
                res[id]['fps'] = re.match(r"<fps>(.*)</fps>", l).groups(0)[0]
            elif l.startswith('<year>'):
                res[id]['year'] = re.match(r"<year>(.*)</year>", l).groups(0)[0]
            elif l.startswith('<release>'):
                res[id]['release'] = re.match(r"<release>(.*)</release>", l).groups(0)[0]
        except:
            print "[DMnapi] Error parse: ", l
    return res

def http_n24(url):
    content = ''
    try:
        req = urllib2.Request(url, headers = {'Referer' : 'http://napisy24.pl', 'User-Agent' : 'DMnapi 13.1.30'})
        socket.setdefaulttimeout(20)
        f = urllib2.urlopen(req)
        content = f.read()
        f.close()
    except urllib2.HTTPError, e:
        print "[DMnapi] Error: n24 HTTP Error: %s - %s" % (e.code, url)
    except urllib2.URLError, e:
        print "[DMnapi] Error: n24 URL Error: %s - %s" % (e.reason, url)
    except:
        print "[DMnapi] Error: n24", url
    return content

def get_n24(subid):
    url = 'http://napisy24.pl/run/pages/download.php?napisId=%i' % subid
    try:
        z = zipfile.ZipFile(StringIO( http_n24(url) ))
        s = 0
        for p in z.infolist():
            if p.file_size > s:
                s = p.file_size
                n = p.filename
        content = z.read(n)
	return content

    except:
        print "[DMnapi] Error: zip n24", url
    return ''


if __name__ == "__main__":
    #x = search_n24('http://napisy24.pl/libs/webapi.php?title=breaking%20bad%204x3')
    #print parse_n34(x.split('\n'))
    print get_n24(43129)
