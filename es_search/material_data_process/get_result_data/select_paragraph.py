
from material_data_process.get_result_data.kmp import *
from material_data_process.get_result_data.get_jie_data2 import *
def match_keyword(keyword,content):
    re_cont=[]
    search_position=[]
    content_list=content.split('<br/>')
    n = len(content_list)
    for i in range(n):
        if not content_list[i].startswith('<im'):
            next_locs = next_loc(keyword)
            loc = KMP(content_list[i], keyword, next_locs)
            if loc!=-1:
                search_position.append(loc)
                search_position.append(loc + len(next_locs))
                con=insert_label(search_position, content_list[i])
                re_cont.append(con)
                if i+1<n:
                    re_cont.append(content_list[i+1])
                if i+2<n:
                    re_cont.append(content_list[i+2])

    return re_cont

def insert_label(search_position,con):
    con_list=list(con)
    con_list.insert(search_position[0], '<h1>')
    con_list.insert(search_position[1]+1, '</h1>')
    new_con = ''.join(con_list)
    return new_con

if __name__ == "__main__":
    content='我是<br/>交换机<br/>和世界经济<br/>拉升阶段加拿大'
    keyword='世界'
    re_cont=match_keyword(keyword,content)
    print(re_cont)





