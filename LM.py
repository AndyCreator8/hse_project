import pandas as pd
from PIL import Image
import os
from abc import abstractmethod
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
import torch.optim
import torch
import torch.nn as nn
from tqdm import tqdm


class CsvDataset:
    @abstractmethod
    def __init__(self, path: str):
        self.path = path
        self.data = pd.read_csv(self.path)

    @abstractmethod
    def get_item(self, filename): ...


class CsvDatasetManager(CsvDataset):
    def __init__(self, path):
        self.path = path
        file = pd.read_csv(self.path)
        self.data = dict(zip(file["filename"], file["rating"]))

    def get_item(self, key):
        return self.data[key]


class Dataset:
    def __init__(self, path: str, csvdata: CsvDataset, transforms=None):
        self.samples = []
        self.path = path
        self.csvdata = csvdata
        self.transforms = transforms
        self.size = 0
        for filename in os.listdir(path):
            img = Image.open(f"{self.path}/{filename}").convert("RGB")
            rating = int(self.csvdata.get_item(filename))
            normilized_rating = round(((rating - 1) / 4), 3)
            self.samples.append(
                (
                    self.transforms(img),
                    torch.tensor(normilized_rating, dtype=torch.float32),
                )
            )
            self.size += 1

    def __getitem__(self, key):
        return self.samples[key]

    def __len__(self):
        return self.size

Empty = object
class LearningMachine:
    def __init__(
        self,
        device="mps",
        new=True,
        train_dataset_path=Empty,
        valid_dataset_path=Empty,
        train_trsf=Empty,
        val_trsf=Empty,
        batch_size=32,
        path=Empty
    ):
        self.device = torch.device(device)
        self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        self.model = self.model.to(self.device)
        in_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(in_features, 2)
        )
        
        if new is True:
            self.batch_size = batch_size
            self.criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
            self.optimizer = torch.optim.AdamW(
                self.model.parameters(), lr=1e-4, weight_decay=1e-4
            )
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer, T_max=20
            )
            self.train_dataset = ImageFolder(train_dataset_path, train_trsf)
            self.valid_dataset = ImageFolder(valid_dataset_path, val_trsf)
            self.train_data_loader = DataLoader(
                self.train_dataset, self.batch_size, shuffle=True, num_workers=4, pin_memory=True
            )
            self.valid_data_loader = DataLoader(
                self.valid_dataset, self.batch_size, shuffle=False, num_workers=4, pin_memory=True
            )
            print("Initialising new model")
        else:
            self.model.load_state_dict(torch.load(path, map_location=device))
            self.val_trsf = val_trsf

    def train(self):
        self.model.to(self.device)
        self.model.train()
        running = 0
        for imgs, results in tqdm(self.train_data_loader):
            imgs, results = imgs.to(self.device), results.to(self.device)
            self.optimizer.zero_grad()
            preds = self.model(imgs)
            loss = self.criterion(preds, results)
            loss.backward()
            self.optimizer.step()
            running += loss.item() * imgs.size(0)
        return running / len(self.train_dataset)

    def evaluate(self):
        self.model.to(self.device)
        with torch.no_grad():
            self.model.eval()
            correct, mae = 0.0, 0.0
            for imgs, targets in self.valid_data_loader:
                imgs, targets = (
                    imgs.to(self.device),
                    targets.to(self.device),
                )
                logits = self.model(imgs)
                preds = logits.argmax(dim=1)
                mae += (preds - targets).abs().sum().item()
                correct += (preds == targets).sum().item()

        n = len(self.valid_dataset)
        return mae / n, correct / n

    def predict(self, filename):
        self.model.to(self.device)
        self.model.eval()
        img = Image.open(filename).convert("RGB")
        x = self.val_trsf(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            pred = self.model(x)
        return pred[0].tolist()

train_tfms = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)), # Случайный зум и обрезка
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15), # Легкие наклоны
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2), 
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
val_tfms = transforms.Compose([
    transforms.Resize(256),           # Увеличиваем меньшую сторону до 256 с сохранением пропорций
    transforms.CenterCrop(224),       # Ровно вырезаем квадрат 224x224 из центра
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
def main(d="mps"):
    torch.set_default_dtype(torch.float32)
   
    # csvdata = CsvDatasetManager("dataset.csv")
    device = torch.device(d)
    train_dataset_path = "dataset/training/"
    valid_dataset_path = "dataset/validation/"
    batch_size = 32
    Lm = LearningMachine(
        d,
        True,
        train_dataset_path,
        valid_dataset_path,
        train_tfms,
        val_tfms,
        batch_size=batch_size,
    )
    
    epochs = 20
    best_eval_acc = 0
    best_model_path = "best_model.pt"
    last_model_path = "last_model.pt"
    for epoch in range(epochs):
        train_loss = Lm.train()
        eval_loss, eval_accuracy = Lm.evaluate()
        Lm.scheduler.step()

        print(
            f"EPOCH: {epoch} | train loss {train_loss} | "
            f"eval loss {eval_loss}, eval acc {eval_accuracy}"
        )

        if eval_accuracy > best_eval_acc:
            best_eval_acc = eval_accuracy
            torch.save(Lm.model.state_dict(), best_model_path)
            print(
                f"saved best model (val loss={eval_loss:.4f}  val acc={eval_accuracy:.3f})"
            )

    torch.save(Lm.model.state_dict(), last_model_path)
    print(f"saved last model (train MSE={train_loss:.4f} val acc={eval_accuracy:.4f})")


# def predict(model, val_tmfs, image):
#     model = models.resnet18(weights=None)
#     model.fc = nn.Linear(model.fc.in_features, 2)
#     model.load_state_dict(torch.load("best_model.pt", map_location="mps"))
#     model.eval()
#     img = Image.open(image)
#     x = val_tmfs(img).unsqueeze(0)
#     with torch.no_grad():
#         pred = model(x).argmax(1).item()
#         print(pred)




if __name__ == "__main__":
    main(d="cuda")
    # main(d="mps")




