# -*- coding: utf-8 -*-

import codecs
from Extractor import Extractor
import sys

extractor = Extractor()
in_file = codecs.open('no_result', 'r', 'utf-8')
result = {}
for line in in_file.readlines():
    if len(line) > 6:
        continue
    res = extractor.extract_simple_tuple(line)
    if len(res) == 0:
        sys.stderr.write(line)
        continue
    for ele in res:
        result[ele] = line.rstrip()

for ele in result.items():
    print(ele)
