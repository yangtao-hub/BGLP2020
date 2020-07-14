import os
import keras

def train(model, x_train, y_train, x_valid, y_valid, batch_size, epochs,
        patience, shuffle, artifacts_path,PID,nb_future_steps):
    history = model.fit(
        x_train,
        y_train,
        validation_data = (x_valid, y_valid),
        epochs          = epochs,
        batch_size      = batch_size,
        shuffle         = shuffle,
        verbose=0,
        callbacks       = [
            keras.callbacks.EarlyStopping(
                monitor  = 'val_loss',
                patience = patience,
                mode     = 'min'
            ),
            keras.callbacks.TensorBoard(
                log_dir=artifacts_path
            ),
            keras.callbacks.ModelCheckpoint(
                filepath       = os.path.join(artifacts_path, "{}-model-{}.hdf5".format(PID,nb_future_steps)),
                monitor        = 'val_loss',
                mode           = 'min',
                save_best_only = True,
                period         = 1
            )
        ]
    )
    print("training successful")
    weights_path = os.path.join(artifacts_path, "{}-model-{}.hdf5".format(PID,nb_future_steps))
    print("saving weights: {}".format(weights_path))
    return model
