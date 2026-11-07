<file_header>
  <author_agent>system-architect</author_agent>
  <timestamp>2026-11-07T18:49:38.7975589+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/requirements/requirements_spec.md</file><file>project_workspace/textstats/requirements/user_stories.md</file></input_files>
  <phase>PHASE_04</phase>
  <status>APPROVED</status>
</file_header>

## 模块总览

| MOD | 名称 | 文件（新建） | 职责 | 覆盖需求/US | 依赖 |
|---|---|---|---|---|---|
| MOD-001 | CLI 入口 | `output/sandbox-v38-textstats/src/textstats.py` | 解析参数、读取文件、调用统计与渲染、决定退出码 | REQ-FUNC-001~006、REQ-NFUNC-002；US-001~004 | MOD-002、MOD-003 |
| MOD-002 | 统计核心 | `output/sandbox-v38-textstats/src/stats.py` | 纯函数：行/词/字符计数与词频 | REQ-FUNC-001~004；US-001、US-002 | 无 |
| MOD-003 | 渲染 | `output/sandbox-v38-textstats/src/render.py` | 把统计结果格式化为文本或 JSON | REQ-FUNC-005；US-003 | MOD-002（类型） |

## 模块详情

### MOD-001 CLI 入口（`src/textstats.py`）
- 职责：唯一的进程入口；把命令行参数转换为对 MOD-002/MOD-003 的调用。
- 接口 IFC-001：`main(argv: list[str]) -> int`
  - 契约：成功返回 0；任何输入类错误返回 2；错误信息写 stderr 且恰好一行。
  - 鉴权方式：无需鉴权（本地单用户进程，不监听网络，不访问远端）。
  - 输入校验：`argv` 必须含且仅含一个文件路径；`--top` 接受整数且 `1 <= N <= 1000`（上限防止病态输出），否则按 REQ-FUNC-006 返回 2；文件必须存在、可读且能按 UTF-8 解码，否则返回 2。
- 外部依赖：`argparse`、`sys`、`pathlib`（标准库）。

### MOD-002 统计核心（`src/stats.py`）
- 职责：不接触文件系统与 stdout 的纯函数，便于单测。
- 接口 IFC-002：`count_text(text: str) -> TextStats`
  - `TextStats` 为 dataclass：`lines: int`、`words: int`、`chars: int`。
  - 语义：`chars = len(text)`；`lines = 0 if text == "" else text.count("\n") + (0 if text.endswith("\n") else 1)`；`words = len(text.split())`。
  - 鉴权方式：无需鉴权（库函数）。
  - 输入校验：`text` 必须为 `str`；类型不符抛 `TypeError`（编程错误，不是用户输入错误）。
- 接口 IFC-003：`top_words(text: str, n: int) -> list[WordCount]`
  - `WordCount` 为 dataclass：`word: str`、`count: int`。
  - 语义：按 `text.split()` 取词、`str.lower()` 归一，频次降序、并列按 `word` 字典序升序，最多返回 `n` 条。
  - 输入校验：`n < 1` 抛 `ValueError`（由 MOD-001 提前拦截并转为退出码 2）。

### MOD-003 渲染（`src/render.py`）
- 职责：把 `TextStats` 与 `list[WordCount]` 转为最终字符串，不含 I/O。
- 接口 IFC-004：`render_text(stats: TextStats, top: list[WordCount]) -> str`
  - 契约：多行文本，至少含 `lines`、`words`、`chars` 三个数值与 Top-N 列表；以换行结尾。
- 接口 IFC-005：`render_json(stats: TextStats, top: list[WordCount]) -> str`
  - 契约：单行合法 JSON，键为 `lines`、`words`、`chars`、`top`；`top` 元素字段为 `word`（字符串）、`count`（整数）。
- 鉴权方式：无需鉴权（库函数）。
- 输入校验：由类型注解约束；`top` 中的 `count` 必须为正整数，否则抛 `ValueError`。

## 需求覆盖表

| REQ | US | MOD |
|---|---|---|
| REQ-FUNC-001 | US-001 | MOD-002（IFC-002）、MOD-001、MOD-003 |
| REQ-FUNC-002 | US-001 | MOD-002（IFC-002、IFC-003） |
| REQ-FUNC-003 | US-001 | MOD-002（IFC-002） |
| REQ-FUNC-004 | US-002 | MOD-002（IFC-003）、MOD-001（`--top` 校验） |
| REQ-FUNC-005 | US-003 | MOD-003（IFC-005） |
| REQ-FUNC-006 | US-004 | MOD-001（IFC-001） |
| REQ-NFUNC-001 | — | 全部 MOD（仅标准库） |
| REQ-NFUNC-002 | US-004 | MOD-001（IFC-001） |

## 依赖关系

- MOD-001 → MOD-002（IFC-002、IFC-003）
- MOD-001 → MOD-003（IFC-004、IFC-005）
- MOD-003 → MOD-002（仅引用 `TextStats`、`WordCount` 类型）

已检查：三个模块构成有向无环图（MOD-002 无出边），无循环依赖。

## 数据迁移

无。工具不持久化任何数据。

## 受影响的运行单元 / 构建

| 运行单元 | 影响 |
|---|---|
| textstats CLI（一次性进程） | 新建；无构建步骤，`py_compile` 即可验证语法；无服务重启 |

画像 P7 无 CI 系统与部署配置文件，本次不新增。

## 领域与外部依赖出处

不适用（画像 P11 为“无”）。
