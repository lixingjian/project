# -*- coding: utf-8 -*-

from pinyin import PinYin

def name2name_pinyin(name_path, name_pinyin_path):
    py = PinYin()
    py.load_word()
    name_file = open(name_path,'r')
    pinyin_file = open(name_pinyin_path,'w')
    for name in name_file:
        name = name.strip('\n')
        yin_list, tone_list = py.hanzi2yintone(string = name)
        res = name + '\t'
        for yin in yin_list:
            res = res  + yin + ' '
        res = res.strip(' ')
        res += ':'
        for tone in tone_list:
            res = res + tone + ' '
        res = res.strip(' ')
        res = res + '\n'
        pinyin_file.write(res)

if __name__ == "__main__":
    name2name_pinyin('name_dict', 'name_yin_tone_dict')
