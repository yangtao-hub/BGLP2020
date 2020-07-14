import pandas as pd
import numpy as np
import copy
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, WhiteKernel, DotProduct
import time


def gpr_1step(train_path, test_path):
    print('2.CGM outlier detection:', train_path)
    print('2.CGM outlier detection:', test_path)
    # trainfile_path---The path to the fil and the file extension is CSV
    # testfile_path---The path to the fil and the file extension is CSV
    print('GPR method is being used to detect outliers. The detection time is too long. Please wait patiently.')
    features = pd.read_csv(train_path)
    features_end = copy.deepcopy(features)
    features_test = pd.read_csv(test_path)
    features_test_end = copy.deepcopy(features_test)

    glucose_level_list = features['glucose_level_value'].tolist()
    time_list_end = features['timestamp'].tolist()
    date_list_end = features['date'].tolist()

    label_train_study = []
    for i in glucose_level_list:
        label_train_study.append(0)
    label_train_end = label_train_study.copy()
    upper_train_end = label_train_study.copy()
    lower_train_end = label_train_study.copy()
    for i in range(len(glucose_level_list)):
        if np.isnan(glucose_level_list[i]):
            continue
        else:
            startnan = i
            break
    for i in range(len(glucose_level_list) - 1, 0, -1):
        if np.isnan(glucose_level_list[i]):
            continue
        else:
            endnan = i
            break
    blanknum = 0
    for i in range(startnan + 1, endnan + 1):
        if np.isnan(glucose_level_list[i]):
            blanknum += 1
        if (np.isnan(glucose_level_list[i - 1])) & (np.isnan(glucose_level_list[i]) == False):
            for j in range(6):
                if i + j < endnan + 1:
                    label_train_study[i + j] = 1
            blanknum = 0
    features['label_train_study'] = label_train_study
    glucose_level_list = features_test['glucose_level_value'].tolist()
    time_list_test_end = features_test['timestamp'].tolist()
    date_list_test_end = features_test['date'].tolist()

    label_test_study = []
    for i in glucose_level_list:
        label_test_study.append(0)
    label_test_end = label_test_study.copy()
    upper_test_end = label_test_study.copy()
    lower_test_end = label_test_study.copy()
    for i in range(len(glucose_level_list)):
        if np.isnan(glucose_level_list[i]):
            continue
        else:
            startnan = i
            break
    for i in range(len(glucose_level_list) - 1, 0, -1):
        if np.isnan(glucose_level_list[i]):
            continue
        else:
            endnan = i
            break
    blanknum = 0
    for i in range(startnan + 1, endnan + 1):
        if np.isnan(glucose_level_list[i]):
            blanknum += 1
        if (np.isnan(glucose_level_list[i - 1])) & (np.isnan(glucose_level_list[i]) == False):
            for j in range(6):
                if i + j < endnan + 1:
                    label_test_study[i + j] = 1
            blanknum = 0

    features_test['label_test_study'] = label_test_study

    features.dropna(subset=['glucose_level_value'], inplace=True)
    features_test.dropna(subset=['glucose_level_value'], inplace=True)

    features_list1 = features['glucose_level_value'].tolist()
    time_list = features['timestamp'].tolist()
    date_list = features['date'].tolist()

    label_train_study = features['label_train_study'].tolist()

    minum = 6
    gl_train_list = []
    gl_train_value_list = []
    time_truth = []
    date_truth = []
    for i in range(minum, len(features_list1)):
        interca1 = []
        if label_train_study[i] == 0:
            for j in range(1, minum + 1):
                interca1.append(features_list1[i - j])

            gl_train_list.append(interca1)
            gl_train_value_list.append(features_list1[i])
            time_truth.append(time_list[i])
            date_truth.append(date_list[i])

    train_fea = gl_train_list[:289]
    train_label = gl_train_value_list[:289]
    test_fea = gl_train_list[289:]
    test_label = gl_train_value_list[289:]
    time_truth = time_truth[289:]
    date_truth = date_truth[289:]

    kernel = ConstantKernel() * DotProduct() + WhiteKernel()
    reg = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, optimizer="fmin_l_bfgs_b")
    reg.fit(np.array(train_fea), np.array(train_label))
    predictions_online = []
    error = []
    del_detail = []
    con_error = 0
    total_error = 0
    for connum in range(len(test_fea)):
        test_test_features = [test_fea[connum]]
        if connum % 48 == 0:
            reg.fit(np.array(train_fea), np.array(train_label))
        predictions, std = reg.predict(test_test_features, return_std=True)
        predictions_online.append(predictions[0])
        uppernum = predictions[0] + 4.5 * std[0]
        lowernum = predictions[0] - 4.5 * std[0]
        if test_label[connum] > uppernum or test_label[connum] < lowernum:
            if con_error == 0:
                # print(date_truth[connum], time_truth[connum])
                del_detail.append([date_truth[connum], time_truth[connum], connum, uppernum, lowernum])
                total_error += 1
                con_error = 6
        if con_error == 0:
            error.append(abs(test_label[connum] - predictions[0]))
            train_fea.append(test_fea[connum])
            train_label.append(test_label[connum])
            del train_fea[0]
            del train_label[0]
        else:
            con_error -= 1

    for i in range(len(del_detail)):
        for time1 in range(len(time_list_end)):
            if del_detail[i][1] == time_list_end[time1] and del_detail[i][0] == date_list_end[time1]:
                label_train_end[time1] = -1
                upper_train_end[time1] = del_detail[i][-2]
                lower_train_end[time1] = del_detail[i][-1]
                break
        else:
            print("No match. There's a problem with the program！！")
    features_end["outliers"] = label_train_end
    features_end["upper"] = upper_train_end
    features_end["lower"] = lower_train_end
    print('{} outliers were detected in the training set.'.format(total_error))
    features_test_list1 = features_test['glucose_level_value'].tolist()
    time_test_list = features_test['timestamp'].tolist()
    date_test_list = features_test['date'].tolist()
    label_test_study = features_test['label_test_study'].tolist()

    gl_test_list = []
    gl_test_value_list = []
    time_test_truth = []
    date_test_truth = []
    for i in range(minum, len(features_test_list1)):
        interca1 = []
        if label_test_study[i] == 0:
            for j in range(1, minum + 1):
                interca1.append(features_test_list1[i - j])

            gl_test_list.append(interca1)
            gl_test_value_list.append(features_test_list1[i])
            time_test_truth.append(time_test_list[i])
            date_test_truth.append(date_test_list[i])

    predictions_online = []
    error = []
    del_detail = []
    con_error = 0
    total_error = 0
    for connum in range(len(gl_test_list)):
        test_test_features = [gl_test_list[connum]]
        if connum % 48 == 0:
            reg.fit(np.array(train_fea), np.array(train_label))
        predictions, std = reg.predict(test_test_features, return_std=True)
        predictions_online.append(predictions[0])
        uppernum = predictions[0] + 4.5 * std[0]
        lowernum = predictions[0] - 4.5 * std[0]
        if gl_test_value_list[connum] > uppernum or gl_test_value_list[connum] < lowernum:
            if con_error == 0:
                del_detail.append([date_test_truth[connum], time_test_truth[connum], connum, uppernum, lowernum])

                total_error += 1
                con_error = 6
        if con_error == 0:
            error.append(abs(gl_test_value_list[connum] - predictions[0]))
            train_fea.append(gl_test_list[connum])
            train_label.append(gl_test_value_list[connum])
            del train_fea[0]
            del train_label[0]
        else:
            con_error -= 1

    for i in range(len(del_detail)):
        for time1 in range(len(time_list_test_end)):
            if del_detail[i][1] == time_list_test_end[time1] and del_detail[i][0] == date_list_test_end[time1]:
                label_test_end[time1] = -1
                upper_test_end[time1] = del_detail[i][-2]
                lower_test_end[time1] = del_detail[i][-1]
                break
        else:
            print("No match. There's a problem with the program！！")
    print('{} outliers were detected in the test set.'.format(total_error))
    features_test_end["outliers"] = label_test_end
    features_test_end["upper"] = upper_test_end
    features_test_end["lower"] = lower_test_end
    return features_end, features_test_end
