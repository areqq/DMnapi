# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from enigma import eTimer, iPlayableService, iServiceInformation, getDesktop
from twisted.web.client import getPage
import urllib, urllib2, json
import os, os.path, socket, re
import dmnapim
reload(dmnapim)

class N24Screen(Screen):
    def __init__(self, session, list = None):
        Screen.__init__(self, session)
        self["list"] = ChoiceBox(title = "napisy24", list = list)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
            "ok": self.cancel,
            "cancel": self.cancel
        }, -1)
    def cancel(self):
        print "[N24Screen] - cancel\n"
        self.close(None)

class DMnapisubs(Screen):
    def __init__(self, session, file = None, auto = False,  save = True):
        self.session = session
        self.amenu = auto
        self.plik = file
        self.save = save
        self.subs = {}
        self.srt = ''

        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth > 1900:
            self.fhdskin = True
        else:
            self.fhdskin = False

        (path, file) = os.path.split(self.plik)
        print "DMnapi init plik: %s, auto: %s" % (self.plik, auto)

        self["status"] = Label("Hint: in DreamExpoler use TEXT button")
        self["info"] = Label("DMnapi 2015.10.22 for AFP -  http://areq.eu.org/")
        self["label"] = Label(" Path: %s\n   File: %s\n" % ( path, file) )
        self["right"] = Label("")

        self.statust = ''
        if self.fhdskin:
           self.skin = """<screen name="DMnapi" position="center,center" size="1500,495" title="DMnapi by areq" flags="wfNoBorder">
                        <widget name="info" position="0,0" size="1500,30" font="Regular;27" halign="right" backgroundColor="#193e"/>
                        <widget name="label" position="0,33" size="1500,66" font="Regular;27" halign="left" backgroundColor="background"/>
                        <widget name="menu" position="10,112" size="600,310" itemHeight="34" font="Regular;26" scrollbarMode="showOnDemand" />
                        <widget name="status" position="0,420" size="1500,66" font="Regular;27" halign="left" backgroundColor="background"/>
                        <widget name="right" position="660,105" size="830,310" font="Regular;27" halign="left" backgroundColor="#193e"/>
                        </screen>"""
        else:
            self.skin = """<screen name="DMnapi" position="center,center" size="1000,330" title="DMnapi by areq" flags="wfNoBorder">
                        <widget name="info" position="0,0" size="1000,20" font="Regular;18" halign="right" backgroundColor="#193e" />
                        <widget name="label" position="0,22" size="1000,44" font="Regular;18" halign="left" backgroundColor="background" />
                        <widget name="menu" position="10,75" size="400,200" scrollbarMode="showOnDemand" />
                        <widget name="status" position="-1,281" size="1000,44" font="Regular;18" halign="left" backgroundColor="background" />
                        <widget name="right" position="442,75" size="550,200" font="Regular;18" halign="left" backgroundColor="#193e" />
                        </screen>"""

        Screen.__init__(self, session)

        self.list = []
        ext = file[-3:]
        self.list.append((_("Pobierz napisy z NapiProjekt"), "getnapi"))
        self.list.append((_("Pobierz napisy z napisy24.pl wg. hash"), "napisy24hash"))
        self.list.append((_("Pobierz napisy z napisy24.pl po nazwie"), "napisy24"))
        self.list.append((_("Konwertuj istniejace napisy"), "convert-off"))

        self["menu"] = MenuList(self.list)
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {"ok": self.run, "cancel": self.koniec, }, -1)
        self.onLayoutFinish.append(self.onStart)
        self.onClose.append(self._onclose)

    def onStart(self):
        self.fps = 0
        self.licz_hash()
        url = 'http://www.napiprojekt.pl/index.php3?www=opis.php3&id=%s&film=%s' % (self.fh['npb'], urllib2.quote(os.path.split(self.plik)[1]))
        getPage(url).addCallback(self.znp_imdb).addErrback(self.znp_imdb_e)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = urllib.urlencode(self.fh)
        getPage('http://subs.areq.eu.org/subs/subs.php', method = 'POST', postdata = body, headers = headers).addCallback(self.aqsubs).addErrback(self.znp_imdb_e)
        self.status('http://areq.eu.org/  |')

        self.timer = eTimer()

        self.timer.callback.append(self.tt)
        self.timer.start(800, False)

        for e in ['srt', 'txt', 'sub']:
            try:
                s = open(self.plik[:-3] + e).read(300000)
            except:
                s = ''
            if len(s) > 100:
                if e == 'srt' and s[0:4] == '\xef\xbb\xbf\x31':
                    self.status('Są już napisy srt')
                    break
                else:
                    s = self.prepare_srt(s)
                    if s:
                        self.status('Skonwertowałem: %s' % e )
                    break
        if s:
            self.srt = s

        self.get_np()

    def _onclose(self):
        self.timer.stop()

    def tt(self):
        s = ''
        for i in ['napiprojekt', 'napisy24']:
            s += i
            if self.subs.has_key(i):
                if len(self.subs[i]) > 100:
                    s += ':ok '
                else:
                    s += ':no '
            else:
                s += ':?  '
        if self.fps > 20:
            s +=" fps:%.2f " % self.fps
        s +="\n%s\n" % self.fh.get('Title','')
        if self.fh.has_key('imdb'):
            s += 'imdb: ' + self.fh['imdb'] + '   rate: ' + self.fh.get('imdbRating','?') + '   votes: ' + self.fh.get('imdbVotes','?') + '   type: ' + self.fh.get('Type','?') + '\n'
        s += self.fh.get('Plot', '')
        #print "DMnapi tt:", s
        self["right"].setText(str(s))
        # tutaj auto pobieranie mozna zrobic
           # for i, v in self.subs.iteritems():
           #     if self.saveSRT(v):
           #         self.runSRT = True
           #         break

    def status(self, s):
        self.statust = self.statust +' ' + s
        self["status"].setText(self.statust)

    def licz_hash(self):
            print "DMnapi: licz_hash"
            self.fh = dmnapim.hashFile(self.plik)
            self.fh['plik'] = self.plik
            self.fh['box'] = 'dmnapi4afp'
            print "DMnapi: licz_hash finish", self.fh

    def koniec(self):
        self.close(None)

    def run(self, val = False):
        returnValue = self["menu"].l.getCurrentSelection()[1]
        if returnValue is not None:
            if self.plik:
                path, video =  os.path.split(self.plik)
            print "[DMnapi] menucb :%s:" % returnValue 
            if returnValue == "getnapi":
                if self.saveSRT(self.subs.get('napiprojekt', '')):
                    print "DMnapi: mam napisy, zwracam do afp"
                    self.close(self.srt)
            elif returnValue == "convert":
                askList = []
                for file in os.listdir(path):
                    if file.lower().endswith( ('.txt', '.sub', '.srt') ):
                            if 100 < os.path.getsize(os.path.join(path,file)) < 200000:
                                        askList.append([file, os.path.join(path,file)])
                dei = self.session.openWithCallback(self.ConvertExecution, ChoiceBox, title="Dla " + video, list=askList)
                dei.setTitle(_("Konwersja istniejacych napisow"))
            elif returnValue == "napisy24":
                print "[DMnapi] menucb napisy24a" 
                try:
                    i = dmnapim.parse_name(video)
                    if i['type'] == 'tvshow':
                        ask = 'title=%s %ix%i' % (i['name'], i['season'], i['episode'])
                    else:
                        imdb = dmnapim.find_imdb(self.plik)
                        if imdb != '':
                            ask = 'imdb=%s' % imdb
                        else:
                            ask = 'title=%s' % (i['name'])
                    self.n24ask = ask
                    self.session.openWithCallback(self.vk_movename, VirtualKeyBoard, title = _("Enter name"), text = ask)
                except:
                    import traceback
                    traceback.print_exc()
            elif returnValue == "napisy24hash":
                if self.saveSRT(self.subs.get('napisy24', '')):
                    print "DMnapi: mam napisy.24, zwracam do afp"
                    self.close(self.srt)
                    
            elif returnValue == "exit":
                self.close(None)

    def saveSRT(self, html):
        print "DMnapi saveSRT:", len(html)
        if len(html) > 100:
            s = self.prepare_srt(html, self.save)
            if s:
                self.srt = s
                if self.save:
                    self.status('SRT zapisane')
                    print "DMnapi saveSRT: zapisane"
                else:
                    print "DMnapi saveSRT: bez zapisu"
                return True
            else:
                self.status('DMnapi saveSRT: problem ;(')
        return False

    def vk_movename(self, res):
        if not res:
            res = self.n24ask
        if not res.startswith(('imdb=', 'title=')):
            res = 'title=' + res 
        url = ('http://napisy24.pl/libs/webapi.php?' + res).replace(' ','%20')
        print "[DMnapi] n24 url:", url
        m24res = dmnapim.parse_n24(dmnapim.http_n24(url).split('\n'))
        print "[DMnapi] n24 list:", m24res
        askList = []
        for x,y in m24res.items():
            askList.append(["%s %s:%s" % (y['title'],  y['language'], y['release']), x])
        dei = self.session.openWithCallback(self.n24get, ChoiceBox, title="Q: %s" % (res), list=askList)
        dei.setTitle(_("Napisy24"))

    def n24get(self, answer):
        answer = answer and answer[1]
        if type(answer).__name__ != 'NoneType':
            if len(str(answer)) > 3:
                print "DMnapi n24get:", answer
                try:
                    s = self.prepare_srt(dmnapim.get_n24(answer), self.save)
                    print "DMnapi n24get: mam napisy", len(s)
                    if s and len(s) > 100:
                        self.close(s)
                except: 
                   print "DMnapi n24get: problem"

    def get_np(self):
        self.napiprojekt()
        self.napisy24h()

    def napiprojekt(self):
        body = dmnapim.np_postdata(self.fh['npb'], 'PL')
        apiUrl = "http://napiprojekt.pl/api/api-napiprojekt3.php"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        getPage(apiUrl, method = 'POST', postdata = body, headers = headers).addCallback(self.znp).addErrback(self.znpe)

    def znpe(self, error = None):
        print "DMnapi: getPageError:", error
        self.subs['napiprojekt'] = ''

    def znp(self, html):
        print "DMnapi: znp", len(html)
        if html and len(html) > 100:
            html = dmnapim.np_parsexml(html)
            if html and len(html) > 100:
                s = self.prepare_srt(html, False)
                if s and len(s) > 100:
                    self.subs['napiprojekt'] = s
            else:
                self.subs['napiprojekt'] = ''

    def napisy24h(self):
        data = {
            'postAction': 'CheckSub',
            'ua': 'dmnapi',
            'ap': '4lumen28',
            'fs': self.fh['fsize'],
            'fn': self.plik.split('/')[-1],
            'fh': self.fh['osb'],
            'md': self.fh['npb'],
            'nl': 'PL'
            }
        apiUrl = 'http://napisy24.pl/run/CheckSubAgent.php'
        body = urllib.urlencode(data)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        getPage(apiUrl, method = 'POST', postdata = body, headers = headers).addCallback(self.n24).addErrback(self.znp_imdb_e)

    def n24(self , html = ''):
        print "DMnapi n24", len(html)
        s = ''
        if len(html) > 100:
            k = {}
            data = html.split('||', 1)
            for i in data[0].split('|')[1:]:
                v, c = i.split(':', 1)
                k[v] = c
            self.fh['n24info'] = k
            if len(data[1]) > 100:
                s = dmnapim.bigestFromZip(data[1])
                if len(s) > 100:
                    s = self.prepare_srt(s, False)
                    if not s:
                        s = ''
                print "DMnapi n24", len(s)
        self.subs['napisy24'] = s

    def get_fps(self):
        print "DMnapi get_fps"
        try:
            service = self.session.nav.getCurrentService()
            info = service and service.info()
            fps = info and info.getInfo(iServiceInformation.sFrameRate)/1000.0
        except:
            print "DMnapi get_fp problem"
            fps = 0
        print "DMnapi get_fps", fps
        if 20 < fps < 40:
                self.fps = fps
        return self.fps

    def prepare_srt(self, txt, save = True):
        print "DMnapi prepartesrt:", len(txt), save
        if not 20 < self.fps < 40:
            self.get_fps()
        return dmnapim.to_srt_utf8(txt, self.plik, digest = self.fh['npb'], fps = self.fps, save = save)

    def aqsubs(self, q = None):
        print 'DMnapi aqsubs:', q
        if q and len(q) > 1000:
            self.prepare_srt(q)

    def znp_imdb_e(self, q = None):
        print 'DMnapi - pobranie imdb z napiprojekt nieudane'

    def omdbapi(self, html = None):
        if html:
            try:
                q = json.loads(html)
                if q.has_key('Title') and q.has_key('Type'):
                    self.fh.update(q)
            except:
                pass

    def znp_imdb(self, html = None):
        print 'DMnapi - pobranie imdb z napiprojekt'
        try:
            for f in html.split('\n'):
                i = f.find('www.imdb.com/title/')
                if i > 0:
                    imdb = f[i+18:].split('/')[1]
                    print 'DMnapi - pobranie imdb:', imdb
                    self.fh['imdb'] = imdb
                    url = 'http://www.omdbapi.com/?i=%s' % imdb
                    getPage(url).addCallback(self.omdbapi).addErrback(self.znp_imdb_e)
                    print 'DMnapi - pobranie imdb z napiprojekt:', imdb
        except:
            print 'DMnapi - imdb - problem'
            import traceback
            traceback.print_exc()
