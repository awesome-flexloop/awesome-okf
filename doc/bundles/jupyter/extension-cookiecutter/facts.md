---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- jupyterlab
- cookiecutter
- extension
- template
sources:
- ../../../../../external/libs/jupyter/extension-cookiecutter/README.md
- ../../../../../external/libs/jupyter/extension-cookiecutter/cookiecutter.json
- ../../../../../external/libs/jupyter/extension-cookiecutter/hooks/post_gen_project.py
type: Facts
title: extension-cookiecutter 源码事实清单
---

# extension-cookiecutter Facts

## 项目元数据

- F-001: README.md:1 — 项目名称为 "Jupyter Server Extension CookieCutter"
- F-002: README.md:5-6 — 基于 cookiecutter 的模板，用于创建 Jupyter Server 扩展
- F-003: README.md:12-14 — 使用方式：pip install cookiecutter 后运行 cookiecutter 命令从 GitHub 生成项目

## Cookiecutter 配置

- F-004: cookiecutter.json:2 — author_name 默认值为 "My Name"
- F-005: cookiecutter.json:3 — author_email 默认值为 "me@me.com"
- F-006: cookiecutter.json:4 — package_name 默认值为 "my_server_extension"
- F-007: cookiecutter.json:5 — project_short_description 默认值为 "A Jupyter Server extension."
- F-008: cookiecutter.json:6 — has_binder 默认值为 "n"（是否包含 Binder 配置）
- F-009: cookiecutter.json:7 — repository 默认值为 "https://github.com/github_username/{{ cookiecutter.package_name }}"，使用 package_name 插值

## 生成后 Hook

- F-010: hooks/post_gen_project.py:7-17 — remove_path() 函数递归删除文件或目录
- F-011: hooks/post_gen_project.py:22-23 — 若 has_binder 不以 "y" 开头，删除 binder/ 目录和 .github/workflows/binder-on-pr.yml 文件

## 包配置模板（pyproject.toml）

- F-012: {{cookiecutter.package_name}}/pyproject.toml:2-3 — 使用 hatchling>=1.5 构建后端
- F-013: {{cookiecutter.package_name}}/pyproject.toml:6-7 — 包名和作者信息使用 cookiecutter 变量
- F-014: {{cookiecutter.package_name}}/pyproject.toml:10 — 要求 Python >=3.8
- F-015: {{cookiecutter.package_name}}/pyproject.toml:11 — keywords 为 ["Jupyter", "Extension"]
- F-016: {{cookiecutter.package_name}}/pyproject.toml:22 — 运行时依赖：jupyter_server>=1.6,<3（兼容 Jupyter Server 1.x 和 2.x）
- F-017: {{cookiecutter.package_name}}/pyproject.toml:25-28 — test 可选依赖：pytest>=7.0、pytest-jupyter[server]>=0.6
- F-018: {{cookiecutter.package_name}}/pyproject.toml:29-34 — lint 可选依赖：black>=22.6.0、mdformat、mdformat-gfm、ruff>=0.0.156
- F-019: {{cookiecutter.package_name}}/pyproject.toml:35 — typing 可选依赖：mypy>=0.990
- F-020: {{cookiecutter.package_name}}/pyproject.toml:43-44 — 版本从 __init__.py 读取
- F-021: {{cookiecutter.package_name}}/pyproject.toml:46-47 — wheel 安装时将 jupyter-config/ 映射到 etc/jupyter/（Jupyter 自动发现扩展配置）
- F-022: {{cookiecutter.package_name}}/pyproject.toml:49-56 — pytest 配置：filterwarnings 将 warning 转为 error，忽略特定 DeprecationWarning
- F-023: {{cookiecutter.package_name}}/pyproject.toml:58-68 — mypy 严格类型检查配置
- F-024: {{cookiecutter.package_name}}/pyproject.toml:70-73 — black 配置：line-length=100、target py38、skip-string-normalization
- F-025: {{cookiecutter.package_name}}/pyproject.toml:75-89 — ruff 配置：启用大量规则（A/B/C/E/F/FBT/I/N/Q/RUF/S/T/UP/W/YTT）

## 扩展入口模块

- F-026: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/__init__.py:1 — docstring 使用 project_short_description
- F-027: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/__init__.py:2 — 导入 Extension 类
- F-028: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/__init__.py:3 — __version__ 初始为 "0.1.0"
- F-029: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/__init__.py:6-10 — _jupyter_server_extension_points() 函数返回扩展点列表，包含 module（package_name 中 - 替换为 _）和 app（Extension 类）

## ExtensionApp 实现

- F-030: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/extension.py:1 — 从 traitlets 导入 Unicode
- F-031: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/extension.py:3 — 继承 jupyter_server.extension.application.ExtensionApp
- F-032: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/extension.py:7 — Extension 类继承 ExtensionApp
- F-033: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/extension.py:9 — name 属性使用 package_name（- 替换为 _）
- F-034: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/extension.py:10-12 — handlers 列表注册路由："{package_name-_}/ping" → PingHandler
- F-035: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/extension.py:16 — ping_response 可配置 Unicode trait，默认值 "pong"，tag(config=True)
- F-036: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/extension.py:18-21 — initialize_settings() 将 ping_response 注入 self.settings 字典

## API Handler

- F-037: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/handlers.py:1 — 导入 json
- F-038: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/handlers.py:3-4 — PingHandler 继承 ExtensionHandlerMixin 和 APIHandler
- F-039: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/handlers.py:12-14 — ping_response 属性从 self.settings 读取
- F-040: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/handlers.py:16-20 — get() 方法使用 @tornado.web.authenticated 装饰器，返回 JSON {"ping_response": "..."}

## Jupyter 配置

- F-041: {{cookiecutter.package_name}}/jupyter-config/jupyter_server_config.d/{{cookiecutter.package_name}}.json:2-6 — Jupyter 配置文件：在 ServerApp.jpserver_extensions 中启用扩展（值为 true）

## 测试模板

- F-042: {{cookiecutter.package_name}}/{{cookiecutter.package_name}}/tests/test_handlers.py:4-11 — test_get 异步测试：使用 jp_fetch fixture 请求 /{package_name-_}/ping 端点，验证返回 200 和 {"ping_response": "pong"}

## CI/CD 和开发配置

- F-043: {{cookiecutter.package_name}}/.github/workflows/build.yml — GitHub Actions 构建工作流
- F-044: {{cookiecutter.package_name}}/.github/workflows/lint.sh — Lint 脚本
- F-045: {{cookiecutter.package_name}}/.github/workflows/binder-on-pr.yml — Binder PR 预览工作流（条件性包含）
- F-046: {{cookiecutter.package_name}}/conftest.py — pytest 配置文件
- F-047: {{cookiecutter.package_name}}/binder/ — Binder 配置目录（条件性包含）
- F-048: {{cookiecutter.package_name}}/.pre-commit-config.yaml — pre-commit hooks 配置
- F-049: {{cookiecutter.package_name}}/LICENSE — BSD 许可证
- F-050: {{cookiecutter.package_name}}/CHANGELOG.md — 变更日志模板
- F-051: {{cookiecutter.package_name}}/RELEASE.md — 发布说明模板
