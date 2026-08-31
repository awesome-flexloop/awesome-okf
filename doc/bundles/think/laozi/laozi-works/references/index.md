# 信源登记簿索引

本目录登记本 bundle 依循的全部权威信源。每条信源含可核查 `resource`（出版社·年份 / 机构 URL），供正文 `[^source-id]` 脚注溯源。

## 信源分类

| 文档 | 内容 |
|------|------|
| [出土文献整理本](core-manuscripts.md) | 帛书、楚简、汉简的整理与校注本 |
| [历代注本信源](historical-commentaries.md) | 王弼、河上公、严遵、苏辙 |
| [现代注本信源](modern-studies.md) | 陈鼓应、楼宇烈、李零 |

## 统一信源 ID 清单

### 出土文献整理本

| 信源 ID | 信源 | 类型 |
|---------|------|------|
| `mawangdui-boshu-yi` | 《马王堆汉墓帛书（壹）》，国家文物局古文献研究室，文物出版社，1980 | 出土文献整理本 |
| `gao-ming-jiaozhu` | 《帛书老子校注》，高明，中华书局，1996 | 出土文献校注 |
| `jimen-bowuguan-guodian` | 《郭店楚墓竹简》，荆门市博物馆，文物出版社，1998 | 出土文献整理本 |
| `liao-mingchun-guodian` | 《郭店楚简老子校释》，廖名春，清华大学出版社，2003 | 出土文献校注 |
| `beida-hanjian-2` | 《北京大学藏西汉竹书（贰）》，北京大学出土文献研究所，上海古籍出版社，2012 | 出土文献整理本 |
| `qiu-xigui-jicheng` | 《长沙马王堆汉墓简帛集成》，裘锡圭主编，中华书局，2014 | 出土文献整理本 |

### 历代注本

| 信源 ID | 信源 |
|---------|------|
| `lou-yulie-wangbi` | 楼宇烈《老子道德经注校释》（王弼注整理本），中华书局，2008 |
| `wang-ka-heshanggong` | 王卡点校《老子道德经河上公章句》，中华书局，1993 |
| `wang-deyou-yanzun` | 王德有点校《老子指归》，中华书局，1994 |
| `suzhe-laozijie` | 苏辙《老子解》，中华书局《苏辙集》，1990 |

### 现代注本

| 信源 ID | 信源 |
|---------|------|
| `chen-guying-jinzhu` | 陈鼓应《老子今注今译及评介》，中华书局，2009 |
| `li-ling-laozibieren` | 李零《人往低处走——〈老子〉天下第一》，三联书店，2008 |

## 使用说明

- 正文引用采用脚注 `[^source-id]` 形式，信源 ID 可回溯至上表。
- `lou-yulie-wangbi` 同时作为「王弼注整理本」列于历代注本与「楼宇烈校释」列于现代注本，两处记录一致。
- 不同文档中的同一条信源使用相同 ID，避免重复登记。

```{toctree}
:hidden:
:maxdepth: 7

core-manuscripts
historical-commentaries
modern-studies
```