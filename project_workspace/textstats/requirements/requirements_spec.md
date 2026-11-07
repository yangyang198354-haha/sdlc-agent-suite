<file_header>
  <author_agent>requirement-analyst</author_agent>
  <timestamp>2026-11-07T18:47:07.3108148+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>.trae/sdlc/project_profile.md</file></input_files>
  <phase>PHASE_01</phase>
  <status>APPROVED</status>
</file_header>

## 执行摘要

业务背景：用户要求「在沙箱内新建一个小项目进行测试」，项目 textstats 在用户确认的画像 P1 中定义为「统计文本文件的行数、词数、字符数，并输出出现频次最高的 N 个词（命令行工具）」。本需求完全来自用户已确认的画像 P1/P6/P8，无现有系统基线（FULL_FLOW / greenfield）。

- 功能需求 6 条（REQ-FUNC-001 ~ 006），非功能需求 2 条（REQ-NFUNC-001 ~ 002）。
- `[INFERRED]` 1 条（REQ-FUNC-005），1 ÷ (6 + 2) = 12.5%，未超过画像 P5 的 `inferred_max` 0.20。
- 优先级默认规则：用户明确提到的核心统计与错误处理为 Must Have；其余为 Should Have。Must Have 4 条（001~004、006 中 4 个功能域见故事映射），Should Have 1 条（005）。

## 功能需求

| ID | 描述（系统应当…） | 来源 | 优先级 | 增量类型 | 备注 |
|---|---|---|---|---|---|
| REQ-FUNC-001 | 接收一个文本文件路径，输出该文件的行数；行数以换行符分隔计，文件末尾无换行符的残余内容计为 1 行 | 用户确认画像 P1 | Must Have | 新增 | 空文件行数为 0 |
| REQ-FUNC-002 | 输出该文件的词数；词以空白字符（空格、制表符、换行符）分隔，连续空白不产生空词 | 用户确认画像 P1 | Must Have | 新增 | 空文件词数为 0 |
| REQ-FUNC-003 | 输出该文件的字符数；按 Unicode 码位计数，换行符也计入 | 用户确认画像 P1 | Must Have | 新增 | 含中文时按字符而非字节 |
| REQ-FUNC-004 | 输出出现频次最高的 N 个词；N 由 `--top N` 指定，缺省为 5；词频统计前把词转为小写；频次并列时按词字典序升序排列 | 用户确认画像 P1（Top-N）；并列规则 `[INFERRED]` | Must Have | 新增 | N ≤ 0 视为参数非法 |
| REQ-FUNC-005 | 支持 `--json` 输出：单行 JSON 对象，含 `lines`、`words`、`chars`、`top` 四个键，`top` 为 `{词, 次数}` 数组 | `[INFERRED]` | Should Have | 新增 | 供脚本消费；无此参数时输出人类可读文本 |
| REQ-FUNC-006 | 参数或输入非法时，向 stderr 输出一行错误说明并以退出码 2 结束；包括：未提供文件路径、文件不存在、文件不可读、`--top` 非整数或 ≤ 0 | 用户确认画像 P6（错误写 stderr、退出码 2）+ 画像 P1 | Must Have | 新增 | 成功时退出码为 0 |

## 非功能需求

| ID | 描述（系统应当…） | 来源 | 优先级 | 增量类型 | 备注 |
|---|---|---|---|---|---|
| REQ-NFUNC-001 | 只使用 Python 标准库，运行时不安装、不导入任何第三方包 | 用户确认画像 P8（禁用第三方依赖）、P1（3.11+） | Must Have | 新增 | 沙箱不可联网 |
| REQ-NFUNC-002 | 退出码契约：统计成功为 0，任何非法输入为 2；两者之外不出现其他退出码 | 用户确认画像 P6、P4 | Must Have | 新增 | 可被测试脚本断言 |

## 约束

- C-01：禁止第三方依赖、禁止联网、禁止容器（来源：画像 P8）。
- C-02：代码写在 `output/sandbox-v38-textstats/src/`，测试写在 `output/sandbox-v38-textstats/tests/`（来源：画像 P3）。
- C-03：本次运行不执行 commit / push（来源：画像 P9、用户任务）。
- C-04：输入文件按 UTF-8 解码；解码失败属于「文件不可读」，按 REQ-FUNC-006 处理。

## 超出范围

- 递归统计目录或多个文件（画像 P1 只要求单个文本文件）。
- 压缩包、二进制文件、编码自动探测。
- 正则过滤、停用词表、自定义分词。
- 图形界面与守护进程形态。

## 待确认推断项

| ID | 推断内容 | 推断依据 | 需谁确认 |
|---|---|---|---|
| REQ-FUNC-005 | 是否需要 `--json` 机器可读输出 | 用户未提及；为便于测试断言而加入，标 Should Have | 用户 |
| REQ-FUNC-004 备注 | 词频并列时按字典序升序 | 保证输出确定性的常规做法 | 用户 |

## 开放问题

1. 词频统计是否应排除纯标点词（如 `--`）？当前按「空白分隔的任意非空串」计入，与 REQ-FUNC-002 的词定义保持一致。
