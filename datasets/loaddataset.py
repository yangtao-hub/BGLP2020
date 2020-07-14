import copy
import os

import numpy as np
import pandas as pd

import datasets.outlier_detection as outlier
import datasets.missing_CGM_data_filling as missing_CGM
import datasets.data_alignment as data_alignment


def remove_nan_strat_end(df, attr):
    index_start = 0
    index_end = 0
    if attr in list(df):
        for i in range(len(df) - 1):
            if np.isnan(df[attr][i]) == False:
                index_start = i
                break
        for j in range(len(df) - 1, 0, -1):
            if np.isnan(df[attr][j]) == False:
                index_end = j + 1
                break
        df = df[index_start:index_end]
        df = df.reset_index(drop=True)
        return df
    else:
        print('没有该属性，无法删除')
        return 0


def bgcheck(bg):
    for i in range(int(len(bg) * 2 / 3), len(bg)):
        if bg[i] == 0:
            return True
    return False


def gettime(currenttime, num):
    # print(currenttime)
    currenttime = int(currenttime * 100)
    if currenttime > num:
        return np.arange(currenttime - num, currenttime, 1) / 100
    else:
        timeafter = np.arange(1, currenttime, 1)
        timebefore = np.arange(288 - num + currenttime, 288 + 1, 1)
        return np.concatenate((timebefore, timeafter)) / 100


def split_data(xs, train_fraction):
    n = len(xs)
    nb_train = int(np.ceil(train_fraction * n))
    i_end_train = nb_train
    return np.split(xs, [i_end_train])


def load_dataset(cfg):
    x_train, y_train, x_valid, y_valid, x_test, y_test = load_data(cfg)
    return x_train, y_train, x_valid, y_valid, x_test, y_test


def load_data(cfg):
    print("Data preprocessing ...")
    trainpath = cfg['train_path']
    testpath = cfg['test_path']

    # 1.Data alignment
    trainpath = data_alignment.data_alignment(trainpath)
    testpath = data_alignment.data_alignment(testpath)
    cfg['train_path'] = trainpath
    cfg['test_path'] = testpath

    past_steps = list(cfg['past_steps'])
    future_steps = int(cfg['future_steps'])
    train_fraction = float(cfg['train_fraction'])
    attributions = list(cfg['attributions'])
    attr = ['outliers', 'upper', 'lower']
    for i in attr:
        attributions.append(i)

    # 2.The training set and test set were tested for outliers
    traindata, testdata_outlier = outlier.gpr_1step(trainpath, testpath)
    traindata = remove_nan_strat_end(traindata, 'glucose_level_value')
    testdata_outlier = remove_nan_strat_end(testdata_outlier, 'glucose_level_value')
    traindata = traindata[attributions]
    traindata = traindata.fillna(0)
    # 2.The training set was reconstructed with outliers

    index_excepts_list = traindata[traindata['outliers'] == -1].index.tolist()
    for index_except in index_excepts_list:
        excpet_bg_value = traindata.loc[traindata.index[index_except], 'glucose_level_value']
        if excpet_bg_value > traindata['upper'][index_except]:
            traindata.loc[index_except, 'glucose_level_value'] = traindata['upper'][index_except]
        else:
            traindata.loc[index_except, 'glucose_level_value'] = traindata['lower'][index_except]

    with open(testpath, encoding='utf-8') as testfile:
        for i in attr:
            attributions.remove(i)
        testdata = pd.read_csv(testfile, usecols=attributions)
        testdata = testdata[attributions]
        testdata = remove_nan_strat_end(testdata, 'glucose_level_value')
        testdata = testdata.fillna(0)
        bgorg = copy.deepcopy(testdata['glucose_level_value'])

        # 2.filling the CGM data
        testdata['glucose_level_value'] = missing_CGM.filling_CGM(testpath)

        # 3.The testing set was reconstructed with outliers
        index_excepts_list = testdata_outlier[testdata_outlier['outliers'] == -1].index.tolist()
        for index_except in index_excepts_list:
            excpet_bg_value = testdata_outlier.loc[testdata_outlier.index[index_except], 'glucose_level_value']
            if excpet_bg_value > testdata_outlier['upper'][index_except]:
                testdata.loc[index_except, 'glucose_level_value'] = testdata_outlier['upper'][index_except]
            else:
                testdata.loc[index_except, 'glucose_level_value'] = testdata_outlier['lower'][index_except]

    for i in attr:
        # attributions.remove(i)
        traindata = traindata.drop([i], axis=1)
        # testdata = testdata.drop([i], axis=1)
    # 拼接训练集和测试集
    data = pd.concat([traindata, testdata], ignore_index=True)
    data_copy = copy.deepcopy(data)
    print("4.Data normalization")
    for i in range(len(attributions)):
        if past_steps[i] != 0:
            if attributions[i] == 'glucose_level_value':
                data[attributions[i]] = data[attributions[i]].map(lambda x: x / 100)
                traindata[attributions[i]] = traindata[attributions[i]].map(lambda x: x / 100)
            elif attributions[i] == 'timestamp':
                data[attributions[i]] = data[attributions[i]].map(lambda x: x / 100)
                traindata[attributions[i]] = traindata[attributions[i]].map(lambda x: x / 100)
            elif attributions[i] == 'basal_value':
                data[attributions[i]] = data[attributions[i]].map(lambda x: x / 12)
                traindata[attributions[i]] = traindata[attributions[i]].map(lambda x: x / 12)
            elif attributions[i] == 'bolus_dose':
                pass
            elif attributions[i] == 'meal_carbs':
                data[attributions[i]] = data[attributions[i]].map(lambda x: x * 0.1)
                traindata[attributions[i]] = traindata[attributions[i]].map(lambda x: x * 0.1)
    # 生成训练数据
    traindata = np.array(traindata)
    x_train_dataset = np.empty(shape=[0, sum(past_steps) - past_steps[1], 2])
    y_train_dataset = []
    for i in range(past_steps[0], len(traindata) - future_steps + 1, 1):
        # 滑窗取BG
        bg = traindata[i - past_steps[0]:i][:, 0]
        bg_time = traindata[i - past_steps[0]:i][:, 1]
        # 判断bg中是否有0
        if bgcheck(bg) == False:
            # 填补趋势缺失值
            # bg = bginterpolate(bg)
            # 循环获取特征数据
            for m in range(2, len(past_steps)):
                if i >= past_steps[m]:
                    locals()["feature" + str(m)] = traindata[i - past_steps[m]:i][:, m].reshape(-1, 1)
                    locals()["feature" + str(m) + "time"] = traindata[i - past_steps[m]:i][:, 1].reshape(-1, 1)
                    locals()["feature" + str(m)] = np.concatenate(
                        (locals()["feature" + str(m) + "time"], locals()["feature" + str(m)]), axis=1)
                else:
                    locals()["feature" + str(m)] = traindata[0:i][:, m]
                    locals()["feature" + str(m) + "time"] = traindata[0:i][:, 1]

                    locals()["feature" + str(m) + 'brfore'] = [locals()["feature" + str(m)][0]] * (past_steps[m] - i)
                    locals()["feature" + str(m) + 'time_before'] = gettime(locals()["feature" + str(m) + "time"][0],
                                                                           past_steps[m] - i)

                    locals()["feature" + str(m)] = np.concatenate(
                        (locals()["feature" + str(m) + 'brfore'], locals()["feature" + str(m)])).reshape(-1, 1)
                    locals()["feature" + str(m) + "time"] = np.concatenate(
                        (locals()["feature" + str(m) + 'time_before'], locals()["feature" + str(m) + "time"])).reshape(
                        -1, 1)

                    locals()["feature" + str(m)] = np.concatenate(
                        (locals()["feature" + str(m) + "time"], locals()["feature" + str(m)]), axis=1)
                    # print(locals()["feature" + str(m)].shape)
                assert len(locals()["feature" + str(m)]) == past_steps[m]
            # 循环拼接数据
            onedata = np.concatenate((bg_time.reshape(-1, 1), bg.reshape(-1, 1)), axis=1)
            for m in range(2, len(past_steps)):
                onedata = np.concatenate((onedata, locals()["feature" + str(m)]), axis=0)
            onedata = onedata.reshape(-1, 2)
            # 存入x_train
            x_train_dataset = np.append(x_train_dataset, [onedata], axis=0)
            # 将标签存入y_train
            y_train_dataset.append(traindata[i + future_steps - 1][0])
    y_train_dataset = np.array(y_train_dataset).reshape(-1, 1)
    # 找到标签为0的序列
    zero_index = list(np.where(y_train_dataset == 0)[0])
    # 去掉这些输入和标签
    x_train_dataset = np.delete(x_train_dataset, zero_index, axis=0)
    y_train_dataset = np.delete(y_train_dataset, zero_index, axis=0)
    # 划分训练集和验证集
    x_train, x_valid = split_data(x_train_dataset, train_fraction)
    y_train, y_valid = split_data(y_train_dataset, train_fraction)

    # 生成测试数据
    data = np.array(data)
    data_copy = np.array(data_copy)
    x_test_dataset = np.empty(shape=[0, sum(past_steps) - past_steps[1], 2])
    y_test_dataset = []
    for i in range(len(traindata) + 12 - future_steps + 1, len(data) - future_steps + 1, 1):
        # 滑窗取BG
        bg = data[i - past_steps[0]:i][:, 0]
        bg_time = data[i - past_steps[0]:i][:, 1]
        # 判断bg中是否有0
        if bgcheck(bg) == False:
            # 循环获取特征数据
            for m in range(2, len(past_steps)):
                locals()["feature" + str(m)] = data[i - past_steps[m]:i][:, m].reshape(-1, 1)
                locals()["feature" + str(m) + "time"] = data[i - past_steps[m]:i][:, 1].reshape(-1, 1)
                locals()["feature" + str(m)] = np.concatenate(
                    (locals()["feature" + str(m) + "time"], locals()["feature" + str(m)]), axis=1)
                assert len(locals()["feature" + str(m)]) == past_steps[m]
            # 循环拼接数据
            onedata = np.concatenate((bg_time.reshape(-1, 1), bg.reshape(-1, 1)), axis=1)
            for m in range(2, len(past_steps)):
                onedata = np.concatenate((onedata, locals()["feature" + str(m)]), axis=0)
            onedata = onedata.reshape(-1, 2)
            # 存入x_train
            x_test_dataset = np.append(x_test_dataset, [onedata], axis=0)

    x_test = x_test_dataset
    y_test = np.array(bgorg)[12:].reshape(-1, 1)
    # print(x_test.shape,y_test.shape)
    print("Data preprocessing completed")
    return x_train, y_train, x_valid, y_valid, x_test, y_test
