# -- coding: utf-8 -- 
# @Createtime：2022-12-1
# @Updatetime：8:59
# @Author：Test008
# @File：delete_data.py
# @Description：

from elasticsearch import Elasticsearch

def delete_es_data(keywords):
    es = Elasticsearch(hosts=['123.56.240.89:9280'],
                       http_auth=('elastic', 'infoyb2015'),
                       sniff_on_start=True,
                       sniff_on_connection_fail=True,
                       sniffer_timeout=600)

    query = {
        "query":
            {"term": {"section.jie": "{}".format(keywords)}
             }
    }

    response = es.search(index='material', body=query)
    article_list = response["hits"]["hits"]
    for i in range(len(article_list)):
        print(article_list[i]['_source']['section'])
    #es.delete_by_query(index='material', body=query)
    print('---- finish -')

if __name__ == "__main__":
    delete_es_data('非金属建筑材料')