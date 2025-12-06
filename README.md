## Person detection using YOLO11n.pt on Nvidia RTX 50 series ##

# URL: https://docs.ultralytics.com/models/
# URL: https://github.com/ultralytics/ultralytics

Explanation:
yolov8n.pt → pre-trained small YOLOv8 model
source=input_video.mp4 → your input video
classes=0 → only detect “person” (class 0 in COCO dataset)
YOLO will automatically download weights and process the video.
YOLO will output results to: runs/detect/predict/

✅ Summary
Step	Description
1	Install Docker + NVIDIA Toolkit
2	Create project directory
3	Write Dockerfile with CUDA & YOLOv8
4	Build image
5	Run container with GPU
6	Perform detection
7	Retrieve results

## 1) Checking latest CUDA container from NVIDIA.
docker run --rm --gpus all nvidia/cuda:13.0.1-cudnn-devel-ubuntu24.04 nvidia-smi

## 2) Create needed DIR on local host
mkdir -p /home/vols/.nvidia-cuda/person_detection

## 3) Create Dockerfile to build the nneded Ubuntu/CUDA container image.
~cat Dockerfile
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

## 4) Check to see the docker image
docker image ls
REPOSITORY                                    TAG                              IMAGE ID       CREATED        SIZE
nvidia/cuda                                   13.0.1-cudnn-devel-ubuntu24.04   123057cf7091   7 weeks ago    7.91GB

## 5) Build yolo-person-detect docker image.
docker build -t yolo-person-detect .
docker image ls
REPOSITORY                                    TAG                              IMAGE ID       CREATED          SIZE
yolo-person-detect                            latest                           c3xf2e71ex45   19 seconds ago   16.3GB

## 6) From the built yolo-person-detect docker image run the docker container.
docker run --gpus all -it --rm -v /home/vols/.nvidia-cuda/person_detection/:/workspace yolo-person-detect

## 7) Run Object or person detection inside the container & output the detection.
yolo detect predict model=yolo11n.pt source=RVIEW_PersonDog-Test.mp4 classes=0 save=True save_crop=True

OR

You can use the above RTSP input script instead of .mp4 file for object(person or any other) detect using yolo11n.
