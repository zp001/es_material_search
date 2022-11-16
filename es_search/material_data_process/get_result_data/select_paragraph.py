# -- coding: utf-8 --
from material_data_process.get_result_data.kmp import *
from material_data_process.get_result_data.get_jie_data2 import *
from material_data_process.get_result_data.entity_label import Catalogue_data
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

if __name__ == "__main__":
    content='我是|交换机|和世界经济|拉升阶段世界加拿大|哈哈哈'
    keyword='哈哈'
    re_cont=match_keyword(keyword,content)
    print(re_cont)
    dic_path='./data/字典/word_dic.txt'
    seg=jieba_seg(keyword,dic_path)
    print(seg)

    '''
    pipreqs. / --encoding = utf8 - -force
    --encoding=utf8 ：为使用utf8编码

--force ：强制执行，当 生成目录下的requirements.txt存在时覆盖 

. /: 在哪个文件生成requirements.txt 文件
    '''
'''
PUT materials
{
  "mappings": {
    "properties": {
      "chapter": {
        "type": "text",
        "analyzer": "ik_smart",
        "fields": {
          "zhang": { 
            "type":  "keyword"
          }
        }
      },
      "section": {
        "type": "text",
        "analyzer": "ik_smart",
        "fields": {
          "jie": { 
            "type":  "keyword"
          }
        }
      },
      "desc": {
        "type": "text"
      },
      "source": {
        "type": "text"
      },
      "top": {
        "type": "text"
      },
      "content": {
        "type": "text",
        "analyzer": "ik_smart"
      },
      "content_text": {
        "type": "text",
        "analyzer": "ik_smart"
      },
      "picture": {
        "type": "text"
      },
      "material_name": {
        "type": "keyword"
      },
      "material_code": {
        "type": "keyword"
      },
      "quote": {
        "type": "text",
        "fields": {
          "jty": { 
            "type":  "keyword"
          }
        }
      },
      "title": {
        "type": "keyword"
      },
      "title_quote": {
        "type": "keyword"
      },
      "combin_title": {
        "type": "keyword"
      },
      "small_title": {
        "type": "keyword"
      },
      "small_title_quote": {
        "type": "keyword"
      },
      "all_quote": {
        "type": "keyword"
      },
      "all_title_tag": {
        "type": "nested"
      },
      "all_title": {
        "type": "keyword"
      },
      "creatTime": {
        "type": "date",
        "format":"yyyy-MM-dd HH:mm:ss"
      },
      "creater": {
        "type": "text"
      },
      "versionNumber": {
        "type": "integer",
        "fields": {
          "versionNo": { 
            "type":  "keyword"
          }
        }
      },
      "modifiedName": {
        "type": "text"
      },
      "updateTime": {
        "type": "date",
        "format":"yyyy-MM-dd HH:mm:ss"
      },
      "dataStatus": {
        "type": "text",
        "fields": {
          "dataStatu": { 
            "type":  "keyword"
          }
        }
      },
      "processStatus": {
        "type": "text"
      },
      "unfreeReason":{
        "type": "text"
      },
      "modifiedReason":{
        "type": "text"
      } 
      }
    }
  }
'''
