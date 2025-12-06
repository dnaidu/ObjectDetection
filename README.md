# Person Detection with YOLO11n.pt on NVIDIA RTX 50 Series  

This project demonstrates how to run **YOLO11n.pt** (a pre-trained YOLOv8 model) on an NVIDIA RTX 50-series GPU using Docker. The model will automatically download weights, process a video file, and output detection results to a specified directory.  

---

## 📘 Overview  
- **Model**: `yolo11n.pt` (small YOLOv8 model) https://docs.ultralytics.com/models/  
- **Input**: Video file or RTSP stream  
- **Output**: Annotated video + cropped detection images  
- **GPU**: NVIDIA RTX 50-series (CUDA 13.0 required)  
- **Docker**: Uses NVIDIA CUDA base image (Ubuntu 24.04)

---

## 📌 Key Parameters  
| Parameter | Description |
|----------|-------------|
| `yolo11n.pt` | Pre-trained small YOLOv8 model (auto-downloaded) |
| `source=input_video.mp4` | Input video file (or RTSP stream URL) |
| `classes=0` | Detect only "person" (class 0 in COCO dataset) |
| `save=True` | Save annotated video |
| `save_crop=True` | Save cropped detection images |

---

## ✅ Summary of Steps  
1. Install Docker + NVIDIA Toolkit  
2. Create project directory  
3. Write Dockerfile with CUDA & YOLOv8  
4. Build Docker image  
5. Run container with GPU  
6. Execute detection command  
7. Retrieve results from `runs/detect/predict/`  

---

## 🛠️ Docker Setup  

### 1. Verify CUDA Availability  
```bash
docker run --rm --gpus all nvidia/cuda:13.0.1-cudnn-devel-ubuntu24.04 nvidia-smi
```

### 2. Create needed DIR on local host  
```bash
mkdir -p /home/vols/.nvidia-cuda/person_detection
```

### 3. Create Dockerfile to build the needed Ubuntu/CUDA container image.
```bash
# Use NVIDIA CUDA base image
FROM nvidia/cuda:13.0.1-cudnn-devel-ubuntu24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip git ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install YOLOv8
COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /bin/
RUN uv venv /uv/.venv
ENV PATH="/uv/.venv/bin:${PATH}"
RUN uv pip install ultralytics opencv-python

# Set working directory
WORKDIR /workspace

# Copy project files
COPY . /workspace

# Default command (runs YOLO)
CMD ["bash"]
```

### 4. Build yolo-person-detect docker image
```bash
docker build -t yolo-person-detect .
docker image ls

REPOSITORY                                    TAG                              IMAGE ID       CREATED          SIZE
yolo-person-detect                            latest                           c3xf2e71ex45   19 seconds ago   16.3GB
```

### 5. From the built yolo-person-detect docker image run the docker container. 
```bash
docker run --gpus all -it --rm -v /home/vols/.nvidia-cuda/person_detection/:/workspace yolo-person-detect
```

### 6. Execute Detection Command
#### Inside the container, run the detection command with your video file or RTSP stream:
```bash
yolo detect predict model=yolo11n.pt source=Person-Test.mp4 classes=0 save=True save_crop=True
```

#### OR use RTSP stream instead of a video file:
```bash
yolo detect predict model=yolo11n.pt source="rtsp://<username>:<password>@<ip>/stream" classes=0 save=True save_crop=True
```

### 7. Run detect_rtsp_with_logging.py for RTSP object(person) detection
```bash
./detect_rtsp_with_logging.py
```
