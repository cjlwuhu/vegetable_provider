# pip install torch torchvision

import os

import torch
from PIL import Image
from torch import nn
from torchvision import transforms


# 英文类别列表
vegetable_list = [
    'Bean', 'Bitter_Gourd', 'Bottle_Gourd', 'Brinjal', 'Broccoli',
    'Cabbage', 'Capsicum', 'Carrot', 'Cauliflower', 'Cucumber',
    'Papaya', 'Potato', 'Pumpkin', 'Radish', 'Tomato'
]

# 中文类别列表（顺序必须与训练时完全一致）
chinese_names = [
    '豌豆', '苦瓜', '蒲瓜', '茄子', '西兰花',
    '卷心菜', '灯笼椒', '胡萝卜', '花菜', '黄瓜',
    '木瓜', '土豆', '南瓜', '萝卜', '西红柿'
]

n_classes = len(chinese_names)

# 自动选择设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class VegetableCNNModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(3, 100, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(100, 150, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(150, 200, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(200, 200, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(200, 250, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(250, 250, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Flatten(),
            nn.Linear(6250, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(32, n_classes),
        )

    def forward(self, x):
        return self.network(x)


# 统一预处理，避免每次 predict 都重复创建
transform = transforms.Compose([
    transforms.Resize(40),       # resize shortest side
    transforms.CenterCrop(40),   # crop longest side
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# 加载模型
model = VegetableCNNModel()
model_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "model.pth"
    )
)
model.load_state_dict(torch.load(model_path, map_location=device))
model.to(device)
model.eval()


def predict(picture_path, top_k=3):
    image = Image.open(picture_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image_tensor)
        probs = torch.softmax(output, dim=1)

        k = min(top_k, len(chinese_names))
        top_probs, top_indices = torch.topk(probs, k=k, dim=1)

    top_probs = top_probs[0].cpu().tolist()
    top_indices = top_indices[0].cpu().tolist()

    top_k_result = []
    for idx, prob in zip(top_indices, top_probs):
        top_k_result.append({
            "name": chinese_names[idx],
            "probability": round(float(prob), 4)
        })

    if not top_k_result:
        return {
            "category_name": None,
            "confidence": None,
            "top_k": []
        }

    best_result = top_k_result[0]

    return {
        "category_name": best_result["name"],
        "confidence": best_result["probability"],
        "top_k": top_k_result
    }