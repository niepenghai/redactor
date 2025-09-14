# 🛠️ 构建脚本

## 文件说明

- `redactor.spec` - PyInstaller 规格文件 (主要构建配置)
- `build-local.sh` - 本地构建脚本 (与CI一致)
- `build-simple.sh` - 简单构建脚本 (快速测试用)

## 使用方法

```bash
# 推荐方法 (与CI一致)
cd scripts/
pyinstaller redactor.spec

# 或使用自动化脚本
./build-local.sh

# 快速测试构建
./build-simple.sh
```

更多详情请查看 `docs/build/BUILD_METHODS.md`