---
title: v6到v7迁移指南
type: concept
bundle: jupyter-notebook
chapter: "11"
difficulty: intermediate
tags: ["migration", "compatibility", "upgrade", "v6", "v7"]
prerequisites: ["00-introduction", "05-shim-layer"]
sources: ["F-003", "F-014"]
next: []
---

# 11 | v6到v7迁移指南

本指南帮助你从Jupyter Notebook 6.x迁移到7.x，涵盖配置迁移、扩展迁移、API变化和常见问题。

## 为什么迁移到v7

| 方面 | Notebook 6.x | Notebook 7.x |
|------|-------------|-------------|
| 前端技术栈 | 旧版JS + require.js | TypeScript + Lumino + React |
| 扩展生态 | nbextension（将弃用） | JupyterLab prebuilt extension |
| 协作功能 | 无 | 内置JupyterLab协作支持 |
| 调试器 | 无 | 内置调试器支持 |
| 主题系统 | 基础CSS | JupyterLab主题系统 |
| 国际化 | 无 | 完整i18n支持 |
| 性能 | 单页面架构 | 现代化SPA架构 |
| 安全维护 | 仅安全修复 | 活跃开发 |

## 破坏性变化总览

### 1. 服务器架构变化

Notebook 7不再是独立服务器，而是Jupyter Server的扩展：

| 变化 | v6 | v7 |
|------|----|----|
| 服务器类 | `NotebookApp` | `JupyterNotebookApp` (作为Jupyter Server扩展) |
| 配置文件 | `jupyter_notebook_config.py` | `jupyter_server_config.py` |
| 启动命令 | `jupyter notebook` | `jupyter notebook`（保留）或 `jupyter server` |
| 内核管理 | Notebook内置 | jupyter_server提供 |

### 2. 配置项迁移

大多数 `c.NotebookApp.*` 配置需要迁移：

| v6配置 | v7配置 | 备注 |
|--------|--------|------|
| `c.NotebookApp.port` | `c.ServerApp.port` | 服务器端口 |
| `c.NotebookApp.ip` | `c.ServerApp.ip` | 监听地址 |
| `c.NotebookApp.notebook_dir` | `c.ServerApp.root_dir` | 工作目录 |
| `c.NotebookApp.token` | `c.ServerApp.token` | 认证token |
| `c.NotebookApp.password` | `c.ServerApp.password` | 密码 |
| `c.NotebookApp.base_url` | `c.ServerApp.base_url` | URL前缀 |
| `c.NotebookApp.open_browser` | `c.LabServerApp.open_browser` | 自动打开浏览器 |
| `c.NotebookApp.allow_origin` | `c.ServerApp.allow_origin` | CORS |
| `c.NotebookApp.disable_check_xsrf` | `c.ServerApp.disable_check_xsrf` | XSRF |
| `c.NotebookApp.allow_root` | `c.ServerApp.allow_root` | root运行 |
| `c.NotebookApp.certfile` | `c.ServerApp.certfile` | SSL证书 |
| `c.NotebookApp.keyfile` | `c.ServerApp.keyfile` | SSL密钥 |
| `c.NotebookApp.trust_xheaders` | `c.ServerApp.trust_xheaders` | 反向代理头 |

> **注意**: `notebook_shim` 包提供自动映射，旧配置在v7中仍可工作（带警告），但建议迁移。

### 3. 扩展系统变化

这是**最大的破坏性变化**：

| 方面 | v6 (nbextension) | v7 (labextension) |
|------|-----------------|-------------------|
| 扩展类型 | nbextension / serverextension | JupyterLab prebuilt extension |
| 安装方式 | `jupyter nbextension install` | `pip install` 或 `jlpm add` |
| 包格式 | JS文件 + `define()` | ES Module + TypeScript |
| UI框架 | jQuery / Bootstrap | Lumino / React |
| 开发工具 | 无标准工具链 | JupyterLab Extension SDK |
| 兼容JupyterLab | 不兼容 | 完全兼容 |

#### nbextension不再工作

v6的nbextension（基于require.js的AMD模块）**不会自动在v7中工作**。你需要：

1. **寻找替代品**：许多nbextension已有JupyterLab版本
2. **使用兼容层**：`nbclassic` 提供v6经典界面，可运行旧nbextension
3. **重写扩展**：使用JupyterLab Extension SDK重写

### 4. 自定义CSS迁移

v6自定义CSS：
```
~/.jupyter/custom/custom.css
```

v7中仍然支持（CustomCssHandler），但由于DOM结构完全不同，旧的CSS选择器很可能不工作。建议：
- 使用JupyterLab主题系统（`@jupyterlab/theme-*`）
- 扩展中注入CSS（通过插件的style导入）

### 5. 模板定制变化

v6的Jinja2模板（`tree.html`, `notebooks.html`等）在v7中存在但结构完全不同。由于前端是SPA，模板只是HTML壳，大部分UI由JavaScript渲染。模板定制能力大幅降低，推荐通过前端扩展定制UI。

## 迁移步骤

### 第一步：备份现有配置

```bash
# 备份v6配置
cp ~/.jupyter/jupyter_notebook_config.py ~/.jupyter/jupyter_notebook_config.py.bak

# 记录已安装扩展
jupyter nbextension list > nbextensions-backup.txt
jupyter serverextension list > serverextensions-backup.txt
```

### 第二步：安装Notebook 7

```bash
# 建议在虚拟环境中安装
pip install --upgrade "notebook>=7.0"

# 验证安装
jupyter notebook --version
# 应输出 7.x.x
```

### 第三步：配置迁移

```bash
# 创建新的配置文件（如果不存在）
jupyter server --generate-config

# 编辑 jupyter_server_config.py
# 将旧的 c.NotebookApp.* 配置手动迁移到 c.ServerApp.* / c.LabServerApp.*
```

#### 配置迁移示例

**v6配置**：
```python
# jupyter_notebook_config.py
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.notebook_dir = '/home/user/projects'
c.NotebookApp.open_browser = False
c.NotebookApp.token = 'my-secret-token'
c.NotebookApp.allow_origin = '*'
```

**v7配置**：
```python
# jupyter_server_config.py
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.root_dir = '/home/user/projects'
c.LabServerApp.open_browser = False
c.IdentityProvider.token = 'my-secret-token'
c.ServerApp.allow_origin = '*'
```

> **注意**: v7中token配置从 `ServerApp.token` 迁移到 `IdentityProvider.token`，但通过shim层两者都可用。

### 第四步：扩展迁移

#### 常用扩展的v7/Lab版本

| v6扩展 | v7/Lab替代 | 安装 |
|--------|-----------|------|
| nbextensions_configurator | 内置（Settings Editor） | 不需要 |
| jupyter_contrib_nbextensions | 各功能独立Lab扩展 | 搜索JupyterLab替代 |
| jupyter-widgets | @jupyter-widgets/jupyterlab-manager | `pip install ipywidgets` |
| rise (幻灯片) | jupyterlab-rise | `pip install jupyterlab-rise` |
| jupyterlab-variableinspector | @lckr/jupyterlab_variableinspector | `pip install lckr-jupyterlab-variableinspector` |
| jupyter_bokeh | jupyter-bokeh | `pip install jupyter_bokeh` |
| plotly | 内置支持 | `pip install plotly` |

#### 检查扩展兼容性

```bash
# 查看已安装的lab扩展
jupyter labextension list

# 如果看到某个扩展只支持v6，需要寻找替代
```

### 第五步：测试验证

```bash
# 启动Notebook测试
jupyter notebook

# 验证以下功能：
# 1. 文件浏览器正常工作
# 2. Notebook能创建和运行
# 3. 终端可用
# 4. 常用扩展加载正常
# 5. 自定义设置生效
```

## 需要nbclassic的场景

如果你依赖以下v6功能，可能需要安装nbclassic：

1. **旧nbextension必须使用**：`pip install nbclassic` 提供v6经典UI
2. **特定模板定制**：nbclassic使用v6的模板系统
3. **教学环境需要稳定经典UI**：nbclassic专门为经典界面兼容而设计

```bash
# 安装nbclassic
pip install nbclassic

# 启动经典界面
jupyter nbclassic
# 或在Notebook 7中检测到nbclassic时可切换
```

> **信源**: app.py中检测nbclassic_enabled（F-021）

## 自定义Kernel/Contents Manager迁移

如果你自定义了Kernel Manager或Contents Manager：

```python
# v6
c.NotebookApp.kernel_manager_class = 'myapp.MyKernelManager'
c.NotebookApp.contents_manager_class = 'myapp.MyContentsManager'

# v7
c.ServerApp.kernel_manager_class = 'myapp.MyKernelManager'
c.ServerApp.contents_manager_class = 'myapp.MyContentsManager'
```

大多数Manager类API在Jupyter Server中保持兼容。

## API变化（Python后端）

### 导入路径变化

| v6导入 | v7导入 |
|--------|--------|
| `from notebook.notebookapp import NotebookApp` | `from notebook.app import JupyterNotebookApp` |
| `from notebook.base.handlers import IPythonHandler` | `from jupyter_server.base.handlers import JupyterHandler` |
| `notebook.utils.url_path_join` | `from jupyter_server.utils import url_path_join` |
| `notebook.services.contents.manager` | `from jupyter_server.services.contents.manager` |

### tornado handlers

如果你的serverextension添加了自定义Handler：
- 基类从 `IPythonHandler` 变为 `JupyterHandler`
- 认证装饰器从 `@authenticated` 变为 `@web.authenticated`（从tornado.web导入）
- 扩展app属性名可能变化

### 页面渲染

如果你需要渲染自定义页面：
- 继承 `NotebookBaseHandler` 或直接使用 `ExtensionHandlerMixin`
- 使用 `self.render_template()` 渲染Jinja2模板
- 模板目录需要通过 `settings["template_path"]` 配置

## API变化（前端）

### 全局变量变化

| v6全局变量 | v7 |
|-----------|-----|
| `IPython` | 不存在（模块化导入） |
| `Jupyter` | 不存在（通过插件系统获取服务） |
| `require` | 不存在（使用ES import） |
| `$` (jQuery) | 不存在（不依赖jQuery） |

### 前端扩展开发模式

v6 nbextension模式：
```javascript
// v6: AMD模块
define(['base/js/namespace'], function(Jupyter) {
    function load_ipython_extension() {
        Jupyter.notebook.events.on('kernel_ready.Kernel', function() {
            // ...
        });
    }
    return { load_ipython_extension: load_ipython_extension };
});
```

v7 JupyterLab扩展模式：
```typescript
// v7: JupyterLab插件
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
    id: 'my-extension:plugin',
    autoStart: true,
    activate: (app: JupyterFrontEnd) => {
        app.serviceManager.kernels.ready.then(() => {
            // ...
        });
    }
};

export default plugin;
```

## Docker部署迁移

### v6 Dockerfile（旧）

```dockerfile
FROM jupyter/base-notebook:latest
# ...
RUN jupyter nbextension install my-extension && \
    jupyter nbextension enable my-extension
```

### v7 Dockerfile（新）

```dockerfile
FROM quay.io/jupyter/docker-stacks-foundation:latest
# ...
RUN pip install my-jupyterlab-extension
# prebuilt extension，无需额外启用命令
```

## 常见问题排查

### Q: 升级后显示404或空白页面

**原因**：前端构建产物缺失或浏览器缓存。

**解决**：
```bash
pip install --force-reinstall notebook
jupyter lab build  # 如果使用源码安装
# 清除浏览器缓存或使用无痕模式
```

### Q: 旧配置不生效

**原因**：配置文件路径或配置节名变化。

**解决**：
1. 启动时检查日志中的弃用警告
2. 将配置迁移到 `jupyter_server_config.py`
3. 使用 `c.ServerApp.*` 和 `c.LabServerApp.*`

### Q: nbextension找不到

**原因**：v7不支持nbextension机制。

**解决**：
1. 寻找对应的JupyterLab扩展版本
2. 安装nbclassic作为过渡方案

### Q: 自定义CSS不生效

**原因**：v7的DOM结构完全不同。

**解决**：
1. 使用浏览器开发者工具检查新的DOM结构
2. 更新CSS选择器
3. 考虑使用JupyterLab主题扩展替代

### Q: `jupyter notebook` 命令报错

**原因**：可能有旧版本的Notebook配置冲突。

**解决**：
```bash
pip uninstall -y notebook jupyter_server jupyterlab
pip install "notebook>=7.0"
```

### Q: 内核无法启动

**原因**：可能是ipykernel版本不兼容。

**解决**：
```bash
pip install --upgrade ipykernel
python -m ipykernel install --user
```

### Q: 端口/token配置不生效

**原因**：v7中这些配置属于 `ServerApp`，如果 `jupyter_notebook_config.py` 和 `jupyter_server_config.py` 都有配置，可能冲突。

**解决**：统一使用 `jupyter_server_config.py`。

## 迁移检查清单

- [ ] 备份v6配置和扩展列表
- [ ] 安装Notebook 7.x
- [ ] 迁移配置项到 `jupyter_server_config.py`
- [ ] 更新所有 `c.NotebookApp.*` → `c.ServerApp.*` / `c.LabServerApp.*`
- [ ] 审查已安装的nbextension，寻找Lab替代品
- [ ] 测试Notebook创建、运行、保存功能
- [ ] 测试终端功能
- [ ] 测试文件上传/下载
- [ ] 测试自定义kernel/contents manager（如果有）
- [ ] 更新Docker部署配置
- [ ] 更新自定义扩展（如果有）
- [ ] 清除浏览器缓存
- [ ] 团队成员文档更新

## 参考资源

- [Jupyter Notebook 7 Migration Guide](https://jupyter-notebook.readthedocs.io/en/latest/migrate_to_notebook7.html)
- [JupyterLab Extension Documentation](https://jupyterlab.readthedocs.io/en/stable/extension/)
- [nbclassic GitHub](https://github.com/jupyter/nbclassic)
- [notebook_shim GitHub](https://github.com/jupyter/notebook_shim)
- [Jupyter Server Documentation](https://jupyter-server.readthedocs.io/)
