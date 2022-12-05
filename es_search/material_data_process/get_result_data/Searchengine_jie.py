# -- coding: utf-8 --
#import datetime
from get_jie_data import *
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import re
from select_paragraph import match_keyword,jieba_seg

class Searchengine:
    def __init__(self):
        self.es = Elasticsearch(hosts=['123.56.240.89:9280'],
                                http_auth=('elastic', 'infoyb2015'),
                                sniff_on_start=True,
                                sniff_on_connection_fail=True,
                                sniffer_timeout=600)

    def title_search(self,query):
        response = self.es.search(index='material', body=query)
        article_list = response["hits"]["hits"]
        return article_list

    def judge_search(self,keywords,query_sec,query_title,query_content):
        sec_list=Searchengine.title_search(self, query_sec)
        sec_list = [d for d in sec_list if d['_source']['versionNumber'] != 0]
        if len(sec_list)==0:
            title_list = Searchengine.title_search(self, query_title)
            if len(title_list)==0:
                content_list1 = Searchengine.title_search(self, query_content)
                content_list = Searchengine.get_new_article_list(self, content_list1)
                content_list = [d for d in content_list if d['versionNumber'] != 0]
                content_list = Searchengine.filter_results(self, content_list)
                return content_list
            else:
                title_list = Searchengine.get_new_article_list(self, title_list)
                title_list = [d for d in title_list if d['versionNumber'] != 0]
                #dic_path='/usr/local/webserver/zhishiku-python/es_search/material_data_process/get_result_data/data/dict/word_dic.txt'
                dic_path = '..//get_result_data//data//dict//word_dic.txt'
                seg=jieba_seg(keywords,dic_path)
                key_sec=seg.split('/')[0]
                title_re_cont = match_keyword(key_sec, title_list[0]['content_text'])
                title_list[0]['highlight_content'] = title_re_cont
                return title_list
        else:
            sec_list=Searchengine.get_new_article_list(self,sec_list)
            sec_re_cont = match_keyword(keywords, sec_list[0]['content_text'])
            sec_list[0]['highlight_content'] = sec_re_cont
            return sec_list

    def process_highlight(self,start, end, s):
        start = re.escape(start)
        end = re.escape(end)
        pattern = re.compile(r'%s(?:.|\s)*?%s' % (start, end))
        updated = ''.join(re.split(pattern, s))
        return updated

    def highlight_data(self,highlight_content):
        for i in range(len(highlight_content)):
            updated=Searchengine.process_highlight(self, 'href', 'blank">', highlight_content[i])
            del highlight_content[i]
            highlight_content.insert(i,updated)
        return highlight_content

    def filter_content(self,c):
        c = c.replace("<h3>", "")
        c = c.replace("</h3>", "")
        c = c.replace("</p>", "")
        c = c.replace("<p>", "")
        c = c.replace("<h4>", "")
        c = c.replace("</h4>", "")
        c = c.replace("</a>", "")
        c = Searchengine.process_highlight(self,'<a', '>', c)
        c = Searchengine.process_highlight(self, '<img', '/>', c)
        return c

    def updete_content(self,content):
        content = content.split("</p><p>")
        new_content = [Searchengine.filter_content(self,c) for c in content if not c.startswith('<im')]
        new_content_s = '|'.join(l for l in new_content)
        return new_content_s

    def filter_results(self,article_list):
        new_article_list=[]
        for article in article_list:
            l=[a['section'] for a in new_article_list]
            if article['section'] not in l:
                new_article_list.append(article)
            else:
                ind=l.index(article['section'])
                if article['versionNumber']>new_article_list[ind]['versionNumber']:
                    del new_article_list[ind]
                    new_article_list.insert(ind, article)
                else:
                    continue

        return new_article_list

    def sec_filter_results(self,article_list):
        if len(article_list)!=1:
            for i in range(1,len(article_list)):
                if article_list[i]['versionNumber']>article_list[0]['versionNumber']:
                    article_list[i],article_list[0]=article_list[0],article_list[i]
                else:
                    continue
            return article_list[:1]
        else:
            return article_list

    def judge_search_details(self,keywords,query_sec):
        sec_list = Searchengine.title_search(self, query_sec)
        sec_list = Searchengine.get_new_article_list(self, sec_list)
        sec_re_cont = match_keyword(keywords, sec_list[0]['content_text'])
        sec_list[0]['highlight_content'] = sec_re_cont
        return sec_list

    def search_details(self, keywords,versionNumber):
        query_sec={
            "query":{"bool":{"must":
                       [{"term": {"section.jie": "{}".format(keywords)}},
                        {"term": {"versionNumber.versionNo": "{}".format(versionNumber)}}
                        ]
            }
            }
        }

        article_list=Searchengine.judge_search_details(self,keywords, query_sec)

        return article_list

    def search(self, keywords):
        query_sec={
            "query":{"bool":{"must":
                       [{"term": {"section.jie": "{}".format(keywords)}
                        }],
                             "filter": {"term": {"dataStatus.dataStatu": "活动"}}
            }
            },
            "sort": [{"versionNumber.versionNo": {'order': "desc"}}],
            "collapse": {"field": "section.jie"}
        }

        query_title = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {
                            "combin_title": {
                                "value": keywords
                            }
                        }
                        }
                    ],
                    "filter": {"term": {"dataStatus.dataStatu": "活动"}}
                }
            },
            "sort": [{"versionNumber.versionNo": {'order': "desc"}}],
            "collapse": {"field": "section.jie"}
        }

        #boost设置字段权重
        query_content = {
            "size": 20,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"section": "{}".format(keywords)}},
                        {"match": {"content_text": "{}".format(keywords)}}
                    ],
                    "filter": {"term": {"dataStatus.dataStatu": "活动"}}
                }
            },
            "highlight": {
                "fields": {
                    "content_text": {}
                },
                "pre_tags": "<font color='red'>",
                "post_tags": "</font>",
                "number_of_fragments": 1,
                "fragment_size": 400
            }
        }

        article_list=Searchengine.judge_search(self,keywords, query_sec,query_title,query_content)

        return article_list

    def search_null(self):
        query = {
            "size": 5000,
            "query": {
                "bool": {
                    "must": [
                        {"match_all": {}}
                    ],
                    "filter": {"term": {"dataStatus.dataStatu": "活动"}}
            }
        },
        "sort": [{"versionNumber.versionNo": {'order': "desc"}}],
        "collapse": {"field": "section.jie"}
        }
        article_list = Searchengine.title_search(self, query)
        article_list_null = Searchengine.get_new_article_list(self, article_list)
        article_list_null=[d for d in article_list_null if d['versionNumber']!=0]
        n = len(article_list_null)
        for i in range(n):
            for j in range(1, n - i):
                if article_list_null[j - 1]['creatTime'] < article_list_null[j]['creatTime']:
                    article_list_null[j - 1], article_list_null[j] = article_list_null[j], article_list_null[j - 1]

        return article_list_null

    def manage_sec(self,keywords):
        query_sec = {
            "query":
                {"term": {"section.jie": "{}".format(keywords)}
                 },
            "sort": [{"versionNumber.versionNo": {'order': "desc"}}],
            "collapse": {"field": "section.jie"}
        }
        article_list = Searchengine.title_search(self, query_sec)
        return article_list
    def manage_sec_text(self,keywords):
        query_sec_text = {
            "size": 10,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"section": "{}".format(keywords)}}
                    ]
                }
            }
        }
        article_list = Searchengine.title_search(self, query_sec_text)
        return article_list

    def manage_search(self, keywords):
        article_list=Searchengine.manage_sec(self,keywords)
        if len(article_list)!=0:
            article_list = Searchengine.manageSearch_data(self,article_list)
            return article_list
        else:
            article_list = Searchengine.manage_sec_text(self, keywords)
            article_list = Searchengine.manageSearch_data(self,article_list)
            return article_list

    def manageSearch_data(self,response):
        new_response = []
        for d in response:
            dic = {}
            dic['chapter'] = d['_source']['chapter'].strip('\n')
            dic['section'] = d['_source']['section'].strip('\n')
            dic['all_quote'] = d['_source']['all_quote']
            dic['dataStatus'] = d['_source']['dataStatus'].strip('\n')
            dic['versionNumber'] = d['_source']['versionNumber']
            dic['processStatus'] = d['_source']['processStatus']
            dic['creatTime'] = d['_source']['creatTime']
            dic['creater'] = d['_source']['creater']
            dic['material_name'] = d['_source']['material_name']
            dic['material_code'] = d['_source']['material_code']
            dic['combin_material_name_code'] = d['_source']['combin_material_name_code']
            new_response.append(dic)
        return new_response

    def search_null_manage(self):
        query = {
            "size": 10000,
            "query": {
                "match_all": {},
                "range": {
                    "versionNumber": {
                        "gt": 0
                    }
                }

            },
            #"sort": [{"versionNumber.versionNo": {'order': "desc"}}],
            "sort": [{"updateTime": {'order': "desc"}}],
            "collapse": {"field": "section.jie"}
        }

        query_ver = {
            "query":
                {"term": {"versionNumber.versionNo": "0"}
                 },
            "sort": [{"updateTime": {'order': "desc"}}],
        }

        article_list1 = Searchengine.title_search(self, query)
        article_list_null1 = Searchengine.manageSearch_data(self, article_list1)

        article_list2 = Searchengine.title_search(self, query_ver)
        article_list_null = Searchengine.manageSearch_data(self, article_list2)

        article_list_null.extend(article_list_null1)
        n = len(article_list_null)
        for i in range(n):
            for j in range(1, n - i):
                if article_list_null[j - 1]['creatTime'] < article_list_null[j]['creatTime']:
                    article_list_null[j - 1],article_list_null[j]=article_list_null[j],article_list_null[j - 1]

        return article_list_null

    def sort_chapter_result(self,article_list):
        n=len(article_list)
        for i in range(n):
            for j in range(1, n - i):
                if article_list[j - 1]['order'] > article_list[j]['order']:
                    article_list[j - 1], article_list[j] = article_list[j], article_list[j - 1]
        return article_list

    def search_chapter(self, keywords):
        query_chapter = {
            "query": {"bool": {"must":
                                   [{"term": {"chapter.zhang": "{}".format(keywords)}
                                     }],
                               "filter": {"term": {"dataStatus.dataStatu": "活动"}}
                               }
                      },
            "sort": [{"versionNumber.versionNo": {'order': "desc"}}],
            "collapse": {"field": "section.jie"}
        }

        article_list=Searchengine.title_search(self,query_chapter)
        article_list = Searchengine.get_new_article_list(self, article_list)
        article_list=Searchengine.sort_chapter_result(self, article_list)

        return article_list

    def search_material_name(self,keywords):
        query_material_label={
            "query": {
                "bool": {
                    "must": [
                        {"term": {
                            "material_name": {
                                "value": keywords
                            }
                        }}
                    ],
                    "filter": {"term": {"dataStatus.dataStatu": "活动"}}
                }
            },
            "sort": [{"versionNumber.versionNo": {'order': "desc"}}],
            "collapse": {"field": "section.jie"}
        }

        article_list=Searchengine.title_search(self, query_material_label)
        new_article_list=Searchengine.get_new_article_list(self,article_list)

        return new_article_list

    def search_material_code(self,keywords):
        query_code_label={
            "query": {
                "bool": {
                    "must": [
                        {"term": {
                            "material_code": {
                                "value": keywords
                            }
                        }}
                    ],
                    "filter": {"term": {"dataStatus.dataStatu": "活动"}}
                }
            },
            "sort": [{"versionNumber.versionNo": {'order': "desc"}}],
            "collapse": {"field": "section.jie"}
        }

        article_list=Searchengine.title_search(self, query_code_label)
        new_article_list=Searchengine.get_new_article_list(self,article_list)
        return new_article_list

    def get_new_article_list(self,article_list):
        new_article_list = []
        for cont in article_list:
            d = {}
            d['chapter'] = cont['_source']['chapter'].strip('\n')
            d['section'] = cont['_source']['section'].strip('\n')
            d['content'] = cont['_source']['content'].replace('\n','')
            d['content_text'] = cont['_source']['content_text'].strip('\n')
            d['quote'] = cont['_source']['quote'].strip('\n')
            d['picture'] = cont['_source']['picture']
            d['small_title']=cont['_source']['small_title']
            d['all_title_tag'] = cont['_source']['all_title_tag']
            d['material_name'] = cont['_source']['material_name']
            d['material_code'] = cont['_source']['material_code']
            d['combin_title'] = cont['_source']['combin_title']
            d['title'] = cont['_source']['title']
            d['creatTime'] = cont['_source']['creatTime']
            d['dataStatus'] = cont['_source']['dataStatus']
            d['versionNumber'] = cont['_source']['versionNumber']
            d['processStatus'] = cont['_source']['processStatus']
            d['desc'] = cont['_source']['desc']
            d['source'] = cont['_source']['source']
            d['top'] = cont['_source']['top']
            d['creater'] = cont['_source']['creater']

            d['title_quote'] = cont['_source']['title_quote']
            d['small_title_quote'] = cont['_source']['small_title_quote']
            d['all_quote'] = cont['_source']['all_quote']
            d['all_title'] = cont['_source']['all_title']
            d['order'] = cont['_source']['order']
            d['combin_material_name_code'] = cont['_source']['combin_material_name_code']
            #d['all_title_tag'] = cont['_source']['all_title_tag']

            if 'highlight' in cont:
                hc=[]
                hl=cont['highlight']['content_text'][0].replace('|','')
                hc.append(hl)
                highlight_content = hc
            else:
                hc=[]
                hc.append(d['content_text'][:400].replace('|',''))
                highlight_content=hc
            d['highlight_content']=highlight_content

            new_article_list.append(d)
        return new_article_list

    def data_slice(self,new_article_list, pageNumber, pageSize):
        start=(int(pageNumber)-1)*int(pageSize)
        end=int(pageNumber)*int(pageSize)
        slice_data=new_article_list[start:end]

        return slice_data

    def process_input(self,input):
        input = re.sub(r'[’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！\[\\\]^_`{|}~]+', '', input)#删除特殊字符
        input = re.sub(r'\w*\d+\w*', '', input)  #
        input = re.sub('\s{2,}', "", input)  # 删除2个及以上的空格
        input = input.strip()  # 删除两端无用空格
        return input

    def strip_stopword(self,input):
        stopword=['了','是','的','有']
        for w in input:
            if w in stopword:
                input = input.replace(w, '')
        return input

    def filter_versionNo(self,new_response,versionNO):
        result_response=[d for d in new_response if d['versionNumber']==versionNO]
        return result_response

    def update_es_data(self, keyword):
        query = {"query":
                         {"term": {"section.jie": "{}".format(keyword)}
                          },
                 "sort": [{"versionNumber": {'order': "asc"}}]
                     }
        article_list=Searchengine.title_search(self,query)

        return article_list

    def history_search(self, keyword,versionNumber):
        query = {"query":{"bool": {"must":[
                         {"term": {"section.jie": "{}".format(keyword)}},
                         {"term": {"versionNumber.versionNo": "{}".format(versionNumber)}}]
                     }
                     }
        }
        article_list=Searchengine.title_search(self,query)

        return article_list

    def data2es_submit_save(self,article_list,data,versionNumber,processStatus):
        content_text = Searchengine.updete_content(self, data[0]['content'])
        title_index, small_title_index, title_list, small_title_list = Searchengine.update_small_title(self,data[0]['all_title'])
        new_title_list = Searchengine.get_combin_title(self, title_list)
        combin_title = [data[0]['section'] + w for w in new_title_list]

        title_quote = get_quote(title_list)
        small_title_quote = get_quote(small_title_list)
        all_quote = get_all_quote(data[0]['quote'], title_quote, small_title_quote)

        material_code = [mc.split('_')[0] for mc in data[0]['combin_material_name_code']]
        material_name = [mc.split('_')[1] for mc in data[0]['combin_material_name_code']]

        res_update = self.es.update(index='material', id=article_list['_id'],
                                    body={'doc':{'content': data[0]['content'], 'picture': data[0]['picture'],'all_title_tag':data[0]['all_title_tag'],
                                                 'title': title_list, 'small_title': small_title_list,'combin_title': combin_title,'section':data[0]['section'],
                                                  'content_text':content_text,'desc': data[0]['desc'], 'source': data[0]['source'],
                                                  'dataStatus': data[0]['dataStatus'],'versionNumber':versionNumber,'all_title':data[0]['all_title'],
                                                 'title_quote': title_quote, 'small_title_quote': small_title_quote,'all_quote': all_quote,
                                                 'material_code': material_code,'material_name': material_name,
                                                    'processStatus':processStatus,'updateTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                  }})
        return res_update

    def frozen(self,article_list,unfreezReason):
        if article_list[0]['_source']['processStatus']=='已完成':
            res_update = self.es.update(index='material', id=article_list[0]['_id'],
                                        body={'doc':{'dataStatus': '冻结','unfreezReason':unfreezReason}})
            return res_update

    def unfrozen(self,article_list,unfreezReason):
        if article_list[0]['_source']['processStatus'] == '已完成':
            res_update = self.es.update(index='material',id=article_list[0]['_id'],
                                        body={'doc':{'dataStatus': '活动'},'unfreezReason':unfreezReason})
            return res_update

    def batch_frozen(self,sections,unfreezReason):
        actions=[]
        for section in sections:
            response = Searchengine.update_es_data(self,section)
            if response[0]['_source']['processStatus']=='已完成':
                action = {
                    "_op_type": 'update',
                    "_index": response[0]['_index'],
                    "_id": response[0]['_id'],
                    "doc": {
                        "dataStatus": '冻结',
                        'unfreezReason': unfreezReason
                    }
                }
                actions.append(action)
        bulk(self.es, actions)
        return 'success'

    def batch_unfrozen(self,sections,unfreezReason):
        actions=[]
        for section in sections:
            response = Searchengine.update_es_data(self,section)
            if response[0]['_source']['processStatus'] == '已完成':
                action = {
                    "_op_type": 'update',
                    "_index": response[0]['_index'],
                    "_id": response[0]['_id'],
                    "doc": {
                        "dataStatus": '活动',
                        'unfreezReason': unfreezReason
                    }
                }

                actions.append(action)
        bulk(self.es, actions)
        return 'success'

    def history_V(self, article_list):
        new_response = []
        for art in article_list:
            if art['_source']['versionNumber']!=0:
                dic = {}
                dic['processStatus'] = art['_source']['processStatus']
                dic['section'] = art['_source']['section']
                dic['quote'] = art['_source']['quote']
                dic['creater']=art['_source']['creater']
                dic['creatTime'] = art['_source']['creatTime']
                dic['versionNumber'] = art['_source']['versionNumber']
                dic['dataStatus'] = art['_source']['dataStatus']
                dic['modifiedName'] = art['_source']['modifiedName']
                dic['updateTime'] = art['_source']['updateTime']
                new_response.append(dic)

        return new_response

    def update_small_title(self,data):
        title_list = []
        title_index = []
        small_title_index = []
        small_title_list = []
        for t in data:
            if re.match(r'^[一二三四五六七八九十—]', t):
                title_list.append(t)
                ind1 = data.index(t)
                title_index.append(ind1)
            else:
                ind2 = data.index(t)
                small_title_index.append(ind2)
                small_title_list.append(t)
        return title_index, small_title_index, title_list, small_title_list

    def get_combin_title(self,title_list):
        new_title_list=[]
        for s in title_list:
            if '引用' in s:
                ind=s.index('引')
                new_s=s[2:ind-1]
                new_title_list.append(new_s)
            if '引用' not in s:
                if '(' in s or '（' in s:
                    s.replace('(','（')
                    new_s=s.split('（')[0]
                else:
                    new_s=s[2:]
                new_title_list.append(new_s)
        return new_title_list

    def delete(self,section,versionNumber):
        query = {"query": {"bool": {"must": [
            {"term": {"section.jie": "{}".format(section)}},
            {"term": {"versionNumber.versionNo": "{}".format(versionNumber)}}]}
        }
        }
        self.es.delete_by_query(index='material', body=query)
        return 'success'

    def delete_search(self,keywords):
        query_sec = {
            "query":
                {"term": {"section.jie": "{}".format(keywords)}
                 },
            "sort": [{"versionNumber.versionNo": {'order': "asc"}}]
        }
        article_list = Searchengine.title_search(self, query_sec)
        return article_list

    def combin_material_name_code(self, material_name, material_code):
        for i in range(len(material_name)):
            combin_name_code = material_code[i] + '_' + material_name[i]


if __name__ == "__main__":
    search_engine = Searchengine()
    str='锚杆钻机'
    a=search_engine.manage_search(str)
    #print(a[0]['versionNumber'])
    b=search_engine.search_null_manage()
    for k in b:
        print(k['section'])
        print(k['versionNumber'])








