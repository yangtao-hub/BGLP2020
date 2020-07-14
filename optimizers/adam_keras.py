import keras

def load(cfg):
    learning_rate = float(cfg['learning_rate'])
    decay = float(cfg['decay'])
    return keras.optimizers.Adam(lr=learning_rate, decay=decay)
