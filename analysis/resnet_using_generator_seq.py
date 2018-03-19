#!/usr/bin/env python3
################################################################################
#                                                                              #
#                                                                              #
#                    Attempt at the UCLA reproduction it uses                  #
#                    an intsance of Sequence generator, to resize              #
#                    resize images on the fly.                                 #
#                                                                              #
#                                                                              #
################################################################################
import os
import imageio
import numpy as np
import pandas as pd
from skimage.transform import resize
from keras.models import Model
from keras import backend as K
from keras.applications import ResNet50
from keras.layers import Dense, Input, Flatten
from keras.preprocessing.image import ImageDataGenerator

from lib.analysis_utils import ResizeSequence
from protestDB import cursor as protest_cursor, models as protest_models

pc         = protest_cursor.ProtestCursor()

#TODO: Include tags into the query/dataframe:
imgs_query = pc.query(
        protest_models.Images.name,
        protest_models.Labels.label
    ).filter_by(
        source = "UCLA"
    ).join(
        protest_models.Labels,
        protest_models.Images.imageHASH == protest_models.Labels.imageID
    )

df         = pd.read_sql(imgs_query.statement, pc.session.bind)


image_dir  = "../images/"

# split 80/20:
train_indices = np.random.choice(df.index, int(len(df)*.8), replace=False)

df_training   = df.iloc[train_indices]
df_testing    = df.drop(train_indices)

ucla_gen      = ResizeSequence(df_training, batch_size=10)

# Building the model:
input_layer  = Input(shape=(224,224,3), name='img_input')
resnet_model = ResNet50(include_top=False, weights = None) (input_layer)
flatten = Flatten()(resnet_model)
violence_out = Dense(1, activation='linear', name='violence_out')(flatten)

model = Model(inputs=input_layer, outputs=violence_out)
model.compile(
    optimizer    = 'rmsprop',
    loss         = {'violence_out': 'mean_squared_error'},
    loss_weights = {'violence_out': 1 }
)

model.summary()

### Fit it:
# (Note: we don't need to set `steps_per_epoch` since the
# sequence generator already knows how many batches
# an epoch should have to see the whole set.)
model.fit_generator(ucla_gen, epochs=1, steps_per_epoch=100)

test_gen  = ResizeSequence(df_testing, batch_size=10)

# Score trained model.
scores    = model.evaluate_generator(test_gen, steps=20)
print('Test loss:', scores)
