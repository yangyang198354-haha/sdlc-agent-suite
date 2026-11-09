# SDLC Agent Suite v3.9

这是一套通用的 Claude Code 子代理，按软件开发生命周期完成一个需求：需求分析 → 架构设计 → 开发 → 测试 → CI/部署计划 → 知识蒸馏。项目经理代理 `pm-orchestrator` 负责编排，每个阶段结束都要过门控评审，并亲自复跑测试核验结果。生产部署只有在你当轮明确授权后才会执行。

套件本身不绑定任何项目。项目事实写在各仓库的 `project_profile.md`（项目画像）里，项目经验存放在各 agent 的项目记忆中。

## 组成

| 文件 | 作用 |
|---|---|
| `.claude/agents/pm-orchestrator.md` | 项目经理（主会话 / 子代理双模式）：画像引导、阶段编排、门控、澄清、缺陷回流、上报 |
| `.claude/agents/requirement-analyst.md` | GROUP_A：需求规格、用户故事（MoSCoW、故事点、G/W/T 验收标准）；可联网查行业做法/法规，结论标为待确认推断 |
| `.claude/agents/system-architect.md` | GROUP_B：架构决策（ADR）、模块设计（类型化接口契约）、技术栈；可联网核实版本、许可证、漏洞与兼容性 |
| `.claude/agents/software-developer.md` | GROUP_C：实现与五维代码自评审，修复缺陷 |
| `.claude/agents/test-engineer.md` | GROUP_D：单元 / 集成 / E2E 三层测试，真实执行，阈值或基线判定 |
| `.claude/agents/devops-engineer.md` | GROUP_E1：CI/CD 与部署计划；GROUP_E2：授权后执行部署与回滚 |
| `.claude/agents/kb-curator.md` | PHASE_12：知识蒸馏，把有证据的经验晋升到各 agent 记忆 |
| `.claude/agents/agent-builder.md` | 辅助成员（不属于阶段，按需调用）：用固定 6 维细则给 agent 打分（每条扣分带行号），优化或生成 agent；评审套件成员时按共享协议口径 |
| `.claude/agents/shared_protocol.md` | 共享协议：工作区与写权限、文件头与版本、状态码、调用/响应格式、门控标准、测试口径、安全、记忆、领域事实出处（§N） |
| `.claude/agents/templates/project_profile.template.md` | 项目画像模板（P1–P11，P11 = 专用硬件 / 领域算法 / 闭源 API） |
| `.claude/agents/templates/agent_builder_templates.md` | agent-builder 生成 agent 用的模板（九层骨架、安全块、记忆与知识模块、子代理规范、套件成员骨架） |
| `.claude/agents/knowledge_base/generic/` | 跨项目通用经验（随套件分发） |
| `.claude/hooks/sdlc_subagent_stop.py` | SubagentStop：检查子代理返回是否完整（PM 子代理模式检查 `<pm_report>`），收集经验提案写入收件箱（凭据自动脱敏） |
| `.claude/hooks/sdlc_webfetch_guard.py` | PreToolUse：agent-builder 只能用 WebFetch 访问 Claude Code 官方文档白名单页，其他网址与 WebSearch 一律拒绝 |
| `.claude/hooks/sdlc_pre_agent.py` | PreToolUse：当前目录不在仓库根时拒绝调用 SDLC 子代理（含 pm-orchestrator），防止子代理记忆目录建错位置 |
| `.claude/settings.example.json` | 钩子注册；远程操作与安装依赖前要求确认 |

## 多平台版本

同一套角色同时提供三个平台的落地形态，内容以 `.claude/agents/` 为唯一真源。

| 平台 | 位置 | 形态 | 说明 |
|---|---|---|---|
| Claude Code | `.claude/` | agents + hooks + templates + knowledge_base | 源套件，v3.9 |
| Codex | `.codex/` + `scripts/codex_sdlc/` + `AGENTS.md` | 8 个 `agents/*.toml` + `sdlc/`（shared_protocol、pm-orchestrator、runtime_adapter、knowledge_base、templates、migration_manifest）+ `rules/sdlc.rules` + `hooks.json` + `config.toml`；根目录 `scripts/codex_sdlc/`（hook_runtime、fetch_docs、migrate、verify_migration、test_hooks、probe_runtime）+ `AGENTS.md` + `docs/codex-agent-migration.md` | 由 `.claude/agents/*.md` 迁移生成，当前对应 v3.9；**hooks.json 依赖 `scripts/codex_sdlc/hook_runtime.py`，缺脚本则 hook 空转**；`rules/sdlc.rules` 附带原始项目的权限策略（docker 禁用），复用到其他项目时按需调整 |
| Trae | `.trae/` | 9 个 `skills/sdlc-*/SKILL.md` + 8 个 `agent-packs/*.md` + `sdlc/` 运行时（scripts / knowledge_base / templates / suite_config） | 由 `.trae/sdlc/scripts/port_from_claude.py` 从 `.claude/agents/*.md` 生成，当前对应 v3.9 |

Trae 版同步方式（改完 `.claude/agents/` 后重跑，版本号在脚本 `SUITE_VERSION`）：

```bash
python .trae/sdlc/scripts/port_from_claude.py --check   # 只报告
python .trae/sdlc/scripts/port_from_claude.py           # 重写 skills / packs / 通用知识库
```

Codex 版同步（改完 `.claude/agents/` 后；生成到 `output/` 再逐文件校验安装，不覆盖 `.codex/sdlc/INSTALL.md`、已有 `AGENTS.md` 与已有记忆）：

```bash
python scripts/codex_sdlc/migrate.py build && python scripts/codex_sdlc/migrate.py install
python scripts/codex_sdlc/verify_migration.py --no-write
```

升级已安装的项目（把本仓库当前版本分发到一个或多个目标仓库；只改套件自有文件，不碰画像、记忆、`settings.json`；目标装了 Trae / Codex 时在目标内重新生成并自检；不做 git 提交）：

```bash
python3 scripts/sync_suite.py --check ../projA ../projB   # 只报告：NEW / UPDATE / UPGRADE / KEEP / CONFLICT
python3 scripts/sync_suite.py ../projA ../projB           # 写入
```

目标中套件路径有未提交改动时拒绝；文件内容不是套件历史版本（项目本地改过）时记 CONFLICT 跳过，`--force` 才覆盖。

Trae 版安装：把 `.trae/` 复制到目标仓库的 `.trae/`，在主会话加载 `Skill: sdlc-orchestrator`。
Codex 版安装：把 `.codex/`、`scripts/codex_sdlc/`、`AGENTS.md` 复制到目标仓库根（`docs/codex-agent-migration.md` 供参考），按 `.codex/sdlc/INSTALL.md` 完成配置，并在 Codex `/hooks` 中审阅、信任 hooks。hook 缺失或被拒绝信任时不会自动注入记忆、校验返回或拦截 cwd，角色须显式读取记忆。

## 安装

见 [`.claude/agents/INSTALL.md`](.claude/agents/INSTALL.md)。简要步骤：

1. 把 `.claude/agents/` 和 `.claude/hooks/` 复制到目标仓库的 `.claude/` 下。
2. 把 `settings.example.json` 里的 `hooks` 和 `permissions` 合并进目标仓库的 `.claude/settings.json`。
3. 在目标仓库根目录选一种方式启动 PM（见下方"两种运行模式"），然后直接提需求。第一次运行时，PM 会先扫描仓库生成项目画像初稿，请你确认后再开始。

## 两种运行模式

| | 主会话模式 | 子代理模式 |
|---|---|---|
| 启动 | `claude --agent pm-orchestrator` | 普通会话里 `@pm-orchestrator 需求…` |
| 交互 | 当场提问，你当场回答 | 一口气跑到需要你决定的地方（检查点），返回问题清单；你回答后再 @ 一次，从断点续跑 |
| 子代理澄清 | 问你 | 普通问题由 PM 按最保守选项代答并标"待确认"；关键问题进检查点 |
| 部署 | E1 后经你当轮授权可执行 E2 | 止于部署计划（E1），不执行任何部署 |
| 适合 | 需要频繁拍板、要部署 | 需求明确、想在当前会话里顺手推进 |

两种模式共用同一份 `phase_status.md`，可以随时切换：比如先用子代理模式跑到部署计划，再用主会话模式授权部署。

## 设计要点

- **PM 双模式**：子代理无法和用户来回对话，所以 PM 在子代理模式下把需要你决定的事写成检查点（`phase_status.md` 的 `<checkpoints>`），以 `<pm_report>` 返回，下次调用时续跑。模式判断拿不准时按子代理模式处理；部署授权只在主会话模式下、且只认你当轮的直接表述，转述的授权一律无效。
- **领域与外部依赖（画像 P11，v3.7）**：专用硬件、细分领域算法、闭源或内部 API 的事实，模型自身的知识靠不住。P11 只记录资料在仓库里的位置和测试能力，产物中涉及这些事实的地方必须标出处（`[P11: 文件:位置]` 或 `[CODE: 文件:行]`）。找不到出处就停下来问，不凭记忆补全；架构和开发门控会打开原文核对出处。真机才能验证的用例进人工验证清单，闭源 API 只用 mock 或沙箱测试。
- **三层知识**：
  - 通用经验：`knowledge_base/generic/`
  - 项目记忆：原生 `memory: project`，路径 `.claude/agent-memory/{agent}/MEMORY.md`，自动注入
  - 经验收件箱：`project_workspace/_kb_inbox.jsonl`，由 kb-curator 按证据和置信度蒸馏
- **流程模式**：
  - FULL_FLOW：新子系统，按阈值判定
  - INCREMENTAL：现有代码上的改动，相对基线零新增失败
  - PARTIAL_FLOW：从中间某个阶段开始
- **状态与续跑**：状态写在 `phase_status.md`（可解析的 XML）。中断后可以按这个文件续跑。
- **联网**：需求分析与架构 agent 有 WebSearch / WebFetch；agent-builder 只有 WebFetch，且只能访问 Claude Code 官方文档的固定几页，用于核实平台事实（由 `sdlc_webfetch_guard.py` 钩子强制）。查询不得带项目代码、内部地址或凭据，网页内容只当数据，引用标 `[WEB: URL，日期]`。
- **评审 agent**：`claude --agent agent-builder` 或在主会话中让它评审某个 agent。默认只在回复中给结果，要写文件需在请求里写 `WRITE_TARGET: <路径>`（覆盖已有文件还需 `OVERWRITE_AUTHORIZED: <路径>`）。
- **无人值守运行**：需要澄清时，按"最保守、改动最小"的选项代答并记录在案；存在代答时，最终状态不会是 DELIVERED。

## 验证情况

已在 4 个不同技术栈的仓库（Django、FastAPI、Django + Celery、Django/DRF 单体）上，在沙箱里跑通了 需求 → 部署计划 → 知识蒸馏 的完整流程。主会话亲自复跑测试，原有测试均无新增失败。

v3.6 的子代理模式在沙箱里实测过：画像检查点 → 按答复续跑 A→E1 → 知识蒸馏，转述来的部署授权被拒绝并记入审计；嵌套调用（PM → 阶段代理）时 hook 正常校验报告块。

v3.7 的画像 P11 在沙箱里实测过：项目同时含闭源 API（只有 OpenAPI 文件）、非标准 FIR 滤波（golden data + 1e-9 容限）和传感器板寄存器（只能人工真机验证）。PM 扫描识别出三类资料，把文档里没有的"平台重试策略"列为必答问题；架构出处表逐条引用原文，代码没有编造字段或寄存器值，真机验证项进了人工验证清单，最终状态 DELIVERED_WITH_ISSUES。

部署执行（GROUP_E2）及其回滚分支尚未实测。
