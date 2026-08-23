---
type: Concept
title: "故障排查与常见问题"
description: "语言包安装、翻译不显示、构建失败、Crowdin同步问题等常见故障的诊断方法和解决方案"
tags: [jupyterlab, language-pack, troubleshooting, faq, debugging, common-issues]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-readme, resource: /references/repo-readme.md, title: "仓库根 README 信源" }
  - { id: release, resource: /references/release-process-source.md, title: "发布流程信源" }
---

# 故障排查与常见问题

汇总 JupyterLab 语言包使用和开发过程中的常见问题及解决方案。

## 安装相关问题

### Q1: pip install 成功但语言选项中找不到

**症状**：安装语言包后，JupyterLab 的 Settings → Language 中没有对应语言选项。

**排查步骤**：
1. 确认安装环境与 JupyterLab 运行环境一致：
   ```bash
   which jupyter lab  # Linux/Mac
   where jupyter      # Windows
   pip show jupyterlab-language-pack-zh-CN
   ```
2. 检查 entry-point 注册：
   ```bash
   python -c "
   from importlib.metadata import entry_points
   for ep in entry_points(group='jupyterlab.languagepack'):
       print(f'{ep.name}: {ep.value}')
   "
   ```
3. 如果列表中没有目标语言，说明包安装位置不对（可能装到了另一个 Python 环境）
4. 确认在 JupyterLab 使用的同一个 Python 环境中安装

**解决方案**：
```bash
# 在 JupyterLab 所在环境中安装
pip install jupyterlab-language-pack-zh-CN
# 重启 JupyterLab（不是刷新页面）
jupyter lab
```

### Q2: 安装后界面部分中文部分英文

**症状**：JupyterLab 界面有中文，但某些部分仍显示英文。

**原因**：
1. 未安装的第三方扩展没有翻译（只翻译了 language-packs 覆盖的17个扩展）
2. 某些字符串在新版 JupyterLab 中新增，尚未翻译
3. 翻译覆盖率不是 100%

**解决方案**：
- 等待下一次翻译更新发布
- 到 https://crowdin.com/project/jupyterlab 贡献未翻译的字符串
- 检查使用的 JupyterLab 版本是否在语言包的 supported-versions 范围内

### Q3: 中文显示乱码/方框

**症状**：界面显示方块或乱码字符。

**原因**：系统缺少中文字体。

**解决方案**：
- Linux：安装中文字体 `sudo apt install fonts-noto-cjk`
- Windows/macOS：通常自带中文字体，检查 JupyterLab 是否使用了正确的字体设置

## 翻译显示问题

### Q4: 翻译已安装但仍显示英文

**排查步骤**：
1. **语言设置正确吗？** Settings → Language 确认选择了目标语言
2. **重启了吗？** 更改语言后需要确认对话框并刷新页面
3. **浏览器缓存？** 尝试硬刷新（Ctrl+Shift+R / Cmd+Shift+R）或无痕窗口
4. **JupyterLab 版本匹配吗？**
   ```bash
   jupyter lab --version
   pip show jupyterlab-language-pack-zh-CN | grep Version
   ```
   语言包版本的 X.Y 应与 JupyterLab 主版本匹配
5. **查看控制台错误**：F12 打开开发者工具，Console 标签查看是否有加载翻译文件的 404 错误

**解决方案**：
- 安装匹配版本的语言包
- 清除浏览器缓存
- 检查 JupyterLab 日志中是否有 i18n 相关错误

### Q5: 翻译内容不正确/过时

**原因**：
1. Crowdin 上的翻译尚未同步到 GitHub
2. 同步了但尚未发布到 PyPI
3. 翻译本身质量问题

**解决方案**：
- 在 Crowdin 上检查对应字符串的翻译状态
- 翻译更新需要等待下一次 post 发布
- 可以在 Crowdin 上建议改进翻译（会被审核）

### Q6: 自定义扩展的翻译不显示

**原因**：第三方扩展默认不在 language-packs 的覆盖范围内。

**解决方案**：
1. 确认扩展本身支持 i18n（使用 `_()` 标记字符串）
2. 参见[添加新扩展到翻译](12-adding-extension.md)指南
3. 或在扩展自己的包中提供翻译

## 构建/开发问题

### Q7: 运行 02_update_catalogs.py 时 clone 失败

**症状**：`git clone` 超时或报错。

**解决方案**：
1. 检查网络连接
2. 配置 Git 代理：
   ```bash
   git config --global http.proxy http://proxy:port
   ```
3. 如果是单包问题，可以删除 repos/ 下对应目录重试：
   ```bash
   rm -rf repos/jupyterlab-git
   python scripts/02_update_catalogs.py
   ```
4. GitHub API 速率限制：设置 `GH_TOKEN` 环境变量

### Q8: 构建 wheel 时 MO/JSON 文件缺失

**症状**：构建的 wheel 中 LC_MESSAGES 目录下只有 .po 没有 .mo/.json，或文件缺失。

**排查**：
1. 确认 jupyterlab-translate 版本：
   ```bash
   pip show jupyterlab-translate
   # 需要 >= 1.2.0
   ```
2. 检查 .po 文件是否有 fuzzy 标记（fuzzy 条目不编译）：
   ```bash
   grep -r "fuzzy" language-packs/jupyterlab-language-pack-zh-CN/
   ```
3. 检查构建日志中 jupyter-translate hook 的输出

**解决方案**：
```bash
pip install --upgrade "jupyterlab-translate>=1.2.0"
# 清理后重新构建
rm -rf dist/ build/ *.egg-info
python -m build
```

### Q9: 04_check_version.py 报告版本不一致

**症状**：CI 检查失败，提示版本不一致。

**原因**：添加新语言包或修改版本号时遗漏了某些包。

**解决方案**：
```bash
# 查看所有语言包版本
python -c "
import ast, pathlib
base = pathlib.Path('language-packs')
for pkg in sorted(base.iterdir()):
    if not pkg.is_dir() or pkg.name == 'README.md':
        continue
    init = pkg / pkg.name.replace('-', '_') / '__init__.py'
    if init.exists():
        content = init.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == '__version__':
                        print(f'{pkg.name}: {node.value.s}')
"
# 找到不一致的，手动修正或运行 03_prepare_release.py 统一版本
```

## Crowdin/同步问题

### Q10: Crowdin PR 有合并冲突

**症状**：Crowdin Bot 创建的翻译 PR 显示冲突。

**解决方案**：
1. **不要尝试手动解决冲突**（Crowdin 会覆盖）
2. 关闭该 PR
3. 删除 `l10n_crowdin_translations` 分支
4. 手动触发 crowdin.yml 工作流重新下载翻译
5. 新 PR 应该无冲突

### Q11: Crowdin 上有翻译但未出现在 GitHub

**原因**：翻译下载是定时的（每日UTC 1:45），不是实时的。

**解决方案**：
- 等待自动同步（最多24小时）
- 或手动触发 crowdin.yml 工作流的下载操作
- 确认翻译没有被标记为"未approved"（但项目配置是下载所有翻译，不只approved的）

### Q12: 上传 POT 后 Crowdin 上看不到新字符串

**排查**：
1. 检查 crowdin.yml 工作流是否成功运行
2. 确认 .pot 文件路径在 crowdin.yml 的 files 配置中
3. 在 Crowdin 项目设置中检查文件映射是否正确
4. 可能需要等待几分钟 Crowdin 处理上传

## CI/CD 问题

### Q13: prepare_release 工作流失败

常见原因：
1. **Crowdin API 调用失败**：CROWDIN_API_KEY 过期或无效
2. **Copier 更新冲突**：cookiecutter 模板与本地修改冲突
3. **某些语言包目录缺失**：ach-UG 等特殊包可能有不同的结构

**解决方案**：
- 检查 Actions 日志中的具体错误
- 验证 CROWDIN_API_KEY 权限
- 本地运行 `copier --defaults update` 查看冲突详情

### Q14: release_publish 某些包上传 PyPI 失败

**原因**：网络问题或 PyPI 临时故障。

**解决方案**：
1. 查看 Actions 日志确认哪些包失败
2. 从 Actions artifacts 下载构建好的 wheel
3. 手动使用 twine 上传失败的包：
   ```bash
   pip install twine
   twine upload dist/jupyterlab_language_pack_zh_CN-*.whl
   ```

## 启动/运行时问题

### Q15: JupyterLab 启动警告 "Language pack not found"

**原因**：配置中指定了某个语言，但对应的语言包未安装。

**解决方案**：
```bash
# 查看当前语言设置
jupyter lab --show-config | grep -i language

# 安装缺失的语言包，或重置为英文
jupyter lab --Language=en
```

### Q16: 切换语言后按钮/菜单空白

**原因**：翻译字符串中包含格式错误（如未闭合的 HTML 标签）。

**解决方案**：
- 切回英文
- 在 Crowdin 上找到有问题的字符串并报告/修正
- 检查最近的翻译更新是否引入了格式问题

## 获取帮助

如果以上方案不能解决问题：

1. **检查 GitHub Issues**：https://github.com/jupyterlab/language-packs/issues
2. **检查 JupyterLab 文档**：https://jupyterlab.readthedocs.io/
3. **Discourse 论坛**：https://discourse.jupyter.org/
4. **提交 Issue**：在 language-packs 仓库提交 bug report，包含：
   - JupyterLab 版本（`jupyter lab --version`）
   - 语言包版本（`pip show jupyterlab-language-pack-xx-XX`）
   - Python 版本和操作系统
   - 浏览器控制台错误截图
   - 复现步骤

## 相关概念

- [Crowdin 翻译平台集成](04-crowdin-integration.md)
- [CI/CD 流水线](08-cicd-pipeline.md)
- [发布流程](09-release-workflow.md)
- [本地开发环境搭建](14-dev-setup.md)
