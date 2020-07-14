#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run an experiment."""
import logging
import os
import yaml
import importlib.util
import itertools
import math
import gc
import metrics
import numpy as np
from keras import backend as K
import randomset
import copy


def train(model, module_train, x_train, y_train, x_valid, y_valid, cfg):
    model = module_train.train(
        model=model,
        x_train=x_train,
        y_train=y_train,
        x_valid=x_valid,
        y_valid=y_valid,
        batch_size=int(cfg['train']['batch_size']),
        epochs=int(cfg['train']['epochs']),
        patience=int(cfg['train']['patience']),
        shuffle=cfg['train']['shuffle'],
        artifacts_path=cfg['train']['artifacts_path'],
        PID=os.path.basename(cfg['dataset']['train_path']).split('-')[0],
        nb_future_steps=cfg['dataset']['future_steps']
    )

    return model


def load_module(script_path):
    spec = importlib.util.spec_from_file_location("module.name", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_cfg(yaml_filepath):
    """
    Load a YAML configuration file.

    Parameters
    ----------
    yaml_filepath : str

    Returns
    -------
    cfg : dict
    """
    # Read YAML experiment definition file
    with open(yaml_filepath, 'r') as stream:
        cfg = yaml.load(stream)
    cfg = make_paths_absolute(os.path.dirname(yaml_filepath), cfg)
    return cfg


def load_cfgs(yaml_filepath):
    """
    Load YAML configuration files.

    Parameters
    ----------
    yaml_filepath : str

    Returns
    -------
    cfgs : [dict]
    """
    # Read YAML experiment definition file
    with open(yaml_filepath, 'r') as stream:
        cfg = yaml.load(stream, Loader=yaml.FullLoader)
    # print(yaml_filepath)
    cfg = make_paths_absolute(os.path.dirname(yaml_filepath), cfg)
    hyperparameters = []
    hyperparameter_names = []
    hyperparameter_values = []
    # TODO: ugly, should handle arbitrary depth
    for k1 in cfg.keys():
        for k2 in cfg[k1].keys():
            if k2.startswith("param_"):
                hyperparameters.append((k1, k2))
                hyperparameter_names.append((k1, k2[6:]))
                hyperparameter_values.append(cfg[k1][k2])

    hyperparameter_valuess = itertools.product(*hyperparameter_values)

    artifacts_path = cfg['train']['artifacts_path']

    cfgs = []
    for hyperparameter_values in hyperparameter_valuess:
        configuration_name = ""
        for ((k1, k2), value) in zip(hyperparameter_names, hyperparameter_values):
            # print(k1, k2, value)
            cfg[k1][k2] = value
            configuration_name += "{}_{}_".format(k2, str(value))

        cfg['train']['artifacts_path'] = os.path.join(artifacts_path, configuration_name)

        cfgs.append(copy.deepcopy(cfg))

    return cfgs


def make_paths_absolute(dir_, cfg):
    """
    Make all values for keys ending with `_path` absolute to dir_.

    Parameters
    ----------
    dir_ : str
    cfg : dict

    Returns
    -------
    cfg : dict
    """
    dir_ = dir_.split('/')[0]
    for key in cfg.keys():
        if key.endswith("_path"):
            cfg[key] = os.path.join(dir_, cfg[key])
            cfg[key] = os.path.abspath(cfg[key])
            if not os.path.exists(cfg[key]):
                # logging.error("%s does not exist.", cfg[key])
                pass
        if type(cfg[key]) is dict:
            cfg[key] = make_paths_absolute(dir_, cfg[key])
    return cfg


def get_parser():
    """Get parser object."""
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--file",
                        dest="filename",
                        help="experiment definition file",
                        metavar="FILE",
                        required=True)
    parser.add_argument("-m", "--mode",
                        dest="mode",
                        help="mode of run",
                        metavar="FILE",
                        required=True)
    return parser


def evaluate(model, x_test, y_test, cfg):
    PID = os.path.basename(cfg['dataset']['train_path']).split('-')[0]
    nb_future_steps = cfg['dataset']['future_steps']
    # load the trained weights
    weights_path = os.path.join(cfg['train']['artifacts_path'], "{}-model-{}.hdf5".format(PID, nb_future_steps))
    print("loading weights: {}".format(weights_path))
    model.load_weights(weights_path)
    y_pred = model.predict(x_test)[:, 0].flatten() * 100
    y_pred[y_pred > 400] = 400
    y_pred[y_pred < 40] = 40
    # The prediction results are post-processing to remove some values that do not need to be predicted
    print('The prediction results are post-processing to remove some values that do not need to be predicted.')
    y_pred, y_test = y_pre_handle(y_pred, y_test, cfg)
    print("y_pred.shape:", y_pred.shape)
    print("y_test.shape:", y_pred.shape)
    rmse = metrics.root_mean_squared_error(y_test, y_pred)
    mae = metrics.mean_absolute_error(y_test, y_pred)
    return [rmse, mae]


def y_pre_handle(y_pre, y_test, cfg):
    y_test = y_test.flatten()
    y_pre_copy = copy.deepcopy(y_pre)
    assert y_pre.shape == y_test.shape
    # 找到标签为0的值，这些值不需要计算指标
    zero_index = list(np.where(y_test == 0)[0])
    # 对y_test中不能用模型进行预测的值进行处理
    # 找到每段缺失的最后一个0值的索引
    del_index = []
    for i in range(1, len(zero_index)):
        if zero_index[i] - zero_index[i - 1] == 1:
            del_index.append(zero_index[i - 1])
    for index in del_index:
        zero_index.remove(index)
    # 排除没有用到未来值的索引
    threshold = 12
    del_index = []
    for one_zero in zero_index:
        if y_test[one_zero - threshold + 1] != 0:
            del_index.append(one_zero)
    for index in del_index:
        zero_index.remove(index)
    # 不能用模型进行预测的缺失段最后一个0的索引
    # 通过该索引算预测值
    future_steps = cfg['dataset']['future_steps']
    for index in zero_index:
        for i in range(1, future_steps + 1):
            y_pre[index + i] = pred_weight(index, y_test, future_steps, i)
        # 用最开始一个保持
        y_pre[index + future_steps + 1] = y_test[index + 1]
    # 找到标签为0的值，这些值不需要计算指标
    zero_index = list(np.where(y_test == 0)[0])
    y_test = np.delete(y_test, zero_index)
    y_pre = np.delete(y_pre, zero_index)
    return y_pre, y_test


def pred_weight(index, y_test, future_steps, point):
    p = copy.deepcopy(point)
    p2 = copy.deepcopy(point)
    for i in range(index - 1, 0, -1):
        p = p + 1
        if y_test[i] != 0:
            D = y_test[i]
            break
    y_test_split = y_test[0:index]
    if len(y_test_split) >= 288 + 1:
        for m in range(1, math.floor(len(y_test_split) / 288.0) + 1):
            E = 0
            index_start = index + p2 - 288 * m
            # print("定位坐标：",index_start)
            if y_test_split[index_start] == 0:
                # print("该坐标指向0，向后寻找6个坐标")
                for findindex in range(1, 7):
                    if y_test_split[index_start + findindex] != 0:
                        index_start = index_start + findindex
                        # print("找到新坐标", index_start)
                        break
                    # print("没有找到新坐标，到288前")
            if y_test_split[index_start] != 0:
                # 前后取12个不为0 的点
                num = []
                n = 0
                # 向前取
                while True:
                    n = n + 1
                    if index_start - n < 0:
                        break
                    if y_test_split[index_start - n] != 0:
                        num.append(y_test_split[index_start - n])
                        if len(num) >= 1:
                            break
                # 向后取
                n = 0
                while True:
                    n = n + 1
                    if index_start + n >= len(y_test_split):
                        break
                    if y_test_split[index_start + n] != 0:
                        num.append(y_test_split[index_start + n])
                        if len(num) >= 1 * 2:
                            break
                num.append(y_test_split[index_start])
                E = np.mean(num)
                if E != 0:
                    break
    else:
        zero_index_split = list(np.where(y_test_split == 0)[0])
        y_test_split = np.delete(y_test_split, zero_index_split)
        E = y_test_split.mean()
    fct = p / (p + 68)
    return (1 - fct) * D + fct * E


def main(yaml_filepath, mode, PID):
    """Run experiments."""
    cfgs = load_cfgs(yaml_filepath)
    for cfg in cfgs:
        module_dataset = load_module(cfg['dataset']['script_path'])
        module_model = load_module(cfg['model']['script_path'])
        module_optimizer = load_module(cfg['optimizer']['script_path'])
        module_loss_function = load_module(cfg['loss_function']['script_path'])
        module_train = load_module(cfg['train']['script_path'])

        # Set the training file and test file paths.
        cfg['dataset']['train_path'] = os.path.join(os.path.dirname(cfg['dataset']['train_path']),
                                                    '{}-train.xlsx'.format(PID))
        cfg['dataset']['test_path'] = os.path.join(os.path.dirname(cfg['dataset']['test_path']),
                                                   '{}-test.xlsx'.format(PID))
        print("Training file path:", cfg['dataset']['train_path'])
        print("Testing file path:", cfg['dataset']['test_path'])
        print("The current task: predict the blood glucose level of subject {} in the next {} steps".format(
            PID, cfg['dataset']['future_steps']))

        # Loading the dataset
        print("*****************Loading dataset*****************")
        # Set random seeds for GPR model
        seed = int(cfg['train']['seed'])
        # randomset.random_set(seed)
        x_train, y_train, x_valid, y_valid, x_test, y_test = module_dataset.load_dataset(cfg['dataset'])
        print("x_train.shape: ", x_train.shape)
        print("y_train.shape: ", y_train.shape)
        print("x_valid.shape: ", x_valid.shape)
        print("y_valid.shape: ", y_valid.shape)
        print("x_test.shape: ", x_test.shape)
        print("y_test.shape: ", y_test.shape)

        # Loading the model
        print("*****************Loading model*****************")
        # Set random seeds for model training
        randomset.random_set(seed)
        optimizer = module_optimizer.load(cfg['optimizer'])
        loss_function = module_loss_function.load()

        locals()["model" + str(PID)] = module_model.load(
            cfg
        )
        locals()["model" + str(PID)].compile(
            optimizer=optimizer,
            loss=loss_function
        )
        if mode == 'train_evaluate':
            # Training model
            print("*****************Training model*****************")
            locals()["model" + str(PID)] = train(locals()["model" + str(PID)], module_train, x_train, y_train, x_valid,
                                                 y_valid, cfg)
            # Evaluating model
            print("*****************Evaluating model*****************")
            results = evaluate(locals()["model" + str(PID)], x_test, y_test, cfg)
            print('The evaluation results is ', results)
        elif mode == 'train':
            # Training model
            print("*****************Training model*****************")
            locals()["model" + str(PID)] = train(locals()["model" + str(PID)], module_train, x_train, y_train, x_valid,
                                                 y_valid, cfg)
        elif mode == 'evaluate':
            # Evaluating model
            print("*****************Evaluating model*****************")
            results = evaluate(locals()["model" + str(PID)], x_test, y_test, cfg)
            print('The evaluation results is ', results)
        else:
            print("Unknown command")
        # Reset the calculation diagram and clear the variables
        K.clear_session()
        for x in list(locals().keys()):
            if x != "results":
                del locals()[x]
        gc.collect()
    return results


if __name__ == '__main__':
    Results = []
    PIDS = [540, 544, 552, 567, 584, 596]
    for PID in PIDS:
        filename = 'experiments/train_6.yaml'
        mode = 'train_evaluate'
        results = main(filename, mode, PID)
        Results.append(results)
        print("Evaluation list:", Results)
    Results = []
    PIDS = [540, 544, 552, 567, 584, 596]
    for PID in PIDS:
        filename = 'experiments/train_12.yaml'
        mode = 'train_evaluate'
        results = main(filename, mode, PID)
        Results.append(results)
        print("Evaluation list:", Results)
