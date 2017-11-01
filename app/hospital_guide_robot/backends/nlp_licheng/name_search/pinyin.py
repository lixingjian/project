#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os.path


class PinYin(object):
    def __init__(self, dict_file='word.data'):
        self.word_dict = {}
        self.dict_file = dict_file

    def load_word(self):
        if not os.path.exists(self.dict_file):
            raise IOError("NotFoundFile")

        with open(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]

    def hanzi2pinyin(self, string=""):
        result = []
        for char in string:
            key = '%X' % ord(char)
            print("%s %s"%(char, key))
            result.append(self.word_dict.get(key, char).split()[0][:-1].lower())
        return result
    
    def hanzi2yintone(self,string=''):
        yin = []
        tone = []
        for char in string:
            key = '%X' % ord(char)
            temp = self.word_dict.get(key, char).split()
            yin.append(temp[0][:-1].lower() )
            tone.append(temp[0][-1])
        return yin,tone
    
    def hanzi2pinyin_split(self, string="", split=""):
        result = self.hanzi2pinyin(string=string)
        if split == "":
            return result
        else:
            return split.join(result)

if __name__ == "__main__":
    test = PinYin()
    test.load_word()
    string = "钓鱼岛是中国的"
    print( "in: %s" % string)
    print( "out: %s" % str(test.hanzi2yintone(string=string)))
    print( "out: %s" % test.hanzi2pinyin_split(string=string, split="-"))
