<file_header>
  <author_agent>system-architect</author_agent>
  <timestamp>2026-11-07T18:49:38.7975589+08:00</timestamp>
  <project_name>textstats</project_name>
  <version>1.0.0</version>
  <input_files><file>project_workspace/textstats/requirements/requirements_spec.md</file><file>project_workspace/textstats/requirements/user_stories.md</file></input_files>
  <phase>PHASE_03</phase>
  <status>APPROVED</status>
</file_header>

## 架构概览

架构风格：单进程、一次性执行的命令行工具，按「参数解析 → 纯统计 → 渲染」三层切分，无网络监听、无持久化。质量属性来自 REQ-NFUNC-001（仅标准库）与 REQ-NFUNC-002（退出码契约）；功能覆盖 REQ-FUNC-001~006。

## 部署视图

| 组件 | 运行单元 | 环境 |
|---|---|---|
| textstats CLI | 一次性 Python 进程（`python src/textstats.py <file>`） | dev/local（画像 P7 中唯一存在的环境） |

画像 P7 声明 staging / production 不存在，本设计不描述这两个环境；不涉及常驻服务、定时任务或容器。

## ADR

### ADR-001: 运行时与依赖边界
- Status: Proposed
- Type: constraint-driven
- Context: REQ-NFUNC-001 要求只用标准库；画像 P1 指定 Python 3.11+、P8 禁止第三方依赖与联网。
- Options: 被排除方案：A 引入 `click`/`rich` 提升 CLI 体验（需 pip 安装，违反 P8/REQ-NFUNC-001）；B 改用 Go 静态二进制（违反画像 P1 技术栈，且沙箱无 Go 工具链）。
- Decision: 使用 Python 3.11+ 标准库（`argparse`、`json`、`collections`、`dataclasses`、`unittest`）。
- Consequences: 正向 零依赖、可离线复制运行；负向 CLI 帮助文案与彩色输出能力弱于第三方库。

### ADR-002: 进程形态
- Status: Proposed
- Type: decision
- Context: REQ-FUNC-001~006 全部是"读一个文件并输出统计"，无跨调用状态。
- Options: A 常驻 HTTP 服务（优：可复用、并发；缺：需要端口与鉴权、与 REQ-NFUNC-001 的沙箱限制无关却增加部署单元）；B 一次性 CLI 进程（优：零部署、退出码即契约；缺：每次调用有进程启动开销）。
- Decision: 选 B。REQ-NFUNC-002 以退出码区分成功/失败，CLI 最直接；画像 P7 仅有本地环境。
- Consequences: 正向 无服务依赖、易在测试中通过子进程驱动；负向 大文件只能单次全量处理，无法增量缓存。

### ADR-003: 模块切分
- Status: Proposed
- Type: decision
- Context: 4 个用户故事分别验证计数、Top-N、JSON 与错误路径，需要可独立测试的单元。
- Options: A 单文件脚本（优：文件少；缺：统计逻辑与参数解析耦合，单元测试需绕过 sys.argv）；B 三层：`textstats.py`（CLI）+ `stats.py`（纯函数）+ `render.py`（格式化）（优：纯函数可直接单测、渲染可互换；缺：文件数增加）。
- Decision: 选 B，使 US-001/US-002 的核心逻辑无需进程即可单测，US-003 的输出格式独立变化。
- Consequences: 正向 单测无 I/O、模块职责单一；负向 需要维护模块间接口。

### ADR-004: 输出格式
- Status: Proposed
- Type: decision
- Context: REQ-FUNC-005 要求可选 JSON；REQ-FUNC-001~004 的默认输出面向人阅读。
- Options: A 只输出文本（优：实现最简；缺：不满足 REQ-FUNC-005）；B 文本为默认 + `--json` 切换（优：兼容人工与脚本；缺：两套渲染需保持数值一致）；C 只输出 JSON（优：机器友好；缺：违背故事 US-001 的人工可读预期）。
- Decision: 选 B，`--json` 输出单行 JSON 对象。
- Consequences: 正向 两种消费方式共存；负向 需用 AC-003-02 约束两套渲染的数值一致性。

### ADR-005: 错误处理与退出码
- Status: Proposed
- Type: constraint-driven
- Context: REQ-FUNC-006 / REQ-NFUNC-002 与画像 P6 规定错误写 stderr、退出码 2。
- Options: 被排除方案：A 用 `sys.exit(1)` 表示参数错误（与 REQ-NFUNC-002 的 0/2 契约冲突）；B 抛出未捕获异常（会输出 traceback，退出码 1）。
- Decision: 统一捕获输入类错误，写一行 stderr 后返回 2；成功返回 0。
- Consequences: 正向 脚本能稳定区分成功/失败；负向 真实编程错误也被归入 2，需要靠错误文案区分。

## 开放问题 / ASSUMPTION

- 开放问题 1（来源 requirements_spec.md）：纯标点词（如 `--`）是否计入词频，当前按"非空空白分隔串"计入，与 REQ-FUNC-002 一致。
- [ASSUMPTION] 未对输入文件大小设上限；若后续需要，需新增 REQ 并按 REQ-FUNC-006 归入退出码 2。
