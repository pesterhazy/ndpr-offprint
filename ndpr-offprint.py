#!/usr/bin/env python

import sys
from BeautifulSoup import BeautifulSoup
import urllib2
import subprocess, tempfile
from optparse import OptionParser

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
	    right: "%(title)s";
		left: $T;
    }
    footer {
        left: $N;
        right: "%(title)s";
    }
}
"""

class LRBParser:
    format = { "title":"LRB" }

    def extract(self,txt):
        s = BeautifulSoup(txt)
        for x in s.findAll(style="display:none"):
            x.extract()

        i=s.find('div',"article-body indent")
        t=s.find('title')
        i=("<html>" + str(t) + "<body>" + str(i) + "</body></html>")
        return str(i)

class NDPRParser:
    format = { "title":"NDPR" }

    def extract(self,txt):
        s = BeautifulSoup(txt)
        s.find('div',id="header").extract()
        s.find('div',id="footer").extract()
        return str(s)

def main():
    parser = OptionParser("usage: %prog [options] URL/file out.pdf")

    parser.add_option("-n","--ndpr",action="store_const",dest="type",const="ndpr",
        help="Notre Dame Philosophical Review")
    parser.add_option("-l","--lrb",action="store_const",dest="type",const="lrb",
        help="London Review of Books")
    parser.set_defaults(type="ndpr")

    (options,args) = parser.parse_args()
    if len(args) < 1:
        parser.error("incorrect number of arguments")

    a = args[0]
    try:
        of = args[1]
    except IndexError:
        of = "out.pdf"

    if options.type == "lrb":
        typeparser = LRBParser()
    else:
        typeparser = NDPRParser()

    if a.lower().startswith("http://"):
        print("Fetching URL: " + a)
        f = urllib2.urlopen(a).read()
    else:
        f = open(a).read()

    print("Read %d bytes." % len(f))

    # extract information
    s=typeparser.extract(f)

    print("Converting to latin1...")
    child = subprocess.Popen(['iconv', '-f', 'utf8', '-t', 'latin1//TRANSLIT'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    s=child.communicate(str(s))[0]

    print("Running html2ps...")
    configfile = tempfile.NamedTemporaryFile()
    configfile.write(HTML2PSCONFIG % typeparser.format)
    configfile.flush()
    child = subprocess.Popen(["html2ps", "-D", "-f", configfile.name],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    s=child.communicate(str(s))[0]
    configfile.close()

    print("Running ps2pdf...")
    child = subprocess.Popen(["ps2pdf", "-", "-"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    s=child.communicate(str(s))[0]

    print("Writing %s..." % of)
    open(of,"w").write(s)

if __name__ == "__main__":
    main()
