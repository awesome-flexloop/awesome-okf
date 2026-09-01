# 信源参考

本目录包含 conmon 源码分析的信源登记文件，每个文件对应一个或多个源码模块的API参考。

---

## 信源列表

| 信源文件 | 覆盖源码 | 主要内容 |
|---------|---------|---------|
| [readme-source.md](readme-source.md) | README.md | 项目定位、功能概述、构建依赖、安装方式 |
| [conmon-source.md](conmon-source.md) | src/conmon.c | 主入口main函数、双fork守护进程化、GMainLoop事件循环、进程管理 |
| [cgroup-source.md](cgroup-source.md) | src/cgroup.c | cgroup v1/v2版本判断、OOM事件监听、memory.events解析 |
| [oom-source.md](oom-source.md) | src/oom.c | oom_score_adj读写、自我保护机制、attempt_oom_adjust/reset_oom_adjust |

---

## 源码路径映射

所有信源对应源码位于：`d:\spaces\SpecWeave\external\dao\action\Containers\conmon\`

| 源码文件 | 对应信源 |
|---------|---------|
| README.md | [readme-source.md](readme-source.md) |
| src/conmon.c | [conmon-source.md](conmon-source.md) |
| src/cgroup.c | [cgroup-source.md](cgroup-source.md) |
| src/oom.c | [oom-source.md](oom-source.md) |

```{toctree}
:maxdepth: 1

readme-source
conmon-source
cgroup-source
oom-source
```
