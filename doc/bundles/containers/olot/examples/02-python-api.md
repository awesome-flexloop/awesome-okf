---
type: Example
title: Python API 打包模型
description: 使用 olot Python API 编写脚本，自动化完成 ModelCar 打包流程，包含 skopeo 和 oras-py 两种后端示例
tags: [python, api, programming, automation, modelcar]
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
  - id: oci-source
    resource: /bundles/containers/olot/references/oci-source.md
    title: "olot OCI 模块源码信源"
  - id: backend-source
    resource: /bundles/containers/olot/references/backend-source.md
    title: "olot 后端抽象层源码信源"
---

# Python API 打包模型

本示例演示如何使用 olot 的 Python API 在代码中集成 ModelCar 打包功能，适合在 CI/CD 流水线、自动化脚本或 ML 训练管道中使用。我们会展示两种后端的用法：skopeo 和纯 Python 的 oras-py。

## 前置条件

```bash
# 基础安装
pip install olot

# 如果要使用纯 Python 后端（无外部 skopeo/oras 依赖）
pip install olot[oras-py]
```

## 示例 1：使用 skopeo 后端

这是最常用的方式，依赖系统安装的 skopeo 命令：

```python
import tempfile
from pathlib import Path
from olot.basics import oci_layers_on_top
from olot.backend.skopeo import skopeo_pull, skopeo_push, is_skopeo

def package_model_with_skopeo(
    base_image: str,
    target_image: str,
    model_files: list[Path],
    modelcard: Path | None = None,
    labels: dict[str, str] | None = None,
    work_dir: Path | None = None
) -> None:
    """使用 skopeo 后端打包 ModelCar

    Args:
        base_image: 基础镜像引用，如 "quay.io/mmortari/hello-world-wait:latest"
        target_image: 目标镜像引用，如 "quay.io/user/my-model:v1"
        model_files: 要打包的模型文件路径列表
        modelcard: ModelCarD README.md 路径（可选）
        labels: 添加到镜像的标签（可选）
        work_dir: 工作目录，如不指定则创建临时目录
    """
    # 检查 skopeo 是否可用
    if not is_skopeo():
        raise RuntimeError(
            "skopeo not found. Please install skopeo first, "
            "or use oras-py backend with: pip install olot[oras-py]"
        )

    # 使用临时目录或指定目录
    cleanup = False
    if work_dir is None:
        work_dir = Path(tempfile.mkdtemp(prefix="olot-"))
        cleanup = True
    else:
        work_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Pulling base image: {base_image}")
        skopeo_pull(
            base_image,
            work_dir,
            params=["--multi-arch", "all"]
        )

        print(f"Adding {len(model_files)} model layers...")
        oci_layers_on_top(
            ocilayout=work_dir,
            model_files=model_files,
            modelcard=modelcard,
            labels=labels
        )

        print(f"Pushing to: {target_image}")
        skopeo_push(
            work_dir,
            target_image,
            params=["--multi-arch", "all"]
        )

        print("Done! Model packaged successfully.")

    finally:
        if cleanup:
            import shutil
            shutil.rmtree(work_dir, ignore_errors=True)


# === 使用示例 ===
if __name__ == "__main__":
    # 准备模型文件
    model_dir = Path("./my-model")
    model_dir.mkdir(exist_ok=True)

    # 创建示例模型文件
    (model_dir / "model.joblib").write_text("fake model content")
    (model_dir / "README.md").write_text("# My Model\n\nA demo model packaged by olot.")
    (model_dir / "config.json").write_text('{"model_type": "demo"}')

    # 调用打包函数
    package_model_with_skopeo(
        base_image="quay.io/mmortari/hello-world-wait:latest",
        target_image="quay.io/your-username/your-model:v1",
        model_files=[
            model_dir / "model.joblib",
            model_dir / "config.json",
        ],
        modelcard=model_dir / "README.md",
        labels={
            "ml.model.name": "demo-model",
            "ml.model.version": "1.0.0",
            "org.opencontainers.image.source": "https://github.com/your-username/your-repo"
        }
    )
```

## 示例 2：使用 oras-py 纯 Python 后端

这个后端不需要安装任何外部 CLI 工具，完全使用 Python 实现，适合环境受限的场景：

```python
import tempfile
from pathlib import Path
from olot.basics import oci_layers_on_top
from olot.backend.oras_py import oras_py_pull, oras_py_push, is_oras_py

def package_model_with_oras_py(
    base_image: str,
    target_image: str,
    model_files: list[Path],
    modelcard: Path | None = None,
    tls_verify: bool = True
) -> None:
    """使用 oras-py 纯 Python 后端打包 ModelCar（无外部依赖）

    Args:
        base_image: 基础镜像引用
        target_image: 目标镜像引用
        model_files: 模型文件列表
        modelcard: ModelCarD 路径（可选）
        tls_verify: 是否验证 TLS 证书
    """
    if not is_oras_py():
        raise RuntimeError(
            "oras-py not installed. Run: pip install olot[oras-py]"
        )

    with tempfile.TemporaryDirectory(prefix="olot-") as tmpdir:
        work_dir = Path(tmpdir)

        print(f"[oras-py] Pulling base image: {base_image}")
        oras_py_pull(
            base_image,
            work_dir,
            tls_verify=tls_verify
        )

        print(f"[oras-py] Adding model layers...")
        oci_layers_on_top(
            ocilayout=work_dir,
            model_files=model_files,
            modelcard=modelcard
        )

        print(f"[oras-py] Pushing to: {target_image}")
        oras_py_push(
            work_dir,
            target_image,
            tls_verify=tls_verify
        )

        print("[oras-py] Done!")


# === 使用示例 ===
if __name__ == "__main__":
    model_dir = Path("./my-model")

    package_model_with_oras_py(
        base_image="quay.io/mmortari/hello-world-wait:latest",
        target_image="quay.io/your-username/your-model:v1",
        model_files=[model_dir / "model.joblib"],
        modelcard=model_dir / "README.md"
    )
```

## 示例 3：自动检测可用后端

可以编写一个智能函数，自动检测环境中可用的后端：

```python
from pathlib import Path
from olot.basics import oci_layers_on_top

def get_backend():
    """自动检测可用的后端"""
    # 优先尝试 skopeo
    try:
        from olot.backend.skopeo import is_skopeo, skopeo_pull, skopeo_push
        if is_skopeo():
            return "skopeo", skopeo_pull, skopeo_push, {"params": ["--multi-arch", "all"]}
    except ImportError:
        pass

    # 然后尝试 oras-py
    try:
        from olot.backend.oras_py import is_oras_py, oras_py_pull, oras_py_push
        if is_oras_py():
            return "oras-py", oras_py_pull, oras_py_push, {}
    except ImportError:
        pass

    raise RuntimeError(
        "No backend available. Please:\n"
        "  1. Install skopeo, or\n"
        "  2. Run: pip install olot[oras-py]"
    )


def auto_package_model(base_image: str, target_image: str, model_dir: Path):
    """自动选择后端打包模型"""
    backend_name, pull_fn, push_fn, backend_kwargs = get_backend()
    print(f"Using backend: {backend_name}")

    import tempfile
    with tempfile.TemporaryDirectory(prefix="olot-") as tmpdir:
        work_dir = Path(tmpdir)

        # 收集模型文件
        model_files = [p for p in model_dir.iterdir() if p.is_file() and p.name != "README.md"]
        modelcard = model_dir / "README.md" if (model_dir / "README.md").exists() else None

        print(f"Found {len(model_files)} model files")

        # 拉取
        pull_fn(base_image, work_dir, **backend_kwargs)

        # 添加层
        oci_layers_on_top(
            ocilayout=work_dir,
            model_files=model_files,
            modelcard=modelcard,
            root_dir=model_dir if any(p.parent != model_dir for p in model_files) else None
        )

        # 推送
        push_fn(work_dir, target_image, **backend_kwargs)

        print(f"Success! Image pushed to: {target_image}")


# 使用
if __name__ == "__main__":
    auto_package_model(
        base_image="quay.io/mmortari/hello-world-wait:latest",
        target_image="quay.io/your-username/auto-model:latest",
        model_dir=Path("./my-model")
    )
```

## 示例 4：从 ModelCar 提取模型

反向操作：从已有的 ModelCar OCI layout 中提取出模型文件：

```python
from pathlib import Path
from olot.basics import crawl_ocilayout_blobs_to_extract

# 假设 ./existing-model 是一个包含 ModelCar 的 OCI layout
ocilayout_path = Path("./existing-model")
output_path = Path("./extracted-model")

extracted_files = crawl_ocilayout_blobs_to_extract(
    ocilayout=ocilayout_path,
    output_path=output_path,
    tar_filter_dir="/models"  # 默认值，只提取 /models 下的内容
)

print(f"Extracted {len(extracted_files)} files:")
for f in extracted_files:
    print(f"  - {f}")

# 提取的文件会在 ./extracted-model/models/ 目录下
```

## 示例 5：使用 add_modelpack 和注解

高级用法：为多架构镜像添加 ModelPack manifest 和自定义注解：

```python
from pathlib import Path
from olot.basics import oci_layers_on_top

work_dir = Path("./multi-arch-layout")
model_files = [Path("./model/model.onnx")]

oci_layers_on_top(
    ocilayout=work_dir,
    model_files=model_files,
    modelcard=Path("./model/README.md"),
    root_dir=Path("./model"),
    add_modelpack=True,  # 添加 ModelPack manifest
    annotations={
        "io.opendatahub.model.name": "my-onnx-model",
        "io.opendatahub.model.framework": "onnxruntime",
        "custom.annotation": "custom-value"
    },
    labels={
        "maintainer": "your-email@example.com",
        "version": "2.0.0"
    }
)
```

## 日志配置

在脚本中配置详细日志：

```python
import logging

# 配置根日志级别
logging.basicConfig(
    level=logging.INFO,  # 改为 logging.DEBUG 查看更详细输出
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)

# 或者只启用 olot 的 DEBUG 日志
# logging.getLogger("olot").setLevel(logging.DEBUG)
```

## 异常处理最佳实践

```python
import logging
from pathlib import Path
from olot.basics import oci_layers_on_top

logger = logging.getLogger(__name__)

def safe_package_model(ocilayout: Path, model_files: list[Path]) -> bool:
    try:
        oci_layers_on_top(
            ocilayout=ocilayout,
            model_files=model_files
        )
        return True
    except ValueError as e:
        logger.error(f"Parameter error: {e}")
        logger.error("Hint: Check if all model files are under root_dir")
        return False
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return False
```

## 相关概念

- [Python API 编程](/bundles/containers/olot/concepts/03-python-api.md)：完整的 API 参数文档
- [后端抽象层](/bundles/containers/olot/concepts/02-backends.md)：后端选择与对比
- [命令行基本使用](/bundles/containers/olot/examples/01-cli-usage.md)：CLI 版本的同一流程
