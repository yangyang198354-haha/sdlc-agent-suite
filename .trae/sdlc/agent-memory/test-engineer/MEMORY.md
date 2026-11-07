# test-engineer 项目记忆 — {PROJECT_NAME}

> TRAE 不自动注入记忆：本文件由对应 `sdlc-*` 技能在开始时**显式 Read**。
> 只允许 agent 自己追加「待验证」区；「已验证」「用户偏好与禁止项」由 kb-curator 维护。

## 已验证
- [M-TE-001] 验收标准中的手工算术（如“汉字 4 + 空格 1 + 换行 1”）易漏项；期望值应从定义（如 Unicode 码位）推出，并回写修正需求文档 — conf 0.6 · 证据 textstats-D-001-1 / AC-001-04、TC-UNIT-004（unit_test_report.md:27）/ GR-A-002 · 首见 2026-11-07 · 命中 1
- [M-TE-002] 按行尾后缀过滤文本输出会把 `lines: 1` 这类字段误计入结果；应先按段落/区段切分再计数 — conf 0.6 · 证据 textstats-D-001-2 / TC-E2E-002（e2e_test_report.md:53）/ GR-D-001 · 首见 2026-11-07 · 命中 1

## 用户偏好与禁止项
<!-- - [M-TE-002] … — 来源：用户原话 / YYYY-MM-DD -->

## 待验证
<!-- - [P-TE-001] 一句话 — 自记 YYYY-MM-DD · 证据（可空） -->
