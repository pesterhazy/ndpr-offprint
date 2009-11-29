#!/usr/bin/env python

import sys
import BeautifulSoup
import urllib2
import subprocess, tempfile

HTML2PSCONFIG = """
BODY {
    font-size: 14pt; 
    font-family: Times; 
    text-align: justify; 
}
A:link {
    color: black;
}
\@page { 
    margin-left: 2.5cm; 
    margin-right: 2.5cm; 
    margin-top: 2.5cm; 
    margin-bottom: 2.5cm; 
}
\@html2ps { 
    option { 
        twoup: 1; 
        landscape: 1; 
        number: 0; 
    } 
    paper { type: a4 } 
	header {
	    right: "NDPR";
		left: $T;
    }
    footer {
        left: $N;
        right: NDPR;
    }
}
"""

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
    print("Fetching URL: " + a)
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
configfile = tempfile.NamedTemporaryFile()
configfile.write(HTML2PSCONFIG)
configfile.flush()
child = subprocess.Popen(["html2ps", "-D", "-f", configfile.name],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
s=child.communicate(str(s))[0]
configfile.close()

print("Running ps2pdf...")
child = subprocess.Popen(["ps2pdf", "-", "-"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
s=child.communicate(str(s))[0]

print("Writing %s..." % of)
open(of,"w").write(s)
