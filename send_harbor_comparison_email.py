"""Send AlphaDiana vs Harbor comparison email via uutils.

Usage:
    # With Gmail app password file (recommended):
    python send_harbor_comparison_email.py --smtp-pass-file ~/keys/gmail_app_password.txt

    # With password directly:
    python send_harbor_comparison_email.py --smtp-pass "your-app-password"

    # Dry-run (saves to local file, no SMTP needed):
    python send_harbor_comparison_email.py --dry-run

Setup (Gmail App Password):
    1. Enable 2-Step Verification: https://myaccount.google.com/security
    2. Create app password: https://myaccount.google.com/apppasswords
    3. Save: echo "your-app-password" > ~/keys/gmail_app_password.txt && chmod 600 ~/keys/gmail_app_password.txt
"""
import argparse
import logging
from pathlib import Path

import importlib.util, sys
_spec = importlib.util.spec_from_file_location(
    "uutils.emailing",
    "/usr/local/lib/python3.11/dist-packages/uutils/emailing.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["uutils.emailing"] = _mod
_spec.loader.exec_module(_mod)
send_email_smtp = _mod.send_email_smtp
DryRunNotifier = _mod.DryRunNotifier

logging.basicConfig(level=logging.INFO)

TO = "brando.science@gmail.com"
SUBJECT = "AlphaDiana vs Harbor Framework: Key Differences Summary"

BODY = """\
Hi Brando,

Here is a comparison of AlphaDiana vs Stanford's Harbor framework (https://www.harborframework.com/, fork: https://github.com/brando90/harbor).

=======================================================================
AlphaDiana vs Harbor: How Are They Different?
=======================================================================

TL;DR: AlphaDiana evaluates LLM *reasoning* agents on math benchmarks.
Harbor evaluates LLM *coding/terminal* agents on software engineering benchmarks.
They are both agent evaluation frameworks but target completely different domains.

-----------------------------------------------------------------------
1. PURPOSE & DOMAIN
-----------------------------------------------------------------------

AlphaDiana:
  - System-level evaluation of LLM-based REASONING agents
  - Focused on mathematical problem-solving (AIME competition math)
  - Measures how agent scaffolding (tools, sandboxes, orchestration)
    affects reasoning performance beyond the base model

Harbor:
  - Evaluation and optimization of LLM-based CODING/TERMINAL agents
  - Focused on software engineering tasks (SWE-Bench, Terminal-Bench)
  - Created by the Laude Institute (not Stanford -- the harborframework.com
    site is from the Terminal-Bench team)
  - Also supports RL training data generation (rollouts, SFT traces)

-----------------------------------------------------------------------
2. BENCHMARKS
-----------------------------------------------------------------------

AlphaDiana:
  - AIME 2024, 2025, 2026 (competition math)
  - Custom inline YAML problem definitions
  - Answer formats: integers, decimals, fractions, symbolic math

Harbor:
  - Terminal-Bench 2.0 (89 terminal tasks -- official harness)
  - SWE-Bench Verified (500 software engineering tasks)
  - SWE-Bench Pro (731 tasks)
  - LawBench (1,000 legal tasks)
  - ReplicationBench (90 research replication tasks)
  - MedAgentBench (300 medical tasks)
  - Public registry at registry.harborframework.com

-----------------------------------------------------------------------
3. AGENT ARCHITECTURE
-----------------------------------------------------------------------

AlphaDiana:
  - Two modes: Direct LLM baseline (single-turn) and OpenClaw agent
    (multi-turn with tool calling via ROCK sandboxes)
  - Measures the *delta* between bare model and agent-augmented performance
  - Deeply integrated with Alibaba's ROCK sandbox system

Harbor:
  - Supports many agents: Claude Code, OpenHands, Codex CLI, Gemini CLI,
    Copilot CLI, Mini-SWE-Agent, Terminus-2, and custom agents
  - Two interfaces: BaseAgent (external, sends bash commands) and
    BaseInstalledAgent (deployed inside the container)
  - Agent-agnostic by design -- plug in any agent

-----------------------------------------------------------------------
4. SANDBOXING
-----------------------------------------------------------------------

AlphaDiana:
  - ROCK SDK (Alibaba) -- specialized sandbox with resource profiling,
    session pooling, workspace snapshots
  - Also has a local execution mode for testing

Harbor:
  - Docker-based containers abstracted through BaseEnvironment
  - Cloud sandbox providers: Daytona, Modal, E2B, Runloop
  - Each task specifies its own Dockerfile/docker-compose
  - Designed for massive parallelism (1000s of concurrent environments)

-----------------------------------------------------------------------
5. SCORING & METRICS
-----------------------------------------------------------------------

AlphaDiana:
  - NumericScorer (tolerant float comparison)
  - ExactMatchScorer (string comparison with math normalization)
  - MathVerifyScorer (symbolic equivalence via SymPy)
  - LLMJudgeScorer (LLM-as-judge for nuanced evaluation)
  - Metrics: Accuracy, Pass@K, Avg@K, per-category breakdown

Harbor:
  - Task-specific test scripts (tests/test.sh) produce reward.txt or
    reward.json
  - Binary pass/fail or continuous reward scores
  - Designed for both evaluation AND reinforcement learning signals
  - Integrates with SkyRL and GEPA optimization frameworks

-----------------------------------------------------------------------
6. SCALE & CONCURRENCY
-----------------------------------------------------------------------

AlphaDiana:
  - ThreadPoolExecutor with configurable max_concurrent
  - Multi-sandbox pre-deployment for OpenClaw
  - Checkpoint/resume for interrupted evaluations

Harbor:
  - Extreme parallelism via cloud sandboxes (--n-concurrent 100+)
  - I/O-bounded design with API-based models
  - Job-based orchestration across datasets/agents/models

-----------------------------------------------------------------------
7. UNIQUE FEATURES
-----------------------------------------------------------------------

AlphaDiana only:
  - Multi-sample evaluation (Pass@K, Avg@K with K=32)
  - Full trajectory logging (every LLM call, tool invocation, execution)
  - Workspace snapshot capture for post-hoc analysis
  - Answer extraction pipeline (\boxed{}, regex, last-number fallback)
  - Web dashboard (React + FastAPI) for launching and monitoring runs
  - Focuses on the science of "does the agent scaffold help reasoning?"

Harbor only:
  - Public registry for sharing datasets and tasks
  - RL optimization pipeline (rollout generation for training)
  - GEPA and SkyRL integration for prompt/agent optimization
  - Multi-cloud sandbox support (Daytona, Modal, E2B, Runloop)
  - Task-level environment specification (each task has its own Dockerfile)
  - Designed for both evaluation AND training data generation

-----------------------------------------------------------------------
8. BOTTOM LINE
-----------------------------------------------------------------------

If you want to evaluate whether an agent framework helps an LLM reason
better at math: use AlphaDiana.

If you want to evaluate coding agents on software engineering tasks, or
generate RL training data from agent rollouts: use Harbor.

They are complementary frameworks, not competitors. A research group
could use both: Harbor to evaluate coding agents, AlphaDiana to evaluate
reasoning agents.

Note: Harbor is NOT affiliated with Stanford despite the user's initial
impression. It's from the Laude Institute / Terminal-Bench team. The
brando90/harbor fork is currently unmodified from upstream.

=======================================================================

Best,
AlphaDiana Analysis (auto-generated)

Sent from AlphaDiana repo via uutils.emailing
"""


def main():
    parser = argparse.ArgumentParser(description="Send Harbor comparison email")
    parser.add_argument("--smtp-user", default="brando.science@gmail.com")
    parser.add_argument("--smtp-pass", default="")
    parser.add_argument("--smtp-pass-file", default="~/keys/gmail_app_password.txt")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        notifier = DryRunNotifier("artifacts/email_outbox")
        notifier.notify(TO, SUBJECT, BODY)
        print(f"Dry-run email saved to artifacts/email_outbox/")
        return

    password = args.smtp_pass
    if not password:
        p = Path(args.smtp_pass_file).expanduser()
        if p.is_file():
            password = p.read_text().strip()

    if not password:
        print("ERROR: No SMTP password found.")
        print("Provide --smtp-pass or --smtp-pass-file, or set up ~/keys/gmail_app_password.txt")
        print("See: https://myaccount.google.com/apppasswords")
        print("\nFalling back to dry-run mode...")
        notifier = DryRunNotifier("artifacts/email_outbox")
        notifier.notify(TO, SUBJECT, BODY)
        print(f"Email saved to artifacts/email_outbox/")
        return

    send_email_smtp(
        to=TO,
        subject=SUBJECT,
        body=BODY,
        smtp_user=args.smtp_user,
        smtp_pass=password,
        from_addr=args.smtp_user,
    )
    print(f"Email sent to {TO}")


if __name__ == "__main__":
    main()
