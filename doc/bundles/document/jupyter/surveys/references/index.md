# 信源登记簿

本目录包含Jupyter Surveys源码的关键信源登记文档，为concepts/和examples/中的溯源引用提供目标。

## 信源清单

- [noxfile.py源码解析](noxfile-source.md) — 文档构建自动化脚本：nox session定义、uv/virtualenv后端、mystmd构建命令
- [myst.yml配置解析](myst-config-source.md) — MyST站点配置：项目元数据、listing插件、TOC glob模式、book-theme选项
- [GitHub Actions部署工作流解析](deploy-workflow-source.md) — CI/CD流水线：触发条件、权限配置、Node.js环境、Pages部署
- [分析工具函数源码解析](analysis-utils-source.md) — 2018用户测试数据处理：时间转换、数据加载、dropzone编码、cleaner函数
- [数据集README模板解析](dataset-readme-source.md) — 各数据集README的frontmatter格式、章节结构、列定义表格规范

```{toctree}
:hidden:

analysis-utils-source
dataset-readme-source
deploy-workflow-source
myst-config-source
noxfile-source
```
