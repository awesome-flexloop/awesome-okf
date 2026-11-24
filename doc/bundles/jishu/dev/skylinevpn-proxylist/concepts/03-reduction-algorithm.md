---
type: Concept
title: "03 归约算法：父后缀吸收与叠加层并集"
description: "merge.py 的 covered() 如何用后缀包含语义消掉冗余条目、并集策略为何让清单只增不减、以及就地写回带来的幂等与风险"
---

# 03 归约算法：父后缀吸收与叠加层并集

## 1. 两个集合先并集

`main()` 的第一件事不是归约，而是**并集**（F-043）：

```python
rules = {s: set() for s in SECTIONS}
parse_upstream(upstream, rules)   # 上游 gfwlist
parse_sections(list_path, rules)  # 现有 proxy.list
```

也就是说，`proxy.list` 既是**产物**，也是**输入**。这意味着：

- 本仓手工策展的条目（2026-10-16 那两批金融/AI/流媒体等，F-009、F-010）在每周自动构建中不会丢失；
- 上游曾经有过、后来删掉的条目，也会一直留在本地；
- 清单规模**单调不减**（除非人工删行或归约变化）。

这个设计通常被称为「叠加层（overlay）」：上游提供增量，本地保留策展。

## 2. 归约：什么样的条目是冗余的

真正的归约只有三段（F-040、F-041）：

```python
def covered(host, suffixes, include_self):
    parts = host.split(".")
    start = 0 if include_self else 1
    return any(".".join(parts[i:]) in suffixes for i in range(start, len(parts)))

suffix = {h for h in suffix if not covered(h, suffix, include_self=False)}
exact  = {h for h in rules["exact"] if not covered(h, suffix, include_self=True)}
```

逐条解释：

| 步骤 | 参数 | 含义 |
|------|------|------|
| 后缀自吸收 | `include_self=False` | 若 `a.b.com` 的**真父级**（`b.com`、`com`）已在后缀集合中，则删掉 `a.b.com` |
| 精确项被吸收 | `include_self=True` | 若 `x.y.com` 的任一父级**或自身**在后缀集合中，则删掉该精确项 |

为什么 `include_self` 两者不同？

- 后缀集合内部：`a.b.com` 与 `b.com` 同时存在时，前者完全冗余（后缀语义已含子域），所以只看父级。
- 精确项：若精确项的主机本身就等于某个后缀（如 `example.com` 同时出现在两节），那就用后缀版即可，所以允许「自身匹配」。

## 3. 举例

假设输入如下（三节合并后）：

```text
domain_suffix: b.com, a.b.com, c.b.com, example.org
exact:         x.a.b.com, b.com, keep.me
regex:         (^|\.)wild\.net$
```

经过归约：

1. `a.b.com`、`c.b.com` 的父级 `b.com` 在后缀集 → **删除**；
2. `x.a.b.com` 的父级 `a.b.com` 虽被删，但它已不在后缀集中，`b.com` 仍是父级 → 仍被吸收 → **删除**；
3. `exact` 中的 `b.com` 自身就在后缀集 → **删除**；
4. `keep.me` 无父级在后缀集 → **保留**；
5. `regex` 不参与归约，原样保留。

输出：

```text
domain_suffix: b.com, example.org
exact:         keep.me
regex:         (^|\.)wild\.net$
```

注意第 2 步的顺序效应：代码先算出精简后的 `suffix` 集合，再用它过滤 `exact`。如果反过来，`x.a.b.com` 会因为 `a.b.com` 已被删除而逃过吸收。当前顺序是对的，但它**依赖「后缀包含子域」这一语义假设**——若消费端语义不同，这次归约就变成了行为变更（D-5）。

## 4. 复杂度与规模

`covered()` 对每个主机做 O(标签数) 次字符串拼接与集合查找，整体接近 O(N × L)，其中 L 通常 ≤ 4。对 2.6 万条数据，这是一次毫秒级到秒级的操作，无需索引结构。

真正的成本不在这里，而在 **I/O**：数据文件 389 KB，写回是整体重写（F-043）。在 GitHub Actions 上可忽略；在低速网络盘上（如 SMB）则可能需要数秒，这也是本束演练中反复提醒「不要在全库上跑重脚本」的原因。

## 5. 输出：排序、覆写与被丢弃的注释

落盘逻辑只有 6 行（F-042、F-044）：

```python
with open(list_path, "w", encoding="utf-8") as f:
    f.write("# skylinevpn-proxylist\n")
    f.write("# License: Skyline Networking Tech LLC\n")
    for s in SECTIONS:
        f.write(f"\n## {s}\n")
        f.writelines(f"{h}\n" for h in sorted(result[s]))
```

三个后果：

1. **头部固定两行**：任何人工添加的注释都会在下一次构建中消失；
2. **节内排序**：`sorted()` 保证 diff 最小化，是「可审自动提交」的前提；
3. **就地覆写**：`open(..., "w")` 直接截断原文件，没有临时文件 + `os.replace` 的原子替换。若进程在写入中途被杀，`proxy.list` 会处于半截状态。

第 3 点在实际运行中风险很低：写入发生在 CI 的一次性容器内，失败则工作区丢弃，不会污染仓库。但它解释了为什么**本地跑构建前应先备份**（见 [演练 00](../examples/00-local-rebuild-and-idempotency.md)）。

## 6. 幂等性从哪来

归约算法是纯函数：输入相同 → 输出逐字节相同。加上 `sorted()`，整条链路对本轮输入是确定性的。

于是「同一份上游跑两次」会产生完全相同的文件，`git diff` 为空。工作流正是靠这一点实现「无变化不提交」（F-052）：

```bash
git add proxy.list
git diff --cached --quiet || git commit -m "Update proxy.list $(date -u +%Y-%m-%d)"
```

注意它判断的是 **staged diff**，而不是「上游是否变化」。二者在大多数时候等价，但在上游新增了已被父后缀覆盖的条目时会出现「上游变了、产物没变」——此时正确地不提交。

## 7. 只增不减的代价

并集策略让清单成为一本**只写不删的账**：

| 好处 | 代价 |
|------|------|
| 策展条目不丢 | 上游删除的条目永久残留 |
| 构建不发生「大规模回退」 | 体积单调增长，26,700 条里有多少是失效域名无从判断 |
| 变更总是「新增若干行」 | 无法从 diff 看出「某站点已不再需要代理」 |

若要引入删除传播，最小改动是给条目加来源标记（如上游段与本地段分文件），而不是在并集里做差集——后者会误删策展条目。这是本仓未来最值得做的一次结构性演进（见 [核验报告](../references/verification.md) D-4）。

## 关键事实

F-040、F-041（归约）、F-042（输出格式）、F-043、F-044（就地写回）、F-052（无变化不提交）、D-4（只增不减）、D-5（语义契约）。
