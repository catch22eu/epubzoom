#!/usr/bin/env python3
#
#    epubzoom is a utility for correcting image sizes in epub files
#    Copyright (C) 2020  Joseph Heller, http://github.com/catch22eu/
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import os							# for filepaths and traversing directories
import zipfile						# (un)compress epub
import xml.etree.ElementTree as ET	# parse xml
import argparse 					# argument parser
import imagesize 					# for getting image dimensions

apversion='''epubzoom v0.2'''
apdescription='''epubzoom is a utility for correcting image sizes in epub files'''
apepilog='''epubzoom Copyright (C) 2020 Joseph Heller
This program comes with ABSOLUTELY NO WARRANTY; for details type use '-w'.
This is free software, and you are welcome to redistribute it under certain 
conditions; use `-c' for details.'''
apwarranty='''
  Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.'''
apcopyright='''
epubzoom is a utility for correcting image sizes in epub files
Copyright (C) 2020  Joseph Heller, http://github.com/catch22eu/

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

printable=" !#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~';"
emsize=16							# html spec em size in pixels
screenwidth=600						# assumed standard screenwidth for epub
screenheight=800					# assumed standard screenheight for epub
emtreshold=2						# image size treshold em vs non-em images
nonemzoom=1.3						# zoomfactor for non-em images
emzoom=0.6							# zoomfactor for em images
hpmaxdef=0.9						# height protect margin
hpmax=hpmaxdef						# set in getpages(), used in setimagedims()
dirlist=[]							# directories that are branched into

def makeprintable(string):
	pstring=""
	for i in range(len(string)):
		if string[i] in printable:
			pstring+=string[i]
		else:
			pstring+="."
	return pstring

def vprint(string,verbositylevel=1,delimiter='\n'):
	if verbositylevel <= verbosity:
		print(makeprintable(string), end=delimiter)

def changedir(infile):
	dirlist.append(os.getcwd())
	if os.path.isdir(infile):
		directory=infile
	else:
		directory=os.path.dirname(infile)
	if len(directory)>0:
		vprint('changeing directory to: '+directory,3)
		os.chdir(directory)

def returndir():
	directory=dirlist[-1]
	vprint('changeing directory back to: '+directory,3)
	os.chdir(directory)
	del dirlist[-1]

def readarguments():
	# note: Parameters starting with - or -- are usually considered optional. All other parameters are positional parameters and as such required by design (like positional function arguments).
	parser = argparse.ArgumentParser(description=apdescription,epilog=apepilog,formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('filename', type=str, help="epub file to be corrected")
	parser.add_argument('-d', type=int, default=1, help="detail level D of output: 0 minimal, 1 default, 2 detail, 3 debug")
	parser.add_argument('-v', action='version', help='show version', version=apversion)
	parser.add_argument('-w', action='version', help='show warranty', version=apwarranty)
	parser.add_argument('-c', action='version', help='show copyright', version=apcopyright)
	args = parser.parse_args()
	if os.path.isfile(args.filename):
		return args.filename, args.d
	else:
		halt("File not found")

def isfontsize(w,h):
	# For formulae and similar, the image should scale relative to the font size. Therefore we guess if this should be done based on the image size. Standard em size is 16px high
	if h<emtreshold*emsize:
		return True
	else:
		return False

def setimagedims(w,h):
	# If the image is deemed to be scaled as character, we return the em size Otherwise, we return the % of the screen width
	if isfontsize(w,h):
		print('(em)',end=' ')
		scale=emzoom*h/emsize
		nh=round(scale,2)
		nw=round(scale*w/h,2)
		nwstr=str(nw)+'em'
		nhstr='auto'
	else:
		scale=100*nonemzoom*w/screenwidth
		if h*scale*h/w/100>hpmax*screenheight:
			# height protect images which would be zoomed larger than screenheight
			print('(hp)',end=' ')
			scale=100*hpmax*(screenheight/h)*(w/screenwidth)
		nw=round(scale)
		nh=round(scale*h/w)
		nwstr=str(nw)+'%'
		nhstr='auto'
	return nwstr,nhstr

def getimagedims(infile):
	w,h=imagesize.get(infile)
	return w,h

def readhtml(infile):
	# Converts the <img> dimenensions, based on the src dimensions. Notes: images contained in an <svg> are not changed, which is usually the case for cover pages. The stylesheet dimensioning is replaced by inline css image dimensions. Only changed xhtml's are overwritten.
	ns={'xhtml':'http://www.w3.org/1999/xhtml'}
	tree=ET.parse(infile)
	root = tree.getroot()
	hreflist=[]
	changedir(infile)
	changed=False
	for img in root.findall(".//xhtml:img",ns):
		#print(img.attrib)
		src=img.get('src')
		print('  image ref: '+src, end=' ')
		w,h=getimagedims(src)
		print('('+str(w)+'x'+str(h)+'px)', end=' ')
		nw,nh=setimagedims(w,h)
		print('--> ('+nw+'x'+nh+')')
		img.set('alt','epubzoom')
		img.set('class','')
		img.set('style','max-width:100%;width:'+nw+';height:'+nh)
		changed=True
	returndir()
	if changed:
		tree.write(infile,encoding='UTF-8',xml_declaration=True, default_namespace=None, method='xml')

def getopf():
	# note the namespace usage, otherwise findall won't find the rootfile
	# TODO: expects only one rootfile, but could be multiple...
	ns={'opf':'urn:oasis:names:tc:opendocument:xmlns:container'}
	tree=ET.parse('META-INF/container.xml')
	root = tree.getroot()
	for rootfile in root.findall('.//opf:rootfile', ns):
		#print(rootfile.attrib)
		fullpath=rootfile.get('full-path')
		print('opf file: '+fullpath)
		return fullpath

def coverpage(root):
	# see opf spec: http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm
	# and https://wiki.mobileread.com/wiki/Ebook_Covers
	ns={'pac':'http://www.idpf.org/2007/opf'}
	coverpage=root.find(".//pac:reference[@type='cover']", ns)
	if coverpage!=None:
		#print(coverpage.attrib)
		return coverpage.get('href')
	else:
		return ''

def getpages(infile):
	global hpmax
	# reads html pages from the .opf file
	ns={'pac':'http://www.idpf.org/2007/opf'}
	# change dir to the .opf file location, and use this as root folder
	changedir(infile)
	tree=ET.parse(os.path.basename(infile))
	root = tree.getroot()
	for item in root.findall(".//pac:item[@media-type='application/xhtml+xml']", ns):
		#print(item.attrib)
		href=item.get('href')
		print('xhtml file: '+href)
		if href==coverpage(root):
			print('  (coverpage)')
			hpmax=1
		else:
			hpmax=hpmaxdef
		readhtml(href)
	returndir()

def zipdir(path):
	zipname=path+'-epubzoom.epub'
	zipf = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk(path):
		for file in files:
			filetozip=os.path.join(root, file)
			filename=filetozip.replace(path+'/','')
			#print(filetozip,filename)
			zipf.write(filetozip, filename)
	zipf.close()

ET.register_namespace('', 'http://www.w3.org/1999/xhtml')
ET.register_namespace('opf', 'http://www.idpf.org/2007/opf')
ET.register_namespace('epub', 'http://www.idpf.org/2007/ops')
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
ET.register_namespace('svg','http://www.w3.org/2000/svg')
infile, verbosity = readarguments()
vprint("extracting: "+infile,0)
epubdir=infile[:-5]
with zipfile.ZipFile(infile, 'r') as file:
	file.extractall(epubdir)
	changedir(epubdir)	
	getpages(getopf())
	returndir()
zipdir(epubdir)


