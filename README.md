# Taiko ML Chart Simplifier (TCS) 🥁

A project to automatically create easified versions of fan-based Taiko no Tatsujin charts, a.k.a. .tja files

## 🚀 Overview

For .tja files lacking easier difficulties, TCS can predict Easy, Normal and Hard chart. TCS will find the closest difficulty to Easy, and generate all difficulties to bridge the gap.

According to Easy, Normal and Hard difficulties, TCS will:
  - Adjust note density
  - Predict simplified patterns
  - while keeping notes in rhythm with the music!

The output .tja file will contain the original chart used for predictions, and all predicted chart(s).

## 📦 Installation

Download Taiko-san Daijiro 3. [iOS App Store link](https://apps.apple.com/us/app/taiko-san-daijiro-3/id1183008625), [Android Google Play link](https://play.google.com/store/apps/details?id=com.daijiro.taiko3).

#### Code setup
- Clone the repository
  - https: `git clone https://github.com/kclkoichi/taiko-ml-chart-simplifier.git`
  - ssh: `git clone git@github.com:kclkoichi/taiko-ml-chart-simplifier.git`

#### Conda environment setup
- Download Anaconda Navigator [(link to download)](https://www.anaconda.com/products/navigator)
- Open the app
- Go to Environments
- Click on Import
- Click on the folder icon next to Import from Local drive
- Pick taiko-ml.yaml from the cloned repository
- Set new environment name to `taiko-ml` (or any name that suits you)
- Click Import
- The conda environment setup is done!

## 🤔 How to generate charts

These instructions assume you opened a terminal at the root folder of the project.

- Run `conda activate taiko-ml` (or any other env name you chose)

The environment has to be activated any time you want to make predictions.

Run the command:
- python3 taiko_predict.py 
With arguments:
- -input (or -i) path_to_tja_file_to_simplify
  - Mandatory
- -output (or -o) path_to_output_folder
  - Optional: Default is prediction/out

Example Usage (with sample song): `python3 taiko_predict.py -i "prediction/in/Kyokuken.tja"`  
Note: Paths may be relative from the root folder of TCS!

## 🎮 How to play

Once your new .tja file is generated:
- Find it. It will be in prediction/out by default, otherwise it is in the folder you specified
- Compress it to a .zip file together with the song's .ogg file
  - song_name.tja and song_name.ogg must match (more precisely, must match WAVE:file_name.ogg parameter of the .tja file)
  - Note: .mp4 are also supported 
- Rename zip file to song_name.zip
- Share to device
  - I use AirDrop or Google Drive with my iPad
- On the device, select the .zip file and share it to Taiko-san Daijiro 3
  - See screenshots below for help on iPad

<img src="instruction_img/share1.jpg?raw=true" alt="Share" width="200"/> <img src="instruction_img/share2.jpg?raw=true" alt="Share" width="200"/>

Then, the game will automatically process the song.  
By default, your song will be in the "Uncategorized" folder!  
Enjoy playing!!!

## ⚙️ How to train or use your own models

`python3 taiko_predict.py` calls tf.keras.models.load_model on .h5 files in models/.  
⚠️ It is your responsibility to ensure that the .h5 prediction model you load is not malicious!  
✅ The original included ones are safe for use.

2 main scripts to train the model:
- `python3 taiko_make_datasets.py`
  - Makes datasets from all .tja files found recursively in raw_data/. Saves in datasets/
  - The idea is to put all songs you want to use to train your model in raw_data/
  - Note: This will overwrite the original datasets/Easy.npy and so on for each difficulty
- `python3 taiko_make_model_and_train.py`
  - Creates models and trains them using datasets/Easy.npy and so on
  - Note: This will overwrite the original models/oni_to_hard_model.h5 and so on for each difficulty

2 scripts to help craft your dataset:
- `python3 src/analysis/choose_songs.py`
  - Finding all .tja files in songs/ recursively, it will paste the filename of .tja files meeting requirements to src/analysis/valid_charts.txt
  - Requirements are specified in variables in `choose_songs.py`
- `python3 taiko_get_rawdata_from_songs.py`
  - Finding all .tja files in songs/ recursively, if the filename appears in src/analysis/valid_charts.txt, then the .tja is copied to raw_data/

## Package versions:
python: 3.11.5  
tensorflow: 2.12.0  
chardet: 5.2.0  
(for more details look at taiko-ml.yaml)
