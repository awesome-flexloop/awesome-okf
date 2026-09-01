---
type: Example
title: 本地文件服务配置
description: 使用nbviewer服务本地Notebook文件的配置方法、安全选项、目录浏览和访问示例
tags:
  - jupyter
  - nbviewer
  - localfiles
  - example
  - configuration
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/local/handlers.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/app.py
---

# 本地文件服务配置

nbviewer支持服务本地文件系统中的Notebook文件，通过`--localfiles`参数指定根目录。

## 基本启用

```bash
python -m nbviewer --localfiles=/path/to/notebooks
```

访问 http://localhost:5000/localfile/ 浏览Notebook目录。

## 配置文件方式

```python
# nbviewer_config.py
c = get_config()

c.NBViewer.localfiles = "/home/user/notebooks"
c.NBViewer.port = 8080
```

```bash
python -m nbviewer --config-file=nbviewer_config.py
```

## 目录结构准备

```
/home/user/notebooks/
├── analysis/
│   ├── data-exploration.ipynb
│   └── model-training.ipynb
├── reports/
│   └── quarterly-report.ipynb
└── README.md  # 非.ipynb文件不会显示
```

访问示例：
- http://localhost:8080/localfile/ — 根目录列表
- http://localhost:8080/localfile/analysis/ — analysis目录
- http://localhost:8080/localfile/analysis/data-exploration.ipynb — 渲染Notebook
- http://localhost:8080/localfile/reports/quarterly-report.ipynb — 渲染Notebook

## 安全选项

### 默认安全行为

默认情况下，LocalFileHandler实施严格的安全检查：

1. **目录遍历防护**：路径必须在指定根目录内，`../`等遍历尝试被拒绝
2. **隐藏文件过滤**：以`.`或`_`开头的文件/目录不显示（如`.git/`、`.env`、`__pycache__/`）
3. **权限检查**：文件必须有others-read权限（`chmod o+r file.ipynb`），目录必须有others-execute权限

设置others-read权限：
```bash
chmod -R o+r /home/user/notebooks/
chmod o+x /home/user/notebooks/ /home/user/notebooks/*/
```

### 放宽权限检查

**--localfile-any-user**：允许服务没有others-read权限的文件

```bash
python -m nbviewer --localfiles=/home/user/notebooks --localfile-any-user
```

适用于文件权限不便修改的环境，但安全性降低。

### 符号链接跟随

**--localfile-follow-symlinks**：使用realpath()解析符号链接

```bash
python -m nbviewer --localfiles=/home/user/notebooks --localfile-follow-symlinks
```

注意：即使跟随符号链接，解析后的最终路径仍必须在localfiles根目录内，防止链接到`/etc/passwd`等敏感文件。

### 推荐的生产安全配置

```python
# 生产环境本地文件配置
c = get_config()

c.NBViewer.localfiles = "/var/notebooks"
# 不要启用localfile_any_user和localfile_follow_symlinks
# 确保Notebook目录和文件权限正确
```

```bash
# 设置专用目录和正确权限
sudo mkdir -p /var/notebooks
sudo chown -R nbviewer:nbviewer /var/notebooks
sudo chmod -R o+r /var/notebooks
sudo find /var/notebooks -type d -exec chmod o+x {} \;
```

## 文件下载

在Notebook URL后添加`?download`参数可下载原始文件：

- http://localhost:8080/localfile/analysis/data-exploration.ipynb?download

下载时Content-Disposition设为attachment，浏览器会下载而非渲染。文件名中的逗号会被替换为下划线（Chrome兼容性处理）。

## 目录浏览

LocalFileHandler自动生成目录列表：
- 子目录在前（fa-folder-open图标），按名称排序
- .ipynb文件在后（fa-book图标），按名称排序
- 每个条目显示修改时间（UTC ISO-8601格式，带Z后缀）
- 隐藏文件/目录不显示
- 提供面包屑导航

## 格式切换

本地Notebook也支持格式切换：

- HTML（默认）：http://localhost:8080/localfile/analysis/data-exploration.ipynb
- Slides：http://localhost:8080/format/slides/localfile/analysis/data-exploration.ipynb（需要slideshow元数据）
- Code：http://localhost:8080/format/script/localfile/analysis/data-exploration.ipynb

## 缓存注意事项

本地文件的缓存键使用完整URI（包含?download参数），确保view和download不混淆。但默认缓存TTL可能导致修改Notebook后仍显示旧版本。

开发环境建议禁用缓存：
```bash
python -m nbviewer --localfiles=/path/to/notebooks --no-cache
```

或手动刷新缓存：
- http://localhost:8080/localfile/analysis/data-exploration.ipynb?flush_cache=1

## Docker中挂载本地目录

```bash
docker run -p 8080:8080 \
  -v /path/to/local/notebooks:/notebooks \
  jupyter/nbviewer \
  python -m nbviewer --localfiles=/notebooks --port=8080 --no-cache
```

docker-compose.yml示例：
```yaml
version: '2'
services:
  nbviewer:
    image: jupyter/nbviewer
    ports:
      - "8080:8080"
    volumes:
      - ./notebooks:/notebooks
    command: python -m nbviewer --localfiles=/notebooks --port=8080 --no-cache
    restart: always
```

## 完整本地文件配置示例

```python
# nbviewer_config.py - 本地文件服务
c = get_config()

c.NBViewer.port = 8080
c.NBViewer.host = "0.0.0.0"
c.NBViewer.localfiles = "/var/notebooks"

# 性能
c.NBViewer.threads = 2
c.NBViewer.rate_limit = 200  # 内部使用，限流可放宽

# 缓存
c.NBViewer.cache_expiry_min = 300   # 5分钟，本地文件更新较频繁
c.NBViewer.cache_expiry_max = 1800  # 30分钟

# 日志
c.Application.log_level = "INFO"
```

## 安全警告

启用本地文件服务时nbviewer会输出警告：
> "Serving local notebooks in /path, this can be a security risk"

在公网部署时务必注意：
1. 不要将根目录`/`或主目录设为localfiles
2. 确保目录中不包含敏感文件
3. 考虑在Nginx层添加访问控制（IP白名单、Basic Auth）
4. 不要在公网启用`--localfile-any-user`和`--localfile-follow-symlinks`

## 相关文档

- [速率限制与安全机制](../concepts/11-rate-limit-security.md)：本地文件安全检查详解
- [部署指南](../concepts/13-deployment.md)：生产部署建议
- [基本配置示例](01-basic-config.md)：通用配置
