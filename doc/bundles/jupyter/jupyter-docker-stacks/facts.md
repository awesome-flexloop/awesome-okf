---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- docker
- jupyterlab
- notebook
- container
sources:
- ../../../../../external/libs/jupyter/docker-stacks/README.md
- ../../../../../external/libs/jupyter/docker-stacks/tagging/hierarchy/images_hierarchy.py
- ../../../../../external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/start.sh
- ../../../../../external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/run-hooks.sh
- ../../../../../external/libs/jupyter/docker-stacks/images/base-notebook/start-notebook.py
- ../../../../../external/libs/jupyter/docker-stacks/images/base-notebook/jupyter_server_config.py
- ../../../../../external/libs/jupyter/docker-stacks/tagging/apps/apply_tags.py
- ../../../../../external/libs/jupyter/docker-stacks/tagging/taggers/tagger_interface.py
- ../../../../../external/libs/jupyter/docker-stacks/tagging/manifests/manifest_interface.py
- ../../../../../external/libs/jupyter/docker-stacks/tagging/apps/write_tags_file.py
- ../../../../../external/libs/jupyter/docker-stacks/tagging/apps/write_manifest.py
- ../../../../../external/libs/jupyter/docker-stacks/tagging/utils/docker_runner.py
- ../../../../../external/libs/jupyter/docker-stacks/tests/conftest.py
- ../../../../../external/libs/jupyter/docker-stacks/tests/utils/tracked_container.py
- ../../../../../external/libs/jupyter/docker-stacks/tests/run_tests.py
- ../../../../../external/libs/jupyter/docker-stacks/images/docker-stacks-foundation/10activate-conda-env.sh
- ../../../../../external/libs/jupyter/docker-stacks/images/base-notebook/start-singleuser.py
- ../../../../../external/libs/jupyter/docker-stacks/images/base-notebook/docker_healthcheck.py
- ../../../../../external/libs/jupyter/docker-stacks/.github/workflows/docker-build-test-upload.yml
- ../../../../../external/libs/jupyter/docker-stacks/.github/workflows/docker-tag-push.yml
- ../../../../../external/libs/jupyter/docker-stacks/.pre-commit-config.yaml
type: Facts
title: jupyter-docker-stacks 源码事实清单
---

# jupyter-docker-stacks 事实清单

> Jupyter 官方 Docker 镜像集，包含 12 个层级化的 ready-to-run 镜像，从基础 OS 到全功能数据科学栈。镜像发布于 Quay.io，支持 x86_64 和 aarch64 双架构。

## 仓库概览

- F-001: README.md:12 — Jupyter Docker Stacks 是一组 ready-to-run Docker 镜像，包含 Jupyter 应用和交互式计算工具
- F-002: README.md:29-31 — 自 2023-10-20 起，镜像仅推送到 Quay.io 注册表（quay.io/jupyter），Docker Hub 上的旧镜像不再更新
- F-003: README.md:103-109 — 支持 x86_64 和 aarch64 双平台；单平台镜像有 aarch64-/x86_64- 前缀；自 2022-09-21 创建多平台镜像（tensorflow-notebook 除外）；2024-02-24 起为 pytorch-notebook 添加 CUDA 变体（x86_64）；2024-03-26 起为 tensorflow-notebook 添加 CUDA 变体（x86_64）；2025-12-02 起 aarch64 也支持 CUDA 变体
- F-004: README.md:83-84 — 默认前端为 JupyterLab，可通过环境变量 DOCKER_STACKS_JUPYTER_CMD=notebook 切换到 Jupyter Notebook
- F-005: README.md:39 — 典型运行命令：docker run -p 10000:8888 quay.io/jupyter/scipy-notebook:<date-tag>
- F-006: README.md:73-77 — 默认 root_dir 为 /home/jovyan，可通过 start-notebook.py --ServerApp.root_dir=/home/jovyan/work 修改
- F-007: README.md:58 — 推荐挂载卷：-v "${PWD}":/home/jovyan/work 将当前目录挂载到容器内

## 镜像层级结构

- F-008: Makefile:41-52 — 12 个镜像的构建依赖顺序（ALL_IMAGES）：docker-stacks-foundation → base-notebook → minimal-notebook → scipy-notebook → {r-notebook, julia-notebook, tensorflow-notebook, pytorch-notebook, datascience-notebook, pyspark-notebook} → all-spark-notebook
- F-009: tagging/hierarchy/images_hierarchy.py:25-80 — ImageDescription 数据类定义每个镜像的 parent_image、taggers（标签生成器）和 manifests（清单生成器）
- F-010: tagging/hierarchy/images_hierarchy.py:26-38 — docker-stacks-foundation 为根镜像（parent_image=None），tagger 包含 commit_sha、date、ubuntu_version、python_major_minor、python、mamba、conda；manifests 包含 conda_environment_manifest、apt_packages_manifest
- F-011: tagging/hierarchy/images_hierarchy.py:39-46 — base-notebook 继承 docker-stacks-foundation，额外 tagger：jupyter_notebook、jupyter_lab、jupyter_hub
- F-012: tagging/hierarchy/images_hierarchy.py:47-48 — minimal-notebook 继承 base-notebook，无额外 tagger 或 manifest
- F-013: tagging/hierarchy/images_hierarchy.py:49-53 — r-notebook 继承 minimal-notebook，添加 r_tagger 和 r_packages_manifest
- F-014: tagging/hierarchy/images_hierarchy.py:54-58 — julia-notebook 继承 minimal-notebook，添加 julia_tagger 和 julia_packages_manifest
- F-015: tagging/hierarchy/images_hierarchy.py:59-64 — tensorflow-notebook 和 pytorch-notebook 继承 scipy-notebook，分别添加 tensorflow_tagger 和 pytorch_tagger
- F-016: tagging/hierarchy/images_hierarchy.py:65-69 — datascience-notebook 继承 scipy-notebook，组合 r_tagger + julia_tagger 和 r_packages_manifest + julia_packages_manifest
- F-017: tagging/hierarchy/images_hierarchy.py:70-74 — pyspark-notebook 继承 scipy-notebook，添加 spark_tagger + java_tagger 和 spark_info_manifest
- F-018: tagging/hierarchy/images_hierarchy.py:75-79 — all-spark-notebook 继承 pyspark-notebook，添加 r_tagger 和 r_packages_manifest

## Foundation 镜像（docker-stacks-foundation）

- F-019: images/docker-stacks-foundation/Dockerfile:10 — 基础镜像为 ubuntu:24.04（noble），使用 sha256 digest 固定版本以确保可重现性
- F-020: images/docker-stacks-foundation/Dockerfile:15 — Micromamba 从 mambaorg/micromamba:2.8.1 digest 固定镜像获取，通过 BuildKit bind mount 挂载，不写入任何镜像层
- F-021: images/docker-stacks-foundation/Dockerfile:20-22 — 默认用户参数：NB_USER=jovyan、NB_UID=1000、NB_GID=100
- F-022: images/docker-stacks-foundation/Dockerfile:26 — SHELL 设置为 ["/bin/bash", "-o", "pipefail", "-c"]，遵循 hadolint/shellcheck 建议
- F-023: images/docker-stacks-foundation/Dockerfile:37-49 — 安装 OS 依赖：ca-certificates、locales、netbase、sudo、tini（僵尸进程回收）、wget；配置 en_US.UTF-8 和 C.UTF-8 locale
- F-024: images/docker-stacks-foundation/Dockerfile:48 — tini 作为容器 entrypoint，用于回收僵尸进程
- F-025: images/docker-stacks-foundation/Dockerfile:56-65 — 环境变量配置：CONDA_DIR=/opt/conda、SHELL=/bin/bash、LC_ALL/LANG/LANGUAGE=C.UTF-8，PATH 包含 ${CONDA_DIR}/bin，HOME=/home/${NB_USER}
- F-026: images/docker-stacks-foundation/Dockerfile:68-69 — 复制 fix-permissions 脚本到 /usr/local/bin/ 并设为可执行
- F-027: images/docker-stacks-foundation/Dockerfile:73-76 — 在 /etc/skel/.bashrc 中启用 force_color_prompt 并添加 conda shell hook（eval "$(conda shell.bash hook)"）
- F-028: images/docker-stacks-foundation/Dockerfile:79-81 — 如果 UID=${NB_UID} 的用户已存在，先删除（userdel --remove）
- F-029: images/docker-stacks-foundation/Dockerfile:85-93 — 创建 jovyan 用户：禁用 su（pam_deny.so）、注释掉 %admin 和 %sudo sudoers 组、useradd 创建用户（no-log-init, create-home, shell /bin/bash, uid 1000, no-user-group）、chown CONDA_DIR、chmod g+w /etc/passwd
- F-030: images/docker-stacks-foundation/Dockerfile:96-100 — 预创建 ~/.cache 目录并设为用户所有，防止 macOS Rosetta 垃圾文件问题
- F-031: images/docker-stacks-foundation/Dockerfile:105 — 默认 Python 版本：ARG PYTHON_VERSION=3.13
- F-032: images/docker-stacks-foundation/Dockerfile:121-143 — 通过 bind-mounted micromamba 安装 jupyter_core、conda、mamba（版本与 micromamba 镜像一致）和指定 Python 版本；使用 mamba 安装（非 micromamba 直接安装到 prefix）；安装后 pin Python major.minor 版本防止意外升级；mamba clean 清理缓存
- F-033: images/docker-stacks-foundation/Dockerfile:140 — Pin Python major.minor 版本：mamba list python | awk 输出 "python X.Y*" 到 conda-meta/pinned
- F-034: images/docker-stacks-foundation/Dockerfile:146 — 复制 _docker_stacks_log.sh、run-hooks.sh、start.sh 到 /usr/local/bin/
- F-035: images/docker-stacks-foundation/Dockerfile:149 — ENTRYPOINT 为 ["tini", "-g", "--", "start.sh"]，tini 的 -g 标志表示在子进程组中发送信号
- F-036: images/docker-stacks-foundation/Dockerfile:154-155 — 创建 hook 目录 /usr/local/bin/start-notebook.d 和 /usr/local/bin/before-notebook.d
- F-037: images/docker-stacks-foundation/Dockerfile:157 — 复制 10activate-conda-env.sh 到 before-notebook.d/ 目录

## start.sh 入口脚本

- F-038: images/docker-stacks-foundation/start.sh:5 — set -e 启用错误即退出
- F-039: images/docker-stacks-foundation/start.sh:13-21 — unset_explicit_env_vars() 函数：根据 JUPYTER_ENV_VARS_TO_UNSET 环境变量（逗号分隔）取消设置指定的环境变量
- F-040: images/docker-stacks-foundation/start.sh:24-28 — 默认无命令时启动 bash
- F-041: images/docker-stacks-foundation/start.sh:32-37 — _START_SH_EXECUTED 防护：防止 CMD 中重复调用 start.sh
- F-042: images/docker-stacks-foundation/start.sh:42 — 执行 start-notebook.d/ 目录下的 hooks（以启动用户身份运行）
- F-043: images/docker-stacks-foundation/start.sh:49 — 如果容器以 root 启动（id -u == 0），则执行用户/权限重新配置
- F-044: images/docker-stacks-foundation/start.sh:61-69 — root 模式下：如果 jovyan 用户存在，通过 usermod 重命名为 NB_USER 并更新 home 目录；如果 jovyan 不存在且 NB_USER 也不存在则 fatal error
- F-045: images/docker-stacks-foundation/start.sh:72-81 — 如果 NB_UID/NB_GID 与当前用户的 UID/GID 不匹配，groupadd 创建目标组（--force --non-unique），userdel + useradd 重建用户
- F-046: images/docker-stacks-foundation/start.sh:84-88 — root 用户特殊处理：修改 /etc/passwd 中 root 的 home 为 /home/root，cp 使用 --no-preserve=ownership
- F-047: images/docker-stacks-foundation/start.sh:93-116 — 如果 NB_USER 不是 jovyan，尝试复制 /home/jovyan 到 /home/NB_USER（cp -a），失败则创建 symlink；更新工作目录
- F-048: images/docker-stacks-foundation/start.sh:120-131 — 可选 CHOWN_HOME（"1"/"yes"）chown 用户 home 目录；CHOWN_EXTRA 逗号分隔路径列表 chown
- F-049: images/docker-stacks-foundation/start.sh:134 — 将 ${CONDA_DIR}/bin 前置到 sudo secure_path
- F-050: images/docker-stacks-foundation/start.sh:137-140 — 可选 GRANT_SUDO（"1"/"yes"）：创建 /etc/sudoers.d/added-by-start-script 授予 NOPASSWD:ALL
- F-051: images/docker-stacks-foundation/start.sh:144 — 执行 before-notebook.d/ 目录下的 hooks（以 root 身份运行）
- F-052: images/docker-stacks-foundation/start.sh:151-155 — root 模式下通过 sudo --preserve-env --set-home --user 切换到 NB_USER 执行命令，显式保留 LD_LIBRARY_PATH、PATH、PYTHONPATH
- F-053: images/docker-stacks-foundation/start.sh:187-249 — 非 root 模式下：警告 GRANT_SUDO 需要 root；尝试修复 /etc/passwd 中缺少当前 UID 条目的问题（通过写临时文件再 cat 覆盖）；警告 NB_USER/NB_UID/NB_GID 不匹配需要 root；检查 home 目录写权限；执行 before-notebook.d/ hooks（以当前用户身份运行）；直接 exec 命令
- F-054: images/docker-stacks-foundation/start.sh:202-212 — 非 root 模式下修复 /etc/passwd：如果 whoami 失败（无 passwd 条目），将 jovyan 重命名为 nayvoj，追加当前 UID:GID 的 NB_USER 条目

## run-hooks.sh Hook 执行系统

- F-055: images/docker-stacks-foundation/run-hooks.sh:11-12 — 查找目录中的 *.sh 脚本 source 执行，其他可执行文件直接运行
- F-056: images/docker-stacks-foundation/run-hooks.sh:30-35 — 临时禁用 errexit（set +e）运行 hooks，防止单个 hook 失败导致启动中止；运行完恢复原始设置
- F-057: images/docker-stacks-foundation/run-hooks.sh:42-52 — .sh 文件：source 执行，失败记录 error 但继续；非 .sh 文件：检查是否可执行，可执行则运行，不可执行则忽略
- F-058: images/docker-stacks-foundation/run-hooks.sh:47-49 — 每次 source hook 后重新 set +e，因为 hook 内部可能启用了 errexit

## Base Notebook 镜像

- F-059: images/base-notebook/Dockerfile:5 — FROM $REGISTRY/$OWNER/docker-stacks-foundation（通过 ARG 可配置注册表和所有者）
- F-060: images/base-notebook/Dockerfile:18-30 — 安装额外 OS 包：fonts-liberation（matplotlib 字体）、pandoc（nbconvert 依赖）、run-one（RESTARTABLE 支持）
- F-061: images/base-notebook/Dockerfile:43-57 — 通过 mamba 安装 jupyterhub-singleuser、jupyterlab、nbclassic、notebook>=7.2.2；运行 jupyter server --generate-config；清理缓存（mamba clean、jupyter lab clean、yarn 缓存）
- F-062: images/base-notebook/Dockerfile:51 — notebook>=7.2.2 版本 pin 原因：旧版 notebook (<v7) 不限制 jupyterlab 版本，可能导致不兼容
- F-063: images/base-notebook/Dockerfile:59 — ENV JUPYTER_PORT=8888，EXPOSE 8888
- F-064: images/base-notebook/Dockerfile:63 — CMD ["start-notebook.py"]（ENTRYPOINT 是 start.sh，CMD 是 jupyter 启动器）
- F-065: images/base-notebook/Dockerfile:66-67 — 复制 start-notebook.py、start-notebook.sh、start-singleuser.py、start-singleuser.sh 到 /usr/local/bin/；复制 jupyter_server_config.py、docker_healthcheck.py 到 /etc/jupyter/
- F-066: images/base-notebook/Dockerfile:76-77 — HEALTHCHECK 配置：--interval=3s --timeout=1s --start-period=3s --retries=3，执行 /etc/jupyter/docker_healthcheck.py

## start-notebook.py 启动器

- F-067: images/base-notebook/start-notebook.py:9-15 — 检测 JUPYTERHUB_API_TOKEN 环境变量：如果存在（JupyterHub 环境），自动委托给 start-singleuser.py
- F-068: images/base-notebook/start-notebook.py:22-23 — RESTARTABLE=yes 时使用 run-one-constantly 包装命令实现自动重启
- F-069: images/base-notebook/start-notebook.py:31 — jupyter 子命令通过 DOCKER_STACKS_JUPYTER_CMD 环境变量选择，默认 "lab"
- F-070: images/base-notebook/start-notebook.py:37-38 — NOTEBOOK_ARGS 环境变量通过 shlex.split 解析后追加到命令
- F-071: images/base-notebook/start-notebook.py:41 — 命令行参数（sys.argv[1:]）直接透传给 jupyter 子命令
- F-072: images/base-notebook/start-notebook.py:44-45 — 通过 os.execvp 替换当前进程，打印完整命令行

## Jupyter Server 配置

- F-073: images/base-notebook/jupyter_server_config.py:14 — c.ServerApp.ip = "" 监听所有接口（IPv4+IPv6）
- F-074: images/base-notebook/jupyter_server_config.py:15 — c.ServerApp.open_browser = False 不在服务器端打开浏览器
- F-075: images/base-notebook/jupyter_server_config.py:18 — c.InlineBackend.figure_formats = {"png", "jpeg", "svg", "pdf"} 配置内联图形格式
- F-076: images/base-notebook/jupyter_server_config.py:21 — c.FileContentsManager.delete_to_trash = False 删除文件不进回收站
- F-077: images/base-notebook/jupyter_server_config.py:29-56 — GEN_CERT 环境变量：自动生成自签名 SSL 证书（openssl req -new -newkey=rsa:2048 -days=365 -nodes -x509），证书存放在 jupyter_data_dir()/notebook.pem，权限设为 600
- F-078: images/base-notebook/jupyter_server_config.py:59-60 — NB_UMASK 环境变量：设置 jupyter server 子进程的 umask（八进制解析）

## Minimal Notebook 镜像

- F-079: images/minimal-notebook/Dockerfile:5 — FROM $REGISTRY/$OWNER/base-notebook
- F-080: images/minimal-notebook/Dockerfile:18-38 — 安装 OS 工具：curl、git、nano-tiny、tzdata、unzip、vim-tiny、openssh-client（git-over-ssh）、less（R help 必需）、texlive-xetex/texlive-fonts-recommended/texlive-plain-generic（nbconvert LaTeX 依赖）、xclip（Linux 剪贴板支持）
- F-081: images/minimal-notebook/Dockerfile:41 — update-alternatives 将 nano 指向 nano-tiny
- F-082: images/minimal-notebook/Dockerfile:50 — 复制 Rprofile.site 到 Conda R 的 etc/ 目录（配置 R mimetype 返回选项）
- F-083: images/minimal-notebook/Dockerfile:53 — 复制 setup-scripts/ 到 /opt/setup-scripts/（供下游镜像使用）

## SciPy Notebook 镜像

- F-084: images/scipy-notebook/Dockerfile:5 — FROM $REGISTRY/$OWNER/minimal-notebook
- F-085: images/scipy-notebook/Dockerfile:17-25 — 安装编译/科学 OS 包：build-essential（cython 编译）、cm-super/dvipng（LaTeX 标签）、ffmpeg（matplotlib 动画）
- F-086: images/scipy-notebook/Dockerfile:32-62 — 通过 mamba 安装 Python 科学计算包：altair、beautifulsoup4、bokeh、bottleneck、cloudpickle、conda-forge::blas=*=openblas、cython、dask、dill、h5py、ipympl、ipywidgets、jupyterlab-git、matplotlib-base、numba、numexpr、openpyxl、pandas、patsy、protobuf、pytables、scikit-image、scikit-learn、scipy、seaborn、sqlalchemy、statsmodels、sympy、widgetsnbextension、xlrd
- F-087: images/scipy-notebook/Dockerfile:68-69 — 首次导入 matplotlib（MPLBACKEND=Agg）以预构建字体缓存

## 高级镜像

- F-088: images/r-notebook/Dockerfile:5 — r-notebook FROM minimal-notebook（不是 scipy-notebook，R 用户可能不需要 Python 科学栈的全部）
- F-089: images/julia-notebook/Dockerfile:5 — julia-notebook FROM minimal-notebook
- F-090: images/pytorch-notebook/Dockerfile:5 — pytorch-notebook FROM scipy-notebook
- F-091: images/pytorch-notebook/Dockerfile:16-21 — PyTorch 通过 pip 安装（非 conda），使用 --index-url https://download.pytorch.org/whl/cpu（CPU 版本），包含 torch、torchaudio、torchvision
- F-092: images/pytorch-notebook/ — 包含 cuda12/ 和 cuda13/ 子目录，提供 CUDA GPU 变体 Dockerfile
- F-093: images/tensorflow-notebook/ — tensorflow-notebook FROM scipy-notebook，包含 cuda/ 子目录提供 CUDA GPU 变体（含 20tensorboard-proxy-env.sh、nvidia-lib-dirs.sh）
- F-094: images/datascience-notebook/Dockerfile:5 — datascience-notebook FROM scipy-notebook，组合 Python+R+Julia 三种语言
- F-095: images/pyspark-notebook/Dockerfile:5 — pyspark-notebook FROM scipy-notebook，包含 ipython_kernel_config.py 和 setup_spark.py
- F-096: images/all-spark-notebook/Dockerfile:5 — all-spark-notebook FROM pyspark-notebook，在 PySpark 基础上添加 R（SparkR + sparklyr 支持）

## 构建系统（Makefile）

- F-097: Makefile:6-7 — REGISTRY?=quay.io，OWNER?=jupyter（可通过环境变量覆盖）
- F-098: Makefile:9 — IMG=$(REGISTRY)/$(OWNER)/$(notdir $@) 自动从目标名推导完整镜像引用
- F-099: Makefile:12-27 — CONTAINER_CLI 自动检测：docker 可用则用 docker，否则用 Apple container framework（macOS 兼容）
- F-100: Makefile:38 — export DOCKER_BUILDKIT:=1 启用 BuildKit
- F-101: Makefile:68-80 — build/% 目标：支持 DOCKER_BUILD_ARGS、ROOT_IMAGE、PYTHON_VERSION 参数；传递 --build-arg REGISTRY/OWNER/ROOT_IMAGE/PYTHON_VERSION；构建上下文为 ./images/<stack-name>/
- F-102: Makefile:71 — PYTHON_VERSION?=3.13（docker-stacks-foundation 专用）
- F-103: Makefile:81 — build-all 目标：按依赖顺序构建所有 12 个镜像
- F-104: Makefile:85-90 — check-outdated/% 目标：运行 pytest tests/by_image/docker-stacks-foundation/test_outdated.py 检查过时包
- F-105: Makefile:112-136 — hook/% 目标：构建后钩子——依次运行 write_tags_file、write_manifest、apply_tags 三个 Python 标记/清单工具
- F-106: Makefile:172-176 — test/% 目标：运行 python3 -m tests.run_tests --registry --owner --image

## Tagging 和 Manifest 系统

- F-107: tagging/apps/apply_tags.py:17-30 — apply_tags() 读取 tags_dir 下的 {prefix}-{image}.txt 文件，逐行对镜像执行 docker tag
- F-108: tagging/apps/apply_tags.py:12 — 使用 plumbum 库调用 docker 命令（plumbum.local["docker"]）
- F-109: tagging/taggers/ — 标签生成器模块：date.py（日期标签）、sha.py（commit SHA 标签）、ubuntu_version.py（Ubuntu 版本标签）、versions.py（Python/Mamba/Conda/Jupyter/R/Julia/Spark/PyTorch/TensorFlow/Java 版本标签）
- F-110: tagging/manifests/ — 清单生成器模块：apt_packages.py、conda_environment.py、julia_packages.py、r_packages.py、spark_info.py、build_info.py，均实现 ManifestInterface
- F-111: tagging/taggers/tagger_interface.py — TaggerInterface 接口，所有 tagger 实现此接口
- F-112: tagging/manifests/manifest_interface.py — ManifestInterface 接口，所有 manifest 生成器实现此接口
- F-113: tagging/apps/write_tags_file.py — 将 tagger 生成的标签写入文件
- F-114: tagging/apps/write_manifest.py — 运行 manifest 生成器，写入镜像构建信息清单
- F-115: tagging/utils/docker_runner.py — Docker 运行工具类，用于在容器内执行命令获取版本信息

## 测试系统

- F-116: tests/conftest.py:8-12 — 使用 docker Python SDK、requests、pytest、urllib3 Retry
- F-117: tests/conftest.py:19-33 — http_client fixture：requests Session 配置 Retry（total=5, backoff_factor=1, 重试 502/503/504）
- F-118: tests/conftest.py:36-41 — docker_client fixture：从环境创建 docker.DockerClient
- F-119: tests/conftest.py:44-61 — pytest_addoption 添加 --registry（docker.io/quay.io）、--owner、--image 三个必需命令行选项
- F-120: tests/conftest.py:76-90 — container fixture（function scope）：创建 TrackedContainer，yield 后自动 container.remove()
- F-121: tests/conftest.py:93-107 — free_host_port fixture：通过 socket.bind(("",0)) 获取空闲端口，SO_REUSEADDR 允许 docker-proxy 绑定同一端口
- F-122: tests/by_image/ — 每个镜像有独立测试目录：base-notebook/（容器选项、健康检查、IP、kernelspec、notebook、pandoc、启动）、docker-stacks-foundation/（包管理、包版本、用户选项、run-hooks、日志等）、minimal-notebook/（nbconvert）、scipy-notebook/（cython、matplotlib、extensions）等
- F-123: tests/shared_checks/ — 共享检查：kernelspec_check.py、nbconvert_check.py、pluto_check.py、r_mimetype_check.py
- F-124: tests/utils/tracked_container.py — TrackedContainer 工具类封装容器生命周期管理
- F-125: tests/run_tests.py — 测试入口脚本，解析 CLI 参数并运行 pytest

## CI/CD 和文档

- F-126: .github/workflows/docker-build-test-upload.yml — 主要 CI 工作流：构建、测试、推送镜像
- F-127: .github/workflows/docker-tag-push.yml — 标签推送工作流
- F-128: docs/ — Sphinx 文档源（.rst 格式），包含 using/（用户指南）、contributing/（贡献指南）、maintaining/（维护指南）
- F-129: .pre-commit-config.yaml — pre-commit 配置（black、flake8、hadolint、markdownlint 等）
- F-130: binder/Dockerfile — Binder 配置，用于在 mybinder.org 上运行示例

## 其他文件

- F-131: images/docker-stacks-foundation/fix-permissions — 权限修复脚本（确保 conda 和 home 目录权限正确）
- F-132: images/docker-stacks-foundation/initial-condarc — 初始 .condarc 配置
- F-133: images/docker-stacks-foundation/10activate-conda-env.sh — before-notebook.d hook，用于激活 conda 环境
- F-134: images/base-notebook/start-singleuser.py — JupyterHub single-user 启动脚本
- F-135: images/base-notebook/docker_healthcheck.py — Docker 健康检查脚本
- F-136: examples/ — 部署示例：docker-compose/、make-deploy/、openshift/、source-to-image/
- F-137: wiki/ — Docker Hub wiki 自动更新工具（update_wiki.py）
