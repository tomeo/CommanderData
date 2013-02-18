# Decode HTML-escapes
import htmlentitydefs

# Get title of webpage libs
import urllib2
import BeautifulSoup
import json
import re

def convert_html_entities(s):
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, unichr(entnum))
            except ValueError:
                pass

    matches = re.findall("&#[xX][0-9a-fA-F]+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            hex = hit[3:-1]
            try:
                entnum = int(hex, 16)
                s = s.replace(hit, unichr(entnum))
            except ValueError:
                pass

    matches = re.findall("&\w+;", s)
    hits = set(matches)
    amp = "&amp;"
    if amp in hits:
        hits.remove(amp)
    for hit in hits:
        name = hit[1:-1]
        if htmlentitydefs.name2codepoint.has_key(name):
            s = s.replace(hit, unichr(htmlentitydefs.name2codepoint[name]))
    s = s.replace(amp, "&")
    return s 

def IsNotNull(value):
    return value is not None and len(value) > 0

def get_markup(url):
    return BeautifulSoup.BeautifulSoup(urllib2.urlopen(url))

def get_json(url):
    req = urllib2.Request(url)
    f = urllib2.build_opener().open(req)
    return json.load(f)