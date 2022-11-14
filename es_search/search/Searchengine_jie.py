import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import re
from  material_data_process.get_result_data.select_paragraph import match_keyword,jieba_seg

class Searchengine:
    def __init__(self):
        self.es = Elasticsearch(hosts="http://localhost:9200",
                                sniff_on_start=True,
                                sniff_on_connection_fail=True,
                                sniffer_timeout=60)

    def title_search(self,query):
        response = self.es.search(index='material', body=query)
        article_list = response["hits"]["hits"]
        return article_list

    def judge_search(self,keywords,query_sec,query_title,query_content):
        sec_list=Searchengine.title_search(self, query_sec)
        if len(sec_list)==0:
            title_list = Searchengine.title_search(self, query_title)
            if len(title_list)==0:
                content_list1 = Searchengine.title_search(self, query_content)
                content_list = Searchengine.get_new_article_list(self, content_list1)
                return content_list
            else:
                title_list = Searchengine.get_new_article_list(self, title_list)
                dic_path='..//material_data_process//get_result_data//data//字典//word_dic.txt'
                seg=jieba_seg(keywords,dic_path)
                key_sec=seg.split('/')[0]
                title_re_cont = match_keyword(key_sec, title_list[0]['content_text'])
                #title_re_cont = Searchengine.highlight_data(self, title_re_cont)
                title_list[0]['highlight_content'] = title_re_cont
                return title_list
        else:
            sec_list=Searchengine.get_new_article_list(self,sec_list)
            sec_re_cont = match_keyword(keywords, sec_list[0]['content_text'])
            #sec_re_cont=Searchengine.highlight_data(self,sec_re_cont)
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
        new_content = [Searchengine.filter_content(self,c) for c in content]
        new_content_s = '|'.join(l for l in new_content)
        return new_content_s

    def search(self, keywords):
        query_sec={
            "query":
                       {"term": {"section.jie": "{}".format(keywords)}
                        },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
            }
            }

        query_title = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {
                            "combin_title": {
                                "value": keywords
                            }
                        }}
                    ]
                }
            },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
            }
        }

        #boost设置字段权重
        query_content = {
            "size": 10,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"section": "{}".format(keywords)}},
                        {"match": {"content_text": "{}".format(keywords)}}
                    ]
                }
            },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
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
            "size": 10000,
            "query": {
                "match_all": {}
            },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
            }
        }
        article_list = Searchengine.title_search(self, query)
        article_list_null = Searchengine.get_new_article_list(self, article_list)
        return article_list_null

    def search_m(self,keywords):
        query_material_label={
            "query": {
                "bool": {
                    "must": [
                        {"term": {
                            "material_name": {
                                "value": keywords
                            }
                        }}
                    ]
                }
            },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
            }
        }

        article_list=Searchengine.title_search(self, query_material_label)
        if len(article_list)!=0:
            new_article_list=Searchengine.get_new_article_list(self,article_list)
            return new_article_list

        else:
            search_engine = Searchengine()
            keywords = search_engine.strip_stopword(keywords)
            new_article_list = search_engine.search(keywords)
            #article_list = Searchengine_materialcate.title_search(self, query_content)
            #new_article_list = Searchengine_materialcate.get_new_article_list(self,article_list)
            return new_article_list

    def search_c(self,keywords):
        query_code_label={
            "query": {
                "bool": {
                    "must": [
                        {"term": {
                            "material_code": {
                                "value": keywords
                            }
                        }}
                    ]
                }
            },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
            }
        }
        query_content = {
            "size": 10,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"content": "{}".format(keywords)}}
                    ]
                }
            },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
            }
        }
        article_list=Searchengine.title_search(self, query_code_label)
        if len(article_list)!=0:
            new_article_list=Searchengine.get_new_article_list(self,article_list)
            return new_article_list
        else:
            article_list = Searchengine.title_search(self, query_content)
            new_article_list = Searchengine.get_new_article_list(self,article_list)
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

    def manageSearch_data(self,response):
        new_response = []
        for d in response:
            dic = {}
            dic['section'] = d['section']
            dic['quote'] = d['quote']
            dic['dataStatus'] = d['dataStatus']
            dic['versionNumber'] = d['versionNumber']
            dic['processStatus'] = d['processStatus']
            dic['creatTime'] = d['creatTime']
            dic['creater'] = d['creater']
            new_response.append(dic)
        return new_response

    def filter_versionNo(self,new_response,versionNO):
        result_response=[]
        for d in new_response:
            if d['versionNumber']==versionNO:
                result_response.append(d)
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

    def data2es_save(self,article_list,data):
        content_text = Searchengine.updete_content(self,data[0]['content'])
        title_index, small_title_index, title_list, small_title_list = Searchengine.update_small_title(data[0]['all_title'])
        combin_title = [data[0]['section'] + w[2:] for w in title_list]
        res_update = self.es.update(index='material', id=article_list['_id'],
                                    body={'doc':{'content': data[0]['content'], 'picture': data[0]['picture'],'all_title_tag':data[0]['all_title_tag'],
                                                 'title':title_list,'small_title':small_title_list,'combin_title':combin_title,
                                                  'content_text':content_text,'desc': data[0]['desc'], 'source': data[0]['source'],
                                                  'top': data[0]['top'],'versionNumber':0,
                                                    'processStatus':'待提交','updateTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                  }})
        return res_update

    def data2es_submit(self,article_list,data,l):
        content_text = Searchengine.updete_content(self, data[0]['content'])
        title_index, small_title_index, title_list, small_title_list = Searchengine.update_small_title(data[0]['all_title'])
        combin_title = [data[0]['section'] + w[2:] for w in title_list]
        res_update = self.es.update(index='material', id=article_list['_id'],
                                    body={'doc':{'content': data[0]['content'], 'picture': data[0]['picture'],'all_title_tag':data[0]['all_title_tag'],
                                                 'title': title_list, 'small_title': small_title_list,'combin_title': combin_title,
                                                  'content_text':content_text,'desc': data[0]['desc'], 'source': data[0]['source'],
                                                  'top': data[0]['top'],'versionNumber':l,
                                                    'processStatus':'已完成','updateTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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


if __name__ == "__main__":
    search_engine = Searchengine()
    str='前言'
    res = search_engine.search(str)
    #new_response=search_engine.manageSearch_data(res)
    print(res[0]['highlight_content'])
    article_list=search_engine.update_es_data('液压支架')
    slice_data= search_engine.data_slice(res,1,5)



