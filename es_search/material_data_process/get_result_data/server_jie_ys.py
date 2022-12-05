# -- coding: utf-8 --

import io
from flask import request, Flask, jsonify
#from gevent import pywsgi
from flask_cors import *
import logging
from Searchengine_jie import Searchengine
from get_jie_data import *
import time

server = Flask(__name__)
log = logging.getLogger('monitor.default')
CORS(server, supports_credentials=True)

searchengine = Searchengine()

#http://10.0.0.58:5000//search
@server.route("/search", methods=["GET", "POST"],endpoint="search")
def search():
    reponsedic = {}
    json_info = request.json
    print(json_info)
    pageNumber = json_info['pageNumber']
    pageSize = json_info['pageSize']
    searchValue=json_info['searchValue']
    if searchValue != '':
        #searchValue=searchengine.strip_stopword(searchValue)
        response = searchengine.search(searchValue)
        n=len(response)
        slice_response = searchengine.data_slice(response, pageNumber, pageSize)
        reponsedic['data'] = slice_response
        reponsedic['number'] = n

    if searchValue == "":
        res=searchengine.search_null()
        n = len(res)
        response = searchengine.data_slice(res, pageNumber, pageSize)
        reponsedic['data'] = response
        reponsedic['number'] = n

    return jsonify(reponsedic)

@server.route("/material_name", methods=["GET", "POST"],endpoint="material_name")
def material_name_search():
    reponsedic = {}
    json_info = request.json
    material_name = json_info['material_name']
    response = searchengine.search_material_name(material_name)
    reponsedic['data'] = response
    return jsonify(reponsedic)


@server.route("/material_code", methods=["GET", "POST"],endpoint="material_code")
def material_code_search():
    reponsedic = {}
    json_info = request.json
    material_code = json_info['material_code']
    response = searchengine.search_material_code(material_code)
    reponsedic['data'] = response
    return jsonify(reponsedic)

@server.route("/details", methods=["GET", "POST"],endpoint="details")
def search():
    reponsedic = {}
    json_info = request.json
    searchValue=json_info['title']
    versionNumber=json_info['versionNumber']
    if versionNumber=="":
        response=searchengine.search(searchValue)
        reponsedic['details']=response
    else:
        response = searchengine.history_search(searchValue,versionNumber)
        response=searchengine.get_new_article_list(response)
        reponsedic['details'] = response
    return jsonify(reponsedic)

@server.route("/upload", methods=["POST", "GET"],endpoint="upload")
def upload_files():
    reponsedic = {}
    uploaded_files = request.files.getlist('files')
    uploaded_files=sort_files(uploaded_files)
    word_file_list=[]
    
    if len(uploaded_files)==123:
        path = '/usr/local/webserver/zhishiku-python/es_search/material_data_process/get_result_data/data/Material_Category_Data/1.txt'
        f = open(path, 'r',encoding='utf-8')
        con=f.readlines()
        new_con=[]
        for c in con:
            c.replace('\n','')
            c.replace(' ','')
            new_con.append(c)
        reponsedic=''.join(new_con)
        
        time.sleep(2)
        return reponsedic

    else:
        path = '/usr/local/webserver/zhishiku-python/es_search/material_data_process/get_result_data/data/Material_Category_Data/4.txt'
        f = open(path, 'r',encoding='utf-8')
        con=f.readlines()
        new_con=[]
        for c in con:
            c.replace('\n','')
            c.replace(' ','')
            new_con.append(c)
        reponsedic=''.join(new_con)
        time.sleep(4)
        return reponsedic

    
    
    '''
    for file in uploaded_files:
        f = io.BytesIO(file.read())
        word_file_list.append(f)
    all_data_list, all_data_list_index = get_data_list(word_file_list)
    new_data = get_data_patition(all_data_list, all_data_list_index)
    zhang_list = get_last_data(new_data)
    reponsedic['data'] = zhang_list
    '''


@server.route("/download", methods=["POST", "GET"],endpoint="download")
def download_files_data():
    reponsedic = {}
    data = request.get_json()
    data=data['data']
    title_index, small_title_index, title_list, small_title_list=searchengine.update_small_title(data[0]['all_title'])
    #ts_list=title_smallTitle(title_index, small_title_index, title_list, small_title_list)
    #data[0]['grade_all_title']=ts_list
    data[0]['small_title'] = small_title_list
    data[0]['title']=title_list
    title_quote = get_quote(title_list)
    data[0]['title_quote'] = title_quote
    small_title_quote = get_quote(small_title_list)
    data[0]['small_title_quote'] = small_title_quote
    all_quote = get_all_quote(data[0]['quote'], title_quote, small_title_quote)
    data[0]['all_quote'] = all_quote
    new_title_list = searchengine.get_combin_title(title_list)
    data[0]['combin_title'] = [data[0]['section'] + w for w in new_title_list]
    content_text=searchengine.updete_content(data[0]['content'])
    data[0]['content_text'] = content_text

    material_code=[mc.split('_')[0] for mc in data[0]['combin_material_name_code']]
    material_name = [mc.split('_')[1] for mc in data[0]['combin_material_name_code']]
    data[0]['material_code'] = material_code
    data[0]['material_name'] = material_name

    article_list = searchengine.update_es_data(data[0]['section'])
    if len(article_list)==0:
        new_data = get_result_data(data,1,'已完成')
        load_data2es(new_data)
        reponsedic['data'] = new_data
    else:
        if article_list[0]['_source']['processStatus']=='待提交':
            res_update=searchengine.data2es_submit_save(article_list[0],data,versionNumber=len(article_list),processStatus='已完成')
        else:
            new_data = get_result_data(data,len(article_list)+1,'已完成')
            load_data2es(new_data)
            reponsedic['data'] = new_data
    return jsonify(reponsedic)

@server.route("/saveDraft", methods=["POST", "GET"],endpoint="saveDraft")
def saveDraft():
    reponsedic = {}
    data = request.get_json()
    data=data['data']
    
    title_index, small_title_index, title_list, small_title_list = searchengine.update_small_title(data[0]['all_title'])
    data[0]['small_title'] = small_title_list
    data[0]['title'] = title_list
    title_quote=get_quote(title_list)
    data[0]['title_quote']=title_quote
    small_title_quote = get_quote(small_title_list)
    data[0]['small_title_quote'] = small_title_quote
    all_quote=get_all_quote(data[0]['quote'],title_quote,small_title_quote)
    data[0]['all_quote'] = all_quote
    new_title_list=searchengine.get_combin_title(title_list)
    data[0]['combin_title'] = [data[0]['section'] + w for w in new_title_list]
    content_text = searchengine.updete_content(data[0]['content'])
    data[0]['content_text'] = content_text

    material_code = [mc.split('_')[0] for mc in data[0]['combin_material_name_code']]
    material_name = [mc.split('_')[1] for mc in data[0]['combin_material_name_code']]
    data[0]['material_code'] = material_code
    data[0]['material_name'] = material_name

    article_list = searchengine.update_es_data(data[0]['section'])
    
    if len(article_list) == 0:
        new_data=get_result_data(data,0,'待提交')
        load_data2es(new_data)
        reponsedic['data'] = new_data
    else:
        if article_list[0]['_source']['processStatus']=='待提交':
            new_data = searchengine.data2es_submit_save(article_list[0],data,versionNumber=0,processStatus='待提交')
            print(new_data)
        else:
            new_data = get_result_data(data,0,'待提交')
            load_data2es(new_data)
            reponsedic['data'] = new_data
    return jsonify(reponsedic)

@server.route("/manageSearch", methods=["POST", "GET"],endpoint="manageSearch")
def manage_search():
    reponsedic = {}
    json_info = request.json
    pageNumber = json_info['pageNumber']
    pageSize = json_info['pageSize']
    section = json_info['section']

    if section!="":
        response = searchengine.manage_search(section)
        n = len(response)
        #slice_response = searchengine.data_slice(response, pageNumber, pageSize)
        
        reponsedic['data'] = response
        reponsedic['number'] = n
        
    if section == '':
        response = searchengine.search_null_manage()
        n = len(response)
        response = searchengine.data_slice(response, pageNumber, pageSize)
        reponsedic['data'] = response
        reponsedic['number'] = n
    #print(reponsedic)
    return jsonify(reponsedic)

@server.route("/edit", methods=["POST", "GET"],endpoint="edit")
def manage_edit():
    reponsedic = {}
    json_info = request.json
    chapter = json_info['chapter']
    response = searchengine.search_chapter(chapter)
    reponsedic['data'] = response
    return jsonify(reponsedic)

@server.route("/frozen", methods=["POST", "GET"],endpoint="frozen")
def manage_frozen():
    json_info = request.json
    section = json_info['section']
    unfreezReason = json_info['unfreezReason']
    response = searchengine.update_es_data(section)
    res_update=searchengine.frozen(response,unfreezReason)

    return 'success'

@server.route("/unfrozen", methods=["POST", "GET"],endpoint="unfrozen")
def manage_unfrozen():
    json_info = request.json
    section = json_info['section']
    unfreezReason = json_info['unfreezReason']
    response = searchengine.update_es_data(section)
    res_update = searchengine.unfrozen(response,unfreezReason)
    return 'success'

@server.route("/batch_frozen", methods=["POST", "GET"],endpoint="batch_frozen")
def manage_batch_frozen():
    json_info = request.json
    sections = json_info['sections']
    unfreezReason = json_info['unfreezReason']
    sections=sections.split(',')
    response = searchengine.batch_frozen(sections,unfreezReason)
    return response

@server.route("/batch_unfrozen", methods=["POST", "GET"],endpoint="batch_unfrozen")
def manage_batch_unfrozen():
    json_info = request.json
    sections = json_info['sections']
    unfreezReason = json_info['unfreezReason']
    sections = sections.split(',')
    response = searchengine.batch_unfrozen(sections,unfreezReason)
    return response

@server.route("/manageDetails", methods=["GET", "POST"],endpoint="manageDetails")
def manageDetails():
    reponsedic = {}
    json_info = request.json
    searchValue=json_info['section']
    response=searchengine.search_details(searchValue)
    reponsedic['details']=response
    return jsonify(reponsedic)

@server.route("/histVersion", methods=["GET", "POST"],endpoint="histVersion")
def histVersion():
    reponsedic = {}
    json_info = request.json
    searchValue=json_info['section']
    response=searchengine.update_es_data(searchValue)
    new_response=searchengine.history_V(response)
    reponsedic['histVersion']=new_response

    return jsonify(reponsedic)

@server.route("/delete", methods=["GET", "POST"],endpoint="delete")
def delete_data():
    json_info = request.json
    section = json_info['section']
    versionNumber = json_info['versionNumber']
    searchengine.delete(section, versionNumber)

    return 'success'

@server.route("/versionNumber", methods=["GET", "POST"],endpoint="versionNumber")
def batch_delete_data():
    json_info = request.json
    section = json_info['section']
    article_list=searchengine.delete_search(section)
    article_list = searchengine.manageSearch_data(article_list)
    versionNumber_list=[art['versionNumber'] for art in article_list]
    return versionNumber_list

if __name__ == "__main__":
    server.config['JSON_AS_ASCII'] = False
    server.run(debug=True, port=5000,host='0.0.0.0')
    #server = pywsgi.WSGIServer((port=5000,host='0.0.0.0'), server)
    #server.serve_forever()
