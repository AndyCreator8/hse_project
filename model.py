
import torch
from PIL import Image
from torchvision import models, transforms

from LM import LearningMachine
from LM import val_tfms

device = "cuda"

model = LearningMachine(device, False, val_trsf=val_tfms, path="best_model.pt")
print("Модель готова к предикту")

# Функция анализа фотографии
def analyze_photo(filename):
    preds = model.predict(filename)
    if preds[0] > preds[1]:
        x = preds[0]
        return round(20000 * x - 10000)
    else:
        x = preds[1]
        return -round(20000 * x - 10000)

