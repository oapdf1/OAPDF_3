#! /usr/bin/env python

import os,sys,glob,time
import re, requests,urllib2,json
requests.packages.urllib3.disable_warnings()

username="oapdf1"
doilinkdir='../doilink'

workingdir=os.path.abspath('.')
nowdir=os.path.basename(os.path.abspath(os.path.curdir))

def doidecompose(suffix):
	lens=len(suffix)
	if (lens<=5):
		return ""
	layer=(lens-1)/5
	dirurl=""
	for i in range(layer):
		## In window, dir name can't end at '.'
		dirurl += suffix[i*5:(i+1)*5].rstrip('.')+"/"
	return dirurl

def quotefileDOI(doi):
	'''Quote the doi name for a file name'''
	return urllib2.quote(doi,'+/()').replace('/','@')

def unquotefileDOI(doi):
	'''Unquote the doi name for a file name'''
	return urllib2.unquote(doi.replace('@','/'))

def is_oapdf(doi,check=False):
	'''Check the doi is in OAPDF library'''
	if (check and "/" not in doi and "@" in doi):
		doi=unquotefileDOI(doi)
	try:#urllib maybe faster then requests
		r=urllib2.urlopen("http://oapdf.github.io/doilink/pages/"+decomposeDOI(doi,url=True)+".html")
		return (r.code is 200)
	except:
		return False

def writeoapdfpage(fname,realdoi,reallink,pdflink):
	fw=open(fname,'w')
	fw.write("<html><head><title>"+realdoi+'</title><meta name="robots" content="noindex,nofollow" /> <meta name="googlebots" content="noindex,nofollow" /></head><body>')
	fw.write('<iframe src="'+reallink+'" width="100%" height="96%"></iframe><div width="100%" align="center"><span style="align:center;">')
	fw.write('<a href="https://github.com/OAPDF/doilink/">OAPDF Project</a> : ')
	fw.write('<a href="https://scholar.google.com.hk/scholar?q='+realdoi+'">Google Scholar</a> | ')
	fw.write('<a href="http://xueshu.baidu.com/s?wd='+realdoi+'">Baidu Scholar</a> | ')
	fw.write('<a href="http://www.ncbi.nlm.nih.gov/pubmed/?term='+realdoi+'">PubMed</a> | ')
	fw.write('<a href="'+pdflink+'">PDFLink</a></span></div></body></html>')
	fw.close()

def combinepage(fname,outdir='_pages/',outdoilinkdir='../doilink/pages/'):
	'''Only suitable here'''
	if (outdir == doilinkdir):return
	doifname=fname.replace(outdir,outdoilinkdir,1)
	if (not os.path.exists(fname)):return
	f=open(fname);s2=f.read();f.close()

	doidir=os.path.split(doifname)[0]
	if (not os.path.exists(doifname)):
		try:
			if (not os.path.exists(doidir)): os.makedirs(doidir)
			f=open(doifname,'w');
			f.write(s2);
			f.close()
		except Exception as e:
			print e
			print "Can't write out to doilink file:",doifname
		return

	f=open(doifname);s1=f.read();f.close()
	pp1=s1.find('PubMed</a>')
	pp2=s2.find('PubMed</a>')
	cp1=s1[pp1:].find('|')#maybe rfind('|') will good, by if | exist at end?
	cp2=s2[pp1:].find('|')
	links1=pl.findall(s1[pp1+cp1:])
	links2=pl.findall(s2[pp2+cp2:])
	for link in links2:
		if link not in links1:
			links1.append(link)
	linkstr=""
	for i in range(len(links1)):
		if (i is 0):
			linkstr+='<a href="'+links1[i]+'">PDFLink</a>'
		else:
			linkstr+=',<a href="'+links1[i]+'">'+str(i+1)+'</a>'
	f=open(doifname,'w')
	f.write(re.sub(r'PubMed</a>.*?</span>','PubMed</a> | '+linkstr+'</span>',s1))
	f.close()
	print "Successful combine for:",fname, 'with',len(links1), 'links'

def genoapdfpage(fname,pdflink,doilinkdir="",postcombine=True, force=False, movetotarget=""):
	#'''Generate page at _pages dir'''
	#try:
		doi=os.path.splitext(os.path.split(fname)[1])[0]
		dois=doi.split("@",1)
		doi1=dois[0]
		doi2=dois[1]
		suffixpath=doidecompose(doi2)
		pagedir='_pages/'+doi1+"/"+suffixpath;
		realdoi=unquotefileDOI(doi)
		r=requests.get("http://dx.doi.org/"+realdoi)
		if (r.status_code != 404 ):
			reallink=r.url
			if (not os.path.exists(pagedir)): os.makedirs(pagedir)
			writeoapdfpage(pagedir+doi+".html",realdoi=realdoi,reallink=reallink,pdflink=pdflink)
			if (force and doilinkdir):
				writeoapdfpage(doilinkdir+"/pages/"+doi+".html",realdoi=realdoi,reallink=reallink,pdflink=pdflink)
			if (postcombine and doilinkdir): 
				combinepage(pagedir+doiat+".html",pagedir,doilinkdir+"/pages/")
			if (movetotarget):
				os.renames(fname,movetotarget+"/"+doi1+"/"+doi+".pdf")
			return True
		else:
			print doi, " Error Link!"
			return False
	#except:
	#	return False


outdict={"owner":username, "repo":nowdir}
fmove={}
fcount=0
ig=glob.iglob("10.*/10.*.pdf")
for f in ig:
	fsize=os.path.getsize(f)
	fmove[f]=fsize
	fcount+=1

fmovefname={}
for k,v in fmove.items():
	fname=os.path.split(k)[1]
	fmovefname[fname]=v
	sout=(fmovefname)

outdict['total']=fcount
outdict['items']=fmovefname

f=open(doilinkdir+os.sep+nowdir+"@"+username+".json",'w')
f.write(json.dumps(outdict))
f.close()

fmove.clear()
fmovefname.clear()
