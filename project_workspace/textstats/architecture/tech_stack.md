<file_header>
  <author_agent>system-architect</author_agent>
  <timestamp>2026-11-07T18:49:38.7975589+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/requirements/requirements_spec.md</file><file>project_workspace/textstats/architecture/module_design.md</file></input_files>
  <phase>PHASE_03,PHASE_04</phase>
  <status>APPROVED</status>
</file_header>

## 技术选型表

| 类别 | 选型 | 版本（出处） | 新增/沿用 | 理由 | 关联 REQ | 风险 |
|---|---|---|---|---|---|---|
| 语言 | Python | 3.14.6（实测 `python --version`；画像 P1 要求 3.11+） | 沿用 | 画像指定技术栈，标准库足够 | REQ-NFUNC-001 | 低：3.11~3.14 语法保持兼容 |
| 运行时依赖 | 无 | — | 沿用 | 画像 P8 禁止第三方依赖与联网 | REQ-NFUNC-001 | 低 |
| CLI 解析 | `argparse`（标准库） | 随 Python 3.14.6 | 新增使用 | 内置、无依赖、错误信息可直接映射退出码 2 | REQ-FUNC-006 | 低 |
| 数据统计 | `str.split` / `collections.Counter`（标准库） | 随 Python 3.14.6 | 新增使用 | 纯函数、确定性排序易实现 | REQ-FUNC-001~004 | 低 |
| 序列化 | `json`（标准库） | 随 Python 3.14.6 | 新增使用 | `--json` 输出 | REQ-FUNC-005 | 低 |
| 测试框架 | `unittest`（标准库） | 随 Python 3.14.6 | 新增使用 | 画像 P4 指定，三层按文件名前缀分层 | REQ-NFUNC-002 | 低 |
| CI/CD | 无 | — | 沿用 | 画像 P7 无 CI 系统，本次不新增 | — | 低：依赖本地命令 |
| 部署方式 | 本地复制 + 直接运行 | — | 沿用 | 画像 P7 仅 dev/local | — | 低 |
| 容器化 | 不使用 | — | 沿用 | 画像 P8 禁用 | — | — |

未新增任何第三方依赖，因此无许可证与维护风险。

## 技术风险

| 等级 | 风险 | 缓解措施 |
|---|---|---|
| Medium | 大文件一次性读入内存（`text = path.read_text()`），极端大文件可能 OOM | 本次范围只要求单文件统计；在开放问题登记文件大小上限，若需要再引入分块统计 |
| Medium | 行数语义在 `\r\n` 与末尾无换行时易与用户预期不符 | `count_text` 的语义写进 IFC-002，并用 AC-001-02/03 固化 |
| Low | 词频小写归一可能把 `İ` 等多字符小写展开计入不同长度 | 不影响计数需求；在开放问题说明 |
| Low | 文本模式读取依赖系统默认换行转换 | 固定以 `encoding="utf-8"`、`newline=""` 读取，避免行数因平台变化 |
