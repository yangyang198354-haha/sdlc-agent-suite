#!/usr/bin/env python3
"""把本仓库（SDLC Agent Suite）分发到目标项目仓库，刷新到当前版本。

用法：
    python3 scripts/sync_suite.py --check /path/to/repo [...]   # 只报告，不写
    python3 scripts/sync_suite.py /path/to/repo [...]           # 写入并重新生成移植版
    python3 scripts/sync_suite.py --force ...                   # 冲突文件也覆盖（慎用）

规则：
- 只处理套件自有文件（本仓库 git 跟踪的 .claude/agents、.claude/hooks、
  .claude/settings.example.json；目标已安装 Trae 时加 .trae；已安装 Codex 时加
  .codex、scripts/codex_sdlc、AGENTS.md、docs/codex-agent-migration.md）。
- 永不触碰：project_profile.md、agent-memory、settings.json / settings.local.json、
  目标项目自己新增的文件（如自定义 agent、skills、_archive）。
- Trae skills/agent-packs/知识库副本、Codex 的 agents/hooks/rules/config/manifest 等是生成产物，
  不复制，由目标仓库内的生成器重新生成（Codex 的 AGENTS.md 与记忆由 migrate.py 保留）。
- AGENTS.md、docs/codex-agent-migration.md 安装后归项目所有：已存在则保留（KEEP）。
- 套件工具（.trae/sdlc/scripts、scripts/codex_sdlc、suite_config、Codex INSTALL）：直接升级（UPGRADE）。
- 其余文件：目标内容等于套件某个历史版本 → 覆盖（UPDATE）；否则 CONFLICT 跳过（--force 才覆盖）。
  目标文件不存在 → 新增（NEW）。
- 目标仓库中这些路径有未提交改动 → 拒绝该目标（先提交或 stash）。
- 写入后：有 Trae 则运行 port_from_claude.py 与 suite_selftest.py；有 Codex 则运行
  migrate.py build/install 与 verify_migration.py --no-write。
- 不执行 git add / commit / push。
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent

NEVER = (
    "project_profile.md",
    "/agent-memory/",
    ".claude/settings.json",
    ".claude/settings.local.json",
)
CLAUDE_PREFIXES = (".claude/agents/", ".claude/hooks/", ".claude/settings.example.json")
TRAE_PREFIXES = (".trae/",)
CODEX_PREFIXES = (".codex/", "scripts/codex_sdlc/", "AGENTS.md", "docs/codex-agent-migration.md")
# 由生成器在目标仓库内重新生成，不从套件复制
GENERATED = (
    ".trae/skills/sdlc-", ".trae/agent-packs/", ".trae/sdlc/knowledge_base/",
    ".codex/agents/", ".codex/agent-memory/", ".codex/sdlc/knowledge_base/", ".codex/sdlc/templates/",
    ".codex/sdlc/shared_protocol.md", ".codex/sdlc/pm-orchestrator.md", ".codex/sdlc/runtime_adapter.md",
    ".codex/sdlc/migration_manifest.json", ".codex/hooks.json", ".codex/config.toml", ".codex/rules/",
)
# 安装后归项目所有：只在不存在时新增
PROJECT_OWNED = ("AGENTS.md", "docs/codex-agent-migration.md")
# 套件工具与说明：目标版本不在套件历史中（早期移植的旧版）也直接升级
TOOLING = (".trae/sdlc/scripts/", ".trae/sdlc/suite_config.md", ".trae/sdlc/project_profile.template.md",
           "scripts/codex_sdlc/", ".codex/sdlc/INSTALL.md")


def git(args, cwd, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {cwd}: {r.stderr.strip()}")
    return r.stdout


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def suite_files():
    return [p for p in git(["ls-files"], SUITE).splitlines()
            if not any(n in "/" + p for n in NEVER)]


def history_blobs(path: str):
    out = git(["log", "--all", "--format=", "--raw", "--no-abbrev", "--", path], SUITE)
    blobs = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4 and line.startswith(":"):
            blobs.update(parts[2:4])
    blobs.discard("0" * 40)
    return blobs


def suite_version():
    first = (SUITE / ".claude/agents/INSTALL.md").read_text(encoding="utf-8").splitlines()[0]
    return first.split("Suite")[-1].split("—")[0].strip()


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
    return r.returncode, tail[0]


def sync(target: Path, check: bool, force: bool):
    print(f"\n== {target}")
    if not (target / ".git").exists():
        print("  SKIP: 不是 git 仓库根")
        return 1
    if not (target / ".claude/agents").is_dir():
        print("  SKIP: 未安装 Claude 版套件（无 .claude/agents）")
        return 1
    has_trae = (target / ".trae/sdlc/scripts/port_from_claude.py").exists()
    has_codex = (target / ".codex").is_dir()
    prefixes = CLAUDE_PREFIXES + (TRAE_PREFIXES if has_trae else ()) + (CODEX_PREFIXES if has_codex else ())
    files = [p for p in suite_files() if p.startswith(prefixes) and not p.startswith(GENERATED)]

    dirty = git(["status", "--porcelain", "--", *{p.split("/")[0] if "/" in p else p for p in files}], target)
    dirty = [l for l in dirty.splitlines() if any(l[3:].startswith(p) for p in prefixes)
             and not any(n in "/" + l[3:] for n in NEVER)]
    if dirty:
        print("  REFUSE: 套件路径有未提交改动，先提交或 stash：")
        for l in dirty[:10]:
            print("   ", l)
        return 1

    old = "未知"
    inst = target / ".claude/agents/INSTALL.md"
    if inst.exists():
        old = inst.read_text(encoding="utf-8").splitlines()[0].split("Suite")[-1].split("—")[0].strip()
    print(f"  版本 {old} -> {suite_version()}；平台：Claude" + ("+Trae" if has_trae else "") + ("+Codex" if has_codex else ""))

    stats = {"NEW": 0, "UPDATE": 0, "UPGRADE": 0, "SAME": 0, "KEEP": 0, "CONFLICT": 0}
    for rel in files:
        src = SUITE / rel
        dst = target / rel
        data = src.read_bytes()
        if dst.exists():
            cur = dst.read_bytes()
            if cur == data:
                stats["SAME"] += 1
                continue
            if rel.startswith(PROJECT_OWNED):
                stats["KEEP"] += 1
                continue
            if blob_id(cur) in history_blobs(rel):
                action = "UPDATE"
            elif rel.startswith(TOOLING) or force:
                action = "UPGRADE"
            else:
                stats["CONFLICT"] += 1
                print(f"  CONFLICT（本地改过，跳过）: {rel}")
                continue
        else:
            action = "NEW"
        stats[action] += 1
        print(f"  {action}: {rel}")
        if not check:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    print("  " + "  ".join(f"{k}={v}" for k, v in stats.items()))

    rc_all = 0
    if not check:
        if has_trae:
            for cmd in (["python3", ".trae/sdlc/scripts/port_from_claude.py"],
                        ["python3", ".trae/sdlc/scripts/suite_selftest.py"]):
                rc, tail = run(cmd, target)
                rc_all |= rc
                print(f"  {'OK ' if rc == 0 else 'ERR'} {' '.join(cmd[1:])}: {tail}")
        if has_codex:
            for cmd in (["python3", "scripts/codex_sdlc/migrate.py", "build"],
                        ["python3", "scripts/codex_sdlc/migrate.py", "install"],
                        ["python3", "scripts/codex_sdlc/verify_migration.py", "--no-write"]):
                rc, tail = run(cmd, target)
                rc_all |= rc
                print(f"  {'OK ' if rc == 0 else 'ERR'} {' '.join(cmd[1:])}: {tail[:160]}")
            gi = target / ".gitignore"
            lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
            if "output/" not in lines:
                with gi.open("a", encoding="utf-8") as f:
                    f.write(("\n" if lines and lines[-1] else "") + "output/\n")
                print("  .gitignore += output/（Codex 构建暂存目录）")
    return 1 if stats["CONFLICT"] and not force else rc_all


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+", type=Path)
    ap.add_argument("--check", action="store_true", help="只报告，不写入")
    ap.add_argument("--force", action="store_true", help="覆盖本地改过的套件文件")
    a = ap.parse_args()
    rc = 0
    for t in a.targets:
        t = t.resolve()
        if t == SUITE:
            print(f"\n== {t}\n  SKIP: 套件仓库自身")
            continue
        rc |= sync(t, a.check, a.force)
    sys.exit(rc)


if __name__ == "__main__":
    main()
