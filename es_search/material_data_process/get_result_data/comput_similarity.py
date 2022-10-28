import numpy as np
import pandas as pd
import jieba
import re

from elasticsearch import Elasticsearch
es = Elasticsearch('http://localhost:9200')

def segment_data(data):
    big_category_data=[]
    mid_category_data=[]
    small_category_data=[]
    for k in data:
        if len(str(k[0]))<=2:
            big_category_data.append(k)
        if len(str(k[0]))>=5:
            small_category_data.append(k)
        else:
            mid_category_data.append(k)
    return big_category_data,mid_category_data,small_category_data


def get_category_data(file):
    data = pd.read_excel(file, index_col=2,skiprows=2)
    data=data.loc[:, ['类别编码', '类别名称']].values
    data = data.tolist()
    big_category_data,mid_category_data,small_category_data=segment_data(data)

    #print(big_category_data)
    return data,big_category_data,mid_category_data,small_category_data

def get_data_dic(big_category_data,mid_category_data,small_category_data):
    mid_cat_data=[]
    mid_cat_code = []
    for m in mid_category_data:
        dic_data = {}
        dic_code={}
        dic_code.setdefault(m[0], [])
        dic_data.setdefault(m[1], [])
        mid_cat_data.append(dic_data)
        mid_cat_code.append(dic_code)

    for i in range(len(mid_cat_code)):
        c=mid_cat_code[i].keys()
        c=list(c)
        d=mid_cat_data[i].keys()
        d=list(d)
        for s in small_category_data:
            sc=str(s[0])
            scj=''
            if len(sc)==6:
                scj=sc[:4]
            if len(sc)==5:
                scj = sc[:3]
            if scj == str(c[0]):
                mid_cat_code[i].setdefault(c[0], []).append(s[0])
                mid_cat_data[i].setdefault(d[0], []).append(s[1])
                #small_category_data.remove(s)

    all_data=[]
    all_code=[]
    for b in big_category_data:
        child_data={}
        child_code={}
        for j in range(len(mid_cat_data)):
            ck=mid_cat_code[j].keys()
            ck=list(ck)
            ck=str(ck[0])
            p=''
            if len(ck)==4:
                p=ck[:2]
            if len(ck)==3:
                p = ck[:1]
            if p==str(b[0]):
                child_data.setdefault(b[1], []).append(mid_cat_data[j])
                child_code.setdefault(b[0], []).append(mid_cat_code[j])

        all_data.append(child_data)
        all_code.append(child_code)

    return all_data,all_code

'''
def match_all_data(word,all_data):
    word_sim_dic = {}
    sim_dic = {}
    if "节" in word or '术语' in word:
        sort_sim_list=[]
        return sort_sim_list
    else:
        for l in all_data:
            for k in l.values():
                for p in k:
                    r = list(p.values())[0]
                    if word == list(p.keys())[0]:
                        for word_c in r:
                            word_c1 = pro_catg_data(word_c)
                            sim = jaccard_list(word, word_c1)
                            sim= sim+1.0
                            sim_dic[word_c] = sim
                    else:
                        for word_c in r:
                            word_c2 = pro_catg_data(word_c)
                            #sim = jaccard(word, word_c)
                            sim = jaccard_list(word, word_c2)
                            sim_dic[word_c] = sim
        sort_sim_dic = sort_data(sim_dic)
        word_sim_dic[word] = sort_sim_dic

        sort_sim_list=list(sort_sim_dic.keys())

        return sort_sim_list
        '''
def match_all_data(word,all_data,all_code):
    word_sim_dic = {}
    sim_dic = {}
    mat_sort_sim_list=[]
    cod_sort_sim_list=[]
    if "节" in word or '术语' in word:
        mat_sort_sim_list=[]
        cod_sort_sim_list=[]
        return mat_sort_sim_list,cod_sort_sim_list
    else:
        for i in range(len(all_data)):
            l=all_data[i]
            t=l.values()
            #big_cat=list(l.keys())[0]
            if len(t)!=0:
                t=list(t)[0]
                #print(t)
                for k in range(len(t)):
                    p=t[k]
                    #mid_cat=list(p.keys())[0]
                    r = list(p.values())[0]
                    if word == list(p.keys())[0]:
                        for word_c in r:
                            word_c1 = pro_catg_data(word_c)
                            sim = jaccard_list(word, word_c1)
                            sim= sim+1.0

                            big=all_code[i]
                            big=big.values()
                            big=list(big)[0]
                            mid=big[k]
                            sma=mid.values()
                            sma=list(sma)[0]
                            ind=r.index(word_c)
                            sma_code=sma[ind]
                            if len(str(sma_code))==5:
                                po='0'+str(sma_code)+'_'+word_c
                                sim_dic[po] = sim
                            else:
                                po = str(sma_code) +'_'+ word_c
                                sim_dic[po] = sim

                    else:
                        for word_c in r:
                            word_c2 = pro_catg_data(word_c)
                            #sim = jaccard(word, word_c)
                            sim = jaccard_list(word, word_c2)

                            big = all_code[i]
                            big = big.values()
                            big = list(big)[0]
                            mid = big[k]
                            sma = mid.values()
                            sma = list(sma)[0]
                            ind = r.index(word_c)
                            sma_code = sma[ind]
                            if len(str(sma_code))==5:
                                po='0'+str(sma_code)+'_'+word_c
                                sim_dic[po] = sim
                            else:
                                po = str(sma_code) +'_'+ word_c
                                sim_dic[po] = sim


        sort_sim_dic = sort_data(sim_dic)
        word_sim_dic[word] = sort_sim_dic

        sort_sim_list=list(sort_sim_dic.keys())

        for s in sort_sim_list:
            cod=s.split('_')[0]
            mat=s.split('_')[1]
            mat_sort_sim_list.append(mat)
            cod_sort_sim_list.append(cod)

        return mat_sort_sim_list,cod_sort_sim_list

def edit_distance(word1, word2):
    len1 = len(word1)
    len2 = len(word2)
    dp = np.zeros((len1 + 1, len2 + 1))
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            temp = 0 if word1[i - 1] == word2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j - 1] + temp, min(dp[i - 1][j] + 1, dp[i][j - 1] + 1))

    return dp[len1][len2]

def simility(word1, word2):
    if word2 == word1:
        return 1.0
    res = edit_distance(word1, word2)
    maxLen = max(len(word1),len(word2))
    sim=1-res*1.0/maxLen
    return sim

def dict_slice(adict,start, end):
    keys = adict.keys()
    dict_slice = {}
    for k in list(keys)[start:end]:
        dict_slice[k] = adict[k]
    return dict_slice

def sort_data(sim_dic):
    d=list(zip(sim_dic.values(),sim_dic.keys()))
    d = sorted(d,reverse=True)
    #d=d[0:10]
    new_d={}
    for k in d:
        if k[0]>=0.5:
            new_d[k[1]]=k[0]
    return new_d

def pro_catg_data(data:str):
    if data.startswith('其他') or data.startswith('各种'):
        data=data[2:]
    if data.startswith('其他各种'):
        data=data[4:]
    else:
        data=data
    data = re.sub('[a-zA-Z0-9]', '', data)
    data = re.sub('/', '', data)
    data = re.sub('/.', '', data)
    data = re.sub('[()（）]', '', data)

    return data
def match_data(word,data):
    word_sim_dic={}
    sim_dic={}
    for i in range(len(data)):
        word_c=pro_catg_data(data[i][1])
        #sim=jaccard(word,word_c)
        sim = jaccard_list(word, word_c)
        if len(str(data[i][0]))==5:
            code='0'+str(data[i][0])
            k=code+'_'+data[i][1]
            sim_dic[k]=sim
        else:
            k=str(data[i][0])+'_'+data[i][1]
            sim_dic[k] = sim
    sort_sim_dic=sort_data(sim_dic)
    word_sim_dic[word]=sort_sim_dic
    sort_sim_list = list(sort_sim_dic.keys())
    return sort_sim_list

def jaccard_list(word1,word2):
    word1_list=jieba_seg_word(word1)
    word2_list = jieba_seg_word(word2)
    interab = list(set(word1_list).intersection(set(word2_list)))
    unionab = list(set(word1_list).union(set(word2_list)))
    sim=len(interab)/len(unionab)

    return sim

def jaccard(word1,word2):
    return len(set(word1).intersection(set(word2))) / len(set(word1).union(set(word2)))

def jieba_seg_word(str):
    seg_list = jieba.cut(str, cut_all=True)
    seg_list = list(seg_list)
    return seg_list

if __name__ == "__main__":
    file='.//data//物料类别数据//物料类别.xls'
    data,big_category_data,mid_category_data,small_category_data=get_category_data(file)
    all_data,all_code=get_data_dic(big_category_data,mid_category_data,small_category_data)
    #word_sim_dic=match_data("截止阀",small_category_data)
    #print(word_sim_dic)

    mat_sort_sim_list,cod_sort_sim_list=match_all_data("液压支架", all_data,all_code)
    print(mat_sort_sim_list)
    print(cod_sort_sim_list)



