<file_header>
  <author_agent>test-engineer</author_agent>
  <timestamp>2026-11-07T18:57:07.9210553+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/testing/test_plan.md</file><file>output/sandbox-v38-textstats/tests/test_e2e_textstats.py</file></input_files>
  <phase>PHASE_09</phase>
  <status>APPROVED</status>
</file_header>

## 摘要

critical path 口径：E2E
total = pass + fail + skip + blocked + not_testable = 6 = 6 + 0 + 0 + 0 + 0
critical path 覆盖率 = 3 / 3 = 100%（Must Have 故事 US-001、US-002、US-004 均有 E2E 用例）
critical path 通过率 = 3 / 3 = 100%；**本层门控：PASSED**

命令：`python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_e2e_*.py" -t output/sandbox-v38-textstats/tests`

## 全量回归

命令：`python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_*.py" -t output/sandbox-v38-textstats/tests`
输出尾部：

```
Ran 25 tests in 0.435s
OK
EXIT_ALL=0
```

相对基线新增失败数：0（greenfield 基线为空）。

## 用户旅程

### TC-E2E-001: 统计真实样本文件
- 关联：US-001 / AC-001-01；环境：真实子进程，`fixtures/sample.txt`
| 步骤 | 操作 | 期望响应 | 实际响应 | 结果 |
|---|---|---|---|---|
| 1 | `python src/textstats.py fixtures/sample.txt` | 退出码 0，lines 2 / words 3 / chars 16 | 一致 | PASS |

### TC-E2E-006: 空文件
- 关联：US-001 / AC-001-02
| 步骤 | 操作 | 期望响应 | 实际响应 | 结果 |
|---|---|---|---|---|
| 1 | 运行空文件 | 退出码 0，三计数 0 | 一致 | PASS |

### TC-E2E-005: 中文 UTF-8 文件
- 关联：US-001 / AC-001-04
| 步骤 | 操作 | 期望响应 | 实际响应 | 结果 |
|---|---|---|---|---|
| 1 | 运行 `你好 世界\n` | chars 6 / words 2 | 一致 | PASS |

### TC-E2E-002: 默认 Top-5
- 关联：US-002 / AC-002-03
| 步骤 | 操作 | 期望响应 | 实际响应 | 结果 |
|---|---|---|---|---|
| 1 | 运行 6 个不同词的文件（无 --top） | top 段恰好 5 行 | 一致 | PASS（首次断言写法错误已修正） |

### TC-E2E-003: JSON 可机器消费
- 关联：US-003 / AC-003-01
| 步骤 | 操作 | 期望响应 | 实际响应 | 结果 |
|---|---|---|---|---|
| 1 | 运行 `--json` 并 `json.loads` | 四键完整，top[0]={"word":"a","count":2} | 一致 | PASS |

### TC-E2E-004: 不存在的文件
- 关联：US-004 / AC-004-01
| 步骤 | 操作 | 期望响应 | 实际响应 | 结果 |
|---|---|---|---|---|
| 1 | 运行不存在的路径 | 退出码 2，stdout 空，stderr 含文件名 | 一致 | PASS |

## 缺陷

| DEF | 级别 | 现象 | 复现用例 | 疑似位置 |
|---|---|---|---|---|
| — | — | 无产品缺陷 | — | — |

## 人工验证清单

无。
