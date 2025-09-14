#!/bin/bash

echo "🔧 本地构建 PDF Redactor"
echo "=========================="

# 检查依赖
echo "✅ 检查依赖..."
python -c "import fitz; print(f'PyMuPDF version: {fitz.version[0]}')"
python -c "import tkinter; print('Tkinter available')"

# 清理之前的构建
echo "🧹 清理构建文件..."
rm -rf dist/ build/ *.spec

# 构建 macOS 版本
echo "🍎 构建 macOS 可执行文件..."
pyinstaller --onefile --name=redactor-macos \
    --hidden-import=fitz \
    --hidden-import=pymupdf \
    --hidden-import=PIL \
    --hidden-import=PIL.Image \
    --hidden-import=numpy \
    --hidden-import=spacy \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    --hidden-import=tkinter.filedialog \
    --hidden-import=tkinter.messagebox \
    --hidden-import=tkinter.scrolledtext \
    --hidden-import=threading \
    --hidden-import=re \
    --hidden-import=os \
    --hidden-import=sys \
    --hidden-import=json \
    --hidden-import=typing \
    --hidden-import=pathlib \
    --hidden-import=tempfile \
    --hidden-import=shutil \
    --hidden-import=random \
    --hidden-import=hashlib \
    --hidden-import=dataclasses \
    --collect-all=fitz \
    --collect-all=pymupdf \
    --collect-all=PIL \
    --collect-all=numpy \
    redactor-gui.py

# 检查构建结果
echo "📊 构建结果:"
ls -la dist/
file dist/redactor-macos
echo "文件大小: $(du -h dist/redactor-macos)"

echo "✅ 构建完成！"
echo "运行: ./dist/redactor-macos"