# -- coding: utf-8 -- 
# @Createtime：2022-11-8
# @Updatetime：9:19
# @Author：张鹏
# @File：parse_data.py
# @Description：从接口获取数据

import requests
def request_data(url,headers):
    """
    获取物料代码数据
    """
    req = requests.get(url,headers, timeout=30) # 请求连接
    req_json = req.json() # 获取数据
    print(req_json)
    return req_json
if __name__ == "__main__":
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjhhOGFiMGIyNDZkYzgxMTIwMTQ2ZGM4MTgxOTUwMDUyIn0.fz4rrq4wsTc2mg0E-PmyntyNqcz8Yox8RTmsrBg2zYg"
    url='http://www.fastmdm.infoyb.com/mdm/rest/api/materialInfo'
    request_data(url,token)















'''
import json
import requests

def get_td():
    url = "http://www.fastmdm.infoyb.com/mdm/rest/api/materialInfo"
    token = {"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjhhOGFiMGIyNDZkYzgxMTIwMTQ2ZGM4MTgxOTUwMDUyIn0.fz4rrq4wsTc2mg0E-PmyntyNqcz8Yox8RTmsrBg2zYg"}
    res = requests.get(url=url, headers=token)
    res1 = res.content.decode()
    connect = json.loads(res1)
    print(connect)


if __name__ == '__main__':
    get_td()
    '''
