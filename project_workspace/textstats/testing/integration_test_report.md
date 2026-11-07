<file_header>
  <author_agent>test-engineer</author_agent>
  <timestamp>2026-11-07T18:57:07.9210553+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/testing/test_plan.md</file><file>output/sandbox-v38-textstats/src/textstats.py</file></input_files>
  <phase>PHASE_08</phase>
  <status>APPROVED</status>
</file_header>

## 摘要

执行时间：2026-11-07T18:57+08:00；环境：Windows / Python 3.14.6。
命令：`python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_integration_*.py" -t output/sandbox-v38-textstats/tests`

total = pass + fail + skip + blocked + not_testable = 8 = 8 + 0 + 0 + 0 + 0
通过率 = 8 / (8 + 0 + 0) = 100%；threshold，integration_pass 0.90；**本层门控：PASSED**

## 执行输出

```
Ran 8 tests in 0.010s
OK
EXIT_INT=0
```

## 分项结果

集成边界：MOD-001 ↔ MOD-002/MOD-003（经 `textstats.main`，stdout/stderr 重定向，临时文件）。

| TC | AC | 描述 | 结果 | 实际输出（FAIL 时） |
|---|---|---|---|---|
| TC-INT-001 | AC-001-01 | main 输出三计数 | PASS | — |
| TC-INT-002 | AC-002-01 | `--top 2` 输出 a/b 且不含 c | PASS | — |
| TC-INT-003 | AC-003-01 | `--json` 字段与值 | PASS | — |
| TC-INT-004 | AC-003-02 | JSON 与文本数值一致 | PASS | — |
| TC-INT-005 | AC-004-01 | 文件不存在 → 2，stderr 含文件名 | PASS | — |
| TC-INT-006 | AC-004-02 | 无参数 → 2，stderr 含 usage | PASS | — |
| TC-INT-007 | AC-004-03 | `--top abc` → 2 | PASS | — |
| TC-INT-008 | AC-004-04 | `--top 0` → 2 | PASS | — |

## 与基线对比（baseline 模式）

不适用（threshold 模式）。

## 失败汇总（需路由给开发）

无。
