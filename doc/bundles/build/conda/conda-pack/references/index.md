# 信源登记簿

本目录登记 conda-pack OKF Wiki 的所有源码信源，每个信源文件对应源码中的一个核心模块。

## 信源清单

* [core.py 核心模块](core-source.md) — `conda_pack/core.py`，包含 CondaEnv、File、Packer、pack() 等所有核心逻辑（约1337行）。
* [formats.py 归档格式模块](formats-source.md) — `conda_pack/formats.py`，包含 TarArchive、ZipArchive、SquashFSArchive、NoArchive 和并行压缩写入器（约577行）。
* [prefixes.py 前缀替换模块](prefixes-source.md) — `conda_pack/prefixes.py`，文本/二进制前缀替换、shebang 正则、macOS codesign、Windows distlib 入口点处理（约196行）。
* [cli.py 与辅助模块](cli-source.md) — `conda_pack/cli.py`（CLI入口，约183行）、`conda_pack/compat.py`（跨平台兼容，约45行）、`conda_pack/_progress.py`（进度条，约99行）。

```{toctree}
:hidden:
:maxdepth: 7

cli-source
core-source
formats-source
prefixes-source
```
