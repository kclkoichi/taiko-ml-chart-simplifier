# Taiko ML Chart Simplifier (TCS) 🥁

A project to automatically create easified versions of fan-based Taiko no Tatsujin charts, a.k.a. .tja files

## 🚀 Features

For .tja files lacking easier difficulties, TCS will predict Easy, Normal and Hard charts from the Oni chart.  
According to Easy, Normal and Hard, TCS will:
  - Adjust note density
  - Predict simplified patterns

## 🤔 How to generate charts

⚠️ First you need to set up your conda environment!  
⚠️ Instructions in the Installation section.

Run the commands:
- conda activate taiko-ml 
- python3 taiko_predict  
With arguments:
- -input (or -i) path_to_tja_file_to_simplify
  - Mandatory
- -output (or -o) path_to_output_folder
  - Optional: Default is prediction/out

Example Usage (with sample song): `python3 taiko_predict.py -i "prediction/in/Grievous Lady.tja"`  
Paths may be relative from the root folder of TCS!

## 🎮 How to play

Download Taiko-san Daijiro 3. [iOS App Store link](https://apps.apple.com/us/app/taiko-san-daijiro-3/id1183008625), [Android Google Play link](https://play.google.com/store/apps/details?id=com.daijiro.taiko3).

Once your new .tja file is generated, compress it to a .zip file together with the song's .ogg file. Then, share the .zip file to Taiko-san Daijiro 3. The game will automatically process the song. By default, your song will be in the Unnamed folder! Enjoy!

## 📦 Installation

Coming soon. Need Numpy, Tensorflow, Chardet. I use anaconda because it simplifies everything.

~~Install by yourself using:~~
~~`conda install conda-forge::tensorflow`~~
~~`conda install conda-forge::chardet`~~

Load conda environment using taiko-ml.yaml. Code will not work with newest version of Tensorflow available with conda (2.18.0 as of 2025/03/24)

## ⚙️ How to train your own models

3 scripts which can be used:
- taiko_get_rawdata_from_songs
- taiko_make_datasets
- taiko_make_model_and_train

## Versions I use:
python: 3.11.5
tensorflow: 2.12.0
chardet: 5.2.0
(for more details look at taiko-ml.yaml)
