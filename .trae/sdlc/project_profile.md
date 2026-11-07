# Project Profile — textstats（v3.8 沙箱验收项目）

> 本画像仅服务于 `output/sandbox-v38-textstats/` 下的套件验收迷你项目，不描述套件仓库自身的产品代码。

<file_header>
  <author_agent>pm-orchestrator(draft)</author_agent>
  <timestamp>2026-11-07T18:41:41.6690877+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.1.0</version>
  <status>APPROVED</status>
</file_header>

## P1. 项目概况
- 一句话描述：统计文本文件的行数、词数、字符数，并输出出现频次最高的 N 个词（命令行工具）。
- 技术栈：| 层 | 技术 | 版本 | ；CLI | Python | 3.11+（本机 3.14.6）；仅标准库
- 运行形态：CLI
- 权威说明文档：`project_workspace/textstats/requirements/requirements_spec.md`

## P2. 文档工作区
- `docs_root`: project_workspace/textstats/
- `docs_layout`: nested
- 是否入库: 是（本次沙箱运行不提交任何文件）

## P3. 代码布局
- `code_mode`: greenfield
- 代码目录：| 组件 | 目录 | 语言 | ；textstats | output/sandbox-v38-textstats/src/ | Python
- 测试位置约定：| 组件 | 新测试放在 | 命名 | 测试基类/框架 | ；textstats | output/sandbox-v38-textstats/tests/ | test_*.py | unittest
- 不可修改的目录（第三方、生成产物、vendor）：无

## P4. 命令（全部在开发机/CI 上运行，严禁连生产；需要仿真器或真实硬件的测试写在 P11-1）
| 用途 | 工作目录 | 命令 | 备注 |
|---|---|---|---|
| 环境准备 | 仓库根 | 无 | 仅标准库，不建 venv、不联网 |
| 静态检查 / 编译检查 | 仓库根 | `python -m py_compile output/sandbox-v38-textstats/src/textstats.py` | 无第三方 linter |
| 单元测试 | 仓库根 | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_unit_*.py" -t output/sandbox-v38-textstats/tests` | 按文件名前缀分层 |
| 集成测试 | 仓库根 | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_integration_*.py" -t output/sandbox-v38-textstats/tests` | 子进程调用 CLI |
| E2E 测试 | 仓库根 | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_e2e_*.py" -t output/sandbox-v38-textstats/tests` | 真实文件 + 真实退出码 |
| 全量回归 | 仓库根 | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_*.py" -t output/sandbox-v38-textstats/tests` | 耗时约数秒 |
| 构建 | 仓库根 | 无 | 纯脚本，无构建产物 |
- 已知既有失败 / 基线来源：无（全新项目）
- 缺依赖时的处理：如实标 BLOCKED，不安装

## P5. 质量判定
- FULL_FLOW `gate_mode`: threshold — unit_pass 0.80 / integration_pass 0.90 / critical_path 1.00 / coverage_min 无
- INCREMENTAL `gate_mode`: baseline — 零新增失败
- `inferred_max`: 0.20（需求中 [INFERRED] 占比上限）

## P6. 开发约定
- 数据迁移方式：不涉及
- 鉴权与权限模型：不涉及
- 代码风格 / lint 规则：PEP 8，标准库风格，模块级 docstring
- 依赖管理（锁文件、版本 pin）：禁止第三方依赖
- 其他必须遵守的约定：CLI 错误统一写 stderr 并返回退出码 2

## P7. 环境、CI 与部署
- 环境：
  | 环境 | 存在 | 访问方式（不含口令） | 部署需用户确认 | 备注 |
  |---|---|---|---|---|
  | dev/local | 是 | 本机命令行 | 否 | 沙箱演练用 |
  | staging | 否 | — | — | 不存在 |
  | production | 否 | — | **是** | 本次不存在 |
- 部署方式：本地演练（复制脚本到本地目录并运行），无远程环境
- 允许的部署策略：recreate（仅本地演练）
- 构建产物管理：无
- 运行单元（服务/进程/定时任务）与"改什么需重启什么"：一次性 CLI 进程，改代码后下次调用即生效
- 目标机上必须保留的本地状态：无
- 回滚方式偏好：覆盖回上一版脚本文件（本地）
- 部署后验证：`python output/sandbox-v38-textstats/src/textstats.py output/sandbox-v38-textstats/fixtures/sample.txt`
- CI 系统与配置文件：无 CI 系统；`.trae/sdlc/project_profile.md` 为唯一配置来源
- 部署相关配置文件：无

## P8. 禁用项（门控时任一出现即 FAIL）
| 禁用的技术 / 操作 | 原因 |
|---|---|
| 第三方 Python 依赖 / pip install | 沙箱不可联网，验证纯标准库路径 |
| 网络访问（含 WebSearch）与容器 / docker | 沙箱边界 |
| 执行 commit / push / ssh / scp | 本次仅验证套件机制，用户明确不提交 |
| 部署到 staging / production | 环境不存在，且未获授权 |

## P9. 版本控制与远程操作权限
- 分支策略：留在 `feat/v3.8-port-fixes`，不新建分支
- 谁执行 commit / push：不执行（本次用户明确不提交）
- 子代理是否可 ssh / 部署：否
- 提交前必须通过的检查：全量回归 + `python .trae/sdlc/scripts/suite_selftest.py`

## P10. 额外必读（PM 填入 required_reading）
| Agent | 额外文件 |
|---|---|
| requirement-analyst | 无 |
| system-architect | 无 |
| software-developer | 无 |
| test-engineer | 无 |
| devops-engineer | 无 |

## P11. 领域与外部依赖（协议 §N）
无
