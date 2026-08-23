---
type: Reference
title: "测试框架源码索引"
description: "Jupyter Docker Stacks 测试框架（tests/）源码信源登记"
tags: [testing, pytest, docker, ci, validation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-run-tests, resource: "external/libs/jupyter/docker-stacks/tests/run_tests.py", title: "run_tests.py（测试入口CLI）" }
  - { id: src-conftest, resource: "external/libs/jupyter/docker-stacks/tests/conftest.py", title: "conftest.py（pytest全局fixture）" }
  - { id: src-tracked, resource: "external/libs/jupyter/docker-stacks/tests/utils/tracked_container.py", title: "tracked_container.py（容器生命周期管理）" }
  - { id: src-hierarchy-test, resource: "external/libs/jupyter/docker-stacks/tests/hierarchy/images_hierarchy.py", title: "hierarchy/images_hierarchy.py（测试目录层级）" }
  - { id: src-by-image, resource: "external/libs/jupyter/docker-stacks/tests/by_image/", title: "by_image/（按镜像组织的测试用例）" }
  - { id: src-shared, resource: "external/libs/jupyter/docker-stacks/tests/shared_checks/", title: "shared_checks/（跨镜像共享检查）" }
---

# 测试框架源码索引

tests/ 目录是 Jupyter Docker Stacks 的容器化测试框架，基于 pytest + Docker SDK，对每个镜像运行端到端验证。

## 目录结构

```
tests/
├── run_tests.py              # CLI入口：python -m tests.run_tests
├── conftest.py               # 全局pytest fixture配置
├── pytest.ini                # pytest配置
├── __init__.py
├── hierarchy/
│   ├── __init__.py
│   ├── get_test_dirs.py      # 根据镜像名获取测试目录
│   └── images_hierarchy.py   # 镜像测试层级（继承父镜像测试）
├── by_image/                 # 按镜像组织的测试
│   ├── docker-stacks-foundation/
│   │   ├── test_python_version.py
│   │   ├── test_package_managers.py
│   │   ├── test_packages.py
│   │   ├── test_user_options.py
│   │   ├── test_run_hooks.py
│   │   ├── test_outdated.py
│   │   ├── test_logging.py
│   │   ├── test_units.py
│   │   └── test_rosetta_junk.py
│   ├── base-notebook/
│   │   ├── test_container_options.py
│   │   ├── test_healthcheck.py
│   │   ├── test_ips.py
│   │   ├── test_kernelspecs.py
│   │   ├── test_notebook.py
│   │   ├── test_pandoc.py
│   │   └── test_start_container.py
│   ├── minimal-notebook/
│   │   └── test_nbconvert.py
│   ├── scipy-notebook/
│   │   ├── test_matplotlib.py
│   │   ├── test_cython.py
│   │   └── test_extensions.py
│   ├── r-notebook/
│   ├── julia-notebook/
│   ├── datascience-notebook/
│   ├── pytorch-notebook/
│   ├── tensorflow-notebook/
│   ├── pyspark-notebook/
│   └── all-spark-notebook/
├── shared_checks/            # 跨镜像共享检查函数
│   ├── kernelspec_check.py
│   ├── nbconvert_check.py
│   ├── pluto_check.py
│   └── r_mimetype_check.py
└── utils/
    ├── tracked_container.py  # TrackedContainer：自动清理的Docker容器封装
    ├── conda_package_helper.py
    └── wait.py               # 等待工具（端口/HTTP就绪）
```

## 核心组件

**TrackedContainer**（utils/tracked_container.py）：
- 封装 Docker SDK 容器操作
- 上下文管理器自动停止和删除容器
- 提供 `run_and_wait()`、`get_logs()`、`exec_cmd()` 等方法

**全局 Fixture**（conftest.py）：
- `docker_client`：Docker SDK客户端（session级）
- `http_client`：带重试的requests Session（5次重试+退避）
- `image_name`：从CLI参数构建镜像全名
- `container`：函数级TrackedContainer实例
- `free_host_port`：自动分配空闲主机端口

**测试入口**（run_tests.py）：
- 参数：--registry, --owner, --image
- 使用 pytest-xdist 并行执行（--numprocesses auto）
- 跳过 info 标记的测试（-m "not info"）
- 通过 hierarchy 自动包含父镜像测试目录
