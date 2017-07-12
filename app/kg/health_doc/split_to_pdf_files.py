import sys, os, time, random
sys.path.append('../../../alg/basic')
import str_util

i = 1
cont = open(sys.argv[1], 'rb').read()
retdir = sys.argv[2]
for part in str_util.cut_windows(cont, b'page: ', b'\n~EOF!\n'):
	fp = open('%s/%d.pdf' % (retdir, i), 'wb')
	fp.write(part)
	fp.close()
	i += 1

