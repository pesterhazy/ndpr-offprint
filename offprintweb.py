#!/usr/bin/env python

import re, yaml, os, logging, subprocess
from flask import Flask, request, render_template, Response
from ndpr import convert

BASEDIR = os.path.dirname(os.path.abspath(__file__))
LOGFILENAME = BASEDIR + "/ndpr.log"
logging.basicConfig(filename=LOGFILENAME,level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template("form.html")

@app.route('/about')
def about():
    gitdir = BASEDIR + "/.git"
    gitlog = subprocess.Popen(["git","--git-dir",gitdir,"log","--format=%ar: %s","--max-count=12"],stdout=subprocess.PIPE).communicate()[0]
    gitlog = [s.strip() for s in gitlog.split("\n")]

    return render_template("about.html", gitlog=gitlog)

@app.route('/offprinturl', methods=["POST"])
def offprinturl():
    url = request.form["url"]

    m=re.search("review.cfm\?id=(\d*)",url)
    if m:
        filename = "ndpr-%s.pdf" % m.group(1)
    else:
        filename = "ndpr.pdf"

    pdf = convert(url)

    r = Response(pdf)
    r.headers["content-type"] = "application/pdf"
    r.headers["content-disposition"] = "attachment;filename=" + filename
    r.headers["content-length"] = len(pdf)
    return r

@app.route('/offprintfile', methods=["POST"])
def offprintfile():
    url = request.form["url"]

    m=re.search("review.cfm\?id=(\d*)",url)
    if m:
        filename = "ndpr-%s.pdf" % m.group(1)
    else:
        filename = "ndpr.pdf"

    pdf = convert(url)

    r = Response(pdf)
    r.headers["content-type"] = "application/pdf"
    r.headers["content-disposition"] = "attachment;filename=" + filename
    r.headers["content-length"] = len(pdf)
    return r

@app.route('/markdown', methods=["POST"])
def markdown():
    url = request.form["url"]

    m=re.search("review.cfm\?id=(\d*)",url)
    if m:
        filename = "ndpr-%s.pdf" % m.group(1)
    else:
        filename = "ndpr.pdf"

    pdf = convert(url)

    r = Response(pdf)
    r.headers["content-type"] = "application/pdf"
    r.headers["content-disposition"] = "attachment;filename=" + filename
    r.headers["content-length"] = len(pdf)
    return r

@app.route('/search')
def search():
    default = "g"

    engines = Engines()

    q = request.args["q"]

    m = re.match(r'(\w+)\s+(.+)',q)

    if m:
        key, to = m.groups()
        try:
            url = engines.get(key).url
        except KeyError:
            to = q
            url = engines.get_default().url
    else:
        url = engines.get_default().url
        to = q

    url = url % (to,)
    return redirect(url)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9291)
