
import torch
from PIL import Image
from torchvision import models, transforms


# Создаём нейросеть ResNet18
model = models.resnet18(weights=None)

# Настраиваем три выходных коэффициента
model.fc = torch.nn.Sequential(
    torch.nn.Linear(model.fc.in_features, 1)
)

# Загружаем обученную модель друга
model.load_state_dict(
    torch.load("best_model.pt", map_location="cpu", weights_only=True)
)

# Режим анализа, а не обучения
model.eval()


# Подготовка фотографии
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# Функция анализа фотографии
def analyze_photo(filename):
    image = Image.open(filename).convert("RGB")
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        result = model(image)

    return result.item()
