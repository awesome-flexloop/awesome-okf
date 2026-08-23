---
okf_version: "0.2"
type: "concept"
title: 前端集成
description: websupport.js jQuery插件架构——评论弹窗、投票、回复、提议修改、审核操作的前端实现，模板系统与COMMENT_OPTIONS契约
tags: [sphinx-websupport, frontend, jquery, websupport.js, ajax, templates]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# 前端集成

websupport 自带一个完整的jQuery前端插件 `websupport.js`，提供评论弹窗、投票、回复、提议修改、审核等全部UI交互功能。后端只需在页面中注入两个JavaScript全局变量，前端即可自动工作。

## 前端架构概览

```
┌─────────────────────────────────────────────┐
│              浏览器页面                      │
│                                             │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ COMMENT_    │  │ COMMENT_METADATA     │  │
│  │ OPTIONS     │  │ {s123:2, s456:0,...} │  │
│  │ (URLs/用户) │  │ (评论计数)           │  │
│  └──────┬──────┘  └──────────┬───────────┘  │
│         │                    │              │
│         ▼                    ▼              │
│  ┌─────────────────────────────────────┐    │
│  │        websupport.js (jQuery插件)    │    │
│  │  ┌───────────┐  ┌────────────────┐  │    │
│  │  │ 评论弹窗   │  │ 投票/回复/删除  │  │    │
│  │  │ show/hide  │  │ accept/propose │  │    │
│  │  └───────────┘  └────────────────┘  │    │
│  │  ┌───────────┐  ┌────────────────┐  │    │
│  │  │ 模板渲染   │  │ 排序/自动增长   │  │    │
│  │  │ renderTpl  │  │ autogrow       │  │    │
│  │  └───────────┘  └────────────────┘  │    │
│  └──────────────┬──────────────────────┘    │
│                 │ AJAX                      │
└─────────────────┼───────────────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Web应用后端     │
         │  (Flask/Django) │
         │  WebSupport API │
         └─────────────────┘
```

## 页面加载流程

页面加载完成后，websupport.js执行两个初始化：

```javascript
$(document).ready(function() {
    init();  // 绑定事件委托 + 初始化排序器
});

$(document).ready(function() {
    // 为所有可评论段落添加评论图标
    $('.sphinx-has-comment').comment();
    
    // 高亮搜索结果中的搜索词
    $("div.context").each(function() { ... });
    
    // 如果URL hash是#comment-{id}，直接打开对应评论
    var anchor = document.location.hash;
    if (anchor.substring(0, 9) == '#comment-') {
        $('#ao' + anchor.substring(9)).click();
        document.location.hash = '#s' + anchor.substring(9);
    }
});
```

## COMMENT_OPTIONS 配置契约

后端通过 `_make_comment_options()` 和 `_make_base_comment_options()` 生成内联 `<script>` 标签，注入配置：

```javascript
var COMMENT_OPTIONS = {
    // API端点URL
    addCommentURL: "/docs/_add_comment",
    getCommentsURL: "/docs/_get_comments",
    processVoteURL: "/docs/_process_vote",
    acceptCommentURL: "/docs/_accept_comment",
    deleteCommentURL: "/docs/_delete_comment",
    // 静态资源URL
    commentImage: "/static/_static/comment.png",
    commentBrightImage: "/static/_static/comment-bright.png",
    closeCommentImage: "/static/_static/comment-close.png",
    loadingImage: "/static/_static/ajax-loader.gif",
    upArrow: "/static/_static/up.png",
    upArrowPressed: "/static/_static/up-pressed.png",
    downArrow: "/static/_static/down.png",
    downArrowPressed: "/static/_static/down-pressed.png",
    // 用户状态
    voting: true,        // 是否已登录（未登录不显示投票按钮）
    username: "reader1", // 当前用户名
    moderator: false     // 是否审核员
};
```

前端代码在默认opts基础上用 `jQuery.extend(opts, COMMENT_OPTIONS)` 合并用户配置。

## COMMENT_METADATA 数据契约

```javascript
var COMMENT_METADATA = {"s123456": 3, "s123457": 0, "s123458": 1};
```

键是节点DOM id（`s{uid}`），值是该节点的评论总数。`.comment()` 方法读取这个数据来决定显示灰色图标（0评论）还是亮色图标（>0评论），并设置title属性显示评论数。

## jQuery插件方法

### .comment() 方法

```javascript
$.fn.comment = function() {
    return this.each(function() {
        var id = $(this).attr('id').substring(1);  // 去掉's'前缀
        var count = COMMENT_METADATA[id];
        var title = count + ' comment' + (count == 1 ? '' : 's');
        var image = count > 0 ? opts.commentBrightImage : opts.commentImage;
        // 添加打开/关闭链接和点击事件
        $(this).append(/* 评论打开链接 */).append(/* 评论关闭链接 */);
    });
};
```

为每个 `.sphinx-has-comment` 元素添加两个链接：
- `#ao{id}`（open）：显示评论图标，点击打开评论弹窗
- `#ah{id}`（close）：关闭图标，默认隐藏，弹窗打开时显示

### .autogrow() 方法

```javascript
$.fn.autogrow = function() {
    return this.each(function() {
        var textarea = this;
        $.fn.autogrow.resize(textarea);
        $(textarea).focus(function() {
            textarea.interval = setInterval(function() {
                $.fn.autogrow.resize(textarea);
            }, 500);
        }).blur(function() {
            clearInterval(textarea.interval);
        });
    });
};
```

自动调整textarea高度的插件。聚焦时每500ms检查内容行数并调整高度，失焦时停止。根据行数 × line-height 计算高度。

## 评论弹窗系统

### show(id)：打开评论弹窗

```javascript
function show(id) {
    $('#ao' + id).hide();     // 隐藏打开链接
    $('#ah' + id).show();     // 显示关闭链接
    var context = $.extend({id: id}, opts);
    var popup = $(renderTemplate(popupTemplate, context)).hide();
    popup.find('textarea[name="proposal"]').hide();  // 提议修改默认隐藏
    popup.find('a.by' + by).addClass('sel');
    var form = popup.find('#cf' + id);
    form.submit(function(event) {
        event.preventDefault();
        addComment(form);
    });
    $('#s' + id).after(popup);  // 插入到段落后面
    popup.slideDown('fast', function() {
        getComments(id);        // 动画完成后加载评论
    });
}
```

弹窗内容包括：排序选项、评论列表区域（初始显示loading）、添加评论表单、提议修改区域。

### hide(id)：关闭评论弹窗

```javascript
function hide(id) {
    $('#ah' + id).hide();
    $('#ao' + id).show();
    var div = $('#sc' + id);
    div.slideUp('fast', function() {
        div.remove();  // 动画完成后移除DOM
    });
}
```

## AJAX交互

### 获取评论：getComments(id)

```javascript
function getComments(id) {
    $.ajax({
        type: 'GET',
        url: opts.getCommentsURL,
        data: {node: id},
        success: function(data, textStatus, request) {
            var ul = $('#cl' + id);
            if (data.comments.length === 0) {
                ul.html('<li>No comments yet.</li>');
                ul.data('empty', true);
            } else {
                var comments = sortComments(data.comments);
                appendComments(comments, ul);
                ul.data('empty', false);
            }
            $('#cn' + id).slideUp(data.comments.length * 100 + 200);
            ul.slideDown(data.comments.length * 100);
        },
        dataType: 'json'
    });
}
```

GET请求 `_get_comments?node={id}`，期望返回 `{source: "...", comments: [...]}` 格式的JSON。

### 添加评论：addComment(form)

```javascript
function addComment(form) {
    var node_id = form.find('input[name="node"]').val();
    var parent_id = form.find('input[name="parent"]').val();
    var text = form.find('textarea[name="comment"]').val();
    var proposal = form.find('textarea[name="proposal"]').val();
    
    if (text == '') { showError('Please enter a comment.'); return; }
    form.find('textarea,input').attr('disabled', 'disabled');
    
    $.ajax({
        type: "POST",
        url: opts.addCommentURL,
        dataType: 'json',
        data: {node: node_id, parent: parent_id, text: text, proposal: proposal},
        success: function(data) {
            form.find('textarea').val('').add(form.find('input')).removeAttr('disabled');
            var ul = $('#cl' + (node_id || parent_id));
            if (ul.data('empty')) { $(ul).empty(); ul.data('empty', false); }
            insertComment(data.comment);
            // 更新图标为亮色（有评论了）
            var ao = $('#ao' + node_id);
            ao.find('img').attr({'src': opts.commentBrightImage});
            if (node_id) { $('#ca' + node_id).slideUp(); }
        }
    });
}
```

POST请求 `_add_comment`，发送node/parent/text/proposal数据。成功后调用 `insertComment()` 将新评论插入正确位置（按排序比较器找到插入点）。

### 投票：handleVote(link)

```javascript
function handleVote(link) {
    if (!opts.voting) { showError("You'll need to login to vote."); return; }
    var id = link.attr('id');
    var value = 0;
    if (id.charAt(1) != 'u') {  // 不是取消投票
        value = id.charAt(0) == 'u' ? 1 : -1;
    }
    // ... 更新本地UI状态（切换箭头、更新评分显示）
    $.ajax({
        type: "POST",
        url: opts.processVoteURL,
        data: {comment_id: d.comment_id, value: d.value}
    });
}
```

投票ID格式：`{u/d}{v/u}{comment_id}`，如 `uv42` 表示comment 42的upvote可点击状态，`uu42` 表示已upvote（点击取消）。第一个字符u/d表示方向，第二个字符v/u表示votable/unvotable。

### 删除评论：deleteComment(id)

```javascript
function deleteComment(id) {
    $.ajax({
        type: 'POST',
        url: opts.deleteCommentURL,
        data: {id: id},
        success: function(data) {
            var div = $('#cd' + id);
            if (data == 'delete') {
                // 审核员硬删除：移除DOM
                div.slideUp('fast', function() { div.remove(); });
                return;
            }
            // 用户软删除：替换文本为[deleted]，移除操作按钮
            div.find('span.user-id:first').text('[deleted]').end()
               .find('div.comment-text:first').text('[deleted]').end()
               .find('#cm' + id + ', #dc' + id + ', #ac' + id + ', ...').remove();
        }
    });
}
```

后端返回 `'delete'` 字符串表示硬删除（审核员模式），否则是软删除。前端通过返回值判断删除模式。

### 审核通过：acceptComment(id)

```javascript
function acceptComment(id) {
    $.ajax({
        type: 'POST',
        url: opts.acceptCommentURL,
        data: {id: id},
        success: function() {
            $('#cm' + id).fadeOut('fast');
            $('#cd' + id).removeClass('moderate');
        }
    });
}
```

审核后移除"等待审核"提示，去除moderate CSS类。

## 模板系统

websupport.js实现了一个轻量级模板引擎：

```javascript
function renderTemplate(template, context) {
    var esc = $(document.createElement('div'));
    function handle(ph, escape) {
        var cur = context;
        $.each(ph.split('.'), function() { cur = cur[this]; });
        return escape ? esc.text(cur || "").html() : cur;
    }
    return template.replace(/<([%#])([\w\.]*)\1>/g, function() {
        return handle(arguments[2], arguments[1] == '%' ? true : false);
    });
}
```

两种占位符：
- `<%variable%>`：HTML转义输出（防止XSS），用于用户输入内容
- `<#variable#>`：不转义输出，用于可信HTML内容（如已在服务端渲染的评论HTML、proposal_diff）

支持点号路径访问嵌套属性，如 `<%time.delta%>` 访问 `context.time.delta`。

### 三个内置模板

**popupTemplate**：评论弹窗整体结构，包含排序选项、评论列表、添加评论表单、提议修改区域。

**commentTemplate**：单条评论的HTML结构，包含投票箭头、用户名、评分、时间、评论文本、操作链接（reply/propose/delete/accept）、子评论列表、proposal_diff显示区域。

**replyTemplate**：回复表单，包含textarea、提交/取消按钮和隐藏的parent字段。

## 排序系统

```javascript
function setComparator() {
    if (by.substring(0,3) == 'asc') {
        var i = by.substring(3);
        comp = function(a, b) { return a[i] - b[i]; };  // 升序
    } else {
        comp = function(a, b) { return b[by] - a[by]; }; // 降序
    }
    $('a.sel').attr('href', '#').removeClass('sel');
    $('a.by' + by).removeAttr('href').addClass('sel');
}
```

三种排序方式：
- **byrating**（默认）：按评分降序
- **byascage**：按age升序（最新的在前，age越小越新）
- **byage**：按age降序（最旧的在前）

排序偏好通过 `sortBy` cookie持久化（有效期365天）。切换排序时，从DOM中提取所有评论数据，重新排序后重渲染。

## 提议修改功能

用户可以点击"Propose a change"按钮对段落原文提出修改建议：

```javascript
function showProposeChange(id) {
    $('#pc' + id).hide();
    $('#hc' + id).show();
    var textarea = $('#pt' + id);
    textarea.val(textarea.data('source'));  // 从data中加载原文
    $.fn.autogrow.resize(textarea[0]);
    textarea.slideDown('fast');
}
```

提议修改的文本框预填充段落原文（从加载评论时 `form.find('textarea[name="proposal"]').data('source', data.source)` 设置），用户编辑后提交，后端用CombinedHtmlDiff生成差异。

查看proposal_diff时：
```javascript
function showProposal(id) {
    $('#sp' + id).hide();
    $('#hp' + id).show();
    $('#pr' + id).slideDown('fast');
}
```

差异显示在 `<pre class="proposal">` 中，包含 `<ins>`/`<del>`/`<span class="prop-added/removed">` 标签。

## 事件委托

所有交互事件使用jQuery事件委托（`$(document).on("click", 'a.vote', ...)`）绑定在document上，这意味着动态添加的评论元素（AJAX加载、回复表单等）不需要重新绑定事件。

## 后端API端点契约

前端期望后端提供以下HTTP端点：

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `{docroot}/_get_comments` | GET | `node` (string) | `{source: str, comments: [...]}` |
| `{docroot}/_add_comment` | POST | `node`, `parent`, `text`, `proposal` | `{comment: {...}}` |
| `{docroot}/_process_vote` | POST | `comment_id`, `value` | 任意（无错误即成功） |
| `{docroot}/_accept_comment` | POST | `id` | 任意 |
| `{docroot}/_delete_comment` | POST | `id` | `'delete'`（硬删）或其他（软删） |

## CSS类约定

前端使用以下CSS类，Web应用需要提供相应样式：

| CSS类 | 用途 |
|-------|------|
| `sphinx-has-comment` | 可评论段落 |
| `sphinx-comments` | 评论弹窗容器 |
| `sphinx-comment` | 单条评论容器 |
| `sphinx-comment-open/close` | 评论打开/关闭链接 |
| `comment-children` | 子评论列表 |
| `comment-text` | 评论文本 |
| `comment-form` | 评论表单 |
| `moderate` | 待审核/审核视图样式 |
| `prop-added/prop-removed` | 提议diff的新增/删除样式 |
| `popup-error`/`error-message` | 错误提示 |
| `highlighted` | 搜索结果高亮 |

## 相关概念

- [评论系统](05-comment-system.md)
- [架构总览](02-architecture-overview.md)
- [WebSupport API 详解](03-websupport-api.md)
- [Flask完整集成示例](../examples/flask-integration.md)
