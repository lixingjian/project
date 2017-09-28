import re
import codecs

class extract:
    def __init__(self):
        self.page_start_match = r'url: http://zzk\.xywy\.com/p/(.*)\.html'
        self.p_start_match = re.compile(self.page_start_match)
        self.page_end_match = r'~EOF!'
        self.extract_match = r'_gaishu.html" target="_blank" title="(.*)">'
        self.p_extract_match = re.compile(self.extract_match)
        self.dict_word = {'erbihouke':'耳鼻喉科',
                          'xueyeke':'血液科',
                          'huxineike':'呼吸内科',
                          'shenjingneike':'神经内科',
                          'neifenmike':'内分泌科',
                          'xiaohuaneike':'消化内科',
                          'fuke':'妇科',
                          'puwaike':'普外科',
                          'miniaowaike':'泌尿外科',
                          'xinxiongwaike':'心胸外科',
                          'gandanwaike':'肝胆外科',
                          'shenjingwaike':'神经外科',
                          'gangchangke':'肛肠科',
                          'nanke':'男科',
                          'yanke':'眼科',
                          'guwaike':'骨外科',
                          'pifuke':'皮肤科',
                          'kouqiangke':'口腔科'}

    def extract_file(self,file_dir):
        department = []
        disease = []
        raw_data = open(file_dir,'r')
        for line in raw_data:
            if  re.match(self.page_start_match,line) != None:
                department = self.p_start_match.findall(line)
            disease = self.p_extract_match.findall(line)
            if  len(disease) != 0:
            #print(len(disease))
#print(department[0])
                print('%s %s' %(disease[0],self.dict_word[department[0]]))

if __name__ == '__main__':
    ex = extract()
    ex.extract_file('/data/lichengDownload/data/xywy/page/2.txt')

