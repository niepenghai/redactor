# GUI 使用指南

## 启动GUI

```bash
python redactor-gui.py
```

## GUI界面说明

GUI窗口包含以下部分：

### 1. 文件选择区域（顶部）
- **选择文件** 按钮: 点击选择要处理的PDF文件（可多选）
- 文件列表: 显示已选择的PDF文件

### 2. 配置区域（中部）

#### 替换模式选择
- **Generic (通用模式)**:
  - 用 `[FULL NAME]`, `[ADDRESS]` 等占位符替换
  - 最安全，但不够真实

- **Realistic (真实模式)**:
  - 生成真实的假数据替换
  - 例如: 用 "John Smith" 替换真实姓名
  - 保持文档格式真实

- **Custom (自定义模式)**:
  - 使用自定义的替换文本
  - 需要在 `redactions.txt` 中配置

#### 选择要遮盖的信息类型
勾选需要遮盖的类别:
- ✅ **Names (姓名)**: 使用V2检测器，高精度
- ✅ **Addresses (地址)**: 使用V2检测器，支持结构化解析
- ✅ **SSN (社会安全号)**: 格式 XXX-XX-XXXX
- ✅ **Phone Numbers (电话号码)**: 各种格式
- ✅ **Account Numbers (账号)**: 银行账号等
- ✅ **Routing Numbers (路由号)**: 9位数字
- ✅ **Credit Card Numbers (信用卡号)**: 16位数字
- ✅ **Tax ID (税号)**: EIN等
- ✅ **Dates (日期)**: MM/DD/YYYY等格式
- ✅ **Currency (金额)**: 支持余额保护
- ✅ **Email Addresses (邮箱)**
- ✅ **Employer Information (雇主信息)**

### 3. 操作按钮区域（底部）

#### 🎯 Actions (操作)

- **👁️ Preview Detection (预览检测)**:
  - 点击后会显示检测到的敏感信息
  - 不会修改原文件
  - 可以查看哪些内容会被遮盖

- **🔒 Process Documents (处理文档)**:
  - 执行实际的遮盖操作
  - 创建新的遮盖后的PDF文件
  - 原文件保持不变
  - 输出文件保存在 `data/output/` 目录

## 使用流程

### 基本流程

1. **启动GUI**
   ```bash
   python redactor-gui.py
   ```

2. **选择文件**
   - 点击 "选择文件" 按钮
   - 选择一个或多个PDF文件
   - 文件会显示在列表中

3. **配置设置**
   - 选择替换模式（推荐 Generic 或 Realistic）
   - 勾选要遮盖的信息类型
   - 默认配置已经很好，通常不需要修改

4. **预览（可选）**
   - 点击 "Preview Detection" 查看会检测到什么
   - 检查是否有误报或漏报

5. **处理文档**
   - 点击 "Process Documents"
   - 等待处理完成
   - 查看输出文件在 `data/output/` 目录

### 高级使用

#### 使用V2检测器（已默认启用）

V2检测器提供更好的名字和地址检测：

**名字检测V2特点**:
- 5步清晰pipeline
- 详细日志输出
- 准确的first/middle/last name解析
- 过滤财务术语（如"Gross Pay"）

**地址检测V2特点**:
- 自动过滤已检测的人名
- 结构化解析（street/city/state/zip）
- 处理混合block（如包含名字和地址的行）
- 保留换行符作为边界

#### 查看处理日志

处理过程中会在终端显示详细日志：
```
🔍 Using Name Detector V2 pipeline...
📍 Starting Address Detection Pipeline V2
STEP 1: Extract and Clean PDF Text
STEP 2: Extract Candidate Addresses
STEP 2.5: Filter Out Known Person Names
STEP 3: Validate Candidates
STEP 4: Parse Addresses into Components
STEP 5: Finalize Parsed Addresses
```

#### 处理结果

处理完成后：
- 原文件: 保持不变
- 输出文件: `data/output/原文件名_redacted.pdf`
- 可以直接打开查看遮盖效果

## 示例场景

### 场景1: 遮盖银行对账单

```bash
python gui_main.py
```

1. 选择银行对账单PDF
2. 选择 "Realistic" 模式
3. 勾选:
   - ✅ Names
   - ✅ Addresses
   - ✅ Account Numbers
   - ✅ SSN
   - ✅ Currency (会保留余额)
4. 点击 "Process Documents"

### 场景2: 遮盖W2表单

1. 选择W2 PDF
2. 选择 "Generic" 模式
3. 勾选:
   - ✅ Names
   - ✅ Addresses
   - ✅ SSN
   - ✅ Tax ID
   - ✅ Employer Information
   - ✅ Currency
4. 点击 "Process Documents"

### 场景3: 只遮盖名字和地址

1. 选择PDF文件
2. 选择 "Realistic" 模式
3. 只勾选:
   - ✅ Names
   - ✅ Addresses
4. 点击 "Process Documents"

## 常见问题

### Q: 如果检测到不该遮盖的内容怎么办？
A:
- 取消勾选对应的类别
- 或者使用 "Preview Detection" 先查看
- V2检测器已经过滤了很多误报（如"Gross Pay"）

### Q: 如果漏检了某些内容怎么办？
A:
- 可以在 `redactions.txt` 中添加自定义pattern
- 或者运行两次，第二次只勾选漏掉的类别

### Q: 输出文件在哪里？
A:
- 默认在 `data/output/` 目录
- 文件名格式: `原文件名_redacted.pdf`

### Q: 可以批量处理吗？
A:
- 可以！选择文件时按住 Ctrl/Cmd 多选
- 或者使用CLI批量处理（见 `README.md`）

### Q: 如何查看详细的检测日志？
A:
- 在终端/命令行窗口中查看
- 会显示每一步的处理过程
- 包括检测到的内容和位置

### Q: 真实模式生成的数据是随机的吗？
A:
- 不是完全随机
- 同样的输入会生成同样的输出（用于一致性）
- 但不同的名字会生成不同的假名字

### Q: 如何处理混合block（名字+地址在同一行）？
A:
- V2检测器会自动处理
- 先检测名字，然后从地址候选中排除名字
- 确保名字和地址分别替换

## 技术细节

### V2检测器架构

**Name Detector V2**:
```
1. Clean PDF Text → 清理文本
2. Pattern Extraction → 提取候选
3. spaCy Validation → 验证真人名
4. Name Parsing → 解析成first/middle/last
5. Position Mapping → 映射到PDF位置
```

**Address Detector V2**:
```
1. Clean PDF Text → 清理文本（保留换行）
2. Pattern Extraction → 提取候选地址
2.5. Filter Person Names → 过滤已知人名
3. Validation → 验证和置信度评估
4. Component Parsing → 解析成street/city/state/zip
5. Finalize → 转换为最终对象
```

### Balance Preservation (余额保护)

启用 Currency 遮盖时，会智能保留余额：
- ✅ 保留: "Ending Balance: $25,785.24"
- ❌ 遮盖: "Transaction: $100.00"

这样可以保留账户整体余额，只隐藏具体交易细节。

## 故障排除

### GUI无法启动
```bash
# 检查依赖
pip install tkinter

# 检查是否有其他GUI在运行
pkill -f redactor-gui

# 重新启动
python redactor-gui.py
```

### 处理很慢
- 这是正常的，V2检测器会详细分析文本
- 第一次运行会加载spaCy模型（较慢）
- 后续运行会快一些

### 没有检测到名字/地址
- 检查是否勾选了对应的类别
- 查看终端日志，看检测过程
- 可能文档中确实没有该类型信息

## 更多帮助

- 查看 `README.md` 了解CLI使用
- 查看 `PROJECT_MEMORY.md` 了解项目历史
- 查看 `CLAUDE.md` 了解开发指南
