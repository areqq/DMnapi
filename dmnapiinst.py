#!/usr/bin/python
#    DMnapi for Dreambox-Enigma2
#    Version: 15.11.08
#    Coded by areq (c) 2010-2015
#    Support: http://dvhk.pl/
#    http://areq.eu.org/

import sys, re, os.path

DM_patch = { "FileBrowser": [[[
"""
					self.SetGB(_("Play"))
					self.SetRB(_("Information"))
""",
"""
					self.SetGB(_("Play"))
					self.SetRB(_("Get Subtitle"))		#dmnapi
"""],[
"""
			elif sel[B_FILTER] & (FILTER_PICS | FILTER_MOVIES | FILTER_SOUND):
				from searchMediaInfo import BrowserFileInfos
				self.session.open(BrowserFileInfos, sel)
""",
"""
			elif sel[B_FILTER] & (FILTER_PICS | FILTER_SOUND):
				from searchMediaInfo import BrowserFileInfos
				self.session.open(BrowserFileInfos, sel)
			elif sel[B_FILTER] & FILTER_MOVIES:
				from Plugins.Extensions.DMnapi.DMnapi import DMnapi
				self.session.openWithCallback(self.__movie_Callback, DMnapi, sel[B_FULL])
"""]],[[   # druga werja
"""
				elif sel[3][B_FILTER] & FILTER_MOVIES:
					self.SetGB(_("Play"))
					if pathExists(sel[3][B_CFILE] + ".txt"):
						self.SetRB(_("Information"))
""",
"""
				elif sel[3][B_FILTER] & FILTER_MOVIES:
					self.SetGB(_("Play"))
					self.SetRB(_("Get Subtitle"))		#dmnapi
"""],[
"""
			elif sel[B_FILTER] & FILTER_MOVIES:
				from confFileBrowser import BrowserFileInfos
				self.session.open(BrowserFileInfos, sel)
""",
"""
			elif sel[B_FILTER] & FILTER_MOVIES:
				from Plugins.Extensions.DMnapi.DMnapi import DMnapi
				self.session.openWithCallback(self.__movie_Callback, DMnapi, sel[B_FULL])
"""]],[[ # trzecia werja
"""
					self.SetGB(_("Show"))
				elif sel[3][B_FILTER] & FILTER_MOVIES:
					self.SetGB(_("Play"))
				elif sel[3][B_FILTER] & FILTER_TS:
					self.SetGB(_("Play"))
					self.SetRB(_("Information"))
""",
"""
					self.SetGB(_("Show"))
				elif sel[3][B_FILTER] & FILTER_MOVIES:
					self.SetGB(_("Play"))
					self.SetRB(_("Get Subtitle"))			#dmnapi
				elif sel[3][B_FILTER] & FILTER_TS:
					self.SetGB(_("Play"))
					self.SetRB(_("Information"))
"""],[
"""
				from Plugins.Extensions.PicturePlayer.plugin import Pic_Exif
				self.session.open(Pic_Exif, picload.getInfo(sel[B_FULL]))
				del picload
		except:
			pass

#----------------------------Gelb-Favo
	def KeyBlue(self):
		if self.filter == FILTER_NONE:
""",
"""
				from Plugins.Extensions.PicturePlayer.plugin import Pic_Exif
				self.session.open(Pic_Exif, picload.getInfo(sel[B_FULL]))
				del picload
			elif sel[B_FILTER] & FILTER_MOVIES:							#dmnapi
				from Plugins.Extensions.DMnapi.DMnapi import DMnapi				#dmnapi
				self.session.openWithCallback(self.__napiCallback, DMnapi, sel[B_FULL])		#dmnapi
		except:
			pass

	def __napiCallback(self, val = False): 				#dmnapi
		self.__fillListe()  					#dmnapi

#----------------------------Gelb-Favo
	def KeyBlue(self):
		if self.filter == FILTER_NONE:
"""]], [[ # czwarta werja od Gemini3.2 v0.73
"""
			menu = []
			if not val[3][B_FILTER] & FILTER_GOUP and self.filter == FILTER_NONE:
""",
"""
			menu = []
			if val[3][B_FILTER] & FILTER_MOVIES:
				menu.append((_("Get Subtitle"), "dmnapi", val[3]))
			if not val[3][B_FILTER] & FILTER_GOUP and self.filter == FILTER_NONE:
"""],[
"""
		elif what[1] == "delete":
""",
"""
		elif what[1] == "dmnapi":
			from Plugins.Extensions.DMnapi.DMnapi import DMnapi
			self.session.openWithCallback(self.__moviePlayerCallback, DMnapi, path[B_FULL])
		elif what[1] == "delete":
"""]]],
"BPBrowser": [[[
"""
					self["key_green"].setText(_("Show"))
				elif sel[3][B_FILTER] & Cbputils.FILTER_MOVIES:
					self["key_green"].setText(_("Play"))
				elif sel[3][B_FILTER] & Cbputils.FILTER_TS:
					self["key_green"].setText(_("Play"))
					self["key_red"].setText(_("Info"))
""",
"""
					self["key_green"].setText(_("Show"))
				elif sel[3][B_FILTER] & Cbputils.FILTER_MOVIES:
					self["key_green"].setText(_("Play"))
					self["key_red"].setText(_("Get Subtitle"))	#dmnapi
				elif sel[3][B_FILTER] & Cbputils.FILTER_TS:
					self["key_green"].setText(_("Play"))
					self["key_red"].setText(_("Info"))
"""],[
"""
			from Plugins.Extensions.PicturePlayer.plugin import Pic_Exif
			self.session.open(Pic_Exif, picload.getInfo(sel[B_FULL]))
			del picload

#----------------------------Gelb-Favo
	def KeyYellow(self):
""",
"""
			from Plugins.Extensions.PicturePlayer.plugin import Pic_Exif
			self.session.open(Pic_Exif, picload.getInfo(sel[B_FULL]))
			del picload
		elif sel[B_FILTER] & Cbputils.FILTER_MOVIES:		#dmnapi
			from Plugins.Extensions.DMnapi.DMnapi import DMnapi		#dmnapi
			self.session.openWithCallback(self.__napiCallback, DMnapi, sel[B_FULL])		#dmnapi

	def __napiCallback(self, val = False):		#dmnapi
		self.fill_liste() 		#dmnapi

#----------------------------Gelb-Favo
	def KeyYellow(self):
"""]]],
"plugin": [[[
"""
			"showMovies": self.CloseAndPlay
		}, -1)
		self.onLayoutFinish.append(self.byLayoutEnd)

	def ok(self):
		global DVDPlayerAviable
""",
"""
			"showMovies": self.CloseAndPlay,
			"dmnapi": self.DMnapi			#dmnapi
		}, -1)
		self.onLayoutFinish.append(self.byLayoutEnd)
	
	def DMnapi(self):		#dmnapi
		if not self["filelist"].canDescent():		#dmnapi
			curSelFile = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()	#dmnapi
			from Plugins.Extensions.DMnapi.DMnapi import DMnapi		#dmnapi
			self.session.openWithCallback(self.dmnapiCallback, DMnapi, curSelFile)		#dmnapi
						
	def dmnapiCallback(self, answer=False):		#dmnapi
		self["filelist"].refresh()		#dmnapi

	def ok(self):
		global DVDPlayerAviable
"""]
]],
"MovieSelection": [[[
"""
			menu = [(_("delete : %s") % name, self.delete)]
""",
"""
			if self.service.getPath()[-3:].lower() in ['mkv', 'mp4', 'avi']:
			    menu = [(_("DMnapi: pobierz napisy do filmu"), self.dmnapi), (_("delete : %s") % name, self.delete)]
			else:
			    menu = [(_("delete : %s") % name, self.delete)]
"""],[
"""
	def delete(self):
""",
"""
	def dmnapi(self):
	    print "CB dmnapi"
	    dm_file = self.service.getPath()
	    print dm_file
	    from Plugins.Extensions.DMnapi.DMnapi import DMnapi
	    self.session.openWithCallback(self.close, DMnapi, dm_file)

	def delete(self):
"""]]],
"kolejny": [[[
"""co""",
"""nco"""],[
"""co""",
"""naco"""]]]
}

def saveDEkeymap():
    q="""<keymap>
    <map context="ColorActions">
        <key id="KEY_TEXT" mapto="dmnapi" flags="m" />
    </map>
</keymap>
"""
    open("/usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer/keymap.xml", 'w').write(q)

def dmnapi_chceck():
    if FB.find('#dmnapi') > 0:
        return "Instaled"
    else:
        return "NOT Instaled"

def patch(fn, FB):
    fn = fn.split('/')[-1].split('.')[0]
    for sub in DM_patch.get(fn,[]):
        for s,r in sub:
            if FB.find(s) < 0:
                break
        else:
            for s,r in sub:
                FB = FB.replace(s, r)
    return FB

def DreamExplorer():
    de = '/usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer/'
    insDE = True
    for i in ['plugin.pyo', 'plugin.pyc', 'plugin.py']:
        f = de + i
        if os.path.isfile(f):
            if open(f).read().find('dmnapi20150328') > 0:
                insDE = False
            else:
                if f[-1] != 'y':
                    os.remove(f)
    if insDE:
        print 'DMnapi, brak DreamExplorer, instaluje...'
        try:
            import zipfile, urllib2
            from StringIO import StringIO
            os.system('rm -fr /usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer/')
            z = zipfile.ZipFile(StringIO(urllib2.urlopen('http://areq.eu.org/dmnapi/DreamExplorer.zip').read() ))
            z.extractall('/usr/lib/enigma2/python/Plugins/Extensions/')
            print "DMnapi, DreamExplorer zainstalowany"
        except:
            print "DMnapi, brak DreamExplorer, problem"
            import traceback
            traceback.print_exc()

if __name__ == "__main__":

    print "DMnapi installer by areq.\n"
    for d, f, v, reg in [ \
        ('Gemini3 FileBrowser', '/usr/lib/enigma2/python/Plugins/Bp/geminimain/FileBrowser.py','/usr/lib/enigma2/python/Plugins/Bp/geminimain/gVersion.py', "gVersion = '(.*)'"),\
        ('Gemini2 BPBrowser','/usr/lib/enigma2/python/Bp/BPBrowser.py','/etc/issue.net', "OpenDreambox (.*) %h"),\
        ('VU+ VTI Movie Selection','/usr/lib/enigma2/python/Screens/MovieSelection.py','/etc/vtiversion.info', " v.(.*)"),\
        ('DreamExplorer','/usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer/plugin.py','/usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer/plugin.py', "Version: (.*)") ]:
        if os.path.exists(f) and os.path.exists(v):
            q = open(v).read()
            try:
                ver = re.search(reg , q).group(1)
            except:
                ver = 'unknown'
            print d,"\n\tVersion:", ver,
            FB = open(f).read()
            if FB.find("Plugins.Extensions.DMnapi.plugin") > 0:
                FBp = FB.replace("Plugins.Extensions.DMnapi.plugin", "Plugins.Extensions.DMnapi.DMnapi")
                try:
                    os.rename(f, f + '.backup')
                    open(f, 'w').write(FBp)
                    print " DMnapi reenabled - fixed old code."
                except:
                    print " but problem with writting ;("
            elif FB.find("DMnapi") > 0:
                print "- skipped - DMnapi support already installed."
            else:
                FBp = patch(f, FB)
                if FBp != FB:
                    print "- patched successfully -",
                    try:
                        os.rename(f, f + '.backup')
                        open(f, 'w').write(FBp)
                        print " DMnapi enabled."
                    except:
                        print " but problem with writting ;("

                    if d == 'DreamExplorer':
                        saveDEkeymap()
                        print "\t keymap.xml saved."
                    else:
                        print "- problem, I didn't recognize the file - DMnapi not enabled."
        else:
            print d, "\n\tnot found."
    print

    try:
        for f in ("/usr/lib/enigma2/python/Plugins/Extensions/DMnapi/dmnapi", "/usr/lib/enigma2/python/Plugins/Extensions/DMnapi/dmnapiinst.py"):
            if not os.access(f, os.X_OK):
                print "DMNapi: fix permission"
                os.chmod(f, 0555)
    except:
        print "DMnapi Error: chmod problem"
        pass

    if not os.path.exists('/var/grun/grcstype'):
        DreamExplorer()
    else:
        print "GOS detected. Please install enigma2-plugin-dreamexplorer package"

    # porzadki po starej wersji
    for f in ['N24.py', 'dmnapi.py']:
        for e in ['', 'o', 'c']:
            d = "/usr/lib/enigma2/python/Plugins/Extensions/DMnapi/" + f + e
            if  os.path.exists(d):
                print "Kasuje:", f
                try:
                     os.remove(d)
                except:
                    pass

    print "Finished."

