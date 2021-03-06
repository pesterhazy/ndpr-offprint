#!/usr/bin/env python

import sys, os, re
from BeautifulSoup import BeautifulSoup
import urllib2
import subprocess, tempfile, shutil
from optparse import OptionParser
import logging

BASEDIR = os.path.dirname(os.path.abspath(__file__))

class LatexFailedError(Exception):
    pass

class DefaultParser:
    format = { "title":"From web" }

    def extract(self,txt):
        return str(txt)

class LRBParser:
    format = { "title":"LRB" }

    def extract(self,txt):
        s = BeautifulSoup(txt)
        for x in s.findAll(style="display:none"):
            x.extract()

        i=s.find('div',"article-body indent")
        return str(i)

class NYRBParser:
    format = { "title":"New York Review of Books" }

    def extract(self,txt):
        s = BeautifulSoup(txt)

        i=s.find(id="article-body")
        return str(i)

class SEPParser:
    format = { "title":"Stanford Encyclopedia" }

    def extract(self,txt):
        s = BeautifulSoup(txt)

        i=s.find(id="aueditable")
        return str(i)

class NDPRParser:
    format = { "title":"NDPR" }

    def extract(self,txt):
        txt = re.sub("</?o:p>","",txt)
        txt = re.sub("&(?!\w*;)","&amp;",txt)

        soup = BeautifulSoup(txt)
        soup = soup.find('div',id="review")
        for tag in soup.findAll("a"):
            tag.replaceWith(tag.renderContents())

        return str(soup)

def deduceParserFromUrl(url):
    if re.search("lrb\.co\.uk", url):
        typeparser = LRBParser
    elif re.search("ndpr\.nd\.edu", url):
        typeparser = NDPRParser
    elif re.search("nybooks\.com", url):
        typeparser = NYRBParser
    elif re.search("plato\.stanford\.edu|stanford\.library\.usyd\.edu\.au|www\.seop\.leeds\.ac\.uk|www\.science\.uva\.nl", url):
        typeparser = SEPParser
    else:
        typeparser = DefaultParser
    return typeparser

def runLatex(html, layout="2up", typ="html"):
    tmpdir = tempfile.mkdtemp(prefix="offprint")
    try:
        i = tmpdir + "/i.html"
        o = tmpdir + "/o.tex"
        p = tmpdir + "/o.pdf"
        l = tmpdir + "/o.log"
        template = BASEDIR + ("/%s.template" % (layout,))

        f = open(i, "wb")
        f.write(html)
        f.close()

        print >>sys.stderr, "tmpdir:", tmpdir

        subprocess.check_call(["pandoc", "-f", typ, "-st", "latex", "--xetex",
            "--template=" + template, "-o", o, i])
        code = subprocess.call(["xelatex", "-interaction=batchmode", "-output-directory", tmpdir, o])

        if code != 0:
            print("Warning: latex returned error code %s" % code)
            logging.warning(open(l,"r").read())

        if not os.path.exists(p):
            raise LatexFailedError("No PDF generated.")

        pdf = open(p, "rb").read()
        if len(pdf) < 1000:
            raise LatexFailedError("Invalid PDF")
    finally:
#        shutil.rmtree(tmpdir)
        pass
    
    return pdf

def convert(url,parser=DefaultParser,layout="2up",typ="url",offprint=True):
    if typ=="url":
        logging.debug("Retrieving url '%s'" % url)
        html = urllib2.urlopen(url).read()
    else:
        # local file
        html = open(url).read()

    if offprint:
        logging.debug("Parsing")

        if typ=="url":
            parser = deduceParserFromUrl(url)

        typeparser = parser() # instantiate
        html = typeparser.extract(html)

    logging.debug("Running latex")
    if offprint:
        pdf = runLatex(html,layout=layout)
    else:
        pdf = runLatex(html,layout=layout,typ="markdown")
    logging.debug("Done.")
    return pdf

def main():
    parser = OptionParser("usage: %prog [options] URL/file out.pdf")

    parser.add_option("-n","--ndpr",action="store_const",dest="type",const="ndpr",
        help="Notre Dame Philosophical Review")
    parser.add_option("-l","--lrb",action="store_const",dest="type",const="lrb",
        help="London Review of Books")
    parser.add_option("-x","--extract",action="store_true",dest="extract",
        help="Extract only (don't generate pdf)")
    parser.set_defaults(type="ndpr")

    (options,args) = parser.parse_args()
    if len(args) < 1:
        parser.error("incorrect number of arguments")

    a = args[0]
    try:
        of = args[1]
    except IndexError:
        if options.extract:
            print("You need to specify an output file name.")
            sys.exit(1)

        if a.lower().startswith("http://"):
            of = "out.pdf"
        else:
            root = os.path.splitext(os.path.basename(a))[0]
            of = root + ".pdf"

    if options.type == "lrb":
        typeparser = LRBParser()
    else:
        typeparser = NDPRParser()

    if not a.lower().startswith("http://"):
#        print("Fetching URL: " + a)
#        f = urllib2.urlopen(a).read()
#    else:
        print "Temporarily disabled."
        sys.exit(1)

        f = open(a).read()

    pdf = convert(a)

#    if options.extract:
#        print("Writing %s..." % of)
#        f = open(of,"w")
#        f.write(s)
#        f.close()
#    else:
#        try:
#            pdf = runLatex(s)
#        except LatexFailedError:
#            print("Error: Latex command failed to generate PDF file.")
#            sys.exit(1)

    print("Writing %s..." % of)
    f=open(of,"w")
    f.write(pdf)
    f.close()

if __name__ == "__main__":
    main()
