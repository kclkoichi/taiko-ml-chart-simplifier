Storing all models as .h5 files

Models used for prediction (those in this dir):
- oni_to_hard_model.h5 : E_model_only_4_beats_charts/oni_to_hard_model600epoch128batchsize.h5
- hard_to_normal_model.h5 : D_first_model_trained_with_many_charts/hard_to_normal_model.h5
- normal_to_easy_model.h5 : D_first_model_trained_with_many_charts/normal_to_easy_model.h5

In old_models, first letter of directory is to maintain chronological order, using ascii values
(excludes some super early ones trained on a few lines written by myself) 

### Notes for myself:

Edit 2025/03/23: New discovery.
Not sure models made with Tensorflow 2.18 can work with tensorflow 2.12.
Seems like models made with Tensorflow 2.12 cannot work with tensorflow 2.18...?

Decision taken 2025/03/24:
Will keep using my environment with Tensorflow 2.12.
Too much of a waste of time to try to move to 2.18, also causing Keras to go from v2 to v3.
AND also have to get rid of Tokenizer (deprecated) for TextVectorization...
AND models made with tf2.12 can't be loaded easily with tf2.18... already lost a few hours which is too much