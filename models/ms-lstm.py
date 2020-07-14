from keras.models import Input, Model
from keras.layers import Dense, CuDNNLSTM, Dropout, Lambda, Reshape, Concatenate


def load(cfg):
    past_steps = list(cfg['dataset']['past_steps'])
    del past_steps[1]
    attributions = list(cfg['dataset']['attributions'])
    out_dim = int(past_steps[0] / 3)
    this_index = 0
    index = [this_index]
    for past_step in past_steps:
        this_index += past_step
        index.append(this_index)
    input_all = Input(name='input_all', shape=(sum(past_steps), 2))
    for i in range(len(past_steps)):
        if attributions[i] == 'glucose_level_value':
            feature_all = Lambda(lambda x: x[:, index[i + 1] - out_dim:index[i + 1], 1])(input_all)
            assert feature_all.shape[1] == out_dim
            feature_all = Reshape((-1, 1))(feature_all)
            locals()["feature" + str(i) + "scale2"] = Lambda(
                lambda x: x[:, index[i + 1] - 2 * out_dim + 1:index[i + 1]:2, 1])(input_all)
            assert locals()["feature" + str(i) + "scale2"].shape[1] == out_dim
            locals()["feature" + str(i) + "scale2"] = Reshape((-1, 1))(locals()["feature" + str(i) + "scale2"])
            locals()["feature" + str(i) + "scale2"] = CuDNNLSTM(units=out_dim)(locals()["feature" + str(i) + "scale2"])
            locals()["feature" + str(i) + "scale2"] = Reshape((-1, 1))(locals()["feature" + str(i) + "scale2"])
            locals()["feature" + str(i) + "scale3"] = Lambda(
                lambda x: x[:, index[i + 1] - 3 * out_dim + 2:index[i + 1]:3, 1])(input_all)
            assert locals()["feature" + str(i) + "scale3"].shape[1] == out_dim
            locals()["feature" + str(i) + "scale3"] = Reshape((-1, 1))(locals()["feature" + str(i) + "scale3"])
            locals()["feature" + str(i) + "scale3"] = CuDNNLSTM(units=out_dim)(
                locals()["feature" + str(i) + "scale3"])
            locals()["feature" + str(i) + "scale3"] = Reshape((-1, 1))(locals()["feature" + str(i) + "scale3"])
            locals()["feature" + str(i) + "scaleall"] = Concatenate(axis=2)(
                [locals()["feature" + str(i) + "scale2"], locals()["feature" + str(i) + "scale3"]])
            locals()["feature" + str(i) + "scaleall"] = CuDNNLSTM(units=out_dim)(
                locals()["feature" + str(i) + "scaleall"])
            locals()["feature" + str(i) + "scaleall"] = Reshape((-1, 1))(locals()["feature" + str(i) + "scaleall"])

            feature_all = Concatenate(axis=2)([feature_all, locals()["feature" + str(i) + "scaleall"]])
        else:
            locals()["feature" + str(i)] = Lambda(lambda x: x[:, index[i]:index[i + 1], :])(input_all)
            assert locals()["feature" + str(i)].shape[1] == past_steps[i]
            for m in range(int(past_steps[i] / 3), past_steps[i] + 1, int(past_steps[i] / 3)):
                locals()["feature" + str(i) + str(m)] = Lambda(lambda x: x[:, past_steps[i] - m:past_steps[i], :])(
                    locals()["feature" + str(i)])
                locals()["feature" + str(i) + str(m)] = Reshape((-1, 2))(locals()["feature" + str(i) + str(m)])
                locals()["feature" + str(i) + str(m)] = CuDNNLSTM(units=out_dim)(locals()["feature" + str(i) + str(m)])
                locals()["feature" + str(i) + str(m)] = Reshape((-1, 1))(locals()["feature" + str(i) + str(m)])
                if m == int(past_steps[i] / 3):
                    locals()["feature" + str(i) + "all"] = locals()["feature" + str(i) + str(m)]
                else:
                    locals()["feature" + str(i) + "all"] = Concatenate(axis=2)(
                        [locals()["feature" + str(i) + "all"], locals()["feature" + str(i) + str(m)]])
            locals()["feature" + str(i) + "all"] = CuDNNLSTM(units=out_dim)(locals()["feature" + str(i) + "all"])
            locals()["feature" + str(i) + "all"] = Reshape((-1, 1))(locals()["feature" + str(i) + "all"])
            feature_all = Concatenate(axis=2)([feature_all, locals()["feature" + str(i) + "all"]])
    feature_all = CuDNNLSTM(units=256)(feature_all)
    feature_all = Dense(units=256, activation='relu')(feature_all)
    feature_all = Dropout(rate=0.2)(feature_all)
    feature_all = Dense(units=64, activation='relu')(feature_all)
    feature_all = Dropout(rate=0.1)(feature_all)
    output = Dense(units=1)(feature_all)
    model = Model(inputs=[input_all], outputs=[output])
    return model
