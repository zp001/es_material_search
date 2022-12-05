# -- coding: utf-8 --
from kmp import *
from get_jie_data import *
from entity_label import Catalogue_data
import jieba

def get_dic():
    path = './/data//目录数据//'
    get_catalogue = Catalogue_data()
    file_names = get_catalogue.sort_files(path)
    locations = get_catalogue.flies_location(path, file_names)
    section_list = get_catalogue.read_files(locations)
    section_list = list(set(section_list))
    dic_path = r'./data/字典/word_dic.txt'
    dic = open(dic_path, 'w+',encoding='utf-8')
    for w in section_list:
        dic.write(w+'\n')
    dic.close()

def jieba_seg(keyword,dic_path):
    jieba.load_userdict(dic_path)
    seg_list = jieba.cut(keyword, cut_all=False)
    seg="/".join(seg_list)
    return seg


def kmp_new_cont(con,keyword):
    search_position=[]
    next_locs = next_loc(keyword)
    loc = KMP(con, keyword, next_locs)
    if loc != -1:
        search_position.append(loc)
        search_position.append(loc + len(next_locs))
        new_con = insert_label(search_position, con)
        return new_con
    else:
        return con

def match_keyword(keyword,content):
    re_cont_list=[]
    re_cont=[]
    search_position=[]
    content_list=content.split('|')
    n = len(content_list)
    for i in range(n):
        if not content_list[i].startswith('<im'):
            next_locs = next_loc(keyword)
            loc = KMP(content_list[i], keyword, next_locs)
            if loc!=-1:
                search_position.append(loc)
                search_position.append(loc + len(next_locs))
                con=insert_label(search_position, content_list[i])
                re_cont.append(con)
                if i+1<n:
                    new_con1=kmp_new_cont(content_list[i+1],keyword)
                    re_cont.append(new_con1)
                    if i+2<n:
                        new_con2 = kmp_new_cont(content_list[i + 2],keyword)
                        re_cont.append(new_con2)
                        break
                    else:
                        break
                else:
                    break
            else:
                continue
    re_cont = ''.join(re_cont)
    re_cont_list.append(re_cont)
    return re_cont_list

def insert_label(search_position,con):
    con_list=list(con)
    con_list.insert(search_position[0], '<font color="red">')
    con_list.insert(search_position[1]+1, '</font>')
    new_con = ''.join(con_list)
    return new_con




