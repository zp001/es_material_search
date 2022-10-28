# -*- coding: utf-8 -*-
import json
import os
from io import BytesIO
import datetime
import docx
import requests
from docx.document import Document
from docx.text.paragraph import Paragraph
from docx.image.image import Image
from docx.parts.image import ImagePart
from docx.oxml.shape import CT_Picture
from PIL import Image
import base64
import re
import tqdm
import time


import material_data_process.get_result_data.comput_similarity as ed
from material_data_process.get_result_data import recog_small_title
from material_data_process.get_result_data.entity_label import get_position
from material_data_process.get_result_data.kmp import insert_label


def get_picture(document: Document, paragraph: Paragraph):
    """
    document 为文档对象
    paragraph 为内嵌图片的段落对象，比如第1段内
    """
    result_list = []
    img_list = paragraph._element.xpath('.//pic:pic')
    if len(img_list) == 0 or not img_list:
        return
    for i in range(len(img_list)):
        img: CT_Picture = img_list[i]
        embed = img.xpath('.//a:blip/@r:embed')[0]
        related_part: ImagePart = document.part.related_parts[embed]
        image: Image = related_part.image
        result_list.append(image)
    return result_list

def get_files(path):
    """
    读取word文档，对文档进行排序
    """
    file_name = []
    files = os.listdir(path)  # 采用listdir来读取所有文件
    for i in files:
        file_name.append(i)
    file_name.sort(key=lambda x: int(x.split('.')[0]))
    return file_name

def sort_files(files_list):
    n=len(files_list)
    if n%2==0:
        for i in range(n//2):
            files_list.insert(2*i+1,files_list[n//2+i])
            del files_list[n//2+i+1]
    if n%2==1:
        for i in range(int(n//2)):
            files_list.insert(2*i+1,files_list[int(n//2)+i+1])
            del files_list[int(n//2)+i+2]

    return files_list
def clean_text(para:str):
    """
        数据清洗
    """
    para=re.sub(r"\s|■|•",'',para)
    para = re.sub(r"\'", '', para)
    #para = para.encode('ascii', 'ignore').decode()  # 删除 unicode 字符（乱码
    #para =re.sub(r'[’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！\[\\\]^_`{|}~]+', ' ', para) # # 删除特殊字符
    #para = re.sub('\s{2,}', "", para) #  # 删除2个及以上的空格
    return para

def get_content(file):
    """
        读取word文档内容，以段落形式组织数据，每张图片等同一个段落。
        """
    data_list=[]
    for i in range(len(file.paragraphs)):
        para = file.paragraphs[i]
        image_list = get_picture(file, para)
        para=para.text.strip()
        para=para.replace(' ','')
        para=clean_text(para)
        p=process_picture(image_list)
        data_list.append(para)
        for pic in p:
            data_list.append(pic)
    return data_list

def process_flies(path,file_name):
    """
        得到文档地址
        """
    locations=[]
    for file in file_name:
        location = os.path.join(path, file)
        locations.append(location)
    return locations

def process_pig_parag(para):
    """
        清洗数据
        """
    para = para.replace(' ', '')
    para = clean_text(para)
    return para

def process_picture(image_list):
    """
        处理word文档图片
        """
    p=[]
    if image_list:
        for image in image_list:
            if image:
                blob = image.blob  # blob方法获取二进制流文件
                #Image.open(BytesIO(blob)).show()
                img_stream = base64.b64encode(blob)
                bs64 = "<img src=\"data:image/png;base64,"+img_stream.decode('utf-8')+"\">"
                p.append(bs64)

    return p

def get_data_list(locations):
    """
        处理上传的文档，得到分节标识'第'位置
        """
    all_data_list=[]
    all_data_list_index=[]
    for i in range(len(locations)):
        file = docx.Document(locations[i])
        data_list = get_content(file)
        data_list=[x for x in data_list if x!='']
        all_data_list.append(data_list)

    all_data_list=[i for j in all_data_list for i in j]
    for i in range(len(all_data_list)):
        if all_data_list[i].startswith('第'):
            all_data_list_index.append(i)
    return all_data_list,all_data_list_index

def remove_pian(l):
    """
        去掉每章开头前面的描述
        """
    if re.match(r'^[第][一二三四五六七八九十—]+篇', l[0][0]):
        l=l[1:]
    return l

def get_data_patition(all_data_list,all_data_list_index):
    """
        将每章数据分成节，形成一个二维数组
        """
    new_data=[]
    for i in all_data_list_index:
        if all_data_list_index.index(i) ==0 and all_data_list_index[0]!=0:
            new_data.append(all_data_list[0:i])
        if all_data_list_index.index(i) != 0:
            new_data.append(all_data_list[all_data_list_index[all_data_list_index.index(i)-1]:i])
        if all_data_list_index.index(i) ==(len(all_data_list_index)-1):
            new_data.append(all_data_list[i:])
    new_data=remove_pian(new_data)

    return new_data

def get_material_catg():
    """
        得到物料名称和代码对应数据
        """
    file = './/data//物料类别数据//物料类别.xls'
    bms_all_data, big_category_data, mid_category_data, small_category_data = ed.get_category_data(file)
    bms_data, bms_code = ed.get_data_dic(big_category_data, mid_category_data, small_category_data)
    return bms_data,bms_code

def get_small_title(con,section):
    """
        识别每节的一级标题，返回标题以及标题去掉引用后和节名称组合形成的组合标题，组合标题为后续搜索使用
        """
    title=[]
    combin_title=[]
    for d in con:
        if re.match(r'^[一二三四五六七八九十—]+、', d):
            s=d.split('、')[1]
            if '引用' in s:
                ind=s.index('引')
                s=s[:ind-1]
                s = section + s
            else:
                s=section+s
            combin_title.append(s)
            title.append(d)
            i=con.index(d)
            new_d= "<h3>" + d + '</h3>'
            con[i]=new_d

    return title,con,combin_title

def get_para_pic(jie_list):
    """
        得到每节图片，并且图片与前面的文本段落对应:{text1：[p1,p2,...],text2:[p1,p2]}
        """
    all_pic = []
    para_pic = {}
    pic = []
    pic_ind = []
    for i in range(len(jie_list)):
        if jie_list[i].startswith('<img'):
            pic.append(jie_list[i])
            pic_ind.append(i)

        else:
            if len(pic_ind) != 0:
                para_pic[jie_list[pic_ind[0] - 1]] = pic
                all_pic.append(para_pic)
                para_pic = {}
                pic = []
                pic_ind = []
    return pic

def get_para_pic_list(jie_list):
    """
        得到整个节的图片，放到数组中
        """
    pic=[]
    for i in range(len(jie_list)):
        if jie_list[i].startswith('<img'):
            pic.append(jie_list[i])
    return pic

def remove_picture(s):
    """
        优化实体标签处理速度，将打标的节内容中图片代码去掉，形成新的不带图片代码的文本去打实体标签
        """
    s_list=s.split("|")
    pic_ind=[]
    pic=[]
    j = 0
    for i in range(len(s_list)):
        if s_list[i].startswith('<img'):
            pic.append(s_list[i])
            pic_ind.append(i)
        else:
            s_list[j] = s_list[i]
            j += 1
    new_s='|'.join(l for l in s_list[0:j])
    return pic,pic_ind,new_s

def insert_picture(pic,pic_ind,label_new_s):
    """
        将图片重新插入到打上标签的内容中
        """
    label_s_list = label_new_s.split("|")
    for i in range(len(pic_ind)):
        label_s_list.insert(pic_ind[i],pic[i])
    label_s = '|'.join(l for l in label_s_list)
    return label_s

def get_last_data(new_data):
    """
        得到处理后的每章数据[{},{}...]
        """
    zhang_list=[]
    bms_data, bms_code = get_material_catg()
    name_zhang=new_data[0][0].split('章')[1]
    for i in range(len(new_data)):
        jie_data={}
        jyy = ''
        if i==0:
            jie_data["chapter"] = name_zhang
            jie_data["section"] = name_zhang+'前言'
            #jie_data["content"] = new_data[i][1:]
            small_index_list = recog_small_title.rec_small_title(new_data[i][1:])
            s, small_title = recog_small_title.concat_cont(small_index_list, new_data[i][1:])
            pic,pic_ind,new_s=remove_picture(s)
            position, position_substr = get_position(new_s, name_zhang+'前言')
            label_new_s = insert_label(position, new_s)
            label_pic_s = insert_picture(pic, pic_ind, label_new_s)
            jie_data["content"] = label_pic_s
            jie_pic=get_para_pic_list(new_data[i][1:])
            jie_data["picture"] = jie_pic
            jie_data['material_name'] = []
            jie_data['material_code'] = []
            jie_data["quote"] = ''
            jie_data["title"] = []
            jie_data["combin_title"] = []
            jie_data["small_title"] = small_title
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            jie_data["creatTime"] = now_time
        if i!=0:
            if '引用' in new_data[i][1]:
                jyy = re.sub('[()（）]', '', new_data[i][1])
            title, con,combin_title= get_small_title(new_data[i],new_data[i][0].split('节')[1])
            jie_data["chapter"] = name_zhang
            jie_data["section"]=new_data[i][0].split('节')[1]
            #jie_data["content"] = con[1:]
            small_index_list = recog_small_title.rec_small_title(con[1:])
            s, small_title = recog_small_title.concat_cont(small_index_list, con[1:])
            pic, pic_ind, new_s = remove_picture(s)
            position, position_substr = get_position(new_s, new_data[i][0].split('节')[1])
            label_new_s = insert_label(position, new_s)
            label_pic_s = insert_picture(pic, pic_ind, label_new_s)
            jie_data["content"] = label_pic_s
            jie_pic = get_para_pic_list(new_data[i][1:])
            jie_data["picture"] = jie_pic
            mat_sort_sim_list, cod_sort_sim_list = ed.match_all_data(new_data[i][0].split('节')[1], bms_data, bms_code)
            jie_data['material_name'] = mat_sort_sim_list
            jie_data['material_code'] = cod_sort_sim_list
            jie_data["quote"] = jyy
            jie_data["title"] = title
            jie_data["combin_title"] = combin_title
            jie_data["small_title"] = small_title
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            jie_data["creatTime"] = now_time

        zhang_list.append(jie_data)
    print(zhang_list)
    return zhang_list

def get_result_data(zhang_list):
    """
        添加一些前端传回的字段
        """
    new_zhang_list = []
    for t in zhang_list:
        updateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        t["updateTime"] =updateTime
        t["creater"] = 'admin'
        t["modifiedName"] = 'admin'
        t["dataStatus"] = '活动'
        t["versionNumber"] = 0
        t["processStatus"] = '待提交'
        t["desc"] = zhang_list[0]['desc']
        t["source"] = zhang_list[0]['source']
        t["top"] = zhang_list[0]['top']
        t["unfreezReason"] = ''
        t["modifiedReason"] = ''
        new_zhang_list.append(t)
    #print(new_zhang_list)
    return new_zhang_list

def get_result_data_s(zhang_list,l):
    """
        添加一些前端传回的字段
        """
    new_zhang_list = []
    for t in zhang_list:
        updateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        t["updateTime"] =updateTime
        t["creater"] = 'admin'
        t["modifiedName"] = 'admin'
        t["dataStatus"] = '活动'
        t["versionNumber"] = l
        t["processStatus"] = '已完成'
        t["desc"] = zhang_list[0]['desc']
        t["source"] = zhang_list[0]['source']
        t["top"] = zhang_list[0]['top']
        t["unfreezReason"] = ''
        t["modifiedReason"] = ''
        new_zhang_list.append(t)
    #print(new_zhang_list)
    return new_zhang_list

def load_data2es(article_list):
    """
        将数据写入到es
        """
    for i in tqdm.tqdm(article_list):
        data = json.dumps(i)
        try:
            base_url = "http://localhost:9200/" + "material" + "/" + "_doc" + "/"
            response = requests.post(base_url, headers={"Content-Type": "application/json"}, data=data.encode())
            print(response)
        except:
            print("失败")

if __name__ == "__main__":
    path="D://work//data//example_data//第一章1//"
    file_name=get_files(path)
    locations=process_flies(path,file_name)
    all_data_list,all_data_list_index=get_data_list(locations)
    new_data=get_data_patition(all_data_list, all_data_list_index)
    zhang_list=get_last_data(new_data)
    #load_data2es(zhang_list)



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
        "type": "integer"
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
'''
POST _analyze
{
  "analyzer": "ik_max_word",
  "text": "target="p"_blank"
}
'''
