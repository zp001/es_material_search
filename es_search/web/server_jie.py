import io

from flask import request, Flask, jsonify
from gevent import pywsgi
from flask_cors import *
import logging
from search.Searchengine_jie import Searchengine
from material_data_process.get_result_data.get_jie_data2 import *

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
    materialName = json_info['materialName']
    materialCode = json_info['materialCode']
    if searchValue!='' and materialName=='' and materialCode=='':
        searchValue=searchengine.strip_stopword(searchValue)
        searchValue = searchValue.strip()
        response = searchengine.search(searchValue)
        n=len(response)
        slice_response = searchengine.data_slice(response, pageNumber, pageSize)
        reponsedic['data'] = slice_response
        reponsedic['number'] = n

    if materialName!='' and searchValue=='' and materialCode=='':
        response = searchengine.search_m(materialName)
        n = len(response)
        slice_response = searchengine.data_slice(response, pageNumber, pageSize)
        reponsedic['data'] = slice_response
        reponsedic['number'] = n
        #reponsedic['data'] = response

    if materialCode!='' and searchValue=='' and materialName=='':
        response = searchengine.search_c(materialCode)
        n = len(response)
        slice_response = searchengine.data_slice(response, pageNumber, pageSize)
        reponsedic['data'] = slice_response
        reponsedic['number'] = n
        #reponsedic['data'] = response

    if materialCode=='' and searchValue=='' and materialName=='':
        res=searchengine.search_null()
        n = len(res)
        response = searchengine.data_slice(res, pageNumber, pageSize)
        reponsedic['data'] = response
        reponsedic['number'] = n

    return jsonify(reponsedic)

@server.route("/details", methods=["GET", "POST"],endpoint="details")
def search():
    reponsedic = {}
    json_info = request.json
    print(json_info)
    searchValue=json_info['title']
    versionNumber=json_info['versionNumber']
    if versionNumber=='':
        response=searchengine.search(searchValue)
        reponsedic['details']=response
    else:
        response = searchengine.history_search(searchValue,versionNumber)
        response=searchengine.get_new_article_list(response)
        print(response)
        reponsedic['details'] = response
    return jsonify(reponsedic)

@server.route("/upload", methods=["POST", "GET"],endpoint="upload")
def upload_files():
    reponsedic = {}
    uploaded_files = request.files.getlist('files')
    print(uploaded_files)
    #uploaded_files=sort_files(uploaded_files)
    word_file_list=[]
    for file in uploaded_files:
        f = io.BytesIO(file.read())
        word_file_list.append(f)
    all_data_list, all_data_list_index = get_data_list(word_file_list)
    new_data = get_data_patition(all_data_list, all_data_list_index)
    zhang_list = get_last_data(new_data)
    #print(zhang_list)
    reponsedic['data'] = zhang_list

    return jsonify(reponsedic)

@server.route("/download", methods=["POST", "GET"],endpoint="download")
def download_files_data():
    reponsedic = {}
    data = request.get_json()
    data=data['data']
    print(data)
    article_list = searchengine.update_es_data(data[0]['section'])
    if len(article_list)==0:
        new_data = get_result_data_s(data,1)
        load_data2es(new_data)
        reponsedic['data'] = new_data
    else:
        if article_list[0]['_source']['processStatus']=='待提交':
            res_update=searchengine.data2es_submit(article_list[0],data,len(article_list))
        else:
            new_data = get_result_data_s(data,len(article_list)+1)
            load_data2es(new_data)
            reponsedic['data'] = new_data
    return jsonify(reponsedic)

@server.route("/saveDraft", methods=["POST", "GET"],endpoint="saveDraft")
def saveDraft():
    reponsedic = {}
    data = request.get_json()
    data=data['data']
    print(data)
    article_list = searchengine.update_es_data(data[0]['section'])
    if len(article_list) == 0:
        new_data=get_result_data(data)
        load_data2es(new_data)
        reponsedic['data'] = new_data
    else:
        if article_list[0]['_source']['processStatus']=='待提交':
            new_data = searchengine.data2es_save(article_list[0], data)
        else:
            new_data = get_result_data(data)
            load_data2es(new_data)
            reponsedic['data'] = new_data
    return jsonify(reponsedic)

@server.route("/manageSearch", methods=["POST", "GET"],endpoint="manageSearch")
def manage_search():
    reponsedic = {}
    json_info = request.json
    print(json_info)
    pageNumber = json_info['pageNumber']
    pageSize = json_info['pageSize']
    section = json_info['section']
    if section!='':
        searchValue = searchengine.strip_stopword(section)
        searchValue = searchValue.strip()
        response = searchengine.search(searchValue)
        new_response=searchengine.manageSearch_data(response)
        print(new_response)
        n = len(response)
        slice_response = searchengine.data_slice(new_response, pageNumber, pageSize)
        reponsedic['data'] = slice_response
        reponsedic['number'] = n

    if section == '':
        response = searchengine.search_null()
        new_response = searchengine.manageSearch_data(response)
        n = len(response)
        response = searchengine.data_slice(new_response, pageNumber, pageSize)
        reponsedic['data'] = response
        reponsedic['number'] = n

    return jsonify(reponsedic)

@server.route("/edit", methods=["POST", "GET"],endpoint="edit")
def manage_edit():
    reponsedic = {}
    json_info = request.json
    print(json_info)
    section = json_info['section']
    response = searchengine.search(section)
    reponsedic['data'] = response
    return jsonify(reponsedic)

@server.route("/frozen", methods=["POST", "GET"],endpoint="frozen")
def manage_frozen():
    json_info = request.json
    print(json_info)
    section = json_info['section']
    unfreezReason = json_info['unfreezReason']
    response = searchengine.update_es_data(section)
    res_update=searchengine.frozen(response,unfreezReason)

    return 'success'

@server.route("/unfrozen", methods=["POST", "GET"],endpoint="unfrozen")
def manage_unfrozen():
    json_info = request.json
    print(json_info)
    section = json_info['section']
    unfreezReason = json_info['unfreezReason']
    response = searchengine.update_es_data(section)
    res_update = searchengine.unfrozen(response,unfreezReason)
    return 'success'

@server.route("/batch_frozen", methods=["POST", "GET"],endpoint="batch_frozen")
def manage_batch_frozen():
    json_info = request.json
    print(json_info)
    sections = json_info['sections']
    unfreezReason = json_info['unfreezReason']
    sections=sections.split(',')
    response = searchengine.batch_frozen(sections,unfreezReason)
    return response

@server.route("/batch_unfrozen", methods=["POST", "GET"],endpoint="batch_unfrozen")
def manage_batch_unfrozen():
    json_info = request.json
    print(json_info)
    sections = json_info['sections']
    unfreezReason = json_info['unfreezReason']
    sections = sections.split(',')
    response = searchengine.batch_unfrozen(sections,unfreezReason)
    return response

@server.route("/manageDetails", methods=["GET", "POST"],endpoint="manageDetails")
def search():
    reponsedic = {}
    json_info = request.json
    print(json_info)
    searchValue=json_info['section']
    response=searchengine.search(searchValue)
    reponsedic['details']=response
    return jsonify(reponsedic)

@server.route("/histVersion", methods=["GET", "POST"],endpoint="histVersion")
def search():
    reponsedic = {}
    json_info = request.json
    print(json_info)
    searchValue=json_info['section']
    response=searchengine.update_es_data(searchValue)
    new_response=searchengine.history_V(response)
    reponsedic['histVersion']=new_response

    return jsonify(reponsedic)

@server.route("/histRecord", methods=["GET", "POST"],endpoint="histRecord")
def search():
    reponsedic = {}
    json_info = request.json
    print(json_info)
    searchValue=json_info['histRecord']
    response=searchengine.update_es_data(searchValue)
    new_response=searchengine.history_V(response)
    reponsedic['histRecord']=new_response
    return jsonify(reponsedic)


if __name__ == "__main__":
    server.config['JSON_AS_ASCII'] = False
    server.run(debug=True, port=5000,host='0.0.0.0')
    #server = pywsgi.WSGIServer((port=5000,host='0.0.0.0'), server)
    #server.serve_forever()
