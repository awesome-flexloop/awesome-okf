---
type: Example
title: 命令行基本使用
description: 使用 olot CLI 完成从基础镜像拉取、添加模型层到推送镜像的完整 ModelCar 打包流程
tags: [cli, command-line, skopeo, modelcar, tutorial]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /bundles/containers/olot/references/readme-source.md
    title: "olot 项目 README 信源"
  - id: cli
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/cli.py"
    title: "olot/cli.py CLI 实现"
---

# 命令行基本使用

本示例演示如何使用 olot CLI 工具完成一个完整的 ModelCar 打包流程：拉取基础镜像 → 添加模型文件 → 推送镜像到 registry。

## 前置条件

1. 已安装 Python >= 3.10
2. 已安装 olot：`pip install olot` 或 `uv tool install olot`
3. 已安装 skopeo（或其他后端工具）
4. 有一个容器 registry 账号（如 Quay.io、Docker Hub、私有 registry 等）

## 查看 CLI 帮助

首先确认 olot 已正确安装：

```bash
olot --help
```

你应该看到类似输出：

```
Usage: olot [OPTIONS] OCILAYOUT [MODEL_FILES]...

Options:
  -m, --modelcard PATH   file to be used for ModelCarD
  --add-modelpack        Add ModelPack manifest
  -v, --verbose          Enable verbose output (DEBUG level logging)
  --root-dir PATH        root directory of the model files
  -r, --remove-originals [default|all]
                         Remove original files after adding layers
  --help                 Show this message and exit.
```

## 完整工作流示例

我们将使用官方示例镜像 `quay.io/mmortari/hello-world-wait:latest` 作为基础镜像，添加一个示例模型文件和 ModelCarD。

### 步骤 1：准备工作目录

```bash
# 设置变量
IMAGE_DIR=./download
OCI_REGISTRY_SOURCE=quay.io/mmortari/hello-world-wait:latest
OCI_REGISTRY_DESTINATION=quay.io/your-username/your-model:v1

# 清理旧目录
rm -rf $IMAGE_DIR

# 准备示例模型文件
mkdir -p my-model
echo "This is a fake model file for demo" > my-model/model.joblib
cat > my-model/README.md << 'EOF'
# My Demo Model

This is a demo ModelCarD for olot tutorial.

- **Model Type**: Demo
- **Framework**: None
- **Version**: 1.0
EOF
```

### 步骤 2：拉取基础镜像

使用 skopeo 将基础镜像拉取到本地 OCI layout 格式：

```bash
skopeo copy --multi-arch all docker://${OCI_REGISTRY_SOURCE} oci:${IMAGE_DIR}:latest
```

成功后，你会看到 `$IMAGE_DIR` 目录已创建，包含 `oci-layout`、`index.json` 和 `blobs/` 子目录。

> **如果使用 oras cp 替代 skopeo**：
> ```bash
> oras copy --to-oci-layout $OCI_REGISTRY_SOURCE ./${IMAGE_DIR}:latest
> chmod +w ${IMAGE_DIR}/blobs/sha256/*
> ```

### 步骤 3：使用 olot 添加模型层

运行 olot 命令，将模型文件和 ModelCarD 作为新层添加：

```bash
olot $IMAGE_DIR \
  --modelcard my-model/README.md \
  my-model/model.joblib
```

如果需要查看详细日志，添加 `-v` 参数：

```bash
olot -v $IMAGE_DIR \
  --modelcard my-model/README.md \
  my-model/model.joblib
```

命令成功后没有输出（正常情况）。使用 `-v` 时可以看到 DEBUG 级别的详细日志，包括每层的处理过程。

### 步骤 4：推送镜像到 registry

使用 skopeo 将更新后的镜像推送到你的 registry：

```bash
skopeo copy --multi-arch all oci:${IMAGE_DIR}:latest docker://${OCI_REGISTRY_DESTINATION}
```

推送成功后，你的 ModelCar 镜像就可以使用了！

> **如果使用 oras cp 推送**：
> ```bash
> oras cp --from-oci-layout ./${IMAGE_DIR}:latest $OCI_REGISTRY_DESTINATION
> ```

### 步骤 5：验证镜像

可以使用 podman 或 docker 运行镜像，验证文件是否在 `/models/` 目录下：

```bash
podman run --rm -it $OCI_REGISTRY_DESTINATION ls -la /models/
```

预期输出：

```
total 16
drwxr-xr-x    2 root     root          4096 Aug 26 07:44 .
drwxr-xr-x    1 root     root          4096 Aug 26 07:44 ..
-rw-r--r--    1 root     root            32 Aug 26 07:44 README.md
-rw-r--r--    1 root     root            35 Aug 26 07:44 model.joblib
```

你还可以查看 ModelCarD 内容：

```bash
podman run --rm -it $OCI_REGISTRY_DESTINATION cat /models/README.md
```

### 步骤 6：清理

```bash
# 删除本地镜像
podman image rm $OCI_REGISTRY_DESTINATION

# 清理临时目录
rm -rf $IMAGE_DIR my-model
```

## CLI 参数详解

### 位置参数

- `OCILAYOUT`：OCI layout 目录路径（必须存在）
- `[MODEL_FILES]...`：一个或多个要添加的模型文件路径

### 选项参数

#### `-m, --modelcard PATH`

指定 ModelCarD 文件（通常是 README.md）。这个文件会被 gzip 压缩并作为最后一层添加，带有特殊的 modelcard 注解。

```bash
olot ./download --modelcard ./model/README.md ./model/model.bin
```

> **重要**：不要将 modelcard 文件同时放在 MODEL_FILES 参数中，否则会导致重复层。

#### `--root-dir PATH`

当模型文件分布在子目录中时，使用此参数保留目录结构：

```bash
# 目录结构：
# my-model/
# ├── config.json
# ├── onnx/
# │   └── model.onnx
# └── tokenizer/
#     └── tokenizer.json

olot ./download \
  --root-dir ./my-model \
  ./my-model/config.json \
  ./my-model/onnx/model.onnx \
  ./my-model/tokenizer/tokenizer.json
```

结果在容器中路径为：
- `/models/config.json`
- `/models/onnx/model.onnx`
- `/models/tokenizer/tokenizer.json`

不使用 `--root-dir` 时，所有文件都会平铺到 `/models/` 下，同名文件会互相覆盖。

#### `-r, --remove-originals [default|all]`

添加层后删除本地原始文件：

```bash
# 删除 model_files 中的原始文件（不删除 modelcard）
olot ./download -r my-model/model.joblib

# 删除所有原始文件，包括 modelcard
olot ./download -r all --modelcard my-model/README.md my-model/model.joblib
```

#### `--add-modelpack`

为多架构镜像添加 ModelPack manifest：

```bash
olot ./download --add-modelpack my-model/model.joblib
```

注意：只能对多架构 OCI layout（包含 index）使用此选项，单架构镜像会报错。

#### `-v, --verbose`

启用 DEBUG 级别详细日志输出：

```bash
olot -v ./download my-model/model.joblib
```

## 使用目录作为输入

olot 支持直接添加整个目录，但会有警告提示这会导致非最优的层结构：

```bash
olot ./download ./my-model-directory/
```

目录会被打包成单个 tar 层。建议还是逐个文件添加，或使用 `--root-dir` 明确列出文件。

## 常见问题

### Q: 推送后 podman/docker 拉取看不到文件？

检查是否使用了 `--multi-arch all` 参数拉取和推送，确保所有架构都被处理。

### Q: 如何复制结果到本地 OCI layout？

使用 skopeo 时添加 `--dest-oci-accept-uncompressed-layers` 选项：

```bash
skopeo copy --dest-oci-accept-uncompressed-layers \
  docker://your-image:latest oci:./local-copy:latest
```

### Q: chmod 错误（permission denied）？

如果使用 oras cp 拉取，记得执行 `chmod +w` 添加写权限：

```bash
chmod +w ${IMAGE_DIR}/blobs/sha256/*
```

## 相关概念

- [olot 定位与 ModelCar 标准](../concepts/00-introduction.md)
- [OCI 层操作与四元组注解](../concepts/01-oci-layers.md)
- [后端抽象层](../concepts/02-backends.md)
- [Python API 打包模型](02-python-api.md)
