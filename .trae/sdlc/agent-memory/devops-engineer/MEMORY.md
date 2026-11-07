# devops-engineer 项目记忆 — {PROJECT_NAME}

> TRAE 不自动注入记忆：本文件由对应 `sdlc-*` 技能在开始时**显式 Read**。
> 只允许 agent 自己追加「待验证」区；「已验证」「用户偏好与禁止项」由 kb-curator 维护。

## 已验证
- [M-DE-001] 本地演练类部署同样需要独立的回滚锚点步骤；目标目录首次不存在时用 `NO_PREVIOUS_VERSION` 标记区分“整目录移除”与“从锚点覆盖恢复”，避免回滚误删既有目录 — conf 0.6 · 证据 textstats-E1-001-1 / deployment_plan.md DEPLOY-001、ROLLBACK-002 / GR-E1-001 · 首见 2026-11-07 · 命中 1
- [M-DE-002] Windows/PowerShell 本地部署的删除类回滚命令必须带路径前缀护栏（`-like '*deploy/anchors/*'`）并在执行前回显变量，等价于远端 ssh 的变量展开核验 — conf 0.6 · 证据 textstats-E1-001-2 / deployment_plan.md ROLLBACK-001/002 / GR-E1-001 · 首见 2026-11-07 · 命中 1

## 用户偏好与禁止项
<!-- - [M-DE-002] … — 来源：用户原话 / YYYY-MM-DD -->

## 待验证
<!-- - [P-DE-001] 一句话 — 自记 YYYY-MM-DD · 证据（可空） -->
