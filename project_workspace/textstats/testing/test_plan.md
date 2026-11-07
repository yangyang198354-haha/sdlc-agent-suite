<file_header>
  <author_agent>test-engineer</author_agent>
  <timestamp>2026-11-07T18:55:03.6342869+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/requirements/user_stories.md</file><file>project_workspace/textstats/architecture/module_design.md</file><file>project_workspace/textstats/development/implementation_plan.md</file><file>project_workspace/textstats/development/code_review_report.md</file></input_files>
  <phase>PHASE_07,PHASE_08,PHASE_09</phase>
  <status>APPROVED</status>
</file_header>

## 测试策略

- 被测改动：MOD-001 CLI 入口、MOD-002 统计核心、MOD-003 渲染（本次全部为新增代码）。
- 范围：in scope 为 REQ-FUNC-001~006 与 REQ-NFUNC-002 对应的 14 条 AC；out of scope 为词频标点语义（需求开放问题 1）与超大文件性能。
- 环境：Windows，Python 3.14.6，仅标准库，不使用网络/容器。
- 判定模式：threshold（画像 P5）：unit_pass 0.80、integration_pass 0.90、critical_path 1.00。
- 基线来源：无（greenfield，画像 P4 无既有失败）。
- 分层机制：按文件名前缀 `test_unit_*` / `test_integration_*` / `test_e2e_*`，与画像 P4 命令一致。

## AC 映射

| AC | 用例 ID | 级别 | 现有/新写 | 位置（文件::方法） | 前置 | 动作 | 预期 | 测试数据 |
|---|---|---|---|---|---|---|---|---|
| AC-001-01 | TC-UNIT-001 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_basic_counts` | 文本 `hello world\nfoo\n` | `count_text` | (2,3,16) | 内联字符串 |
| AC-001-01 | TC-INT-001 | integration | 新写 | `test_integration_cli.py::CliTest::test_reports_basic_counts` | 临时文件 | `main([path])` | 退出码 0，stdout 含 `lines: 2` | 临时文件 |
| AC-001-01 | TC-E2E-001 | e2e | 新写 | `test_e2e_textstats.py::E2ETest::test_sample_file` | fixtures/sample.txt | 子进程运行 CLI | 退出码 0，三计数为 2/3/16 | `fixtures/sample.txt` |
| AC-001-02 | TC-UNIT-002 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_empty_text` | 空串 | `count_text` | (0,0,0) | 内联 |
| AC-001-02 | TC-E2E-006 | e2e | 新写 | `test_e2e_textstats.py::E2ETest::test_empty_file` | 空文件 | 子进程运行 CLI | 退出码 0，三计数为 0 | 临时空文件 |
| AC-001-03 | TC-UNIT-003 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_no_trailing_newline` | `a b` | `count_text` | (1,2,3) | 内联 |
| AC-001-04 | TC-UNIT-004 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_unicode_counts_code_points` | `你好 世界\n` | `count_text` | (1,2,5) | 内联 |
| AC-001-04 | TC-E2E-005 | e2e | 新写 | `test_e2e_textstats.py::E2ETest::test_unicode_file` | UTF-8 中文文件 | 子进程运行 CLI | chars=5，words=2 | 临时文件 |
| AC-002-01 | TC-UNIT-005 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_top_words_limit` | `a a b b c\n`, n=2 | `top_words` | [(a,2),(b,2)] | 内联 |
| AC-002-01 | TC-INT-002 | integration | 新写 | `test_integration_cli.py::CliTest::test_top_flag` | 临时文件 | `main([path,"--top","2"])` | 输出含 a、b，不含 c | 临时文件 |
| AC-002-02 | TC-UNIT-006 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_top_words_lowercases` | `B a B\n`, n=1 | `top_words` | [(b,2)] | 内联 |
| AC-002-03 | TC-E2E-002 | e2e | 新写 | `test_e2e_textstats.py::E2ETest::test_default_top_is_five` | 6 个不同词 | 子进程运行 CLI（无 --top） | 输出恰好 5 行词条 | 临时文件 |
| AC-002-04 | TC-UNIT-007 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_ties_sorted_lexicographically` | `b a\n`, n=2 | `top_words` | [(a,1),(b,1)] | 内联 |
| AC-003-01 | TC-INT-003 | integration | 新写 | `test_integration_cli.py::CliTest::test_json_output` | 临时文件 `a a\n` | `main([path,"--json"])` | 合法 JSON，字段与值符合 | 临时文件 |
| AC-003-01 | TC-E2E-003 | e2e | 新写 | `test_e2e_textstats.py::E2ETest::test_json_is_machine_readable` | 临时文件 | 子进程 + `json.loads` | 字段完整 | 临时文件 |
| AC-003-02 | TC-INT-004 | integration | 新写 | `test_integration_cli.py::CliTest::test_json_matches_text` | 同一临时文件 | 两次 `main` | 两次数值一致 | 临时文件 |
| AC-004-01 | TC-INT-005 | integration | 新写 | `test_integration_cli.py::CliTest::test_missing_file` | 路径不存在 | `main([path])` | 退出码 2，stderr 含文件名，stdout 空 | 不存在的路径 |
| AC-004-01 | TC-E2E-004 | e2e | 新写 | `test_e2e_textstats.py::E2ETest::test_missing_file_exit_code` | 不存在的路径 | 子进程 | 退出码 2，stderr 非空 | 不存在的路径 |
| AC-004-02 | TC-INT-006 | integration | 新写 | `test_integration_cli.py::CliTest::test_missing_argument` | 无参数 | `main([])` | 退出码 2，stderr 含 `usage` | — |
| AC-004-03 | TC-INT-007 | integration | 新写 | `test_integration_cli.py::CliTest::test_invalid_top_value` | `--top abc` | `main` | 退出码 2，stderr 含 `--top` | — |
| AC-004-04 | TC-INT-008 | integration | 新写 | `test_integration_cli.py::CliTest::test_zero_top` | `--top 0` | `main` | 退出码 2，stderr 含 `--top` | — |
| AC-004-04 | TC-UNIT-008 | unit | 新写 | `test_unit_stats.py::UnitStatsTest::test_top_words_rejects_non_positive_n` | n=0 | `top_words` | 抛 ValueError | — |

## 测试数据需求

- 单元与集成：内联字符串与 `tempfile.TemporaryDirectory` 创建的临时文件，随用例销毁。
- E2E：画像 P3 目录下的 `fixtures/sample.txt`（已存在，内容 `hello world\nfoo\n`）与临时文件。
- 不需要 `[DATA_REQUIRED]`；不使用网络、数据库或外部服务。

## 不可测项

无。
