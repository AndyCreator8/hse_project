import pandas as pd
from PIL import Image
import os
from abc import abstractmethod
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
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
    def get_item(self, filename):
        ...


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
            self.samples.append((self.transforms(img), normilized_rating))
            self.size += 1

    def __getitem__(self, key):
        return self.samples[key]

    def __len__(self):
        return self.size

    

class LearningMachine:
    def __init__(self, device: str, train_dataset: Dataset, valid_dataset: Dataset, batch_size=32):
        self.batch_size = batch_size
        self.device = torch.device(device)
        self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        self.model = self.model.to(self.device)
        in_features = self.model.fc.in_features
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-4, weight_decay=1e-4)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=20)
        self.model.fc = nn.Sequential(
            nn.Linear(in_features, 1),
            nn.Sigmoid()
        )
        self.train_dataset = train_dataset
        self.valid_dataset = valid_dataset
        self.train_data_loader = DataLoader(
            self.train_dataset,
            self.batch_size,
            shuffle=True
        )
        self.valid_data_loader = DataLoader(
            self.valid_dataset,
            self.batch_size,
            shuffle=False
        )

    def train(self):
        self.model.to(self.device)
        self.model.train()
        running = 0
        for imgs, results in tqdm(self.train_data_loader):
            imgs, results = imgs.to(self.device), results.to(self.device).unsqueeze(1)
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
            running, mae = 0.0, 0.0
            for imgs, targets in self.valid_data_loader:
                imgs, targets = imgs.to(self.device), targets.to(self.device).unsqueeze(1)
                preds = self.model(imgs)
                running += self.criterion(preds, targets).item() * imgs.size(0)
                mae += (preds - targets).abs().sum().item()
            n = len(self.valid_dataset)
            return running / n, mae / n


def main():
    train_tfms = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.2, 0.2, 0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    val_tfms = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    csvdata = CsvDatasetManager("dataset.csv")
    device = torch.device("cuda")
    train_dataset = Dataset("dataset/training", csvdata, train_tfms)
    valid_dataset = Dataset("dataset/validation", csvdata, val_tfms)
    batch_size = 32
    Lm = LearningMachine(device, train_dataset, valid_dataset, batch_size=batch_size)
    epochs = 50
    best_val_mae = float("inf")
    best_model_path = "best_model.pt"
    last_model_path = "last_model.pt"
    for epoch in range(epochs):
        train_loss = Lm.train()
        eval_loss, eval_mae_normalized = Lm.evaluate()
        eval_mae_real = eval_mae_normalized * 4 + 1
        Lm.scheduler.step()

        print(f"EPOCH: {epoch} | train MSE {train_loss} | "
              f"eval MSE {eval_loss} | eval MAE {eval_mae_real}")

        if eval_mae_real < best_val_mae:
            best_val_mae = eval_mae_real
            torch.save(Lm.model.state_dict(), best_model_path)
            print(
                f"saved best model (val MSE={eval_loss:.4f}  val MAE={eval_mae_real:.3f})"
            )

    torch.save(Lm.model.state_dict(), last_model_path)
    print(f"saved last model (train MSE={train_loss:.4f} val MAE={eval_mae_real:.4f})")




if __name__ == "__main__":
    main()
