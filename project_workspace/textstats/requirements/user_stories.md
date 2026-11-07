<file_header>
  <author_agent>requirement-analyst</author_agent>
  <timestamp>2026-11-07T18:56:08.7804323+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>2.0.0</version>
  <input_files><file>project_workspace/textstats/requirements/requirements_spec.md</file></input_files>
  <phase>PHASE_02</phase>
  <status>APPROVED</status>
</file_header>

## 角色 × 功能矩阵

| 角色 | 基础统计 | Top-N | 机器可读输出 | 错误处理 |
|---|---|---|---|---|
| 命令行用户（开发者/测试脚本） | US-001 | US-002 | US-003 | US-004 |

## 用户故事

### US-001: 统计文件的行数、词数与字符数
- 故事：As a 命令行用户, I want to 对一个文本文件一次性得到行数、词数和字符数, so that 我能快速了解文件规模而不用打开编辑器。
- 关联需求：REQ-FUNC-001、REQ-FUNC-002、REQ-FUNC-003；优先级：Must Have；故事点：3 [ESTIMATE]
- AC-001-01：Given 文件 `sample.txt` 内容为 `hello world\nfoo\n`, When 执行 `textstats.py sample.txt`, Then stdout 显示行数 2、词数 3、字符数 16，退出码 0。
- AC-001-02：Given 文件为空文件 `empty.txt`, When 执行 `textstats.py empty.txt`, Then stdout 显示行数 0、词数 0、字符数 0，退出码 0。
- AC-001-03：Given 文件内容为 `a b`（末尾无换行）, When 执行 `textstats.py a.txt`, Then 行数为 1、词数为 2、字符数为 3。
- AC-001-04：Given 文件含中文 `你好 世界\n`, When 执行 `textstats.py cn.txt`, Then 字符数为 6（汉字 4 + 空格 1 + 换行 1），词数为 2。

### US-002: 查看出现频次最高的词
- 故事：As a 命令行用户, I want to 用 `--top N` 指定查看频次最高的 N 个词, so that 我能快速定位文件的主要用词。
- 关联需求：REQ-FUNC-004；优先级：Must Have；故事点：3 [ESTIMATE]
- AC-002-01：Given 文件内容为 `a a b b c\n`, When 执行 `textstats.py f.txt --top 2`, Then 输出中首位为 `a`（2 次）、次位为 `b`（2 次），不出现 `c`，退出码 0。
- AC-002-02：Given 文件内容为 `B a B\n`, When 执行 `textstats.py f.txt --top 1`, Then 输出为 `b`（2 次），说明统计前已转小写。
- AC-002-03：Given 未提供 `--top`, When 执行 `textstats.py f.txt`, Then 最多输出 5 个词；文件不足 5 个不同词时输出全部。
- AC-002-04：Given 文件内容为 `b a\n`（频次并列）, When 执行 `textstats.py f.txt --top 2`, Then 输出顺序为 `a`、`b`（字典序升序）。

### US-003: 以 JSON 获取统计结果
- 故事：As a 测试脚本, I want to 让工具输出 JSON, so that 我可以直接解析字段断言而不必解析人类可读文本。
- 关联需求：REQ-FUNC-005；优先级：Should Have；故事点：2 [ESTIMATE]
- AC-003-01：Given 文件 `a a\n`, When 执行 `textstats.py f.txt --json`, Then stdout 是单行合法 JSON，含 `lines`=1、`words`=2、`chars`=4，`top` 首元素为 `{"word": "a", "count": 2}`，退出码 0。
- AC-003-02：Given 同一文件, When 分别执行带与不带 `--json`, Then 两次报告的行数、词数、字符数完全一致。

### US-004: 非法输入得到明确错误与退出码 2
- 故事：As a 命令行用户, I want to 在参数或文件非法时看到明确错误并以退出码 2 结束, so that 脚本能可靠区分成功与失败。
- 关联需求：REQ-FUNC-006、REQ-NFUNC-002；优先级：Must Have；故事点：2 [ESTIMATE]
- AC-004-01：Given 不存在的路径 `nope.txt`, When 执行 `textstats.py nope.txt`, Then stderr 含文件名且非空，stdout 无统计结果，退出码 2。
- AC-004-02：Given 未提供任何文件参数, When 执行 `textstats.py`, Then stderr 含用法提示，退出码 2。
- AC-004-03：Given 合法文件, When 执行 `textstats.py f.txt --top abc`, Then stderr 说明 `--top` 非法，退出码 2。
- AC-004-04：Given 合法文件, When 执行 `textstats.py f.txt --top 0`, Then stderr 说明 `--top` 必须为正整数，退出码 2。

## 汇总

| 优先级 | 故事数 | 故事点合计 |
|---|---|---|
| Must Have | 3 | 8 |
| Should Have | 1 | 2 |
| 合计 | 4 | 10 |
