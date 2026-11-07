<file_header>
  <author_agent>devops-engineer</author_agent>
  <timestamp>2026-11-07T18:59:24.9646875+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/architecture/architecture_design.md</file><file>project_workspace/textstats/architecture/module_design.md</file><file>project_workspace/textstats/architecture/tech_stack.md</file><file>project_workspace/textstats/development/implementation_plan.md</file><file>project_workspace/textstats/testing/test_plan.md</file><file>project_workspace/textstats/testing/unit_test_report.md</file><file>project_workspace/textstats/testing/integration_test_report.md</file><file>project_workspace/textstats/testing/e2e_test_report.md</file></input_files>
  <phase>PHASE_10</phase>
  <status>APPROVED</status>
</file_header>

## 现状与影响

- 画像 P7 明确：**无 CI 系统**，`.trae/sdlc/project_profile.md` 为唯一配置来源；因此本次**不新增、不修改任何 CI 配置文件**（若是 GitHub Actions / GitLab CI，需新建 `.github/workflows/` 或 `.gitlab-ci.yml`，与画像冲突）。
- 本次改动的影响：全部为新增文件（3 个产品模块 + 4 个测试文件 + `fixtures/`），无新依赖（仅标准库）、无新服务、无新环境变量、无数据迁移。
- 结论：把流水线定义为**可在开发机按顺序手工执行的命令序列**（等价流水线），命令全部取自画像 P4，工具全部在 tech_stack.md 登记，未引入未登记工具。

## 流水线概览

[Source] → [Compile] → [Unit] → [Integration] → [Package] → [Deploy(本地)] → [Smoke] → [E2E]

说明：画像 P7 无构建产物与制品库，`Package` 阶段退化为"装配运行目录"；`Deploy(本地)` 只对应 dev/local 环境。

## 阶段定义

| PIPE | 阶段 | 触发条件 | 命令（仓库根执行） | 成功标准 | 失败处理 |
|---|---|---|---|---|---|
| PIPE-001 | Source | 待部署提交/文件清单确定 | `git status --porcelain` 与变更清单核对 | 仅含已批准文件；无未预期修改 | abort-and-notify，不进入后续阶段 |
| PIPE-002 | Compile / 静态检查 | PIPE-001 通过 | `python -m py_compile output/sandbox-v38-textstats/src/textstats.py output/sandbox-v38-textstats/src/stats.py output/sandbox-v38-textstats/src/render.py` | 退出码 0 | abort-and-notify（画像 P4 无第三方 linter，不引入新工具） |
| PIPE-003 | Unit | PIPE-002 通过 | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_unit_*.py" -t output/sandbox-v38-textstats/tests` | 退出码 0；通过率 ≥ 0.80（画像 P5） | abort-and-notify，缺陷回流 software-developer |
| PIPE-004 | Integration | PIPE-003 通过 | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_integration_*.py" -t output/sandbox-v38-textstats/tests` | 退出码 0；通过率 ≥ 0.90（画像 P5） | abort-and-notify，缺陷回流 software-developer |
| PIPE-005 | Package / 装配 | PIPE-004 通过 | 在开发机建立运行目录并复制 `src/*.py`（见 deployment_plan.md DEPLOY-002） | 3 个 `.py` 文件齐全；`python -m py_compile` 对装配后的入口退出码 0 | abort-and-notify |
| PIPE-006 | Deploy（dev/local） | PIPE-005 通过且获得本次本地演练授权（画像 P7：dev/local 部署需确认=否，由 PM 发起即可） | 见 deployment_plan.md | 见 deployment_plan.md 预检与 DEPLOY 步骤 | abort-and-notify；已变更则按 ROLLBACK 逆序回滚 |
| PIPE-007 | 部署后冒烟 | PIPE-006 成功 | `python <运行目录>/textstats.py output/sandbox-v38-textstats/fixtures/sample.txt`（画像 P7 指定的验证命令） | 退出码 0；`lines: 2`、`words: 3`、`chars: 16` | abort-and-notify，按 ROLLBACK 逆序回滚 |
| PIPE-008 | E2E | PIPE-007 通过 | `python -m unittest discover -s output/sandbox-v38-textstats/tests -p "test_e2e_*.py" -t output/sandbox-v38-textstats/tests` | 退出码 0；critical path 通过率 1.00（画像 P5） | abort-and-notify；不自动回滚，由 PM 结合冒烟结果决定 |

- 失败处理只有 abort-and-notify，不设自动 retry（命令均为确定性本地命令，失败即真实问题）；**禁止跳过失败继续部署**。
- 无外部依赖与网络阶段；画像 P8 的禁用项（第三方依赖、联网、容器、commit/push/ssh/scp、staging/production 部署）不出现在任何阶段。

## 环境矩阵

| 配置项 | dev/local |
|---|---|
| 存在性（画像 P7） | 是 |
| 实例数 | 1 个一次性 Python 进程（非常驻） |
| 资源 | 无特殊要求；仅需 Python 3.11+（本机 3.14.6）与可写本地目录 |
| 外部依赖 | 无（仅标准库） |
| 配置来源 | 无配置文件；参数由命令行传入 |
| 部署需确认（画像 P7） | 否（由 PM 发起本地演练） |
| staging / production | 画像 P7 声明不存在，本流水线不设计、不包含这两个环境 |

## 制品管理

- 画像 P7「构建产物管理：无」，无制品库，流水线不产出打包制品。
- 采用**目标机（本机）本地装配**：从已批准的工作树复制 `src/*.py` 到运行目录，文件内容即源码，无编译产物。
- 命名：运行目录 `output/sandbox-v38-textstats/deploy/<YYYY-MM-DD>/`。
- 晋升条件：PIPE-002~004 全绿 + PM 门控 GROUP_D=APPROVED（当前已是 APPROVED）。
- 风险：本地装配没有版本号与校验和，无法证明"部署的字节"就是"通过测试的字节"。缓解：DEPLOY 后对目标文件计算 SHA-256 并与源文件逐项比对（见 deployment_plan.md 部署后验证）。
