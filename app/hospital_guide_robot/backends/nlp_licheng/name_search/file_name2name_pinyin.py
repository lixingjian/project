# -*- coding: utf-8 -*-

from pinyin import PinYin

def name2name_pinyin(name_path, name_pinyin_path):
    py = PinYin()
    py.load_word()
    name_file = open(name_path,'r')
    pinyin_file = open(name_pinyin_path,'w')
    for name in name_file:
        name = name.strip('\n')
        pinyin_list = py.hanzi2pinyin(string = name)
        res = name + '\t'
        for pinyin in pinyin_list:
            res = res  + pinyin + ' '
        res = res.strip(' ')
        res = res + '\n'
        pinyin_file.write(res)

if __name__ == "__main__":
    name2name_pinyin('name_dict', 'name_pinyin_dict')


