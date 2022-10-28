# -*- coding: utf-8 -*-
import numpy as np
def KMP(main_str, sub_str, next_locs):
    """
    作用：寻找子串(sub_str)在主串(main_str)中的位置
    返回：若子串在主串中存在，则返回子串第一个字符的位置；若不存在，则返回0
    """
    main_len = len(main_str)
    sub_len = len(sub_str)
    i, j = 0, 0  # 指针初始化
    result = -1
    while i < main_len:
        if main_str[i] == sub_str[j]:
            if j >= sub_len - 1:  # 已经找到了sub_str在main_str中的位置
                result = i - sub_len + 1
                break
            i += 1
            j += 1
        elif next_locs[j] == -1:
            i += 1
            j = 0
        else:
            j = next_locs[j]
    return result


def next_loc(sub_str):
    """
    作用：计算sub_str中每一位字符的next()函数值
    返回：一个与sub_str长度相同的整形列表，记录着sub_str对应位置的next()值
    """
    result = []
    sub_len = len(sub_str)
    for i in range(sub_len):
        if i == 0:
            # sub_str的第一位字符的next()值为-1
            result.append(-1)
        else:
            k = result[i - 1]
            if sub_str[i - 1] == sub_str[k]:
                result.append(k + 1)
            else:
                # 迭代查找
                while True:
                    if k == -1:
                        result.append(0)
                        break
                    if sub_str[i - 1] == sub_str[result[k]]:
                        result.append(result[k] + 1)
                        break
                    k = result[k]

    for i in range(sub_len):
        # 对next()函数进行改进
        if result[i] != -1 and sub_str[i] == sub_str[result[i]]:
            result[i] = result[result[i]]
            pass
    return result

def get_entity_position(sup_str,main_str):
    """
        得到实体位置
        """
    entity_position=[]
    next_locs = next_loc(sup_str)
    loc = KMP(main_str, sup_str, next_locs)
    if loc!=-1:
        entity_position.append(loc+1)
        entity_position.append(loc+len(next_locs))
    return entity_position

def sort_position(position,position_substr):
    """
        根据实体位置进行排序
        """
    n = len(position)
    for i in range(n):
        for j in range(1, n - i):
            if position[j - 1][0] > position[j][0]:
                position[j - 1], position[j] = position[j], position[j - 1]
                position_substr[j - 1], position_substr[j] = position_substr[j], position_substr[j - 1]
    return position,position_substr

def sort_sub_list(sup_list):
    sup_list = sorted(sup_list, key=lambda i: len(i),reverse=True)
    return sup_list

def get_new_main_str(contain_in,main_str):
    ss = 'sssssssssssssssssss'
    for c in contain_in:
        l = c[1] - c[0]
        main_str = main_str[0:c[0] - 1] + ss[0:l + 1] + main_str[c[1]:]
    return main_str

def removeElement(nums, val):
    #快慢双指针
    n=len(nums)
    slow=0
    for fast in range(n):
        #当fast的值不等于val，将其赋给slow，并让slow前进1步
        #当fast的值等于val,slow不动，fast继续前进
        if nums[fast]!=val:
            nums[slow]=nums[fast]
            slow+=1
    return nums[0:slow]

#最大匹配优先原则
def get_all_entity_position(p_list,s,section):
    already_entity_position = []
    already_entity_position_substr=[]
    p_list=sort_sub_list(p_list)
    for k in p_list:
        if k!=section:
            cross = []
            for i in range(len(already_entity_position)):
                cross_s = get_new_main_str(cross, s)
                entity_position_cro = get_entity_position(k, cross_s)

                if len(entity_position_cro) != 0:
                    # 交叉关系判断
                    if already_entity_position[i][0]<=entity_position_cro[0]<=already_entity_position[i][1] or\
                            already_entity_position[i][0]<=entity_position_cro[1]<=already_entity_position[i][1]:
                        cross.append(already_entity_position[i])

            if len(cross) == 0:
                entity_position2 = get_entity_position(k, s)
                if len(entity_position2)!= 0:
                    already_entity_position.append(entity_position2)
                    already_entity_position_substr.append(k)

            if len(cross)!= 0:
                cross_new_main_str = get_new_main_str(cross, s)
                entity_position4 = get_entity_position(k, cross_new_main_str)

                if len(entity_position4)!=0:
                    already_entity_position.append(entity_position4)
                    already_entity_position_substr.append(k)

                else:
                    for c in cross:
                        cross_new_main_str2 = get_new_main_str([c], s)
                        i=already_entity_position.index(c)
                        p=already_entity_position_substr[i]
                        entity_position5 = get_entity_position(p, cross_new_main_str2)
                        if len(entity_position5) != 0:
                            already_entity_position.append(entity_position5)
                            already_entity_position_substr.append(already_entity_position_substr[i])

                            already_entity_position[i] = 'h'
                            already_entity_position_substr[i] = 't'

                            entity_position6 = get_entity_position(k, s)
                            already_entity_position.append(entity_position6)
                            already_entity_position_substr.append(k)

    already_entity_position_substr = removeElement(already_entity_position_substr, 't')
    already_entity_position = removeElement(already_entity_position, 'h')

    already_entity_position,already_entity_position_substr=sort_position(already_entity_position,already_entity_position_substr)

    return already_entity_position,already_entity_position_substr

def insert_label(position,s):
    s=list(s)
    i=0
    for entity_position in position:
        s.insert(entity_position[0]-1+2*i,'<a>')
        s.insert(entity_position[1]+1+2*i, '</a>')
        i=i+1
    s=''.join(s)
    return s

if __name__ == "__main__":
    main_str = '石棉制动制品和石棉水泥制品以及石棉和石棉'
    sup_list = ['石棉制动制品','石棉水泥制品','石棉','和']
    section = '液压支架'
    position,position_substr=get_all_entity_position(sup_list, main_str, section)
    label_main_str=insert_label(position, main_str)
    print(label_main_str)
