# -- coding: utf-8 -- 
# @Createtime：2022-11-9
# @Updatetime：14:34
# @Author：Test008
# @File：get_dic.py
# @Description：

def get_dic(dic_path,main_dic_path,new_dic_path):
    dic = open(dic_path, 'r', encoding='utf-8')
    main_dic = open(main_dic_path, 'r', encoding='utf-8')
    new_dic = open(new_dic_path, 'w+', encoding='utf-8')
    dic_w = dic.readlines()
    main_dic_w = main_dic.readlines()
    for w1 in dic_w:
        if w1 not in main_dic_w:
            new_dic.write(w1)


if __name__ == "__main__":
    dic_path='D://work//data//dic.txt'
    main_dic_path='D://work//data//main_dic.txt'
    new_dic_path='D://work//data//new_dic.txt'
    get_dic(dic_path, main_dic_path, new_dic_path)


