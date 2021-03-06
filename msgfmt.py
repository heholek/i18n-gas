# msgfmt.py - a utility to generate a script file that adds translations into the catalog
#
# Copyright (c) 2013 Ondrej Mosnáček
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
import polib
from itertools import *

CATALOG_VAR = u'I18N.catalogs'

def get_plural_form(s):
	s = dict(imap(lambda s: imap(unicode.strip, s.partition('=')[::2]), ifilter(lambda s: len(s) != 0, s.split(';'))))
	return (s[u'nplurals'], s[u'plural'])

def process_po(path, output):
	po = polib.pofile(path)
	output.write(u'(function(){{\nvar a={0}["{1}"]={0}["{1}"]||{{}};a=a["{2}"]=a["{2}"]||{{}};\n'.format(CATALOG_VAR, polib.escape(u'messages'), polib.escape(po.metadata[u'Language'])))
	pl = get_plural_form(po.metadata[u'Plural-Forms'])
	output.write(u'var b=a.messages=a.messages||{{}};a.nplurals={0};a.plural=function(n){{return {1}}};\n'.format(pl[0], pl[1]))
	for e in po:
		output.write(u'b["{0}"]={{'.format(polib.escape(e.msgid)))
		output.write(u'msgstr:"{0}",msgstr_plural:{{'.format(polib.escape(e.msgstr)))
		for k in e.msgstr_plural:
			output.write(u'{0}:"{1}",'.format(k, polib.escape(e.msgstr_plural[k])))
		output.write(u'}};\n')
	output.write(u'})();\n')

import argparse

parser = argparse.ArgumentParser(description='Generate message catalog for Gettext.gs from textual translation description.')
parser.add_argument('files', metavar='filename.po', nargs='+', help='input files')
parser.add_argument('-D', '--directory', metavar='DIRECTORY', action='append', help='add DIRECTORY to list for input files search')
parser.add_argument('-f', '--use-fuzzy', action='store_true')
parser.add_argument('-o', '--output-file', metavar='FILE', default='messages.gs', help='write output to specified file')

args = parser.parse_args()

import sys
import os
import codecs

files = args.files
for d in args.directory or ():
	files += ifilter(lambda f: f.endswith('.po'), os.listdir(d))

output_file_name = args.output_file
output_file = codecs.open(output_file_name, 'w', 'utf-8') if output_file_name != '-' else EncodedFile(sys.stdout, 'utf-8')

for f in files:
	process_po(f if f != '-' else '/dev/stdin', output_file)

output_file.close()
