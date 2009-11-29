#!/usr/bin/env python

import sys
import BeautifulSoup
import urllib2
import subprocess

try:
    a = sys.argv[1]
except IndexError:
    print "Syntax: ndpr-offprint.py URL/file [out.pdf]"
    sys.exit(1)

try:
    of = sys.argv[2]
except IndexError:
    of = "out.pdf"

if a.lower().startswith("http://"):
    print("Fechting URL: " + a)
    f = urllib2.urlopen(a).read()
else:
    f = open(a).read()

print("Read %d bytes." % len(f))

s = BeautifulSoup.BeautifulSoup(f)
s.find('div',id="header").extract()
s.find('div',id="footer").extract()

print("Converting to latin1...")

child = subprocess.Popen(['uconv', '-f', 'utf8', '-t', 'latin1', '-c'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
s=child.communicate(str(s))[0]

print("Running html2ps...")
child = subprocess.Popen(["html2ps", "-D", "-f", "html2ps.conf"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
s=child.communicate(str(s))[0]

print("Running ps2pdf...")
child = subprocess.Popen(["ps2pdf", "-", "-"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
s=child.communicate(str(s))[0]

print("Writing %s..." % of)
open(of,"w").write(s)
