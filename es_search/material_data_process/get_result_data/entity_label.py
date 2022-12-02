# -*- coding: utf-8 -*-
import os
import re
from kmp import get_all_entity_position,insert_label

class Catalogue_data:
    def sort_files(self,path):
        file_names = []
        files = os.listdir(path)  # 采用listdir来读取所有文件
        for i in files:
            file_names.append(i)
        file_names.sort(key=lambda x: int(x.split('.')[0]))
        return file_names

    def flies_location(self,path, file_names):
        locations = []
        for file in file_names:
            location = os.path.join(path, file)
            locations.append(location)
        return locations

    def read_files(self,locations):
        section_list=[]
        for location in locations:
            with open(location, encoding='utf-8') as file:
                content = file.readlines()
                for line in content:
                    if '节' in line:
                        line=line.strip()
                        line=re.sub('\n', '',line)
                        line = re.sub('\t', '', line)
                        line = re.sub(' ', '', line)
                        sec_key=line.split('节')[1]
                        section_list.append(sec_key)
        return section_list

def get_position(content,section):
    path = '/usr/local/webserver/zhishiku-python/es_search/material_data_process/get_result_data/data/catalog_data/'
    path = '..//get_result_data//data//catalog_data//'
    get_catalogue = Catalogue_data()
    file_names = get_catalogue.sort_files(path)
    locations = get_catalogue.flies_location(path, file_names)
    section_list = get_catalogue.read_files(locations)
    section_list = list(set(section_list))
    position,position_substr=get_all_entity_position(section_list,content,section)
    return position,position_substr







