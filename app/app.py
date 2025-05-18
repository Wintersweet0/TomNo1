from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from pathlib import Path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['FRAMES_FOLDER'] = 'app/static/frames'

# 确保上传文件夹存在
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path(app.config['FRAMES_FOLDER']).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def calculate_similarity(img1_path, img2_path, size=(224, 224)):
    try:
        # 打开并调整图片大小
        img1 = Image.open(img1_path).convert('RGB').resize(size)
        img2 = Image.open(img2_path).convert('RGB').resize(size)
        
        # 转换为numpy数组
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # 计算均方误差
        mse = np.mean((arr1 - arr2) ** 2)
        # 转换为相似度分数（0-1之间，1表示完全相同）
        similarity = 1 / (1 + mse)
        
        return similarity
    except Exception as e:
        print(f"Error comparing images: {e}")
        return 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("收到上传请求")  # 添加调试信息
    if 'file' not in request.files:
        print("没有文件在请求中")  # 添加调试信息
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        print("文件名为空")  # 添加调试信息
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        print(f"处理文件: {file.filename}")  # 添加调试信息
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"文件已保存到: {filepath}")  # 添加调试信息
        
        # 寻找相似帧
        similar_frames = []
        frames_dir = app.config['FRAMES_FOLDER']
        
        print(f"开始检查帧目录: {frames_dir}")  # 添加调试信息
        print(len(os.listdir(frames_dir)))
        for frame_file in os.listdir(frames_dir):
            print(f"检查帧文件: {frame_file}")  # 添加调试信息
            if not allowed_file(frame_file):
                print(f"跳过非图片文件: {frame_file}")  # 添加调试信息
                continue
                
            frame_path = os.path.join(frames_dir, frame_file)
            similarity = calculate_similarity(filepath, frame_path)
            print(f"帧 {frame_file} 的相似度: {similarity}")  # 添加调试信息
            
            if similarity > 0.0097:
                similar_frames.append({
                    'frame': frame_file,
                    'similarity': float(similarity)
                })
        
        print(f"找到 {len(similar_frames)} 个相似帧")  # 添加调试信息
        similar_frames.sort(key=lambda x: x['similarity'], reverse=True)
        
        return jsonify({
            'success': True,
            'similar_frames': similar_frames[:5]
        })
    
    return jsonify({'error': '不支持的文件类型'}), 400

if __name__ == '__main__':
    app.run(debug=True) 