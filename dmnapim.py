#!/usr/bin/python
# -*- coding: UTF-8 -*-

# napiprojekt.pl API is used with napiproject administration consent

import os, os.path, re, string, sys, time, urllib, urllib2, socket
import base64, struct, zipfile
from hashlib import md5 as md5
from StringIO import StringIO
import subutil

class GetFPS(object):
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        return self.fps

    def fps(self):
        self.file = open(self.filename,"r+b")
        s = self.file.read(4)
        if s == "\x1a\x45\xdf\xa3":
            return self.get_mkv_fps()
        elif s == "RIFF":
            self.file.seek(32)
            return 1000000.0 / float(struct.unpack('<I', self.file.read(4))[0])
        else:
            raise Exception('Error: Unknown file format not AVI/MKV')

    def __exit__(self, type, value, traceback):
        try:
            self.file.close()
        except:
            pass

    def eblm(self, bits = 0xf0):
        suma = 0x00
        mask = 0x01
        while not (suma & mask):
            suma =  ( suma << 8 ) + ord(self.file.read(1))
            if (mask == 0x01) and not (suma & bits):
                raise Exception('Error: MKV stream is broken')
            mask <<= 7
        if bits == 0xf0:
            return (suma, self.eblm( bits = 0xff ) )
        else:
            return suma ^ mask

    def get_mkv_fps(self):
        track = 0
        self.file.seek(0)
        while 1:
            class_id, length = self.eblm()
            # print "class_id: %X length %i position:%i" % (class_id, length, self.file.tell())
            if (class_id == 0x83):
                track = ord( self.file.read(1) )
            elif (class_id == 0x23E383 and track == 1):
                break
            elif (class_id not in [ 0x18538067, 0x1654AE6B, 0xAE, 0x83 ]):  #Segment,Tracks,TrackEntry,TrackType
                self.file.seek(length,1)
        return ( 1000000000/ float( struct.unpack('>I', self.file.read(4))[0] ) )

def convert_to_unicode( sub ):
    if sub.startswith('\xef\xbb\xbf'):
        return sub.decode("utf-8-sig",'ignore'), "utf-8-sig"
    iso = 0
    for i in (161, 166, 172, 177, 182, 188):
        iso += sub.count(chr(i))
    win = 0
    for i in (140, 143, 156, 159, 165, 185):
        win += sub.count(chr(i))
    utf = 0
    for i in (195, 196, 197):
        utf += sub.count(chr(i))
    if win > utf and win > iso:
        return sub.decode("CP1250",'ignore'), "CP1250"
    if utf > iso and utf > win:
        return sub.decode("utf-8",'ignore'), "utf-8"
#    if iso > utf and iso > win:
    return sub.decode("iso-8859-2",'ignore'), "iso-8859-2"

def f(z):
    idx = [ 0xe, 0x3,  0x6, 0x8, 0x2 ]
    mul = [   2,   2,    5,   4,   3 ]
    add = [   0, 0xd, 0x10, 0xb, 0x5 ]

    b = []
    for i in xrange(len(idx)):
        a = add[i]
        m = mul[i]
        i = idx[i]

        t = a + int(z[i], 16)
        v = int(z[t:t+2], 16)
        b.append( ("%x" % (v*m))[-1] )

    return ''.join(b)

def get_subtitle(digest, lang = "PL"):
    sub = ''
    try:
        req = urllib2.Request("http://napiprojekt.pl/api/api-napiprojekt3.php", np_postdata(digest, lang))
        t = urllib2.urlopen(req).read()
        sub = np_parsexml(t)
    except:
        pass
    return sub

def np_postdata(digest, lang = "PL"):
    data = {
        "downloaded_subtitles_id" : digest,
        "mode" : "1",
        "client" : "DMnapi",
        "client_ver" : "15.11.08",
        "downloaded_subtitles_lang" : lang,
        "downloaded_subtitles_txt" : "1" }
    return urllib.urlencode(data)

def np_parsexml(t):
    sub = ''
    try:
        if t.find('<status>success</status>') > 0:
            s = t.find('><content><![CDATA[') + 19
            e = t.find(']]></content><')
            if s > 30 and e > s:
                sub = base64.b64decode(t[s:e])
    except:
        pass
    return sub

def napiprojekt_fps(digest):
    url = "http://napiprojekt.pl/api/api.php?mode=file_info&client=dreambox&id=%s" % (urllib2.quote(digest))
#    element = ET.parse( urllib2.urlopen(url)  )
#    fps = element.find("video_info/fps").text
    try:
        fps = float([ re.match(r".*<fps>(.*)</fps>.*", x).groups(0)[0] for x in urllib2.urlopen(url) if x.find('<fps>')>0 ][0])
    except:
        fps = 23.976
    return float(fps)

def to_srt_utf8(subs_org, file, digest = 0, info = "", fps = 0, save = True):
    p, f = os.path.split(file)
    if fps > 0:
        tfps = " fps: %.2f" % fps
    else:
        tfps = ""
    print "Processing subtitle for:\n Path: %s\n File: %s %s %s" % (p, f, info, tfps)
    if len(subs_org) < 100:
        print "Subtitle not found ;("
        return ""
    try:
        dest = file[:-4] + '.srt'
        subs_u , org_cod = subutil.tounicode( subs_org )
        subs_u = subs_u.replace('\r', '').replace('{Y:i}',' ').replace('{y:i}',' ') 
        subs = subs_u.split('\n')
        fmt = subutil.detect_format( subs )
        print " Oryginal subtitle format: ", fmt, org_cod,
        if fmt == 'unknown':
            return None

        if fmt == "mdvd":
            if not 22 < fps < 32:
                f = GetFPS(file)
                fps = f.fps()
                print "DMnapi: GetFPS", fps
            if not 22 < fps < 32:
                print " failback to napifps ",
                fps = napiprojekt_fps(digest)
            print "FPS:", str(fps)[0:5], 
            subs = "".join(subutil.to_srt( subutil.sub_fix_times( subutil.read_mdvd(subs, fps))))
        elif fmt != "srt" :
            subs = "".join(subutil.to_srt( subutil.sub_fix_times( subutil.read_subs(subs, fps))))
        else:
            subs = subs_u
        subs = subs.encode("utf-8-sig")
        if save:
            print "     Saved as SRT utf8."
            dst = open( dest, 'w')
            dst.write(subs)
            dst.close()
            print " Saved:", dest
        return subs
    except:
        print "  Error: %s" % ( sys.exc_info()[1])
    return None

def get_sub_from_napi(file, fps = 0 ):
    digest = hashFile(file)['npb']
    if digest:
        to_srt_utf8( get_subtitle(digest), file, digest, fps = fps )

def convert(file, src, fps = 0):
    try:
        if not  100 < os.path.getsize(src) < 200000:
            raise Exception('Suspicious file size: %s %i' % (src, os.path.getsize(src)) )
        to_srt_utf8( subs_org = open(src).read(), file = file, info = "\n Convert from: " + os.path.split(src)[1], fps = fps )
    except:
        print "  Error: %s" % ( sys.exc_info()[1])


prere = (("[^\w\d]", " "),
("[\.]", " "),
("[\[\]-_]", " "),
("^[^-\s]*-", " "),
("_", " "),
(" (720p|1080i|1080p)( |$)+", " "),
(" (x264|blu-ray|bluray|hdtv|xvid)( |$)+", " "),
(" (eng|rus)( |$)+", " "),
(" (oar)( |$)+", " "),
(" (miniseries)( |$)+", " "),
(" (dts|dd5|ac3|stereo)( |$)+", " "),
(" (xbox)( |$)+", " "),
(" [\[](720p|1080i|1080p)[\]]( |$)+", " "))

tvshowRegex = re.compile('(?P<show>.*)S(?P<season>[0-9]{2})E(?P<episode>[0-9]{2}).(?P<teams>.*)', re.IGNORECASE)
tvshowRegex2 = re.compile('(?P<show>.*).(?P<season>[0-9]{1,2})x(?P<episode>[0-9]{1,2}).(?P<teams>.*)', re.IGNORECASE)
movieRegex = re.compile('(?P<movie>.*)[\.|\[|\(| ]{1}(?P<year>(?:(?:19|20)[0-9]{2}))(?P<teams>.*)', re.IGNORECASE)

def parse_name(name):
    fn = name.lower()
    for co, naco in prere:
        fn = re.sub(co, naco, fn)
    res = {'type' : 'unknown', 'name' : fn, 'teams' : [] }

    # usun rok z nazwy serialu
    tv_fn = re.sub(' (19|20)[0-9]{2}','', fn)

    matches_tvshow = tvshowRegex.match(tv_fn)
    if matches_tvshow:
        (tvshow, season, episode, teams) =  matches_tvshow.groups()
        tvshow ,  tvshow.replace(".", " ").strip()
        teams ,  teams.split('.')
        res = {'type' : 'tvshow', 'name' : tvshow.strip(), 'season' : int(season), 'episode' : int(episode), 'teams' : teams}
    else:
        matches_tvshow = tvshowRegex2.match(tv_fn)
        if matches_tvshow:
            (tvshow, season, episode, teams) =  matches_tvshow.groups()
            tvshow ,  tvshow.replace(".", " ").strip()
            teams ,  teams.split('.')
            res = {'type' : 'tvshow', 'name' : tvshow.strip(), 'season' : int(season), 'episode' : int(episode), 'teams' : teams}
        else:
            matches_movie = movieRegex.match(fn)
            if matches_movie:
                (movie, year, teams) = matches_movie.groups()
                res = {'type' : 'movie', 'name' : movie.strip(), 'year' : year, 'teams' : teams}
    return res

def find_imdb(path):
    ImdbId = ''
    try:
        (dir, fname) = os.path.split(path)
        if os.path.exists(path[:-3] + 'nfo'):
            nfof = [ path[:-3] + 'nfo' ]
        else:
            nfof = []
            for f in os.listdir(dir):
                if f.lower().endswith('.nfo'):
                    nfof.append(f)
        for f in nfof:
            for l in open(os.path.join(dir,f)):
                m = re.search(r'title\/(?P<imdbid>tt\d{5,9})', l)
                if m and m.group("imdbid"):
                    ImdbId = m.group("imdbid")
    except:
        pass
    return ImdbId

def hashFile(name):
    try:
        filesize = hash = 0
        imdb = ''
        d = md5()
        longlongformat = 'Q'  # unsigned long long little endian
        bytesize = struct.calcsize(longlongformat)
        format= "<%d%s" % (65536//bytesize, longlongformat)
        f = open(name, "rb") 
        filesize = os.fstat(f.fileno()).st_size
        hash = filesize 
        buffer= f.read(10485760)
        longlongs= struct.unpack(format, buffer[0:65536])
        hash+= sum(longlongs)
        d.update(buffer)
        f.seek(-65536, os.SEEK_END) # size is always > 131072
        longlongs= struct.unpack(format, f.read(65536))
        hash+= sum(longlongs)
        hash&= 0xFFFFFFFFFFFFFFFF
        f.close() 
        imdb = find_imdb(name)
    except:
        print "[DMnapi] Error hashFile: ", name

    return dict( osb = "%016x" % hash, npb = d.hexdigest(), fsize = filesize, imdb = imdb )

def get_sub_from_n24(file, id, fps = 0):
    try:
        to_srt_utf8( get_n24( int(id) ), file, fps = fps)
    except:
        pass

def bigestFromZip(txt):
    try:
        z = zipfile.ZipFile(StringIO(txt))
        s = 0
        for p in z.infolist():
            if p.file_size > s:
                s = p.file_size
                n = p.filename
        content = z.read(n)
        return content
    except:
        print "[DMnapi] Error: zip n24"
    return ''

def get_n24_by_hash(file, item ):
    try:
        data = {
            'postAction': 'CheckSub',
            'ua': 'dmnapi',
            'ap': '4lumen28',
            #'ua': 'service.subtitles.napisy24',
            #'ap': 'eqpXLJLp',
            'fs': item['fsize'],
            'fn': file.split('/')[-1],
            'fh': item['osb'],
            'md': item['npb'],
            'nl': 'PL'
            }
        apiUrl = 'http://napisy24.pl/run/CheckSubAgent.php'
        post = urllib.urlencode(data)
        req = urllib2.Request(apiUrl, post)
        response = urllib2.urlopen(req)
        result = response.read()
        k = {}
        if len(result) > 10:
            data = result.split('||', 1)
            for i in data[0].split('|')[1:]:
                v, c = i.split(':', 1)
                k[v] = c
            s = bigestFromZip(data[1])
            print "DMnapi n24 by hash OK", len(s), k
            return s, k
    except:
        print "DMnapi n24 by hash problem"
        import traceback
        traceback.print_exc()
    return '', k

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

