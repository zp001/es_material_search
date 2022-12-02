# -- coding: utf-8 --
import re

def rec_small_title_kuohao(cont: list):
    """
        识别带括号的二级小标题，
        """
    index_list = []
    for c in cont:
        if re.match(r'[\(][一二三四五六七八九十—]+[一二三四五六七八九十—]?[\)]', c) or re.match(r'[（][一二三四五六七八九十—]+[一二三四五六七八九十—]?[）]', c):
            k = cont.index(c)
            index_list.append(k)
    return index_list

def rec_small_title(cont: list):
    """
        识别二级小标题不是带括号形式的二级标题
        """
    index_list = rec_small_title_kuohao(cont)
    if len(index_list) == 0:
        index_list_s = []
        for c in cont:
            #if re.match(r'^\d+[\.]', c):
            if re.match(r'^\d+[.]+[\u4e00-\u9fa5]',c):
                k = cont.index(c)
                index_list_s.append(k)
        return index_list_s
    else:
        return index_list

def concat_cont(index_list,cont):
    """
        二级小标题打标签，形成字符串形式，得到二级标题数组。
        """
    child_small_title=[]
    if len(index_list) != 0:
        for i in index_list:
            cont_i = cont[i].replace('(', '（')
            cont_i = cont_i.replace(')', '）')
            child_small_title.append(cont_i)
            cont_i = "<h4>" + cont_i + '</h4>'
            cont.insert(i, cont_i)
            del cont[i + 1]
        small_title_content = "|".join(cont)
        return small_title_content,child_small_title
    else:
        small_title_content = "|".join(cont)
        return small_title_content, child_small_title


