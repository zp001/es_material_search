import re

def rec_small_title_kuohao(cont: list):
    """
        识别带括号的二级小标题，
        """
    index_list = []
    for c in cont:
        if re.match(r'[\(][一二三四五六七八九十—]+[一二三四五六七八九十—]?[\)]', c):
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
            if re.match(r'^\d+[\.]', c):
                k = cont.index(c)
                index_list_s.append(k)

        return index_list_s
    else:
        return index_list

def concat_cont(index_list, cont):
    """
        二级小标题打标签，形成字符串形式，得到二级标题数组。
        """
    child_small_title=[]
    if len(index_list) != 0:
        for i in index_list:
            child_small_title.append(cont[i])
            cont[i]="<b>" + cont[i] + '</b>'
        small_title_content = "|".join(cont)
        return small_title_content,child_small_title
    else:
        small_title_content = "|".join(cont)
        return small_title_content, child_small_title


if __name__ == "__main__":
    cont = ['1.到厂验收','1.液压支架型号', ' 1.到厂验收', '啦啦啦', '2.计划', '急急急', '拉开看看', '3.老师的课', '解决实际数据']
    #cont = ['kskjk', '哈哈哈', '啦啦啦', '计划', '急急急', '拉开看看', '老师的课', '解决实际数据']
    #cont = ['kskjk', '(一).哈哈哈', '啦啦啦', '(二)计划', '急急急', '拉开看看', '(十五)老师的课', '解决实际数据']
    index_list = rec_small_title(cont)
    small_title_content,child_small_title = concat_cont(index_list, cont)
    print(small_title_content)

'''

启动es和可视化界面
bin下elasticsearch.bat
可视化
D:\elasticsearch-head-master
启动命令：npm run start
http://localhost:5601/
'''
'''
PUT material
{
  "mappings": {
    "properties": {
      "chapter": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "zhang": { 
            "type":  "keyword"
          }
        }
      },
      "section": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "jie": { 
            "type":  "keyword"
          }
        }
      },
      "desc": {
        "type": "text"
      },
      " source": {
        "type": "text"
      },
      " top": {
        "type": "text"
      },
      "content": {
        "type": "text",
        "analyzer": "ik_max_word"
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
      "combin_title": {
        "type": "keyword"
      },
      "small_title": {
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
        "type": "text"
      },
      "processStatus": {
        "type": "text"
      },
      "unfreezReason":{
        "type": "text"
      },
      "modifiedReason":{
        "type": "text"
      } 
      }
    }
  }
'''

'''
POST /material/_search
{
  "size": 10,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"section": "液压支架"}},
                        {"match": {"content": "液压支架"}}
                    ]
                }
            },
            "sort": [{"versionNumber": {"order": "desc"}}],
            "collapse": {
                "field": "section.jie"
            },
  "highlight": {
    "fields": {
      "content": {}
    },
    "pre_tags": "<font color='red'>",
    "post_tags": "</font>",
    "number_of_fragments" : 3,
    "fragment_size" : 150
  }
}
'''



