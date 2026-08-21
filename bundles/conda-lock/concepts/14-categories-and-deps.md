---
okf_version: "0.2"
type: "concept"
title: "依赖类别与传播"
sources:
  - "conda_lock/lockfile/__init__.py"
  - "conda_lock/models/lock_spec.py"
  - "conda_lock/lockfile/v2prelim/models.py"
---

# 依赖类别与传播

conda-lock 支持依赖类别（category）机制，允许将依赖分组为 main（生产依赖）、dev（开发依赖）、test（测试依赖）、docs（文档依赖）等自定义类别。类别标签通过 BFS 算法从显式依赖向传递依赖传播，支持选择性安装（如生产环境只安装 main，开发环境安装 main+dev+test）。

## 为什么需要类别

在实际项目中，不同场景需要不同的依赖集合：

- **生产环境**：只需要运行应用的核心依赖（main）
- **开发环境**：需要测试框架、lint 工具、文档生成器（main + dev + test + docs）
- **CI 环境**：需要测试依赖但不需要文档工具（main + test）

conda-lock 的 category 机制允许在一个锁文件中锁定所有依赖，安装时通过选项选择需要的类别集合。

[F-001]

## 类别定义

### 在源文件中标记类别

**environment.yml 扩展语法**：

```yaml
dependencies:
  # main 类别（默认）
  - python=3.10
  - numpy
  - pandas
  # dev 类别
  - pytest:
      category: dev
  - black:
      category: dev
  # docs 类别
  - sphinx:
      category: docs
  # pip 子段也支持类别
  - pip:
      - requests>=2.28        # main
      - pytest-cov:           # dev
          category: dev
```

[F-002]

**pyproject.toml**（通过 Poetry 的 dependency groups 或 PEP 621 optional-dependencies）：

```toml
[project]
dependencies = ["numpy", "pandas"]  # main

[project.optional-dependencies]
dev = ["pytest", "black"]    # category: dev
docs = ["sphinx"]            # category: docs
```

[F-003]

默认情况下，不指定 category 的依赖归入 `main` 类别。

## apply_categories()：BFS 传播算法

求解器只知道显式依赖的类别，传递依赖的类别需要通过传播算法推断。核心思想：**如果包 A 是 dev 类别的显式依赖，那么 A 的所有传递依赖也应该标记为 dev**（除非它们已经是 main）。

```python
# conda_lock/lockfile/__init__.py

def apply_categories(
    lockfile: Lockfile,
    specs: Dict[str, List[Dependency]],
    categories: Optional[Set[str]] = None,
) -> Lockfile:
    """从显式依赖向传递依赖传播 category 标签。

    使用 BFS 遍历依赖图：
    1. 首先标记所有显式依赖（用户在源文件中指定的包）的 categories
    2. BFS 遍历依赖图，将每个包的 categories 传播给它的直接依赖
    3. 最后通过 _truncate_main_category() 清理
    """
    # 构建 name → LockedDependency 映射（按平台分组）
    pkgs_by_platform = {}
    for pkg in lockfile.package:
        pkgs_by_platform.setdefault(pkg.platform, {})[pkg.name] = pkg

    # 1. 标记显式依赖的初始 categories
    explicit_categories = {}  # (platform, name) → Set[str]
    for platform, deps in specs.dependencies.items():
        for dep in deps:
            key = (platform, dep.name)
            if dep.manager == "conda":  # 仅处理 conda 包的传播
                explicit_categories.setdefault(key, set()).add(dep.category)

    # 2. BFS 传播
    for platform in lockfile.metadata.platforms:
        pkgs = pkgs_by_platform.get(platform, {})
        visited = set()
        queue = list(explicit_categories.get((platform, name), set())
                     for name in pkgs)

        # 初始化：显式依赖的 categories
        for name, pkg in pkgs.items():
            key = (platform, name)
            if key in explicit_categories:
                pkg.categories = set(explicit_categories[key])
                visited.add(name)

        # BFS：将 categories 传播给传递依赖
        while queue:
            # ... 遍历每个包，将其 categories 添加到其依赖的 categories 中
```

[F-004]

### 传播示例

考虑以下依赖关系：

```
pytest (dev)
  ├── iniconfig
  ├── packaging
  ├── pluggy
  └── tomli

numpy (main)
  └── libgcc-ng (main)
```

传播过程：
1. 初始标记：pytest={dev}, numpy={main}
2. BFS 第一层：pytest 的依赖 iniconfig/packaging/pluggy/tomli 获得 {dev}
3. BFS 第二层：numpy 的依赖 libgcc-ng 获得 {main}
4. 最终：
   - pytest: {dev}
   - numpy: {main}
   - iniconfig: {dev}
   - packaging: {dev}
   - pluggy: {dev}
   - tomli: {dev}
   - libgcc-ng: {main}

[F-005]

### 一包多类别的情况

考虑 packaging 包被 numpy（main）和 pytest（dev）同时依赖的情况：

```
pytest (dev) ──→ packaging
numpy (main) ──→ packaging
```

传播过程：
1. 初始标记：pytest={dev}, numpy={main}
2. packaging 通过 pytest 获得 {dev}
3. packaging 通过 numpy 获得 {main}
4. packaging 的 categories = {main, dev}
5. `_truncate_main_category()` 截断：main 优先 → packaging.categories = {main}

这就是 v2 格式需要 categories 集合而非单值的原因——传播过程中一个包可能同时属于多个类别。

[F-006]

## _truncate_main_category()：main 截断规则

```python
def _truncate_main_category(lockfile: Lockfile):
    """main category 的包移除其他 category。

    规则：如果一个包属于 main（生产依赖），
    即使它也通过 dev 路径被依赖，仍然只标记为 main。

    理由：生产安装时只安装 main，如果一个包同时是 main 和 dev，
    它在生产环境中已经安装，不需要额外标记 dev。
    这样避免了安装 dev 时重复安装已在 main 中的包。
    """
    for pkg in lockfile.package:
        if "main" in pkg.categories:
            pkg.categories = {"main"}
```

[F-007]

这个规则确保：
- 生产环境安装 `main` 类别时，所有核心依赖都被安装
- 开发环境安装 `main + dev` 时，dev 中与 main 重叠的包不会重复处理
- 类别标记清晰：main 包就是生产依赖，dev 包是纯开发依赖（main 的真超集）

## 安装时类别过滤

```bash
# 仅安装 main（生产环境，默认）
conda-lock install --name myenv conda-lock.yml

# 安装 main + dev（开发环境）
conda-lock install --name myenv --dev conda-lock.yml

# 安装 main + dev + test + docs
conda-lock install --name myenv --dev --extras test --extras docs conda-lock.yml
```

```python
# install 命令内部逻辑
categories = {"main"}
if dev:
    categories.add("dev")
for extra in extras:
    categories.add(extra)

# 过滤锁文件中的包
filtered_packages = [
    pkg for pkg in lockfile.package
    if pkg.categories & categories  # 集合交集非空
]
```

[F-008]

## v1 单 category vs v2 categories 集合

| 特性 | v1 (category: str) | v2 (categories: Set[str]) |
|------|-------------------|--------------------------|
| 每个包类别数 | 1 个 | 多个 |
| 一包多类别 | 需要多条记录（同 key 不同 category） | 单条记录，categories 集合 |
| 存储效率 | 低（冗余记录） | 高（去重） |
| category 传播 | 需要在多条记录间同步 | 直接操作集合 |
| 当前版本 | 遗留兼容 | 默认使用 |

[F-009]

v2 的 categories 集合设计动机：
1. **去重**：同一份包不需要存储多条记录
2. **传播效率**：BFS 传播时直接操作集合，无需处理重复记录
3. **表达力**：准确表达"一个包同时属于多个类别"的语义

## 自定义 category

除了内置的 `main` 和 `dev`，用户可以创建任意自定义 category：

```yaml
dependencies:
  - python=3.10           # main
  - pytest:               # dev
      category: dev
  - sphinx:               # docs
      category: docs
  - cudatoolkit:          # gpu
      category: gpu
```

安装时通过 `--extras` 指定：

```bash
# 安装 main + docs
conda-lock install --name myenv --extras docs conda-lock.yml

# 安装 main + dev + gpu（GPU 开发环境）
conda-lock install --name myenv --dev --extras gpu conda-lock.yml
```

[F-010]

## 相关概念

- [锁文件 v1/v2 格式](06-lockfile-formats.md)
- [源文件解析](07-source-parsers.md)
- [四类依赖模型](05-dependency-types.md)
- [CLI 命令体系](11-cli-commands.md)
- [开发依赖与 category 过滤示例](../examples/dev-dependencies.md)
