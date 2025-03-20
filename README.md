# Taiko ML Chart Simplifier (TCS) 🥁

A project to automatically create easified versions of fan-based Taiko no Tatsujin charts

(attach image here maybe)

## 🚀 Features

- Predicts simplified patterns for easier gameplay
- Adjusts note density (while preserving song structure (rly?))
- Supports any simplification
  - E.g: Oni -> Easy, Normal -> Easy, Oni -> Hard and so on

## 🤔 How to use

3 commands:
- taiko_make_datasets
- taiko_train
- taiko_simplify

Coming soon. But probably command line tool. Can also attach text to explain in more detail how to use, from pre-processing to training.

## 📦 Installation

Coming soon. Need Numpy, Tensorflow, Chardet. I use anaconda because it simplifies everything.

## Compatible files

TCS can take .tja and .zip files compatible with OpenTaiko and 太鼓さん次郎 (Taiko-san jiro). The output will be of the same format as the input.

## Notes

This project converts note patterns between different difficulty levels using a neural network. Maybe explain more about it here?

## ⚙️ Technical Details
Same as Notes?
- Uses LSTM neural networks for sequence learning
- Enforces valid output lengths (0,1,2,4,8,16,32,48,64)
- Supports character-level tokenization
