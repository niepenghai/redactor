# Windows spaCy Installation Guide

## 问题说明

Windows版本在GitHub Actions构建过程中遇到spaCy编译问题，这是一个已知的Windows + spaCy组合问题。

## 当前解决方案

### 自动回退机制
- Windows构建**自动使用SimpleNLPNameDetector**
- 提供基于规则的人名检测，无需spaCy依赖
- 保证功能完整性和跨平台兼容性

### 检测能力对比

| 平台 | NLP引擎 | 人名检测 | 优势 |
|------|---------|----------|------|
| **Linux/Mac** | spaCy NER | 高精度 | 深度学习模型 |
| **Windows** | SimpleNLP | 规则检测 | 无编译依赖，快速部署 |

## Windows用户选项

### 选项1: 使用预构建版本（推荐）
```bash
# 下载预构建的Windows版本
wget https://github.com/niepenghai/redactor/releases/latest/PDF-Redactor-Windows-Offline.zip
```
- ✅ 无需安装Python或依赖
- ✅ 包含所有必要组件
- ✅ 开箱即用

### 选项2: 手动安装spaCy（高级用户）
如果你希望在Windows上获得完整的spaCy功能：

```bash
# 安装Visual Studio Build Tools
# 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 安装spaCy
pip install spacy --only-binary=all
python -m spacy download en_core_web_sm

# 验证安装
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy OK')"
```

### 选项3: 使用Docker（开发者）
```dockerfile
FROM python:3.9-slim
RUN pip install spacy
RUN python -m spacy download en_core_web_sm
COPY . /app
WORKDIR /app
```

## 技术背景

### 为什么Windows编译spaCy困难？
1. **C++编译器依赖** - 需要Visual Studio Build Tools
2. **复杂依赖链** - blis, thinc, cymem等科学计算库
3. **架构兼容性** - AVX512指令集支持问题
4. **构建环境** - GitHub Actions Windows runner限制

### SimpleNLPNameDetector功能
我们的fallback方案提供：
- ✅ 称谓词识别 (Mr./Mrs./Dr.等)
- ✅ 常见姓名库匹配
- ✅ 上下文分析
- ✅ 商业词汇过滤
- ✅ 语言学模式识别

## 测试结果

Windows版本经过全面测试：
- ✅ 基础PDF处理功能
- ✅ 账号、SSN、电话号码检测
- ✅ 人名检测（基于规则）
- ✅ 地址和日期检测
- ✅ 货币金额识别

## 问题报告

如果遇到问题，请提供：
1. Windows版本 (Win 10/11)
2. 错误截图
3. 使用的PDF类型
4. 是否需要spaCy功能

📧 提交Issue: https://github.com/niepenghai/redactor/issues