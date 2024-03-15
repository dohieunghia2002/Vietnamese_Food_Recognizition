from ultralytics import YOLO

model = YOLO("yolov8x.pt")

# CLI statement
# !yolo task=detect mode=train model=yolov8x.pt data=/content/drive/MyDrive/Computer_Vision/NLN/demo/dataset_food/cfg.yaml epochs=28