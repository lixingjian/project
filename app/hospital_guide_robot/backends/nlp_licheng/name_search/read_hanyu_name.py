# -*- coding -*- :utf-8

f = open('hanyu_name','r').readlines()
f2 = open('name_dict','w')
name_list = f[0].split('\\n')
for ele in name_list:
  f2.write(ele + '\n')  
print(name_list)



