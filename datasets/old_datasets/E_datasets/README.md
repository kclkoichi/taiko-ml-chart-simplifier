Only 4 beats charts. Restrictions on #SCROLL #BPMCHANGE count (apart from a few exceptions)
Can look at src/analysis/to_make_model_E for more info

Unfortunately, many many charts have different line count among difficulties, 
Oni/Edit being the odd one out very very often
Got 8531 lines for each difficulty (88 charts)

If this model doesn't work well, might make:
- Hard -> Normal model
- Normal -> Easy model
together because they are easier to make

And make
- Edit/Oni -> Hard model
separately because making this model is harder
(in terms of prediction and also in terms of preparing the dataset)

Edit: Well, this model did work well. 
Btw Oni.npy in datasets/ is this EditOni.npy. 
Just renamed for easier understanding if someone looks at code for grading project.
