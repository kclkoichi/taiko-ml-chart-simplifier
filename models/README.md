Storing all models as .h5 files
First letter is to be able to maintain chronological order, using ascii values
(excludes super early ones trained on a few lines written by myself) 

Edit 2025/03/23: New discovery.
Not sure models made with Tensorflow 2.18 can work with tensorflow 2.12.
Seems like models made with Tensorflow 2.12 cannot work with tensorflow 2.18...?

Decision taken 2025/03/24:
Will keep using my environment with Tensorflow 2.12.
Too much of a waste of time to try to move to 2.18, also causing Keras to go from v2 to v3.
AND also have to get rid of Tokenizer (deprecated) for TextVectorization...
AND models made with tf2.12 can't be loaded easily with tf2.18... already lost a few hours which is too much