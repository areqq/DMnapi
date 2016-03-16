#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re

def tounicode( sub ):
    if sub.startswith('\xef\xbb\xbf'):
        return sub.decode("utf-8-sig",'ignore'), "utf-8-sig"
    elif sub.startswith( ('\xff\xfe\x00\x00', '\x00\x00\xfe\xff') ):
        return sub.decode("utf-32",'ignore'), "utf-32"
    elif sub.startswith( ('\xff\xfe', '\xfe\xff') ):
        return sub.decode("utf-16",'ignore'), "utf-16"
    iso = win = utf = 0
    for i in (161, 166, 172, 177, 182, 188):
        iso += sub.count(chr(i))
    for i in (140, 143, 156, 159, 165, 185):
        win += sub.count(chr(i))
    for i in (195, 196, 197):
        utf += sub.count(chr(i))
    if win > utf and win > iso:
        return sub.decode("CP1250",'ignore'), "CP1250"
    if utf > iso and utf > win:
        return sub.decode("utf-8",'ignore'), "utf-8"
    return sub.decode("iso-8859-2",'ignore'), "iso-8859-2"

def detect_format(list):
    """
    Detect the format of input subtitles file.
    input: contents of a file as list
    returns: format (srt, tmp, mdvd) or "" if unknown
    """
    re_mdvd = re.compile("^\{(\d+)\}\{(\d*)\}\s*(.*)")
    re_srt = re.compile("^(\d+):(\d+):(\d+),\d+\s*-->.*")
    re_tmp = re.compile("^(\d+):(\d+):(\d+):(.*)")
    re_sub2 = re.compile("^(\d+):(\d+):(\d+)\.\d+\s*\,.*")
    re_mpl2 = re.compile("^\[(\d+)\]\[(\d+)\]\s*(.*)")
    for line in list:
        if re_mdvd.match(line):
            return "mdvd"
        elif re_srt.match(line):
            return "srt"
        elif re_tmp.match(line):
            return "tmp"
        elif re_sub2.match(line):
            return "sub2"
        elif re_mpl2.match(line):
            return "mpl2"
    return "unknown"

def read_mdvd(list, fps):
    """
    Read micro-dvd subtitles.
    input: contents of a file as list
    returns: list of subtitles in form: [[time_start in secs, time_end in secs, line1, ...],....]
    """
    re1 = re.compile("^\{(\d+)\}\{(\d*)\}\s*(.*)")

    subtitles = []
    while len(list)>0:
        x = list.pop(0)
        m = re1.match(x, 0)
        if m:
            time1 = int(m.group(1))
            subt = [ time1 / fps ]
            time2 = m.group(2)
            if time2 == '':
                time2 = int(time1) + 20
            subt.append(int(time2) / fps)
            texts = m.group(3).strip().split("|")
            for i in range(len(texts)):
                text = texts[i]
                if text.lower().startswith('{c:') or text.lower().startswith('{y:'):
                    end_marker = text.index('}')
                    if end_marker:
                        text = text[end_marker + 1:]
                        texts[i] = text
            subt.extend(texts)
            subtitles.append(subt)
    return subtitles

def read_mpl2(list):
    """
    Read mpl2 subtitles
    input: contents of a file as list
    returns: list of subtitles in form: [[time_start in secs, time_end is secs, line1, ...],.....]
    """
    re1 = re.compile("^\[(\d+)\]\[(\d+)\]\s*(.*)")
    subtitles = []
    while len(list)>0:
        m = re1.match(list.pop(0),0);
        if m:
            subt = [int(m.group(1))*0.1]
            subt.append(int(m.group(2))*0.1)
            subt.extend(m.group(3).strip().split("|"))
            subtitles.append(subt)
    return subtitles

def read_sub2(list):
    """
    Reads subviewer 2.0 format subtitles, e.g. :
        00:01:54.75,00:01:58.54
        You shall not pass!
    input: contents of a file as list
    returns: list of subtitles in form: [[time_dep, time_end, line1, ...],[time_dep, time_end, line1, ...],....]
    """
    re1 = re.compile("^(\d+):(\d+):(\d+)\.(\d+)\s*\,\s*(\d+):(\d+):(\d+)\.(\d+).*$")
    subtitles = []
    try:
        while len(list)>0:
            m = re1.match(list.pop(0), 0)
            if m:
                subt = [int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)) + int(m.group(4))/100.0]
                subt.append(int(m.group(5))*3600 + int(m.group(6))*60 + int(m.group(7)) + int(m.group(8))/100.0)
                l = list.pop(0).strip()
                lines = l.split("[br]")
                for i in range(0,len(lines)):
                    subt.append(lines[i])
                subtitles.append(subt)
    except IndexError:
        sys.stderr.write("Warning: it seems like input file is damaged or too short.\n")
    return subtitles

def read_srt(list):
    """
    Reads srt subtitles.
    input: contents of a file as list
    returns: list of subtitles in form: [[time_dep, time_end, line1, ...],[time_dep, time_end, line1, ...],....]
    """
    re1 = re.compile("^(\d+)\s*$")
    re2 = re.compile("^(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+).*$")
    re3 = re.compile("^\s*$")
    subtitles = []
    try:
        while len(list)>0:
            if re1.match(list.pop(0), 0):
                m = re2.match(list.pop(0), 0)
                if m:
                    subt = [int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)) + int(m.group(4))/1000.0]
                    subt.append(int(m.group(5))*3600 + int(m.group(6))*60 + int(m.group(7)) + int(m.group(8))/1000.0)
                    l = list.pop(0)
                    while not re3.match(l, 0):
                        #subt.append(string.replace(l[:-1], "\r", ""))
                        subt.append(l.strip())
                        l = list.pop(0)
                    subtitles.append(subt)
    except IndexError:
        sys.stderr.write("Warning: it seems like input file is damaged or too short.\n")
    return subtitles

def read_tmp(list):
    """
    Reads tmplayer (tmp) subtitles.
    input: contents of a file as list
    returns: list of subtitles in form: [[time_dep, time_end, line1, ...],[time_dep, time_end, line1, ...],....]
    """
    re1 = re.compile("^(\d+):(\d+):(\d+):(.*)")
    subtitles = []
    subs={}
    while len(list)>0:
        m = re1.match(list.pop(0), 0)
        if m:
            time = int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3))
            if subs.has_key(time) :
                subs[time].extend(m.group(4).strip().split("|"))
            else:
                subs[time] = m.group(4).strip().split("|")

    times = subs.keys()
    times.sort()
    for i in range(0,len(times)):
        next_time = 1;
        while not subs.has_key(times[i]+next_time) and next_time < 4 :
            next_time = next_time + 1
        subt = [ times[i] , times[i] + next_time]
        subt.extend(subs[times[i]])
        subtitles.append(subt)
    return subtitles

def to_srt(list):
    """
    Converts list of subtitles (internal format) to srt format
    """
    outl = []
    count = 1
    for l in list:
        secs1 = l[0]
        h1 = int(secs1/3600)
        m1 = int(int(secs1%3600)/60)
        s1 = int(secs1%60)
        f1 = (secs1 - int(secs1))*1000
        secs2 = l[1]
        h2 = int(secs2/3600)
        m2 = int(int(secs2%3600)/60)
        s2 = int(secs2%60)
        f2 = (secs2 - int(secs2))*1000
        outl.append("%d\n%.2d:%.2d:%.2d,%.3d --> %.2d:%.2d:%.2d,%.3d\n%s\n\n" % (count,h1,m1,s1,f1,h2,m2,s2,f2,"\n".join(l[2:])))
        count = count + 1
    return outl


def sub_fix_times(sub):
    for i in range( len(sub) - 2 ):
        approx = min(1 + ( len(" ".join(sub[i][2:])) / 10 ), 9.9)                 # 10 char per second
#       print sub[i][0],sub[i][1], sub[i][1] - sub[i][0], approx
        if (sub[i + 1 ][0] <= sub[i][0]):
            sub[i + 1 ][0] = sub[i][0] + approx + 0.2
        #jesli mniej niz 1s
        if sub[i][1] - sub[i][0] < 1:
                sub[i][1] = sub[i][0] + approx
        # end < start or end > start++ or displayed longer then 15s
        if (sub[i][1] < sub[i][0]) or (sub[i][1] > sub[i + 1][0]) or ( sub[i][1] - sub[i][0] > 15):
            if ( sub[i][0] + approx ) < sub[i + 1][0]:
                sub[i][1] = sub[i][0] + approx
            else:
                sub[i][1] = sub[i + 1][0] - 0.2
    return sub

def read_subs(subs, fps):
    """
    Import subtitles from list src, using format fmt
    input : strings, format (srt,mdvd,tmp)
    returns: list of subtitles in form: [[time in secs, line1, ...],[time in secs, line1, ...],....]
    """
    fmt = detect_format(subs)
    if fmt == "tmp":
        return read_tmp(subs)
    elif fmt == "srt":
        return read_srt(subs)
    elif fmt == "mdvd":
        return read_mdvd(subs, fps)
    elif fmt == "sub2":
        return read_sub2(subs)
    elif fmt == "mpl2":
        return read_mpl2(subs)
    else:
        return []

def xxto_srt_utf8(subs, fps = 0):
        subs_u , org_cod = tounicode(subs)
        subs = subs_u.replace('\r','').split('\n')
        subs = "".join(to_srt( sub_fix_times(read_sub(subs, fps) )))
        subs = subs.encode("utf-8-sig")
        return subs
