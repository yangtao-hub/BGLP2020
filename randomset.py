def random_set(seed_value):
    print('set random seed:', seed_value)

    # 1. Set `PYTHONHASHSEED` environment variable at a fixed value
    import os
    os.environ['PYTHONHASHSEED'] = str(seed_value)
    # 忽悠警告信息
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # 2. Set `python` built-in pseudo-random generator at a fixed value
    import random
    random.seed(seed_value)

    # 3. Set `numpy` pseudo-random generator at a fixed value
    import numpy as np
    np.random.seed(seed_value)

    # 4. Set `tensorflow` pseudo-random generator at a fixed value
    import tensorflow as tf
    tf.reset_default_graph()
    tf.set_random_seed(seed_value)

    # 5. Configure a new global `tensorflow` session
    from keras import backend as K
    session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
    sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
    K.set_session(sess)

    # 6.GPU多线程训练的随机性，需要1.14.0以上的tf版本
    # import tensorflow as tf
    # import os
    # os.environ['TF_DETERMINISTIC_OPS'] = '1'
    # from tfdeterminism import patch
    # patch()
