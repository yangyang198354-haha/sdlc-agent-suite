<file_header>
  <author_agent>devops-engineer</author_agent>
  <timestamp>2026-11-07T18:59:24.9646875+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/architecture/architecture_design.md</file><file>project_workspace/textstats/architecture/module_design.md</file><file>project_workspace/textstats/development/implementation_plan.md</file><file>project_workspace/textstats/testing/e2e_test_report.md</file><file>project_workspace/textstats/deployment/cicd_pipeline.md</file></input_files>
  <phase>PHASE_11a</phase>
  <status>APPROVED</status>
</file_header>

## 变更摘要

| 组件 | 文件 | 迁移 | 构建 | 需重启/发布的运行单元 |
|---|---|---|---|---|
| textstats CLI（architecture_design 部署视图中唯一组件） | `output/sandbox-v38-textstats/src/stats.py`、`render.py`、`textstats.py`（均新增） | 无（module_design「数据迁移：无」） | 无（纯 Python 脚本，`py_compile` 仅做语法检查） | 无；一次性 CLI 进程，改代码后下次调用即生效（画像 P7） |

不涉及常驻服务、定时任务、数据库、容器与网络监听；画像 P7 中 staging / production 不存在，本计划只覆盖 dev/local。

## 目标环境与策略

- 目标环境：**dev/local**（画像 P7 唯一存在的环境；接入方式：本机命令行）。
- 部署方式：本地演练（复制脚本到本地目录并运行），不使用 ssh/scp/git push（画像 P8 禁用）。
- 部署策略：**recreate**（画像 P7 允许的唯一策略）。
  - 理由：单实例、一次性执行的 CLI，没有并发请求与常驻进程；不存在旧版本进程与新版本并存的问题，无需 rolling / blue-green / canary。
  - 预计停机：**无**。复制文件期间没有运行中的服务；唯一需要的时序约束是"不在某次 CLI 调用执行中替换其源码"，由预检第 6 项保证。
- 部署目录：`output/sandbox-v38-textstats/deploy/2026-11-07/`（运行目录）；回滚锚点：`output/sandbox-v38-textstats/deploy/anchors/20261107T190000/`。
- 执行位置：全部在开发机执行，由 PM 协调；本次 **GROUP_E2 未获授权**，本文件仅为计划，不执行任何步骤。

## 预检清单

| # | 检查项 | 命令 | 通过标准 |
|---|---|---|---|
| 1 | 测试门控已通过 | 读取 `project_workspace/textstats/phase_status.md` | GROUP_D 状态为 APPROVED（当前已满足） |
| 2 | 目标环境在画像中且策略被允许 | 读取画像 P7 | 环境=dev/local；策略=recreate；staging/production 未被引用 |
| 3 | Python 版本满足画像 P1 | `python --version` | 主版本 ≥ 3.11（当前 3.14.6） |
| 4 | 待部署源码可编译 | `python -m py_compile output/sandbox-v38-textstats/src/stats.py output/sandbox-v38-textstats/src/render.py output/sandbox-v38-textstats/src/textstats.py` | 退出码 0 |
| 5 | 全量回归通过（部署前基线） | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_*.py" -t output/sandbox-v38-textstats/tests` | 退出码 0；25/25 通过 |
| 6 | 无并发调用占用运行目录 | `Get-Process python -ErrorAction SilentlyContinue` | 无正在执行 textstats 的进程（人工确认） |
| 7 | 运行目录现状已记录（回滚锚点来源） | `Test-Path "output/sandbox-v38-textstats/deploy/2026-11-07"` | 返回 True/False 并写入部署记录；首次部署为 False |
| 8 | 回滚变量取值正确 | `Write-Output "$RUN_DIR"` / `Write-Output "$ANCHOR_DIR"` | 与本节定义的路径逐字符一致；路径以 `deploy\` 结尾不含通配符 |
| 9 | 磁盘空间足够 | `python -c "import shutil;print(shutil.disk_usage('.').free)"` | 可用空间 ≥ 10 MB |
| 10 | 必须保留的本地状态 | 画像 P7「目标机上必须保留的本地状态：无」 | 无额外保留项，本次复制不触碰 `fixtures/`、`tests/`、`project_workspace/` |
| 11 | 无迁移/备份需求 | 读取 module_design「数据迁移」 | 为"无"即通过 |

预检失败处理：在**目标运行目录尚未发生任何变更**时停止，报告 DEPLOYMENT_FAILED（无需回滚）。

## 部署步骤

变量（部署前在同一 PowerShell 会话中定义，并在预检第 8 项回显核对）：

```powershell
$RUN_DIR    = "output/sandbox-v38-textstats/deploy/2026-11-07"
$ANCHOR_DIR = "output/sandbox-v38-textstats/deploy/anchors/20261107T190000"
$SRC_DIR    = "output/sandbox-v38-textstats/src"
$FILES      = @("stats.py", "render.py", "textstats.py")
```

### DEPLOY-001: 建立回滚锚点
- 组件: textstats CLI（architecture_design 部署视图）
- 位置: 开发机
- 命令:
```powershell
New-Item -ItemType Directory -Force -Path $ANCHOR_DIR | Out-Null
if (Test-Path $RUN_DIR) {
  Copy-Item -Path (Join-Path $RUN_DIR '*') -Destination $ANCHOR_DIR -Recurse -Force
} else {
  Set-Content -Path (Join-Path $ANCHOR_DIR 'NO_PREVIOUS_VERSION.txt') -Value '首次部署：部署前不存在运行目录'
}
Get-ChildItem -Recurse $ANCHOR_DIR | Select-Object FullName
```
- 预期: 锚点目录创建成功；若为首次部署，目录内只有 `NO_PREVIOUS_VERSION.txt`；否则为上一版运行目录的完整副本。
- 回滚: ROLLBACK-001

### DEPLOY-002: 装配并落地源码
- 组件: textstats CLI（module_design MOD-001/002/003）
- 位置: 开发机
- 命令:
```powershell
New-Item -ItemType Directory -Force -Path $RUN_DIR | Out-Null
foreach ($f in $FILES) {
  Copy-Item -Path (Join-Path $SRC_DIR $f) -Destination (Join-Path $RUN_DIR $f) -Force
}
Get-FileHash (Join-Path $SRC_DIR '*') , (Join-Path $RUN_DIR '*') -Algorithm SHA256 |
  Select-Object Path, Hash
```
- 预期: 3 个文件复制成功；源目录与运行目录同名文件 SHA-256 两两相同；退出码 0。
- 回滚: ROLLBACK-002

## 回滚步骤（逆序）

### ROLLBACK-002: 回滚 DEPLOY-002（恢复运行目录内容）
- 类型: 正式回滚
- 命令:
```powershell
if (Test-Path (Join-Path $ANCHOR_DIR 'NO_PREVIOUS_VERSION.txt')) {
  # 首次部署：运行目录由本次部署创建，整目录移除即为完全回滚
  if ($RUN_DIR -like '*deploy/2026-11-07*' -and (Test-Path $RUN_DIR)) {
    Remove-Item -Path $RUN_DIR -Recurse -Force
  }
} else {
  # 重复部署：按锚点覆盖回上一版文件（只覆盖锚点中存在的文件，不删除运行目录其他文件）
  Copy-Item -Path (Join-Path $ANCHOR_DIR '*') -Destination $RUN_DIR -Recurse -Force
}
Test-Path $RUN_DIR
```
- 变量取值与核验: `$RUN_DIR`、`$ANCHOR_DIR` 与"部署步骤"定义一致，执行前用 `Write-Output` 回显；`$ANCHOR_DIR` 必须是 `deploy/anchors/` 下的时间戳目录；`$RUN_DIR -like '*deploy/2026-11-07*'` 作为删除护栏，不匹配则拒绝删除并上报。
- 预期: 首次部署时 `Test-Path $RUN_DIR` 返回 `False`；重复部署时运行目录内 3 个文件恢复为锚点版本（SHA-256 与锚点一致）。

### ROLLBACK-001: 回滚 DEPLOY-001（清理锚点目录）
- 类型: 收尾清理（必须在 ROLLBACK-002 之后执行）
- 命令:
```powershell
if ($ANCHOR_DIR -like '*deploy/anchors/*' -and (Test-Path $ANCHOR_DIR)) {
  Remove-Item -Path $ANCHOR_DIR -Recurse -Force
}
Test-Path $ANCHOR_DIR
```
- 变量取值与核验: 同上；`-like '*deploy/anchors/*'` 护栏防止误删其他目录。若是重复部署且需保留历史锚点，则由 PM 批准后跳过本步并登记原因（不得静默跳过）。
- 预期: 返回 `False`；`deploy/anchors/` 下不再残留本次锚点，工作树回到部署前状态。

## 不可逆步骤汇总

**无。** 本次变更不包含数据迁移、外部系统调用、通知发送、覆盖式同步或删除用户文件；回滚锚点为本地副本，两步回滚后可完全恢复部署前状态。

## 部署后验证

| # | 检查项 | 命令 | 成功标准 |
|---|---|---|---|
| 1 | 落地文件与源一致 | `Get-FileHash` 对 `$SRC_DIR` 与 `$RUN_DIR` 的同名文件 | 3/3 SHA-256 相同 |
| 2 | 装配后可编译 | `python -m py_compile (Join-Path $RUN_DIR 'textstats.py')` | 退出码 0 |
| 3 | 冒烟（画像 P7 指定） | `python (Join-Path $RUN_DIR 'textstats.py') output/sandbox-v38-textstats/fixtures/sample.txt` | 退出码 0；输出含 `lines: 2`、`words: 3`、`chars: 16` |
| 4 | JSON 路径可用且与文本数值一致 | 同一文件加 `--json`，用 `json.loads` 解析 | 四键齐全；`lines/words/chars` 与第 3 项一致 |
| 5 | 错误路径符合退出码契约 | 对不存在路径运行 | 退出码 2；stdout 为空；stderr 恰一行且含文件名；无 traceback |
| 6 | 服务存活 / 健康检查 | 不适用（无常驻进程、无端口） | 以第 3、5 项代替；无 traceback 视为通过 |
| 7 | 日志无新错误 | 不适用（无日志文件，输出即 stdout/stderr） | 第 3、5 项输出符合预期即视为通过 |
| 8 | 外部可达性 | 不适用（本地 CLI，不监听网络） | 不适用 |

验证失败处理：任一验证项失败 → 立即按 ROLLBACK-002 → ROLLBACK-001 逆序回滚（当时尚未执行 ROLLBACK-001 之前），报告 `ROLLED_BACK`；不得跳过失败继续后续验证。
