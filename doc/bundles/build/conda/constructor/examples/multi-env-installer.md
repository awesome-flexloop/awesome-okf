---
type: example
title: "多环境安装程序"
description: "构建一个包含 base 环境和多个额外 conda 环境的安装程序，适用于数据科学工作站、AI/ML 平台等多场景。"
tags: [多环境, extra_envs, 数据科学, 机器学习, 工作站]
status: stable
stale_after: 2027-12-31
level: advanced
prerequisites: ["basic-miniconda", "../concepts/11-multi-env-and-channels"]
reading_time: 10
generated: { by: "example_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-fcp
    resource: "constructor/fcp.py"
---

# 多环境安装程序

本例演示如何构建一个包含多个 conda 环境的数据科学工作站安装程序。一个安装程序同时配置：base 管理环境、Python 3.14 数据分析环境、Python 3.12 深度学习环境。

## 使用场景

- **企业数据科学工作站**：为数据分析师提供一键安装的完整环境
- **培训/教学**：为学员预装多个环境（课程环境、练习环境）
- **AI/ML 平台**：不同 CUDA 版本的深度学习框架需要独立环境
- **多 Python 版本**：在同一安装中提供 Python 3.12/3.13/3.14

## construct.yaml

```yaml
name: DataScienceWorkstation
version: "2026.08"
company: "DataCorp"

channels:
  - conda-forge
  - nvidia
specs:
  - python=3.14
  - conda
  - mamba
  - pip
  - conda-libmamba-solver  # 快速 solver

# === conda 配置 ===
initialize_conda: classic
initialize_by_default: true
write_condarc: true
conda_default_channels:
  - conda-forge
condarc:
  channels:
    - conda-forge
  channel_priority: strict
  solver: libmamba
  auto_activate_base: true

# === 额外环境 ===
extra_envs:
  # 环境1: Python 3.14 数据分析环境
  analysis:
    specs:
      - python=3.14
      - numpy
      - pandas>=2.2
      - scipy
      - scikit-learn
      - matplotlib
      - seaborn
      - plotly
      - jupyterlab
      - notebook
      - ipykernel
      - polars
      - pyarrow
      - duckdb
      - sqlite
      - openpyxl
      - requests
      - beautifulsoup4
      - black
      - ruff
    channels:
      - conda-forge
    menu_packages:
      - jupyterlab

  # 环境2: Python 3.12 深度学习环境（独立 CUDA）
  deeplearning:
    specs:
      - python=3.12
      - pytorch
      - torchvision
      - torchaudio
      - pytorch-cuda=12.4
      - cudnn
      - transformers
      - datasets
      - accelerate
      - sentencepiece
      - tensorboard
      - wandb
      - opencv
      - pillow
      - jupyterlab
    channels:
      - pytorch
      - nvidia
      - conda-forge
    menu_packages: []

  # 环境3: 文档编写环境
  docs:
    specs:
      - python=3.13
      - sphinx
      - mkdocs
      - mkdocs-material
      - pandoc
      - jupytext
      - nbconvert
      - quarto
    channels:
      - conda-forge
    menu_packages: []

# === Windows 特定 ===
register_python: false    # 多环境不注册系统 Python
menu_packages: []         # base 环境不创建快捷方式（由各环境控制）
default_prefix: "%USERPROFILE%\\DataScience"  # [win]
default_prefix: "$HOME/datascience"           # [unix]

# === 安装行为 ===
keep_pkgs: true           # 多环境共享 pkgs 缓存，保留可节省空间
ignore_duplicate_files: true  # 多环境强制 true
check_path_spaces: true

# === 安装后脚本 ===
post_install: scripts/post_setup.sh   # [unix]
post_install: scripts/post_setup.bat  # [win]
post_install_desc: "注册 Jupyter 内核和配置 IDE 集成"

script_env_variables:
  DEFAULT_ENV: analysis
  JUPYTER_ENV: analysis

# === 构建产物 ===
build_outputs:
  - hash
  - info.json
  - licenses
  - lockfile
  - pkgs_list
```

## 安装后脚本

### scripts/post_setup.sh

```bash
#!/bin/bash
# 注册 Jupyter 内核

echo "注册 Jupyter 内核..."

# 在每个环境中注册 ipykernel
for env in analysis deeplearning docs; do
    env_path="$PREFIX/envs/$env"
    if [ -f "$env_path/bin/python" ]; then
        "$env_path/bin/python" -m ipykernel install \
            --user --name "$env" --display-name "Python ($env)" 2>/dev/null || true
    fi
done

# 创建环境切换快捷脚本
cat > "$PREFIX/bin/activate-env" << 'SCRIPT'
#!/bin/bash
ENV_NAME="${1:-analysis}"
source "$(dirname "$0")/../etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
SCRIPT
chmod +x "$PREFIX/bin/activate-env"

echo "配置完成！使用 'conda activate analysis' 切换到数据分析环境。"
```

### scripts/post_setup.bat

```batch
@echo off
echo 注册 Jupyter 内核...

for %%E in (analysis deeplearning docs) do (
    if exist "%PREFIX%\envs\%%E\python.exe" (
        "%PREFIX%\envs\%%E\python.exe" -m ipykernel install --user --name %%E --display-name "Python (%%E)" 2>nul
    )
)

echo 配置完成！使用 conda activate analysis 切换到数据分析环境。
```

## 构建

```bash
constructor . -o ./dist --verbose
```

## 安装后目录结构

```
~/datascience/                    # 安装前缀
├── bin/                          # base 环境命令
│   ├── python -> python3.14
│   ├── conda
│   └── activate-env              # 自定义快捷脚本
├── envs/
│   ├── analysis/                 # 数据分析环境
│   │   ├── bin/python -> python3.14
│   │   └── lib/python3.14/site-packages/
│   │       ├── numpy/
│   │       ├── pandas/
│   │       └── jupyterlab/
│   ├── deeplearning/             # 深度学习环境
│   │   └── bin/python -> python3.12
│   └── docs/                     # 文档环境
│       └── bin/python -> python3.13
├── pkgs/                         # 共享包缓存（所有环境共享）
├── conda-meta/
└── .condarc
```

## 验证安装

```bash
# 激活 base 环境
source ~/datascience/bin/activate
# 或
conda activate base

# 切换到数据分析环境
conda activate analysis
python -c "import pandas, numpy, jupyterlab; print('analysis OK')"

# 切换到深度学习环境
conda activate deeplearning
python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"

# 列出所有环境
conda env list
# base        /home/user/datascience
# analysis    /home/user/datascience/envs/analysis
# deeplearning /home/user/datascience/envs/deeplearning
# docs        /home/user/datascience/envs/docs
```

## 关键注意事项

### 1. base 必须包含 conda

当使用 `extra_envs` 时，base 环境必须包含 `conda`（或 mamba），因为额外环境由 base 中的 conda 管理。这在 [../concepts/11-multi-env-and-channels.md](../concepts/11-multi-env-and-channels.md) 中有详细说明。

### 2. 全局 exclude 传递到所有环境

```yaml
exclude:
  - tk          # 所有环境都排除 tk
extra_envs:
  analysis:
    specs: [...]
    exclude: [] # 空列表覆盖，analysis 环境包含 tk
```

### 3. 通道继承

额外环境的 `channels` 列表是**追加**到全局 channels 的，不是替换。环境专属通道优先级更高。

### 4. 包去重和共享

`pkgs/` 目录是所有环境共享的包缓存。相同版本的包只下载和存储一份，多环境不会重复占用磁盘空间。

### 5. lockfile 为每个环境生成

`build_outputs: [lockfile]` 会为每个环境生成独立的锁文件：
- `DataScienceWorkstation-2026.08-Linux-x86_64.lock`（base）
- `DataScienceWorkstation-2026.08-Linux-x86_64-analysis.lock`
- `DataScienceWorkstation-2026.08-Linux-x86_64-deeplearning.lock`

### 6. frozen 环境保护特定环境

可以选择性地冻结特定环境：

```yaml
extra_envs:
  analysis:
    specs: [...]
    freeze_env:
      conda:
        message: "分析环境已锁定，请联系管理员更新"
  dev:
    specs: [...]
    # dev 环境不冻结，可自由安装包
```

## 体积估算

多环境安装程序体积较大，constructor 会计算所有环境的包大小总和：
- base + analysis：约 1.5-2 GB（压缩）
- deeplearning（含 CUDA）：约 4-8 GB（压缩）
- docs：约 200-500 MB

构建前建议使用 `--dry-run` 预览：
```bash
constructor . --dry-run
```

## 下一步

- [Docker 镜像构建](./docker-installer.md)：将环境打包为 Docker 镜像
- [签名安装程序](./signed-installer.md)：为发布版本添加代码签名
