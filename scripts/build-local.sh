#!/bin/bash

echo "🔧 本地构建 PDF Redactor (与CI完全一致)"
echo "======================================="

# 切换到脚本目录
cd "$(dirname "$0")"

# 检查依赖
echo "✅ 检查依赖..."
python -c "import fitz; print(f'PyMuPDF version: {fitz.version[0]}')"
python -c "import tkinter; print('Tkinter available')"

# 清理之前的构建
echo "🧹 清理构建文件..."
rm -rf ../dist/ ../build/

# 构建 macOS 版本 (与CI完全相同的方法)
echo "🍎 构建 macOS 可执行文件使用 spec 文件..."
echo "Building macOS executable using spec file..."
# Use the same spec file as local build
pyinstaller redactor.spec

# Copy the app to expected location for release (与CI相同)
echo "复制可执行文件到发布位置..."
cp -r dist/PDFRedactor.app/Contents/MacOS/PDFRedactor dist/redactor-macos

echo "macOS build completed:"
ls -la dist/
du -h dist/redactor-macos

# 检查构建结果
echo ""
echo "📊 构建结果:"
echo "App Bundle: dist/PDFRedactor.app"
echo "Executable: dist/redactor-macos"
file dist/redactor-macos
echo "文件大小: $(du -h dist/redactor-macos)"

echo ""
echo "✅ 构建完成！与CI完全一致"
echo "运行方式："
echo "  - App Bundle: open dist/PDFRedactor.app"
echo "  - 直接执行: ./dist/redactor-macos"