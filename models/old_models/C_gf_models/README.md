WARNING: Because of setup of library versions (especially TF2.18 on gf machine vs 2.12 on my machine), 
doesn't seem like I can load these models... Even though tried a lot of fixes, none worked.

Changed LSTM to LSTMV1 (using slightly different tensorflow keras library)??
Run on gf's macbook pro
Took like 50min each model

output_dim=64
64 LSTM units
epochs=100, batch_size=32

Trained with game music songs only
With only the songs which had the same number of lines
about 17500 lines for each difficulty

Similar to D_first_model_trained_with_many_songs
But much faster because only 100 epochs
