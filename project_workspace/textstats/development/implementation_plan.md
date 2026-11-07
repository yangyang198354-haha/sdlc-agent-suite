<file_header>
  <author_agent>software-developer</author_agent>
  <timestamp>2026-11-07T18:52:06.0936901+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/architecture/module_design.md</file><file>project_workspace/textstats/architecture/architecture_design.md</file><file>project_workspace/textstats/architecture/tech_stack.md</file></input_files>
  <phase>PHASE_05</phase>
  <status>APPROVED</status>
</file_header>

## 实现概览

3 个模块、3 个产品代码文件、1 个冒烟测试文件（FULL_FLOW 且无现有测试，按协议 §A 例外）。实现顺序按依赖拓扑：MOD-002（无依赖）→ MOD-003（依赖 MOD-002 类型）→ MOD-001（依赖两者）。

## 改动清单（按拓扑顺序）

| 序号 | MOD | 文件 | 新建/修改 | 依赖前置 | 复杂度 | 改动要点 | 状态 |
|---|---|---|---|---|---|---|---|
| 1 | MOD-002 | `output/sandbox-v38-textstats/src/stats.py` | 新建 | 无 | L | `TextStats`/`WordCount` dataclass；`count_text`；`top_words`（小写归一、频次降序、并列字典序） | DONE |
| 2 | MOD-003 | `output/sandbox-v38-textstats/src/render.py` | 新建 | MOD-002 | L | `render_text` / `render_json` | DONE |
| 3 | MOD-001 | `output/sandbox-v38-textstats/src/textstats.py` | 新建 | MOD-002、MOD-003 | M | argparse、文件读取、`--top` 校验、错误映射退出码 2 | DONE |
| 4 | — | `output/sandbox-v38-textstats/tests/test_smoke_textstats.py` | 新建 | MOD-002 | L | 最小冒烟：空文件与简单文本的计数 | DONE |

## 迁移

无。

## 架构偏差

无。

## 开放问题

- `[ASSUMPTION]` `--top` 上限取 1000（module_design IFC-001 的输入校验要求有上限，未给具体数值）。
- `[ASSUMPTION]` 文本输出采用 `label: value` 行格式，具体文案由 IFC-004 的"至少含三个数值与 Top-N 列表"推导，未逐字规定。
- 文件读取使用 `newline=""` 保留原始换行符，使字符数等于原始码位数。
