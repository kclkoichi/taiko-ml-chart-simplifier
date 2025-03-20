import os
from src.make_model_and_train.chartSimplificationModel import ChartSimplificationModel

# Change directory to script file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Paths to directory 
datasets_path = os.path.join("datasets")
models_path = os.path.join("models")
tokenizer_path = os.path.join(models_path, "tokenizer.json")

chart_model = ChartSimplificationModel(datasets_path, models_path, tokenizer_path)
chart_model.train_all_models()
