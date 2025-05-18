from PIL import Image
import cv2
import os
from pathlib import Path

def extract_frames(video_path, output_dir, frame_interval=24):  # 每秒提取一帧
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    video = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # 将BGR转换为RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转换为PIL图像
            pil_image = Image.fromarray(frame_rgb)
            # 保存图像
            frame_path = os.path.join(output_dir, f'frame_{saved_count:05d}.jpg')
            pil_image.save(frame_path, quality=85)  # 使用较低的压缩率
            saved_count += 1
            
        frame_count += 1
    
    video.release()
    print(f'已提取 {saved_count} 帧')

if __name__ == '__main__':
    video_path = 'app/assets/猫和老鼠CD8-西部大懒猫.avi'  # 替换为您的视频路径
    output_dir = 'app/static/frames'
    extract_frames(video_path, output_dir) 