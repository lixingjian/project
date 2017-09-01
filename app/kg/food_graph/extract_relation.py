import sys, os, json
sys.path.append('../../../alg/basic')
sys.path.append('../../../lib/nlp/basic')
import str_util, ltp_seg

class FoodGraph:
    def __init__(self):
        self.seg_dict = ltp_seg.LexParser('./ltp_data', use_ner = False, use_parser = False)
        self.food_dict = str_util.read_kv_file('./dict/food_list', read_value = False)
        self.nutr_dict = str_util.read_kv_file('./dict/nutr_list', read_value = False)
        self.adj_dict = str_util.read_kv_file('./dict/adj_list', read_value = True)
        self.verb_dict = str_util.read_kv_file('./dict/verb_list', read_value = False)

    def extract(self, page_str):
        page_obj = json.loads(page_str, encoding = 'utf8')
        if not 'content' in page_obj:
            return []
        
        result = []
        cur_entity = ''
        if 'title' in page_obj:
            for word in self.seg_dict.run(page_obj['title'])[0]:
                if word in self.food_dict:
                    cur_entity = word
                    break

        for item in page_obj['content']:
            if (not 'type' in item) or (item['type'] != 'text'):
                continue
            cont = item['data']
            for sent in cont.split('。'):
                word_list = self.seg_dict.run(sent)[0]

                #确定当前句子所描述的实体，如不提及，认为是title的实体
                for word in word_list:
                    if word in self.food_dict:
                        cur_entity = word
                        break
                if cur_entity == '':
                    continue

                #筛选出包含指定动词的句子
                is_valid = False
                for word in word_list:
                    if word in self.verb_dict:
                        is_valid = True
                        break
                if not is_valid:
                    continue
                
                #抽取营养素和含量
                adj = 'normal'
                word_count = len(word_list)
                for i in range(0, word_count):
                    word = word_list[i]
                    if not word in self.nutr_dict:
                        continue
                    for j in range(max(0, i-3), min(i+3, word_count)):
                        if word_list[j] in self.adj_dict:
                            adj = self.adj_dict[word_list[j]]
                            break
                    result.append((cur_entity, word, adj))
                    print(sent, str((cur_entity, word, adj)))
        return result

if __name__ == '__main__':
    fg = FoodGraph()
    while 1:
        try:
            buf = input().rstrip().lower()
        except:
            break
        ret = fg.extract(buf)
        '''
        for item in ret:
            print(buf + '\t' + str(item))
        '''
