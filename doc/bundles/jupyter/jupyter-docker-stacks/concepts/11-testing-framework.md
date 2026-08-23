---
type: Concept
title: "测试框架"
description: "基于pytest+Docker SDK的容器化端到端测试框架、TrackedContainer、共享检查、并行测试"
tags: [testing, pytest, docker-sdk, tracked-container, parallel-testing, xdist]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-tests, resource: "/references/tests-source.md", title: "测试框架源码索引" }
---

# 测试框架

Jupyter Docker Stacks 使用基于 pytest 的容器化端到端测试框架，对每个镜像启动真实Docker容器，执行功能验证。测试代码位于`tests/`目录。

## 测试架构

```
tests/
├── run_tests.py          # CLI入口
├── conftest.py           # 全局fixture
├── pytest.ini            # pytest配置
├── hierarchy/            # 测试目录层级（继承关系）
├── by_image/             # 按镜像组织的测试用例
├── shared_checks/        # 跨镜像共享检查函数
└── utils/                # 工具类
```

## 测试入口：run_tests.py

```bash
python3 -m tests.run_tests --registry quay.io --owner jupyter --image base-notebook
```

等价于执行：

```bash
python3 -m pytest --numprocesses auto -m "not info" \
    tests/by_image/docker-stacks-foundation \
    tests/by_image/base-notebook \
    --registry quay.io --owner jupyter --image base-notebook
```

关键参数：
- `--numprocesses auto`：使用pytest-xdist并行测试（自动检测CPU核心数）
- `-m "not info"`：跳过标记为`@pytest.mark.info`的信息性测试（这些只打印版本信息，不做断言）
- 自动包含父镜像的测试目录（hierarchy机制）

## 全局Fixtures（conftest.py）

### docker_client

```python
@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    client = docker.from_env()
    return client
```

Session级Docker SDK客户端，所有测试共享一个连接。

### http_client

```python
@pytest.fixture(scope="session")
def http_client() -> requests.Session:
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s
```

带5次重试和指数退避的HTTP客户端。特别处理502/503/504，因为jupyter-server-proxy在代理服务启动期间会返回这些错误。

### image_name

```python
@pytest.fixture(scope="session")
def image_name(request) -> str:
    return f"{option('--registry')}/{option('--owner')}/{option('--image')}"
```

从CLI参数构建完整镜像名称。

### container（函数级）

```python
@pytest.fixture(scope="function")
def container(docker_client, image_name) -> Generator[TrackedContainer]:
    container = TrackedContainer(docker_client, image_name)
    yield container
    container.remove()
```

每个测试函数获得一个独立的TrackedContainer实例，测试结束后自动清理（停止+删除容器）。

### free_host_port

```python
@pytest.fixture(scope="function")
def free_host_port() -> Generator[int]:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", 0))
        yield s.getsockname()[1]
```

自动分配空闲主机端口。使用SO_REUSEADDR保持端口绑定状态，防止其他测试进程获取同一端口。docker-proxy同样使用SO_REUSEADDR，可以绑定到该端口。

## TrackedContainer

TrackedContainer是测试框架的核心工具类，封装Docker SDK的容器操作：

```python
class TrackedContainer:
    def __init__(self, docker_client, image_name):
        self.docker_client = docker_client
        self.image_name = image_name
        self.container = None

    def run_and_wait(self, **kwargs):
        """启动容器并等待服务就绪"""
        ...

    def get_logs(self) -> str:
        """获取容器日志"""
        ...

    def exec_cmd(self, cmd) -> tuple[int, str]:
        """在容器内执行命令，返回(退出码, 输出)"""
        ...

    def remove(self):
        """停止并删除容器"""
        ...
```

它确保：
- 容器在测试结束后被清理（上下文管理器模式）
- 端口映射自动处理
- 容器日志在失败时可获取用于调试

## 测试目录层级（hierarchy/）

与镜像层级对应，测试也具有继承关系。子镜像自动运行父镜像的所有测试：

| 镜像 | 自有测试目录 | 继承的测试 |
|------|------------|----------|
| docker-stacks-foundation | by_image/docker-stacks-foundation/ | 无 |
| base-notebook | by_image/base-notebook/ | foundation测试 |
| minimal-notebook | by_image/minimal-notebook/ | foundation+base测试 |
| ... | ... | 所有父层测试 |

hierarchy/images_hierarchy.py定义了测试继承关系（与镜像层级一致），get_test_dirs()函数递归收集需要运行的测试目录。

## 按镜像测试用例

### docker-stacks-foundation 测试

| 测试文件 | 测试内容 |
|---------|---------|
| test_python_version.py | Python版本正确性 |
| test_package_managers.py | conda/mamba可用且工作正常 |
| test_packages.py | 基础包（jupyter_core等）已安装 |
| test_user_options.py | NB_USER/NB_UID/GRANT_SUDO等用户选项功能 |
| test_run_hooks.py | Hook机制（start-notebook.d/before-notebook.d） |
| test_outdated.py | 检查过时包 |
| test_logging.py | 日志输出格式正确 |
| test_units.py | 单元测试（fix-permissions等脚本） |
| test_rosetta_junk.py | Rosetta缓存已清理 |

### base-notebook 测试

| 测试文件 | 测试内容 |
|---------|---------|
| test_container_options.py | 容器启动选项（端口、环境变量等） |
| test_healthcheck.py | HEALTHCHECK正常工作 |
| test_ips.py | 服务器监听正确地址 |
| test_kernelspecs.py | Jupyter内核规范正确注册 |
| test_notebook.py | Notebook基本功能（创建、执行） |
| test_pandoc.py | pandoc已安装且可用 |
| test_start_container.py | 容器启动流程 |

### minimal-notebook 测试

| 测试文件 | 测试内容 |
|---------|---------|
| test_nbconvert.py | nbconvert（含TeX PDF导出）功能 |

### scipy-notebook 测试

| 测试文件 | 测试内容 |
|---------|---------|
| test_matplotlib.py | matplotlib绘图功能、字体缓存 |
| test_cython.py | Cython编译扩展功能 |
| test_extensions.py | JupyterLab扩展正常加载 |

### 专项镜像测试

每个专项镜像（r/julia/pytorch/tensorflow/pyspark/datascience/all-spark）都有对应的测试，验证其核心功能：
- r-notebook：R内核执行、R包安装
- julia-notebook：Julia内核执行、Pluto支持
- pytorch-notebook：PyTorch导入、CUDA可用性（GPU变体）
- tensorflow-notebook：TensorFlow导入、TensorBoard代理
- pyspark-notebook：Spark初始化、PyArrow、Spark UI
- datascience-notebook：三语言内核可用
- all-spark-notebook：SparkR和sparklyr可用

## 共享检查（shared_checks/）

跨多个镜像复用的验证函数：

| 模块 | 功能 |
|------|------|
| kernelspec_check.py | 检查Jupyter内核规范（Python/R/Julia） |
| nbconvert_check.py | 检查nbconvert执行notebook导出 |
| pluto_check.py | 检查Julia Pluto notebook支持 |
| r_mimetype_check.py | 检查R图形MIME类型 |

这些函数被多个镜像的测试调用，避免重复代码。

## 测试标记

pytest标记用于分类测试：

| 标记 | 说明 |
|------|------|
| `@pytest.mark.info` | 信息性测试（只打印版本，不做断言），默认跳过 |
| 无标记 | 功能验证测试 |

## 工具模块（utils/）

| 模块 | 功能 |
|------|------|
| tracked_container.py | TrackedContainer类实现 |
| conda_package_helper.py | Conda包查询辅助函数 |
| wait.py | 端口/HTTP等待工具（轮询直到服务就绪） |

## 运行测试

### 测试单个镜像

```bash
make test/base-notebook
```

### 测试所有镜像

```bash
make test-all
```

### 手动运行pytest

```bash
python3 -m pytest tests/by_image/base-notebook/ \
    --registry quay.io --owner jupyter --image base-notebook \
    -v
```

### 运行特定测试

```bash
python3 -m pytest tests/by_image/base-notebook/test_notebook.py \
    --registry quay.io --owner jupyter --image base-notebook \
    -v -k "test_execute_notebook"
```

## 并行测试

pytest-xdist的`--numprocesses auto`自动并行执行测试。由于每个测试启动独立容器，并行度取决于Docker daemon的资源容量。free_host_port fixture确保并行测试的端口不会冲突。

## 相关概念

- [构建与CI/CD](12-build-ci-cd.md)
- [Tagging元数据系统](10-tagging-system.md)
- [最佳实践](13-best-practices.md)
