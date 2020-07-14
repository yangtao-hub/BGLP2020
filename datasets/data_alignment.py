import xlrd
import time
import os
import datetime
import pandas as pd


## 提升了心率等采样率为1min的数值准确度
## 改进bolus时间戳冲突问题，但没有更改类型
def read_excel(file_path):
    '''

    :param file_path:
    :return: 所有数据
    '''
    # 获取数据
    data = xlrd.open_workbook(file_path)
    # 获取所有sheet名字
    sheet_names = data.sheet_names()
    for sheet in sheet_names:
        # 获取sheet
        table = data.sheet_by_name(sheet)
        # 获取总行数
        nrows = table.nrows  # 包括标题
        # 获取总列数
        ncols = table.ncols
        # print(ncols)
        col_all = []
        for j in range(ncols):
            col = []
            for i in range(1, nrows):
                col.append(table.cell_value(i, j))
            col_all.append(col)
            # print(col)
    return col_all


def cmpalso(lis):
    while '' in lis:
        lis.remove('')

    set_lst = set(lis)
    # set会生成一个元素无序且不重复的可迭代对象，也就是我们常说的去重
    if len(set_lst) != len(lis):
        print('列表里有重复的元素！')
        print(lis)


def timestump(lis):
    '''
    转换为 1-288
    input = ["", "time" , "时间值"...]
    output = [时间戳值...]
    num为需要将日期更改为下一天的日期的
    :param list1:
    :return:
    '''
    num = []
    interval2 = []
    timestumplist = []
    hourl = []
    minl = []
    for i in lis[1:]:
        if (i != "") & (i != "time"):
            interval2.append(i)

    # interval2 = ['13:20','15:20','20:20','01:20']
    for i in interval2:
        hourl.append(int(i[:2]))
        minl.append(int(i[3:]))
    # print(len(hourl))
    # print(len(minl))
    # print(interval2)
    for i in range(len(interval2)):
        #     # print(int(i[3:])%5)
        if (minl[i] % 5) != 0:
            timestump = hourl[i] * 12 + int(minl[i] / 5) + 2
        else:
            timestump = hourl[i] * 12 + int(minl[i] / 5) + 1
        if timestump == 289:
            timestump = 1
            num.append(i)
        timestumplist.append(timestump)
    # print(len(timestumplist))
    return timestumplist, num


def buchong1(lis):
    # input: 3个list 像list1一样
    # output:2个list list1，list2

    list1 = ['', 'date']
    list2 = ['', 'timestamp']
    list3 = []
    dateline = lis[0]
    timeline = lis[1]
    # print(dateline)
    # print(timeline)
    ## 第一天
    num = 288 - timeline[2] + 1
    for i in range(num):
        list3.append(288 - i)
    list3.reverse()
    for i in list3:
        list2.append(i)
        list1.append(dateline[2])

    ## 中间
    dateline1 = []
    for i in dateline[4:]:
        if i not in dateline1:
            dateline1.append(i)
    del dateline1[0]
    del dateline1[-1]

    for i in range(len(dateline1)):
        for j in range(1, 289):
            list2.append(j)
            list1.append(dateline1[i])

    ## 最后一天
    num = timeline[-1]
    for i in range(1, num + 1):
        list2.append(i)
        list1.append(dateline[-1])

    # print(list1)
    # print(list2)
    list3 = [list1, list2]
    return list3


# def cmp_add_two1(lis1,lis2,lis3,lis4,lis5):
#     # deallist = cmp_add_two(interval1,timestumptp,deallist,constnat[0],list1[1])
#     weizhi1 = []
#     weizhi2 = []
#     interval = []
#     interval.append(lis4)
#     interval.append(lis5[1])
#     for i in range(len(lis3[0])-2):
#         interval.append("")
#     # print(lis1)
#     # # # # print(len(interval))
#     # print(lis2)
#     # print(lis5)
#     # print(lis3[0])
#     # print(lis3[1])
#     # list000 = [1,2,3]
#     # for i in range(0,len(list000)):
#     #     print(i)
#     for i in range(2,len(lis2)):
#         for j in range(2,len(lis3[1])):
#             if (lis1[i] == lis3[0][j])&(lis2[i] == lis3[1][j]):
#                 # if lis1[i] == lis3[0][j]:
#                 weizhi1.append(i)
#                 weizhi2.append(j)
#     # print(len(weizhi1))
#     # print(len(weizhi2))
#     for i in range(1, len(weizhi1)):
#         if weizhi1[i] - weizhi1[i - 1] != 1:
#             print(i)
#             print("两列寻找时wrong" + lis4)
#     # if len(weizhi1) == len(lis2) - 2:
#     #     print("正确")
#     # print(lis5)
#     # print(weizhi1)
#     # print(weizhi2)
#     for i in weizhi1:
#         interval[weizhi2[i-2]] = lis5[i]
#     lis3.append(interval)
#     return lis3
#     # print(interval)
#     # print(weizhi1)
#     # print(weizhi2)
#     # print(lis3[1][weizhi2[0]])

def cmp_add_two(lis1, lis2, lis3, lis4, lis5):
    # 前两个没标题，第三个有表头，第四个标题名，第五个对应的添加值
    # deallist = cmp_add_two(interval1,timestumptp,deallist,constnat[1],list1[1])
    weizhi1 = []
    weizhi2 = []
    interval = [lis4, lis5[0]]
    for i in range(len(lis3[0]) - 2):
        interval.append("")
    # print(lis1)
    # # # # # print(len(interval))
    # print(lis2)
    # print(lis5)
    # print(lis3[0])
    # print(lis3[1])
    for i in range(len(lis2)):
        for j in range(1, len(lis3[1])):
            if (lis1[i] == lis3[0][j]) & (lis2[i] == lis3[1][j]):
                # if lis1[i] == lis3[0][j]:
                weizhi1.append(i)
                weizhi2.append(j)
    # print(len(weizhi1))
    # print(len(weizhi2))
    for i in range(1, len(weizhi1)):
        if weizhi1[i] - weizhi1[i - 1] != 1:
            # print(i)
            print("两列寻找时wrong" + lis4)
    if len(weizhi1) != len(lis2):
        print("不正确")
    # print(lis5)
    # print(weizhi1)
    # print(weizhi2)
    for i in weizhi1:
        interval[weizhi2[i]] = lis5[i + 1]
    lis3.append(interval)
    return lis3
    # print(interval)
    # print(weizhi1)
    # print(weizhi2)
    # print(lis3[1][weizhi2[0]])


def dealdate(lis):
    '''
    转换日期格式，拆分
    input:excel原数据的日期
    output:[纯日期]
            [纯时间]
    :param lis:
    :return:
    '''
    date1 = []
    time1 = ['']
    for i in lis:
        # print(i.split(" "))
        interval1 = i.split(" ")
        if len(interval1) == 2:
            date1.append(interval1[0])
            time1.append(interval1[1][:5])
    # print(len(date1))
    # print(len(time1))
    timestumpt, cdate = timestump(time1)
    # print(timestumpt)
    for i in cdate:
        con = datetime.datetime.strptime(date1[i], "%d-%m-%Y").date()
        # print(con)
        con = con + datetime.timedelta(days=1)
        con = con.timetuple()
        # print(type(time.strftime('%d-%m-%Y', con)))
        # date[i+2] = str(con.tm_mday) + "-" + str(con.tm_mon) + "-" + str(con.tm_year)
        date1[i] = time.strftime('%d-%m-%Y', con)
    return date1, timestumpt


def buchongreset(d1, t1, d2, t2):  # d1,t1,d2,t2,value
    '''
        补充使其连续
        每一个都为值
    :param lis:
    :return:
    '''
    # print(d1)
    # print(d2)
    # jishu = 0
    date1 = ['', 'date']
    timestump1 = ['', 'timestamp']

    startday = datetime.datetime.strptime(d1, "%d-%m-%Y")
    endday = datetime.datetime.strptime(d2, "%d-%m-%Y")
    chazhi = (endday - startday).days
    # print((endday - startday).days)
    if chazhi < 0:
        print("开始日期与终止日期写反了")
    else:
        ## 第一天
        num = 288 - t1 + 1
        list3 = []
        for k in range(num):
            list3.append(288 - k)
        list3.reverse()
        for k in list3:
            # jishu += 1
            timestump1.append(k)
            date1.append(d1)
            # type2.append(typel)
            # name1.append(lis1)
            # name2.append(lis2)

        ## 中间
        for j in range(1, chazhi):
            dateTime_z = startday + datetime.timedelta(days=j)
            dateTime_z = dateTime_z.timetuple()
            dateTime_z = time.strftime('%d-%m-%Y', dateTime_z)
            # print(dateTime_z)
            # print(dateline1)
            # list1 = [1,2]
            # ppp = []
            # for i in range(len(list1)):
            #     ppp.append(list1[i])
            # print(ppp)
            for k in range(1, 289):
                # jishu += 1
                timestump1.append(k)
                date1.append(dateTime_z)
                # type2.append(typel)
                # name1.append(lis1)
                # name2.append(lis2)

        ## 最后一天
        for k in range(1, t2 + 1):
            # jishu += 1
            timestump1.append(k)
            date1.append(d2)
            # type2.append(typel)
            # name1.append(lis1)
            # name2.append(lis2)

    # con1 = round((lis1 / jishu), 3)
    # con2 = round((lis2 / jishu), 3)
    # for i in range(len(date1)):
    #     name1.append(con1)
    #     name2.append(con2)
    list3 = []
    list3.append(date1)
    list3.append(timestump1)

    # print(timestump1)
    # print(date1)
    # print(type2)
    # print(name2)
    return list3


def reset0(d1, t1, biglist):
    # deallist2 = reset0(interval1, timestumptp, deallist1)
    # 前两个没标题，第三个有表头
    # list1 = ['', 'date']
    # list2 = ['', 'timestamp']
    # list3 = []
    if len(d1) != 0:
        Flag = False
        interva1 = []
        # 0指初始值，1指末尾值
        datenew0 = d1[0]
        datenew00 = datetime.datetime.strptime(datenew0, "%d-%m-%Y")

        timenew0 = t1[0]

        dateold0 = biglist[0][2]
        dateold00 = datetime.datetime.strptime(dateold0, "%d-%m-%Y")

        timeold0 = biglist[1][2]

        datenew1 = d1[-1]
        datenew11 = datetime.datetime.strptime(datenew1, "%d-%m-%Y")

        timenew1 = t1[-1]

        dateold1 = biglist[0][-1]
        dateold11 = datetime.datetime.strptime(dateold1, "%d-%m-%Y")

        timeold1 = biglist[1][-1]

        if (datenew00 < dateold00) | ((datenew00 == dateold00) & (timenew0 < timeold0)):
            if (datenew11 > dateold11) | (((datenew11 == dateold11) & (timenew1 > timeold1))):
                interva1 = buchongreset(datenew0, timenew0, datenew1, timenew1)
                Flag = True
            else:
                interva1 = buchongreset(datenew0, timenew0, dateold1, timeold1)
                Flag = True
        else:
            if (datenew11 > dateold11) | (((datenew11 == dateold11) & (timenew1 > timeold1))):
                interva1 = buchongreset(dateold0, timeold0, datenew1, timenew1)
                Flag = True

        if Flag:
            # print("in")
            for i in range(2, len(biglist)):
                interva1 = cmp_add_two(biglist[0][2:], biglist[1][2:], interva1, biglist[i][0], biglist[i][1:])
                # print("success")
            return interva1
    return biglist


def buchongbasal(d1, t1, d2, t2, value):  # d1,t1,d2,t2,value
    '''
        补充使其连续
    :param lis:
    :return:
    '''
    # d1 = ["11-11-2020","12-11-2020"]
    # d2 = ["12-11-2020","13-11-2020"]
    # t1 = [20,60]
    # t2 = [40,20]
    # value = ["", 3, 5]
    # print(len(d1))
    # print(d2)

    # d1.remove(d1[-1])
    # print(len(d1))
    # print(len(d2))
    date1 = []
    timestump1 = []
    value1 = []
    value1.append(value[0])
    # print(len(t2))
    # print(d1)
    for i in range(len(t2)):
        # print(i)
        dateline1 = d1[i]
        dateline2 = d2[i]
        valuer = value[i + 1]
        timeline1 = t1[i]
        timeline2 = t2[i]
        if dateline1 == dateline2:

            for j in range(timeline1, timeline2 + 1):
                date1.append(dateline1)
                timestump1.append(j)
                value1.append(valuer)
        else:
            startday = datetime.datetime.strptime(dateline1, "%d-%m-%Y")
            endday = datetime.datetime.strptime(dateline2, "%d-%m-%Y")
            chazhi = (endday - startday).days
            # print((endday - startday).days)
            if chazhi < 0:
                print("开始日期与终止日期写反了")
            else:
                ## 第一天
                num = 288 - timeline1 + 1
                list3 = []
                for k in range(num):
                    list3.append(288 - k)
                list3.reverse()
                for k in list3:
                    timestump1.append(k)
                    date1.append(dateline1)
                    value1.append(valuer)

                ## 中间
                for j in range(1, chazhi):
                    dateTime_z = startday + datetime.timedelta(days=j)
                    dateTime_z = dateTime_z.timetuple()
                    dateTime_z = time.strftime('%d-%m-%Y', dateTime_z)
                    # print(dateTime_z)
                    # print(dateline1)
                    # list1 = [1,2]
                    # ppp = []
                    # for i in range(len(list1)):
                    #     ppp.append(list1[i])
                    # print(ppp)
                    for k in range(1, 289):
                        timestump1.append(k)
                        date1.append(dateTime_z)
                        value1.append(valuer)

                ## 最后一天
                for k in range(1, timeline2 + 1):
                    timestump1.append(k)
                    date1.append(dateline2)
                    value1.append(valuer)
    # print(len(timestump1))
    # print(len(date1))
    # print(len(value1))
    Flag = True
    while Flag:
        timestump1_len = len(timestump1)
        # print(timestump1_len)
        for i in range(timestump1_len - 1):
            if i == timestump1_len - 2:
                Flag = False
                break
            if (date1[i + 1] == date1[i]) & (timestump1[i + 1] == timestump1[i]):
                del date1[i + 1]
                del timestump1[i + 1]
                del value1[i + 1 + 1]
                # date1.pop(j)
                # timestump1.pop(j)
                # value1.pop(j+1)
                #     Flag = True
                break
            # if Flag:
            #     break

    # print(date1)
    # print(value1)
    # print("buchongbasal")
    # print(timestump1)
    return date1, timestump1, value1

    # timeline = lis[1]
    # print(dateline)
    # print(timeline)
    ## 第一天
    '''
    num = 288 - timeline[2] + 1
    for i in range(num):
        list3.append(288 - i)
    list3.reverse()
    for i in list3:
        list2.append(i)
        list1.append(dateline[2])

    ## 中间
    dateline1 = []
    for i in dateline[4:]:
        if i not in dateline1:
            dateline1.append(i)
    dateline1.remove(dateline1[0])
    dateline1.remove(dateline1[-1])
    # print(dateline1)
    # list1 = [1,2]
    # ppp = []
    # for i in range(len(list1)):
    #     ppp.append(list1[i])
    # print(ppp)
    for i in range(len(dateline1)):
        for j in range(1, 289):
            list2.append(j)
            list1.append(dateline1[i])

    ## 最后一天
    num = timeline[-1]
    for i in range(1, num + 1):
        list2.append(i)
        list1.append(dateline[-1])

    # print(list1)
    # print(list2)
    list3 = []
    list3.append(list1)
    list3.append(list2)
    # for i in list3:
    #     print(i)
    return list3
    '''


def hebingbasal(d1, t1, d2, t2, value1, value2):
    weizhi = []
    interv1 = []
    # print(len(value1))
    # print(t1)
    for i in range(len(t2)):
        Flag = True
        for j in range(len(t1)):
            if (d1[j] == d2[i]) & (t1[j] == t2[i]):
                # if (t2[i] > 190)& (t2[i] <204):
                #     print(j)
                #     print(t1[j])
                #     print(value2[i + 1])
                #     print(value1[j+1])
                value1[j + 1] = value2[i + 1]

                Flag = False
                break
        if Flag:
            weizhi.append(i)
    if len(weizhi) != 0:  # 有瑕疵 在temp_basal的最后一个时间大于basal最后的时间时处理不了
        datenew0 = d1[0]
        datenew00 = datetime.datetime.strptime(datenew0, "%d-%m-%Y")

        timenew0 = t1[0]

        dateold0 = d2[0]
        dateold00 = datetime.datetime.strptime(dateold0, "%d-%m-%Y")

        timeold0 = t2[0]

        datenew1 = d1[-1]
        datenew11 = datetime.datetime.strptime(datenew1, "%d-%m-%Y")

        timenew1 = t1[-1]

        dateold1 = d1[-1]
        dateold11 = datetime.datetime.strptime(dateold1, "%d-%m-%Y")

        timeold1 = t2[-1]

        if (datenew00 < dateold00) | ((datenew00 == dateold00) & (timenew0 < timeold0)):
            if (datenew11 > dateold11) | (((datenew11 == dateold11) & (timenew1 > timeold1))):
                interv1 = buchongreset(datenew0, timenew0, datenew1, timenew1)

            else:
                interv1 = buchongreset(datenew0, timenew0, dateold1, timeold1)

        else:
            if (datenew11 > dateold11) | (((datenew11 == dateold11) & (timenew1 > timeold1))):
                interv1 = buchongreset(dateold0, timeold0, datenew1, timenew1)
            # else:
            #     interv1 = buchongreset(dateold0, timeold0, dateold1, timeold1)

        # print(interv1)
        interv1 = cmp_add_two(d1, t1, interv1, "", value1)
        # for i in interva1:
        #     print(interva1)

        del interv1[0][0]
        del interv1[0][0]
        del interv1[1][0]
        del interv1[1][0]
        del interv1[2][0]
        # interv1[0].remove(interv1[0][0])
        # interv1[0].remove(interv1[0][0])
        # interv1[1].remove(interv1[1][0])
        # interv1[1].remove(interv1[1][0])
        # interv1[2].remove(interv1[2][0])
        for i in interv1:
            pass
            # print(len(i))
            # print(i)
        # while 1:
        #     i = 0
        Flag = True
        for i in weizhi:
            for j in range(len(interv1[0])):
                if (interv1[0][j] == d2[i]) & (interv1[1][j] == t2[i]):
                    interv1[2][j + 1] = value2[i + 1]
                    Flag = False
                    break
            if Flag:
                print("hebingbasal出错了")
        return interv1[0], interv1[1], interv1[2]
    else:
        # print("weizhi none")
        pass
    # print(value1)
    return d1, t1, value1


def buchongbolus(d1, t1, d2, t2, typel, lis1, lis2):  # d1,t1,d2,t2,value
    '''
        补充使其连续
    :param lis:
    :return:
    '''
    # print(d1)
    # print(lis2)
    Flag = False
    if lis2 == "":
        Flag = True
    jishu = 0
    date1 = []
    timestump1 = []
    type2 = []
    name1 = []
    name2 = []

    if d1 == d2:

        for j in range(t1, t2 + 1):
            jishu += 1
            date1.append(d1)
            timestump1.append(j)
            type2.append(typel)
            # value1.append(valuer)
    else:
        startday = datetime.datetime.strptime(d1, "%d-%m-%Y")
        endday = datetime.datetime.strptime(d2, "%d-%m-%Y")
        chazhi = (endday - startday).days
        # print((endday - startday).days)
        if chazhi < 0:
            print("开始日期与终止日期写反了")
        else:
            ## 第一天
            num = 288 - t1 + 1
            list3 = []
            for k in range(num):
                list3.append(288 - k)
            list3.reverse()
            for k in list3:
                jishu += 1
                timestump1.append(k)
                date1.append(d1)
                type2.append(typel)
                # name1.append(lis1)
                # name2.append(lis2)

            ## 中间
            for j in range(1, chazhi):
                dateTime_z = startday + datetime.timedelta(days=j)
                dateTime_z = dateTime_z.timetuple()
                dateTime_z = time.strftime('%d-%m-%Y', dateTime_z)
                # print(dateTime_z)
                # print(dateline1)
                # list1 = [1,2]
                # ppp = []
                # for i in range(len(list1)):
                #     ppp.append(list1[i])
                # print(ppp)
                for k in range(1, 289):
                    jishu += 1
                    timestump1.append(k)
                    date1.append(dateTime_z)
                    type2.append(typel)
                    # name1.append(lis1)
                    # name2.append(lis2)

            ## 最后一天
            for k in range(1, t2 + 1):
                jishu += 1
                timestump1.append(k)
                date1.append(d2)
                type2.append(typel)
                # name1.append(lis1)
                # name2.append(lis2)

    con1 = round((lis1 / jishu), 3)
    if Flag:
        con2 = ""
    else:
        con2 = round((lis2 / jishu), 3)
    for i in range(len(date1)):
        name1.append(con1)
        name2.append(con2)

    # print(timestump1)
    # print(date1)
    # print(type2)
    # print(name2)
    return date1, timestump1, type2, name1, name2


def dealbolus(d1, t1, d2, t2, typel, lis1, lis2):  # d1,t1,d2,t2,typel,lis1,lis2
    date1 = []
    timestump1 = []
    type2 = []
    name1 = []
    name2 = []
    type2.append(typel[0])
    name1.append(lis1[0])
    name2.append(lis2[0])
    typel = typel[:len(d1) + 1]
    lis1 = lis1[:len(d1) + 1]
    lis2 = lis2[:len(d1) + 1]
    # print(len(d1))
    # print(len(t1))
    # print(len(typel))
    # print(lis1)

    # d1 = ['12-12-2020','13-12-2020']
    # t1 = [122,120]
    # d2 = ['12-12-2020','14-12-2020']
    # t2 = [130,201]
    # typel = ["", 'norma','sa']
    # lis1 = ["", 6, 2015]
    # lis2 = ["", 12, 2000]
    # print(lis2)
    for i in range(1, len(typel)):
        if typel[i] == "normal":
            date1.append(d1[i - 1])
            timestump1.append(t1[i - 1])
            type2.append(typel[i])
            name1.append(lis1[i])
            name2.append(lis2[i])
        else:
            if (d1[i - 1] == d2[i - 1]) & (t1[i - 1] == t2[i - 1]):
                date1.append(d1[i - 1])
                timestump1.append(t1[i - 1])
                type2.append(typel[i])
                name1.append(lis1[i])
                name2.append(lis2[i])
            else:
                datein, timein, typein, name1in, name2in = buchongbolus(d1[i - 1], t1[i - 1], d2[i - 1], t2[i - 1],
                                                                        typel[i], lis1[i], lis2[i])
                for i in range(len(datein)):
                    date1.append(datein[i])
                    timestump1.append(timein[i])
                    type2.append(typein[i])
                    name1.append(name1in[i])
                    name2.append(name2in[i])

    # print(date1)
    # print(timestump1)
    # print(type2)
    # print(name1)
    # print(name2)

    return date1, timestump1, type2, name1, name2


# 7,8,11,18
def buchongsleep(d1, t1, d2, t2, value):  # d1,t1,d2,t2,value
    '''
        补充使其连续
    :param lis:
    :return:
    '''
    # print(len(d1))
    # print(d2)
    # d1.remove(d1[-1])
    # print(len(d1))
    # print(len(d2))
    date1 = []
    timestump1 = []
    value1 = []
    value1.append(value[0])

    # d1 = ["11-11-2020","12-11-2020"]
    # d2 = ["12-11-2020","13-11-2020"]
    # t1 = [20,60]
    # t2 = [40,20]
    # value = ["", 3, 5]
    for i in range(len(d1)):
        dateline1 = d1[i]
        if d2[i] == "":
            d2[i] = d1[i]
        dateline2 = d2[i]
        valuer = value[i + 1]
        timeline1 = t1[i]
        if t2[i] == "":
            t2[i] = t1[i]
        timeline2 = t2[i]
        if dateline1 == dateline2:

            for j in range(timeline1, timeline2 + 1):
                date1.append(dateline1)
                timestump1.append(j)
                value1.append(valuer)
        else:
            startday = datetime.datetime.strptime(dateline1, "%d-%m-%Y")
            endday = datetime.datetime.strptime(dateline2, "%d-%m-%Y")
            chazhi = (endday - startday).days
            # print((endday - startday).days)
            if chazhi < 0:
                print("开始日期与终止日期写反了")
            else:
                ## 第一天
                num = 288 - timeline1 + 1
                list3 = []
                for k in range(num):
                    list3.append(288 - k)
                list3.reverse()
                for k in list3:
                    timestump1.append(k)
                    date1.append(dateline1)
                    value1.append(valuer)

                ## 中间
                for j in range(1, chazhi):
                    dateTime_z = startday + datetime.timedelta(days=j)
                    dateTime_z = dateTime_z.timetuple()
                    dateTime_z = time.strftime('%d-%m-%Y', dateTime_z)
                    # print(dateTime_z)
                    # print(dateline1)
                    # list1 = [1,2]
                    # ppp = []
                    # for i in range(len(list1)):
                    #     ppp.append(list1[i])
                    # print(ppp)
                    for k in range(1, 289):
                        timestump1.append(k)
                        date1.append(dateTime_z)
                        value1.append(valuer)

                ## 最后一天
                for k in range(1, timeline2 + 1):
                    timestump1.append(k)
                    date1.append(dateline2)
                    value1.append(valuer)

    # print(timestump1)
    # print(date1)
    # print(value1)
    return date1, timestump1, value1

    # timeline = lis[1]
    # print(dateline)
    # print(timeline)
    ## 第一天
    '''
    num = 288 - timeline[2] + 1
    for i in range(num):
        list3.append(288 - i)
    list3.reverse()
    for i in list3:
        list2.append(i)
        list1.append(dateline[2])

    ## 中间
    dateline1 = []
    for i in dateline[4:]:
        if i not in dateline1:
            dateline1.append(i)
    dateline1.remove(dateline1[0])
    dateline1.remove(dateline1[-1])
    # print(dateline1)
    # list1 = [1,2]
    # ppp = []
    # for i in range(len(list1)):
    #     ppp.append(list1[i])
    # print(ppp)
    for i in range(len(dateline1)):
        for j in range(1, 289):
            list2.append(j)
            list1.append(dateline1[i])

    ## 最后一天
    num = timeline[-1]
    for i in range(1, num + 1):
        list2.append(i)
        list1.append(dateline[-1])

    # print(list1)
    # print(list2)
    list3 = []
    list3.append(list1)
    list3.append(list2)
    # for i in list3:
    #     print(i)
    return list3
    '''


def avg_1(d1, t1, value):
    if len(d1) == 0:
        return value

    avg_num = 0
    avg_num_num = 0
    for i in range(1, len(d1)):
        if (d1[i] == d1[i - 1]) & (t1[i] == t1[i - 1]):
            avg_num += value[i]
            avg_num_num += 1
        elif ((d1[i] != d1[i - 1]) | (t1[i] != t1[i - 1])) & (avg_num != 0):
            avg_num += value[i]
            avg_num_num += 1
            value[i] = round((avg_num / avg_num_num), 4)
            avg_num = 0
            avg_num_num = 0
    return value


def sum_1(d1, t1, value):
    if len(d1) == 0:
        return value
    if value[2] == "":
        return value
    # print(value)
    avg_num = 0
    # avg_num_num = 0
    for i in range(1, len(d1)):
        if (d1[i] == d1[i - 1]) & (t1[i] == t1[i - 1]):
            avg_num += value[i]
            # avg_num_num += 1
        elif ((d1[i] != d1[i - 1]) | (t1[i] != t1[i - 1])) & (avg_num != 0):
            avg_num += value[i]
            # avg_num_num += 1
            # value[i] = round((avg_num / avg_num_num),4)
            value[i] = avg_num
            avg_num = 0
            # avg_num_num = 0
    return value


def qiusubtime(time0):
    ## 求血糖值和真实时间戳的差值
    time0 = int(time0[3:])
    # print(type(time0))
    chazhi = 0
    if time0 % 5:
        while 1:
            time0 += 1
            chazhi += 1
            if (time0 % 5) == 0:
                # print(chazhi)
                return chazhi
    else:
        return 0


def dealser(data):
    '''
        处理第一列数据
        '''
    # print(data)
    deallist = []
    changeFlag = False
    con_num_local = 0
    list1 = data[:con_num[con_num_local]]
    con_num_local += 1
    cmpalso(list1[0])
    # print(list1)
    date = ['', 'date']
    timelist = ['', 'time']
    timestumplist = ['', 'timestamp']
    # 转换日期格式，拆分
    for i in list1[0]:
        # print(i.split(" "))
        interval1 = i.split(" ")
        if len(interval1) == 2:
            date.append(interval1[0])
            timelist.append(interval1[1][:5])
    ## 先算个时间差，补充到con13-con18
    global shijiancha
    shijiancha = qiusubtime(timelist[2])
    # print(shijiancha)
    if shijiancha == 0:
        changeFlag = False
    # print(shijiancha)
    # while 1 :
    #     print(shijiancha)
    dealnum = [11, 12, 13, 14, 15, 17]
    for bbb in dealnum:
        if data[con_num[bbb] + 1][1] == "":
            continue
        else:
            contime1 = datetime.datetime.strptime(data[con_num[bbb] + 1][1], "%d-%m-%Y %H:%M:%S")
            contime2 = datetime.datetime.strptime(data[con_num[bbb] + 1][2], "%d-%m-%Y %H:%M:%S")
            timeadd = contime2 - contime1
            timeadd = (timeadd.days * 24 * 3600 + timeadd.seconds) / 60
            if timeadd < 2.5:
                changeFlag = True
                break
        # print(data[con_num[bbb] + 1])
    # while 1 :
    #     i = 0
    # print(changeFlag)
    ## 确定什么时候改
    if changeFlag:
        for aaa in dealnum:
            for i in range(1, len(data[con_num[aaa] + 1])):
                if data[con_num[aaa] + 1][i] == "":
                    break
                con = datetime.datetime.strptime(data[con_num[aaa] + 1][i], "%d-%m-%Y %H:%M:%S")
                # print(con)
                con = con + datetime.timedelta(minutes=shijiancha)
                con = con.timetuple()
                # print(type(time.strftime('%d-%m-%Y', con)))
                # date[i+2] = str(con.tm_mday) + "-" + str(con.tm_mon) + "-" + str(con.tm_year)
                data[con_num[aaa] + 1][i] = time.strftime('%d-%m-%Y %H:%M:%S', con)

    interval1, cdate = timestump(timelist)
    # 加标注
    for i in interval1:
        timestumplist.append(i)
    for i in cdate:
        con = datetime.datetime.strptime(date[i + 2], "%d-%m-%Y").date()
        con = con + datetime.timedelta(days=1)
        con = con.timetuple()
        date[i + 2] = time.strftime('%d-%m-%Y', con)

    deallist.append(date)
    deallist.append(timestumplist)

    interval1 = ["glucose_level"]
    for i in list1[1]:
        if i != "":
            interval1.append(i)
    deallist.append(interval1)
    # output:["" "标题"  “正值”]
    # deallist = dealsame1(deallist)
    # 插值
    deallist1 = buchong1(deallist)

    deallist1 = cmp_add_two(deallist[0][2:], deallist[1][2:], deallist1, constant[0], deallist[2][1:])

    # new
    for i in con_num[:-1]:
        interval1, timestumptp1 = dealdate(data[i + 1])
        deallist1 = reset0(interval1, timestumptp1, deallist1)

    #
    # '''
    #         处理两列数据
    #         :param data:
    #         :return:
    #         '''
    # con2
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    # print(list1[0])
    cmpalso(list1[0])

    interval1, timestumptp = dealdate(list1[0])
    # print(interval1)
    # print(timestumptp)
    deallist2 = reset0(interval1, timestumptp, deallist1)  # dao这都对
    # for i in deallist1:
    #     print(i)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist2 = cmp_add_two(interval1, timestumptp, deallist2, constant[1], list1[1])
    # print("con2")

    '''
                处理三列数据
            '''

    # con3 = con2
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    # for i in list1:
    #     print(i)
    interval1, timestumptp1 = dealdate(list1[0])
    # print(interval1)
    # print(len(interval1))
    # print(len(timestumptp1))
    # deallist3 = reset0(interval1, timestumptp1, deallist2)
    # for i in deallist3:
    #     print(i)
    # while 1 :
    #     i = 0
    interval2 = interval1[1:]
    timestumptp2 = timestumptp1[1:]
    # deallist3 = reset0(interval2, timestumptp2, deallist3)

    interval11, timestumptp11, value11 = buchongbasal(interval1, timestumptp1, interval2, timestumptp2, list1[1])
    # deallist1 = add_pre(interval11, timestumptp11, deallist1)
    # print(interval11)
    # print(timestumptp11)
    # print(value11)
    # deallist3 = reset0(interval11, timestumptp11, deallist2)
    # print("con3")

    # con4 = con7
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 3:
        for i in range(3 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    # for i in list1:
    #     print(i)
    interval1, timestumptp1 = dealdate(list1[0])
    interval2, timestumptp2 = dealdate(list1[1])
    # print(interval1)
    # print(interval2)
    # print(list1[2])
    # print(interval1)
    # print(timestumptp1)
    # deallist1 = add_pre(interval1, timestumptp1, deallist1)
    # deallist1 = add_pre(interval2, timestumptp2, deallist1)
    if len(interval1) != 0:
        interval12, timestumptp12, value12 = buchongbasal(interval1, timestumptp1, interval2, timestumptp2, list1[2])
        # deallist3 = reset0(interval12, timestumptp12, deallist3)
        interval11, timestumptp11, value11 = hebingbasal(interval11, timestumptp11, interval12, timestumptp12, value11,
                                                         value12)
    # print(interval11)
    # print(timestumptp12)
    # print(value12)
    # while 1 :
    #     io = 0
    # print(interval11)
    # print(timestumptp11)
    deallist3 = reset0(interval11, timestumptp11, deallist2)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist3 = cmp_add_two(interval11, timestumptp11, deallist3, constant[2], value11)
    # print("con4")

    # con5
    '''
        如果是时间点，就插值
        如果是时间段，取平均值
    '''
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 5:
        for i in range(5 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    interval1, timestumptp1 = dealdate(list1[0])
    interval2, timestumptp2 = dealdate(list1[1])

    interval11, timestumptp, typel, lis1, lis2 = dealbolus(interval1, timestumptp1, interval2, timestumptp2, list1[2],
                                                           list1[3], list1[4])
    deallist4 = reset0(interval11, timestumptp, deallist3)

    # print(lis1)
    # while 1:
    #     i = 0
    lis1 = sum_1(interval11, timestumptp, lis1)
    lis2 = sum_1(interval11, timestumptp, lis2)
    # for i in deallist4:
    #     print(i)
    # deallist1 = add_pre(interval11, timestumptp, deallist1)
    deallist4 = cmp_add_two(interval11, timestumptp, deallist4, constant[4], typel)
    deallist4 = cmp_add_two(interval11, timestumptp, deallist4, constant[4], lis1)
    deallist4 = cmp_add_two(interval11, timestumptp, deallist4, constant[4], lis2)
    # print("con5")

    # con6
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 3:
        for i in range(3 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    # print(interval1)
    # print(timestumptp)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist5 = reset0(interval1, timestumptp, deallist4)
    deallist5 = cmp_add_two(interval1, timestumptp, deallist5, constant[5], list1[1])
    deallist5 = cmp_add_two(interval1, timestumptp, deallist5, constant[5], list1[2])
    # print("con6")

    # con7 sleep
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 3:
        for i in range(3 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    # for i in list1:
    #     print(i)
    interval1, timestumptp1 = dealdate(list1[0])
    interval2, timestumptp2 = dealdate(list1[1])
    # print(interval1)
    # print(timestumptp1)
    # deallist1 = add_pre(interval1, timestumptp1, deallist1)
    # deallist1 = add_pre(interval2, timestumptp2, deallist1)
    interval1, timestumptp, value1 = buchongsleep(interval2, timestumptp2, interval1, timestumptp1, list1[2])
    deallist6 = reset0(interval1, timestumptp, deallist5)
    deallist6 = cmp_add_two(interval1, timestumptp, deallist6, constant[6], value1)
    # print("con7")

    # con8 = con7
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 3:
        for i in range(3 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    # for i in list1:
    #     print(i)
    interval1, timestumptp1 = dealdate(list1[0])
    interval2, timestumptp2 = dealdate(list1[1])
    # print(interval1)
    # print(timestumptp1)
    # deallist1 = add_pre(interval1, timestumptp1, deallist1)
    # deallist1 = add_pre(interval2, timestumptp2, deallist1)
    interval1, timestumptp, value1 = buchongsleep(interval1, timestumptp1, interval2, timestumptp2, list1[2])
    deallist7 = reset0(interval1, timestumptp, deallist6)
    deallist7 = cmp_add_two(interval1, timestumptp, deallist7, constant[7], value1)
    # print("con8")

    # con9 = con6
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 3:
        for i in range(3 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    # print(interval1)
    # print(timestumptp)
    deallist8 = reset0(interval1, timestumptp, deallist7)
    for i in range(len(interval1)):
        list1[1][i + 1] = 1
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist8 = cmp_add_two(interval1, timestumptp, deallist8, constant[8], list1[1])
    deallist8 = cmp_add_two(interval1, timestumptp, deallist8, constant[8], list1[2])
    # print("con9")

    # con10 = con2
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    # print(interval1)
    # print(timestumptp)
    deallist9 = reset0(interval1, timestumptp, deallist8)
    for i in range(len(interval1)):
        list1[1][i + 1] = 1

        # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist9 = cmp_add_two(interval1, timestumptp, deallist9, constant[9], list1[1])
    # print("con10")

    # con11 = con7 ??
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 4:
        for i in range(4 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    # for i in list1:
    #     print(i)
    interval1, timestumptp1 = dealdate(list1[0])
    interval2, timestumptp2 = dealdate(list1[1])
    # print(interval1)
    # print(timestumptp1)
    # deallist1 = add_pre(interval1, timestumptp1, deallist1)
    # deallist1 = add_pre(interval2, timestumptp2, deallist1)
    shuzhi = len(interval1) - len(interval2)
    for i in range(shuzhi):
        interval2.append("")
        timestumptp2.append("")
    interval11, timestumptp, value1 = buchongsleep(interval1, timestumptp1, interval2, timestumptp2, list1[2])
    interval11, timestumptp, value2 = buchongsleep(interval1, timestumptp1, interval2, timestumptp2, list1[3])
    # print(interval11)
    # print(timestumptp)
    # print(value1)
    deallist10 = reset0(interval11, timestumptp, deallist9)
    for i in range(len(interval1)):
        value1[i + 1] = 1
    deallist10 = cmp_add_two(interval11, timestumptp, deallist10, constant[10], value1)
    deallist10 = cmp_add_two(interval11, timestumptp, deallist10, constant[10], value2)
    # print("con11")

    # con12 = con6
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 5:
        for i in range(5 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    deallist11 = reset0(interval1, timestumptp, deallist10)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    # print(interval1)
    # print(timestumptp)
    deallist11 = cmp_add_two(interval1, timestumptp, deallist11, constant[11], list1[1])
    deallist11 = cmp_add_two(interval1, timestumptp, deallist11, constant[11], list1[2])
    deallist11 = cmp_add_two(interval1, timestumptp, deallist11, constant[11], list1[3])
    deallist11 = cmp_add_two(interval1, timestumptp, deallist11, constant[11], list1[4])
    # print("con12")

    # con13
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    ## 求重复的平均值 未加  拉同一时间的值求平均
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    # print(interval1)
    # print(timestumptp)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist12 = reset0(interval1, timestumptp, deallist11)
    # print("1")
    value00 = avg_1(interval1, timestumptp, list1[1])
    # print(value00)
    deallist12 = cmp_add_two(interval1, timestumptp, deallist12, constant[12], value00)
    # print("con13")

    # con14 = con13
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    ## 求重复的平均值 未加  拉同一时间的值求平均
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    # print(interval1)
    # print(timestumptp)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist13 = reset0(interval1, timestumptp, deallist12)
    # print("1")
    value00 = avg_1(interval1, timestumptp, list1[1])
    # print(value00)
    deallist13 = cmp_add_two(interval1, timestumptp, deallist13, constant[13], value00)
    # print("con14")

    # con15 = con13
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    ## 求重复的平均值 未加  拉同一时间的值求平均
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    # print(interval1)
    # print(timestumptp)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    deallist14 = reset0(interval1, timestumptp, deallist13)
    value00 = avg_1(interval1, timestumptp, list1[1])
    deallist14 = cmp_add_two(interval1, timestumptp, deallist14, constant[14], value00)
    # print("con15")

    # con16 = con13
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    ## 求重复的平均值 未加  拉同一时间的值求平均
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    deallist15 = reset0(interval1, timestumptp, deallist14)
    # print(interval1)
    # print(timestumptp)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    # value00 = avg_1(interval1, timestumptp, list1[1])
    deallist15 = cmp_add_two(interval1, timestumptp, deallist15, constant[15], list1[1])
    # print("con16")

    # for i in deallist15:
    #     print(i)

    # con17 = con13
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    ## 求重复的平均值 未加  拉同一时间的值求平均
    # for i in list1:
    #     print(i)
    interval1, timestumptp = dealdate(list1[0])
    deallist16 = reset0(interval1, timestumptp, deallist15)
    # print(interval1)
    # print(timestumptp)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    value00 = sum_1(interval1, timestumptp, list1[1])
    deallist16 = cmp_add_two(interval1, timestumptp, deallist16, constant[16], value00)
    # print("con17")

    # con18 = con11
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 4:
        for i in range(4 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    # for i in list1:
    #     print(i)
    interval1, timestumptp1 = dealdate(list1[0])
    interval2, timestumptp2 = dealdate(list1[1])
    # print(interval1)
    # print(timestumptp1)
    # deallist1 = add_pre(interval1, timestumptp1, deallist1)
    # deallist1 = add_pre(interval2, timestumptp2, deallist1)
    interval11, timestumptp, value1 = buchongsleep(interval1, timestumptp1, interval2, timestumptp2, list1[2])
    interval11, timestumptp, value2 = buchongsleep(interval1, timestumptp1, interval2, timestumptp2, list1[3])
    deallist17 = reset0(interval11, timestumptp, deallist16)
    deallist17 = cmp_add_two(interval11, timestumptp, deallist17, constant[17], value1)
    deallist17 = cmp_add_two(interval11, timestumptp, deallist17, constant[17], value2)
    # print("con18")

    # con19 = con2
    list1 = data[(con_num[con_num_local - 1] + 1):con_num[con_num_local]]
    if con_num[con_num_local] - (con_num[con_num_local - 1] + 1) != 2:
        for i in range(2 - (con_num[con_num_local] - (con_num[con_num_local - 1] + 1))):
            zanzhu = []
            for j in range(len(list1[0])):
                zanzhu.append("")
            list1.append(zanzhu)
    con_num_local += 1
    cmpalso(list1[0])
    interval1, timestumptp = dealdate(list1[0])
    deallist18 = reset0(interval1, timestumptp, deallist17)
    # print(interval1)
    # print(timestumptp)
    # deallist1 = add_pre(interval1, timestumptp, deallist1)
    value00 = avg_1(interval1, timestumptp, list1[1])
    deallist18 = cmp_add_two(interval1, timestumptp, deallist18, constant[18], value00)
    # print("con19")

    for i in range(len(deallist18)):
        if deallist18[i][0] == "hypo_event":
            for j in range(len(deallist18[i])):
                if deallist18[i][j] == "":
                    deallist18[i][j] = 0
        elif (deallist18[i][0] == "stressors") & (deallist18[i - 1][0] != "stressors"):
            deallist18[i][1] = "type"
            deallist18[i + 1][1] = "description"
            for j in range(len(deallist18[i])):
                if deallist18[i][j] == "":
                    deallist18[i][j] = 0
        elif (deallist18[i][0] == "illness") & (deallist18[i - 1][0] != "illness"):
            deallist18[i][1] = "type"
            deallist18[i + 1][1] = "description"
            for j in range(len(deallist18[i])):
                if deallist18[i][j] == "":
                    deallist18[i][j] = 0
    # for i in range(2,len(deallist1)):
    #     deallist1[i][1] = deallist1[i][0] + "_" + deallist1[i][1]
    for i in range(len(deallist18)):
        deallist18[i].remove(deallist18[i][0])

    deallist18[2][0] = "glucose_level_value"

    deallist18[3][0] = "finger_stick_value"

    deallist18[4][0] = "basal_value"

    deallist18[5][0] = "bolus_type"
    deallist18[6][0] = "bolus_dose"

    deallist18[7][0] = "bolus_bwz_carb_input"

    deallist18[8][0] = "meal_type"

    deallist18[9][0] = "meal_carbs"
    # elif i == 10:
    deallist18[10][0] = "sleep_quality"
    # elif i == 11:
    deallist18[11][0] = "work_intensity"
    # elif i == 12:
    deallist18[12][0] = "stressors_type"
    # elif i == 13:
    deallist18[13][0] = "stressors_description"
    # elif i == 14:
    deallist18[14][0] = "hypo_event_name"
    # elif i == 15:
    deallist18[15][0] = "illness_type"
    # elif i == 16:
    deallist18[16][0] = "illness_description "
    # elif i == 17:
    deallist18[17][0] = "exercise_intensity"
    # elif i == 18:
    deallist18[18][0] = "exercise_type"
    # elif i == 19:
    deallist18[19][0] = "exercise_duration"
    # elif i == 20:
    deallist18[20][0] = "exercise_competitive"
    # elif i == 21:
    deallist18[21][0] = "basis_heart_rate_value"
    # elif i == 22:
    deallist18[22][0] = "basis_gsr_value "
    # elif i == 23:
    deallist18[23][0] = "basis_skin_temperature_value "
    # elif i == 24:
    deallist18[24][0] = "basis_air_temperature_value "
    # elif i == 25:
    deallist18[25][0] = "basis_steps_value"
    # elif i == 26:
    deallist18[26][0] = "basis_sleep_quality"
    # elif i == 27:
    deallist18[27][0] = "basis_sleep_type"
    # elif i == 28:
    deallist18[28][0] = "acceleration_value"

    return deallist18


def data_alignment(filePath):
    print('1.Data alignment:', filePath)
    filename = os.path.basename(filePath)
    global con_num
    if filename == '540-test.xlsx':
        con_num = [2, 5, 8, 12, 17, 21, 23, 25, 27, 29, 31, 33, 35, 38, 41, 43, 45, 50, 53]
    elif filename == '544-test.xlsx' or filename == '552-test.xlsx' or filename == '567-test.xlsx' or filename == '584-test.xlsx' or filename == '596-test.xlsx':
        con_num = [2, 5, 8, 12, 17, 21, 25, 29, 31, 34, 36, 42, 44, 47, 50, 52, 54, 59, 62]
    else:
        con_num = [2, 5, 8, 12, 17, 21, 25, 29, 33, 36, 41, 47, 49, 52, 55, 57, 59, 64, 67]

    # 标题属性
    global constant
    constant = ["glucose_level", "finger_stick", "basal", "temp_basal", "bolus", "meal", "sleep", "work",
                "stressors",
                "hypo_event", "illness", "exercise", "basis_heart_rate", "basis_gsr", "basis_skin_temperature",
                "basis_air_temperature", "basis_steps", "basis_sleep", "acceleration"]
    savefilepath = filePath + ".csv"
    if os.path.exists(savefilepath):
        print("The data alignment CSV file already exists.")
        return savefilepath
    else:
        data = read_excel(filePath)
        outdata = dealser(data)
        enddata = []
        for i in range(len(outdata[0])):
            list2 = []
            for j in range(len(outdata)):
                list2.append(outdata[j][i])
            enddata.append(list2)
        data2 = pd.DataFrame(columns=enddata[0], data=enddata[1:])
        data2.to_csv(savefilepath, index=0)
        print("Save CSV file to:", savefilepath)
        return savefilepath
