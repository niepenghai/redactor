#!/bin/bash

echo "🚀 简单本地构建 (可能你之前用的方法)"
echo "================================"

# 清理
rm -rf dist/ build/ *.spec

# 最简单的构建 
echo "构建中..."
pyinstaller --onefile --windowed --name=redactor-macos redactor-gui.py

echo "📊 简单构建结果:"
ls -la dist/
echo "文件大小: $(du -h dist/redactor-macos)"

echo "⚠️  注意：这个版本可能缺少依赖，建议使用 build-local.sh"