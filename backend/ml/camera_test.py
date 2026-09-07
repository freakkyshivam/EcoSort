"""Use a trained EcoSort checkpoint with a PC webcam.

python camera_test.py --checkpoint outputs/ecosort_convnext_tiny_best.pt
Controls: Q/Esc quits; S saves the current test frame.
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

import cv2
import torch
from PIL import Image

from Brain import DEFAULT_CONFIDENCE_THRESHOLD, get_device, load_model, make_transforms


def predict_frame(frame, model, classes, transform, device):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    tensor = transform(image).unsqueeze(0).to(device)
    if device.type == "cuda":
        tensor = tensor.contiguous(memory_format=torch.channels_last)
    with torch.inference_mode(), torch.autocast(device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"):
        probabilities = model(tensor).softmax(1)[0]
    confidence, index = probabilities.max(0)
    return classes[index.item()], confidence.item()


def main():
    parser = argparse.ArgumentParser(description="Test an EcoSort model with a PC webcam")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD)
    parser.add_argument("--interval", type=float, default=0.25)
    parser.add_argument("--snapshots-dir", default="snapshots")
    args = parser.parse_args()
    device = get_device(); model, classes, checkpoint = load_model(Path(args.checkpoint), device)
    _, transform = make_transforms(checkpoint["config"]["image_size"])
    print(f"Model ready on {device}. Classes: {', '.join(classes)}")
    camera = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not camera.isOpened(): raise RuntimeError(f"Could not open camera {args.camera}. Try --camera 1.")
    label, confidence, last = "Waiting for camera…", 0.0, 0.0
    try:
        while True:
            ok, frame = camera.read()
            if not ok: raise RuntimeError("Could not read a camera frame.")
            if time.monotonic() - last >= args.interval:
                label, confidence = predict_frame(frame, model, classes, transform, device); last = time.monotonic()
            accepted = confidence >= args.threshold
            text = f"{label}: {confidence:.1%}" if accepted else f"RETRY / DON'T SORT: {label} ({confidence:.1%})"
            color = (45, 190, 45) if accepted else (30, 30, 235)
            cv2.rectangle(frame, (8, 8), (min(frame.shape[1] - 8, 650), 58), (20, 20, 20), -1)
            cv2.putText(frame, text, (18, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
            cv2.putText(frame, "Q/Esc: quit | S: save frame", (18, frame.shape[0] - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow("EcoSort Camera Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27): break
            if key == ord("s"):
                folder = Path(args.snapshots_dir); folder.mkdir(parents=True, exist_ok=True)
                path = folder / f"waste_{datetime.now():%Y%m%d_%H%M%S}.jpg"; cv2.imwrite(str(path), frame); print(f"Saved {path}")
    finally:
        camera.release(); cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
