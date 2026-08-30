from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms
from torchvision.models import ConvNeXt_Tiny_Weights, convnext_tiny
from tqdm.auto import tqdm

PROJECT_DIR = Path(__file__).resolve().parent
torch.hub.set_dir(str(PROJECT_DIR / "model_cache"))
IMAGENET_MEAN, IMAGENET_STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
DEFAULT_CONFIDENCE_THRESHOLD = 0.70


@dataclass(frozen=True)
# Training ki basic settings ek jagah store karta hai.
class Config:
    image_size: int = 224
    batch_size: int = 32
    epochs: int = 20
    learning_rate: float = 3e-4
    weight_decay: float = 1e-4
    val_fraction: float = 0.15
    test_fraction: float = 0.15
    seed: int = 42
    num_workers: int = 0


# Dataset ke selected images par transform apply karta hai.
class TransformSubset(Dataset):
    def __init__(self, dataset, indices, transform):
        self.dataset, self.indices, self.transform = dataset, indices, transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        image, label = self.dataset[self.indices[index]]
        return self.transform(image), label


# Same random result ke liye seed set karta hai.
def set_seed(seed):
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# GPU mile to CUDA, warna CPU choose karta hai.
def get_device():
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.set_float32_matmul_precision("high")
        return torch.device("cuda")
    return torch.device("cpu")


# Images ko model ke liye resize aur normalize karta hai.
def make_transforms(image_size):
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.70, 1.0)),
        transforms.RandomHorizontalFlip(), transforms.RandomRotation(12),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.10),
        transforms.ToTensor(), transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    evaluation_transform = transforms.Compose([
        transforms.Resize(round(image_size / 0.875)), transforms.CenterCrop(image_size),
        transforms.ToTensor(), transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    return train_transform, evaluation_transform


# Har class ko train/validation/test mein fairly divide karta hai.
def stratified_split(labels, val_fraction, test_fraction, seed):
    groups = {}
    for index, label in enumerate(labels):
        groups.setdefault(label, []).append(index)
    rng = random.Random(seed)
    train, val, test = [], [], []
    for label, indices in groups.items():
        if len(indices) < 5:
            raise ValueError(f"Class {label} has fewer than 5 images.")
        rng.shuffle(indices)
        n_test, n_val = max(1, round(len(indices) * test_fraction)), max(1, round(len(indices) * val_fraction))
        if len(indices) - n_test - n_val < 1:
            raise ValueError("Not enough images for train/validation/test splits.")
        test += indices[:n_test]
        val += indices[n_test:n_test + n_val]
        train += indices[n_test + n_val:]
    rng.shuffle(train); rng.shuffle(val); rng.shuffle(test)
    return train, val, test


# Dataset load karke training ke DataLoaders banata hai.
def build_loaders(data_dir, config, device):
    print("\n[1/5] Checking dataset folders and loading the labeled image list...")
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Dataset folder not found: {data_dir.resolve()}")
    base = datasets.ImageFolder(data_dir)
    if len(base.classes) < 2:
        raise ValueError("Add at least two class folders with images.")
    print("Classes:", base.classes)
    counts = Counter(base.targets)
    print("Images per class:", {base.classes[i]: count for i, count in counts.items()})
    train_i, val_i, test_i = stratified_split(base.targets, config.val_fraction, config.test_fraction, config.seed)
    print("[2/5] Preparing images: resizing, normalizing, and adding safe random training variations...")
    train_tf, eval_tf = make_transforms(config.image_size)
    options = dict(batch_size=config.batch_size, num_workers=config.num_workers, pin_memory=device.type == "cuda", persistent_workers=config.num_workers > 0)
    loaders = (
        DataLoader(TransformSubset(base, train_i, train_tf), shuffle=True, **options),
        DataLoader(TransformSubset(base, val_i, eval_tf), shuffle=False, **options),
        DataLoader(TransformSubset(base, test_i, eval_tf), shuffle=False, **options),
    )
    print(f"Split sizes — train: {len(train_i)}, validation: {len(val_i)}, test: {len(test_i)}")
    return loaders, base.classes, [base.targets[i] for i in train_i]


# ConvNeXt model ko EcoSort ke classes ke liye ready karta hai.
def build_model(num_classes, device):
    print("[3/5] Loading the pretrained ConvNeXt-Tiny vision model and replacing its final layer for EcoSort classes...")
    model = convnext_tiny(weights=ConvNeXt_Tiny_Weights.DEFAULT)
    model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)
    memory_format = torch.channels_last if device.type == "cuda" else torch.contiguous_format
    return model.to(device, memory_format=memory_format)


# Ek complete training ya validation round chalata hai.
def run_epoch(model, loader, criterion, device, optimizer=None, scaler=None, description="Running"):
    training = optimizer is not None
    model.train(training)
    total_loss = total_correct = total_samples = 0
    preds, labels_all = [], []
    for images, labels in tqdm(loader, desc=description, unit="batch", dynamic_ncols=True):
        images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
        if device.type == "cuda": images = images.contiguous(memory_format=torch.channels_last)
        if training: optimizer.zero_grad(set_to_none=True)
        with torch.set_grad_enabled(training), torch.autocast(device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"):
            logits = model(images)
            loss = criterion(logits, labels)
        if training:
            scaler.scale(loss).backward(); scaler.step(optimizer); scaler.update()
        batch = labels.size(0); predicted = logits.argmax(1)
        total_loss += loss.item() * batch; total_correct += (predicted == labels).sum().item(); total_samples += batch
        preds += predicted.detach().cpu().tolist(); labels_all += labels.detach().cpu().tolist()
    return total_loss / total_samples, total_correct / total_samples, preds, labels_all


# Best model weights aur settings file mein save karta hai.
def save_checkpoint(path, model, class_names, config, val_accuracy):
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"architecture": "convnext_tiny", "model_state_dict": model.state_dict(), "class_names": class_names, "config": asdict(config), "validation_accuracy": val_accuracy}, path)
    print("  New best validation result found — saving the model checkpoint safely.")


# Kaunsi class kis se confuse hui, woh table print karta hai.
def print_confusion_matrix(preds, actual, class_names):
    matrix = torch.zeros((len(class_names), len(class_names)), dtype=torch.int64)
    for truth, prediction in zip(actual, preds): matrix[truth, prediction] += 1
    print("\nConfusion matrix (rows=actual, columns=predicted):")
    print(matrix)


# Pura model training, validation aur final testing control karta hai.
def train(args):
    config = Config(epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.learning_rate, num_workers=args.num_workers, seed=args.seed)
    set_seed(config.seed); device = get_device()
    print(f"Training on: {device}" + (f" ({torch.cuda.get_device_name(0)})" if device.type == "cuda" else ""))
    (train_loader, val_loader, test_loader), classes, train_labels = build_loaders(Path(args.data_dir), config, device)
    model = build_model(len(classes), device)
    counts = torch.bincount(torch.tensor(train_labels), minlength=len(classes)).float()
    weights = (counts.sum() / (len(classes) * counts)).to(device)
    print("Class weights:", {name: round(weights[i].item(), 3) for i, name in enumerate(classes)})
    print("[4/5] Setting up learning: balancing the smaller class, using mixed precision, and preparing the optimizer...")
    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.05)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    output, best = Path(args.output), -1.0
    for epoch in range(1, config.epochs + 1):
        print(f"\n--- Epoch {epoch}/{config.epochs}: learning from training images ---")
        tr_loss, tr_acc, _, _ = run_epoch(model, train_loader, criterion, device, optimizer, scaler, f"Epoch {epoch:02d}/{config.epochs} train")
        print(f"--- Epoch {epoch}/{config.epochs}: checking performance on unseen validation images ---")
        va_loss, va_acc, _, _ = run_epoch(model, val_loader, criterion, device, description=f"Epoch {epoch:02d}/{config.epochs} validate")
        scheduler.step(); print(f"Epoch {epoch:02d}/{config.epochs} | train loss {tr_loss:.4f}, acc {tr_acc:.2%} | val loss {va_loss:.4f}, acc {va_acc:.2%}")
        if va_acc > best:
            best = va_acc; save_checkpoint(output, model, classes, config, va_acc); print(f"  Saved best model: {output}")
    print("\n[5/5] Loading the best saved model and testing it on images it never trained on...")
    checkpoint = torch.load(output, map_location=device, weights_only=False); model.load_state_dict(checkpoint["model_state_dict"])
    loss, acc, preds, actual = run_epoch(model, test_loader, criterion, device, description="Testing")
    print(f"Best validation accuracy: {best:.2%}\nTest loss: {loss:.4f} | Test accuracy: {acc:.2%}"); print_confusion_matrix(preds, actual, classes)


# Saved checkpoint se trained model dobara load karta hai.
def load_model(checkpoint_path, device):
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model = build_model(len(checkpoint["class_names"]), device)
    model.load_state_dict(checkpoint["model_state_dict"]); model.eval()
    return model, checkpoint["class_names"], checkpoint


@torch.inference_mode()
# Ek image ka waste class aur confidence predict karta hai.
def predict(args):
    device = get_device(); model, classes, checkpoint = load_model(Path(args.checkpoint), device)
    _, transform = make_transforms(checkpoint["config"]["image_size"])
    image = Image.open(args.image).convert("RGB"); tensor = transform(image).unsqueeze(0).to(device)
    if device.type == "cuda": tensor = tensor.contiguous(memory_format=torch.channels_last)
    with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"):
        probabilities = model(tensor).softmax(1)[0]
    score, index = probabilities.max(0)
    print(json.dumps({"prediction": classes[index.item()], "confidence": round(score.item(), 4), "should_sort": score.item() >= args.threshold}, indent=2))


# Terminal se diye gaye commands/options read karta hai.
def parse_args():
    parser = argparse.ArgumentParser(description="EcoSort ConvNeXt-Tiny fine-tuning pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    train_p = commands.add_parser("train"); train_p.add_argument("--data-dir", default="data"); train_p.add_argument("--output", default="outputs/ecosort_convnext_tiny_best.pt"); train_p.add_argument("--epochs", type=int, default=20); train_p.add_argument("--batch-size", type=int, default=32); train_p.add_argument("--learning-rate", type=float, default=3e-4); train_p.add_argument("--num-workers", type=int, default=0); train_p.add_argument("--seed", type=int, default=42)
    predict_p = commands.add_parser("predict"); predict_p.add_argument("--checkpoint", required=True); predict_p.add_argument("--image", required=True); predict_p.add_argument("--threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    train(arguments) if arguments.command == "train" else predict(arguments)
