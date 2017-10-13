
#去重，用比较简单的方法，python的字典

dis_dict = {} #key is disease\tdir1\tdir2  val is repeate times

def read_file(file_path):
    raw_data = open(file_path, 'r')
    for line in raw_data:
        line = line.strip()
        if line in dis_dict.keys():
            dis_dict[line] += 1
        else:
            dis_dict[line] = 1


def save():
    for keys in dis_dict:
#print("%s:%d" %(keys,dis_dict[keys]))
        print(keys)

if __name__ == '__main__':
    read_file('disease_location_120ask')
    read_file('disease_location_21fh')
    read_file('disease_location_xywy')

    save()
