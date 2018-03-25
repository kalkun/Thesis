
# coding: utf-8

# # UCLA Results Validation
# 
# This notebook is aimed at attemping to validate the results achieved by UCLA in their paper

# In[1]:


from protestDB import cursor
import time
from protestDB import models
from lib import analysis_utils as au
import pandas as pd
import os
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
import scipy
from keras import models as Kmodels
from keras import backend as Kbackend
from keras import applications as Kapplications
from keras import layers as Klayers
from keras import callbacks as Kcallbacks
from keras import optimizers as Koptimizers
from keras import losses as Klosses
import h5py


# ### Loading up the data

# In[2]:


pc = cursor.ProtestCursor()
imgs = pc.getLabelledImages(source="UCLA")
len(imgs)


# Get the labels

# In[3]:



cols = ["name", "label", "protest"]
tag_cols = ["sign", "photo", "fire", "police", "children", "group_20", "group_100", "flag", "night", "shouting"]
split_tags = ['ucla-test', 'ucla-train']
imgs = imgs[cols + tag_cols + split_tags]
indx_non_violence = imgs['label'].isnull()

imgs.loc[:,tag_cols] = imgs.loc[:,tag_cols].astype(int)
imgs = imgs.rename(columns={"label": "violence"})
imgs


# ### Pre-processing

# In[4]:


# Apply a cut point and normalize violence scores
cutpoint = 0.43

#clips
imgs = au.clipDFColumn(imgs, 'violence', cutpoint)

# normalize
imgs = au.minMax(imgs, 'violence')

# mask values that did not had violence labels
imgs.loc[indx_non_violence, "violence"] = -1
# df.loc[indx_non_violence, 'violence'] = -1

# masks the visual attributes that where image is not a protest
# for column, value in df.iloc[:,3:].iteritems(): # fill visual attributes with masking
#     df.loc[pd.isnull(df['protest']), column] = -1
imgs.loc[indx_non_violence, tag_cols[1:]] = -1
    
# fill nas
# df.fillna(0, inplace = True)

# df = imgs.rename(columns={"label": "violence"})
df = imgs
df


# In[5]:


i = df['violence'].idxmax()
df.loc[i]


# Get the images

# In[6]:


batch_size = 32

# df = df.rename(columns={"label": "violence"})

train_idx = df['ucla-train']
train = df.loc[train_idx, ["name", "violence", "protest"] + tag_cols]

test_idx = df['ucla-test']
test = df.loc[test_idx, ["name", "violence", "protest"] + tag_cols]

# ...and as UCLA used their test set also for validation:
val = test

# size in percentage of the various splits:
# test_size = .2
# val_size = .2
# train_size = .6

# train, val, test = au.getSplits(df, train_size, val_size, test_size)
print("{} rows split into train: {}, validation: {}, and test: {}".format(len(df), len(train), len(val), len(test)))
train


# In[7]:


dummy_test_generator = au.ResizeSequence(df[np.random.randint(10):np.random.randint(20, 30)], batch_size, 
                                         targets = ['protest', 'violence', tag_cols])
train_generator = au.ResizeSequence(train, batch_size, 
                                    targets = ['protest', 'violence', tag_cols])
validation_generator = au.ResizeSequence(val, batch_size, 
                                         targets = ['protest', 'violence', tag_cols])
test_generator = au.ResizeSequence(test, 1, 
                                   targets = ['protest', 'violence', tag_cols])

test_visual = test[tag_cols]
test_violence = test['violence'] 
test_protest = test['protest']


# In[8]:


# test generator
first = dummy_test_generator.__getitem__(0)
image = first[0][0]
protest = first[1][0]
violence = first[1][1]
visual = first[1][2]
# img = scipy.misc.toimage(image)
# plt.imshow(img)
print("protest has shape", protest.shape, " violence has shape", violence.shape, " visual has shape", visual.shape)


# Select training and validation sets

# ### Modeling

# In[9]:


mask_value = -1
Kbackend.clear_session()


# In[10]:


img_input = Klayers.Input(shape=(224,224,3), name='img_input')

resnet_model = Kapplications.ResNet50(include_top=False, weights = 'imagenet') (img_input)

flatten = Klayers.Flatten()(resnet_model)

protest_out = Klayers.Dense(1, activation='sigmoid', name='protest_out')(flatten)
violence_out = Klayers.Dense(1, activation='sigmoid', name='violence_out')(flatten)
visual_out = Klayers.Dense(10, activation='sigmoid', name='visual_out')(flatten)

model = Kmodels.Model(inputs= img_input, outputs=[protest_out, violence_out, visual_out])




# In[11]:


lr = 0.01; momentum = 0.9; epochs = 1000; patience = 15


# In[12]:


optimizer = Koptimizers.SGD(lr=lr, momentum=momentum, nesterov=False)
model.compile(optimizer='rmsprop',
              loss={'protest_out': Klosses.binary_crossentropy,
                    'visual_out': au.buildMaskedLoss(Klosses.binary_crossentropy, mask_value), 
                    'violence_out': au.buildMaskedLoss(Klosses.mean_squared_error, mask_value)},
              loss_weights={'protest_out': 1., 
                            'visual_out': 5, 
                            'violence_out': 10 })
model.summary()


# In[13]:


model_checkout_path = "models/UCLA_validation.hdf5"
csv_logger_path = "logs/UCLA_validation_log.csv"
log_dir="logs/{}".format(time.time())

# callbacks
change_lr = Kcallbacks.LearningRateScheduler(au.lrUpdateUCLA, 
                                            verbose = True)

checkpoint = Kcallbacks.ModelCheckpoint(model_checkout_path,
                                       monitor='val_loss', 
                                       verbose=1,
                                       save_best_only=True,
                                       save_weights_only=False,
                                       mode='auto',
                                       period=1)

# Disable for now:
# earlystop = Kcallbacks.EarlyStopping(monitor='val_loss',
#                                     min_delta=0, 
#                                     patience=patience,
#                                     verbose=1, 
#                                     mode='auto')

tensor_board = Kcallbacks.TensorBoard(log_dir='logs/',
                                     histogram_freq=0,
                                     batch_size=32, 
                                     write_graph=True,
                                     write_grads=False, 
                                     write_images=False, 
                                     embeddings_freq=0,
                                     embeddings_layer_names=None,
                                     embeddings_metadata=None)

csv_logger = Kcallbacks.CSVLogger(csv_logger_path, 
                                 separator=',', 
                                 append=False)


# In[14]:


history = model.fit_generator(
    train_generator,
    validation_data= validation_generator,
    epochs=epochs,
    callbacks = [change_lr, checkpoint, tensor_board, csv_logger])


# ### Test set evaluation

# In[15]:


preds = model.predict_generator(test_generator)
preds_protest = preds[0]
preds_violence = preds[1]
preds_visual = preds[2]
print("protest shape is ", preds_protest.shape, " violence shape is ", preds_violence.shape, "visual shape is ", preds_visual)


# ### Protest

# In[16]:


au.plotROC("protest", test_protest, preds_protest, save_as="logs/ROC_protest.png")


# ### Visual

# In[22]:


for i in range(preds_visual.shape[1]):
    pred = preds_visual[:,i]
    target = test_visual.iloc[:,i]
    
    # remove masked values from test set
    target_non_masked = target[target!= -1]
    pred_non_masked = pred[target!= -1]
    
    attr_indx = 3 + i # the visual attributes start from the 4th pos
    attr = df.columns[attr_indx]
    print(attr)
    try:
        au.plotROC(attr, target_non_masked, pred_non_masked, save_as="logs//ROC_{}.png".format(i))
    except Exception as e:
        print(e)


# ### Violence

# In[23]:


# remove masked values from test set
non_masked_violence_true = test_violence[test_violence!= -1].tolist()
non_masked_violence_preds = preds_violence[test_violence!= -1].flatten().tolist()


# In[25]:


fig, ax = plt.subplots()
plt.scatter(non_masked_violence_true, non_masked_violence_preds, label = "violence")
plt.xlim([-.05,1.05])
plt.ylim([-.05,1.05])
plt.xlabel('Annotation', fontsize = 15)
plt.ylabel('Predicton', fontsize = 15)
corr, pval = scipy.stats.pearsonr(non_masked_violence_true, non_masked_violence_preds)
plt.title(('Scatter Plot for {attr} (Correlation = {corr:.3f})'
            .format(attr = "violence", corr= corr)), fontsize = 15)
plt.savefig("logs/pred_vs_truth_scatter.png")

