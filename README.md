# SDLC Agent Suite v3.5.1

这是一套通用的 Claude Code 子代理，按软件开发生命周期完成一个需求：需求分析 → 架构设计 → 开发 → 测试 → CI/部署计划 → 知识蒸馏。项目经理代理 `pm-orchestrator` 负责编排，每个阶段结束都要过门控评审，并亲自复跑测试核验结果。生产部署只有在你当轮明确授权后才会执行。

套件本身不绑定任何项目。项目事实写在各仓库的 `project_profile.md`（项目画像）里，项目经验存放在各 agent 的项目记忆中。

## 组成

| 文件 | 作用 |
|---|---|
| `.claude/agents/pm-orchestrator.md` | 项目经理（主会话运行）：画像引导、阶段编排、门控、澄清、缺陷回流、上报 |
| `.claude/agents/requirement-analyst.md` | GROUP_A：需求规格、用户故事（MoSCoW、故事点、G/W/T 验收标准）；可联网查行业做法/法规，结论标为待确认推断 |
| `.claude/agents/system-architect.md` | GROUP_B：架构决策（ADR）、模块设计（类型化接口契约）、技术栈；可联网核实版本、许可证、漏洞与兼容性 |
| `.claude/agents/software-developer.md` | GROUP_C：实现与五维代码自评审，修复缺陷 |
| `.claude/agents/test-engineer.md` | GROUP_D：单元 / 集成 / E2E 三层测试，真实执行，阈值或基线判定 |
| `.claude/agents/devops-engineer.md` | GROUP_E1：CI/CD 与部署计划；GROUP_E2：授权后执行部署与回滚 |
| `.claude/agents/kb-curator.md` | PHASE_12：知识蒸馏，把有证据的经验晋升到各 agent 记忆 |
| `.claude/agents/agent-builder.md` | 辅助成员（不属于阶段，按需调用）：用固定 6 维细则给 agent 打分（每条扣分带行号），优化或生成 agent；评审套件成员时按共享协议口径 |
| `.claude/agents/shared_protocol.md` | 共享协议：工作区与写权限、文件头与版本、状态码、调用/响应格式、门控标准、测试口径、安全、记忆 |
| `.claude/agents/templates/project_profile.template.md` | 项目画像模板（P1–P10） |
| `.claude/agents/templates/agent_builder_templates.md` | agent-builder 生成 agent 用的模板（九层骨架、安全块、记忆与知识模块、子代理规范、套件成员骨架） |
| `.claude/agents/knowledge_base/generic/` | 跨项目通用经验（随套件分发） |
| `.claude/hooks/sdlc_subagent_stop.py` | SubagentStop：检查子代理返回是否完整，收集经验提案写入收件箱（凭据自动脱敏） |
| `.claude/hooks/sdlc_webfetch_guard.py` | PreToolUse：agent-builder 只能用 WebFetch 访问 Claude Code 官方文档白名单页，其他网址与 WebSearch 一律拒绝 |
| `.claude/hooks/sdlc_pre_agent.py` | PreToolUse：主会话不在仓库根时拒绝调用 SDLC 子代理，防止子代理记忆目录建错位置 |
| `.claude/settings.example.json` | 钩子注册；远程操作与安装依赖前要求确认 |

## 安装

见 [`.claude/agents/INSTALL.md`](.claude/agents/INSTALL.md)。简要步骤：

1. 把 `.claude/agents/` 和 `.claude/hooks/` 复制到目标仓库的 `.claude/` 下。
2. 把 `settings.example.json` 里的 `hooks` 和 `permissions` 合并进目标仓库的 `.claude/settings.json`。
3. 在目标仓库根目录运行 `claude --agent pm-orchestrator`，然后直接提需求。第一次运行时，PM 会先扫描仓库生成项目画像初稿，请你确认后再开始。

## 设计要点

- **pm-orchestrator 必须作为主会话运行**：子代理虽然可以再调用子代理（默认最多三层），但无法直接与用户对话；澄清、门控争议和部署授权都需要读到你当轮的消息。
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

部署执行（GROUP_E2）及其回滚分支尚未实测。
