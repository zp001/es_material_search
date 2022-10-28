import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import re

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

    def judge_search(self,query_sec,query_title,query_content):
        sec_list=Searchengine.title_search(self, query_sec)
        if len(sec_list)==0:
            title_list = Searchengine.title_search(self, query_title)
            title_list = Searchengine.get_new_article_list(self, title_list)
            if len(title_list)==0:
                content_list = Searchengine.title_search(self, query_content)
                content_list = Searchengine.get_new_article_list(self, content_list)
                return content_list
            return title_list

        else:
            sec_list=Searchengine.get_new_article_list(self,sec_list)
            return sec_list

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
            "size": 20,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"section": "{}".format(keywords)}},
                        {"match": {"content": "{}".format(keywords)}}
                    ]
                }
            },
            "sort": [{"versionNumber": {'order': "desc"}}],
            "collapse": {
                "field": "section.jie"
            }
        }

        article_list=Searchengine.judge_search(self, query_sec,query_title,query_content)
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
            chapter = cont['_source']['chapter'].strip('\n')
            section = cont['_source']['section'].strip('\n')
            content = cont['_source']['content'].strip('\n')
            quote = cont['_source']['quote'].strip('\n')
            picture = cont['_source']['picture']
            small_title=cont['_source']['small_title']
            material_name = cont['_source']['material_name']
            material_code = cont['_source']['material_code']
            title = cont['_source']['title']
            creatTime = cont['_source']['creatTime']
            dataStatus = cont['_source']['dataStatus']
            versionNumber = cont['_source']['versionNumber']
            processStatus = cont['_source']['processStatus']
            desc = cont['_source']['desc']
            source = cont['_source']['source']
            top = cont['_source']['top']

            creater = cont['_source']['creater']

            content=content.replace('\n','')
            d['chapter'] = chapter
            d['section'] = section
            d['content'] = content
            d['picture'] = picture
            d['material_name'] = material_name
            d['material_code'] = material_code
            d['quote'] = quote
            d['title'] = title
            d['small_title'] = small_title
            d['creatTime'] = creatTime
            d['dataStatus']=dataStatus
            d['versionNumber']=versionNumber
            d['processStatus']=processStatus
            d['desc'] = desc
            d['source'] = source
            d['top'] = top
            d['creater'] = creater
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
        res_update = self.es.update(index='material', id=article_list['_id'],
                                    body={'doc':{'content': data[0]['content'], 'picture': data[0]['picture'],
                                                  'desc': data[0]['desc'], 'source': data[0]['source'],
                                                  'top': data[0]['top'],'versionNumber':0,
                                                    'processStatus':'待提交','updateTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                  }})
        return res_update

    def data2es_submit(self,article_list,data,l):
        res_update = self.es.update(index='material', id=article_list['_id'],
                                    body={'doc':{'content': data[0]['content'], 'picture': data[0]['picture'],
                                                  'desc': data[0]['desc'], 'source': data[0]['source'],
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


if __name__ == "__main__":
    search_engine = Searchengine()
    str='液压支架有哪些用途'
    str=search_engine.strip_stopword(str)
    res = search_engine.search(str)
    #new_response=search_engine.manageSearch_data(res)
    print(res)
    article_list=search_engine.update_es_data('液压支架')
    #print(article_list)
    slice_data= search_engine.data_slice(res,1,5)
    #print(slice_data)



