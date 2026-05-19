# Hermes memory stack

A practical memory stack for Hermes Agent users who want their agent to stop forgetting after long chats, cron runs, tool calls, and context compression.

The design is simple:

```text
raw transcript -> durable notes -> searchable docs -> entity graph -> RRF router -> focus brief -> regression tests -> nightly maintenance
```

This repo packages the implementation pattern behind my own Hermes memory setup. The companion benchmark repo shows the final score: **100/100 A+**, **27/27 retrieval checks passed**, and **35 Hermes profiles verified**.

Benchmark pack: https://github.com/duclamvan/hermes-memory-benchmarks

## What you get

- A profile-safe Hermes memory configuration guide.
- Public-safe scripts for:
  - entity graph extraction from Markdown and LCM SQLite transcripts
  - hybrid RRF retrieval over QMD, native docs, LCM, and the graph
  - task-local focus briefs with citations
  - retrieval regression checks
  - global stack verification
  - nightly maintenance
- Config templates for `.env`, Hermes `config.yaml`, and cron prompts.
- Tests and CI so the public kit stays runnable.

## Who this is for

Use this if your agent:

- forgets decisions after compression
- remembers preferences but cannot recover the original chat
- has notes, logs, and transcripts but no routing layer
- answers from the current prompt when it should look things up
- has memory features but no regression tests

## Stack layers

1. **LCM raw transcript store** keeps exact conversation history.
2. **Native memory** keeps compact durable facts.
3. **QMD or Markdown wiki** keeps searchable project/user/system docs.
4. **Entity graph** links people, projects, topics, files, and sessions.
5. **Hybrid RRF router** ranks candidates across all sources.
6. **Focus brief builder** turns ranked recall into a short, cited task brief.
7. **Retrieval regression harness** catches memory drift.
8. **Nightly maintenance** updates indexes and runs health checks.

## Quick start

```bash
git clone https://github.com/duclamvan/hermes-memory-stack.git
cd hermes-memory-stack
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
cp configs/memory-stack.env.example .env
python scripts/memory_stack_verify.py --hermes-home ~/.hermes --workspace ~/my-hermes-workspace
```

If you already run QMD, LCM, and Hermes profiles, add your paths to `.env`, then try a query:

```bash
python scripts/memory_stack_router.py "what did we decide about memory?" --json
python scripts/memory_stack_focus_brief.py "continue the memory benchmark work" --out /tmp/focus-brief.md
```

## Minimal Hermes config

In `~/.hermes/config.yaml`:

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
context:
  engine: lcm
compression:
  enabled: true
```

In `~/.hermes/.env`:

```bash
LCM_LARGE_OUTPUT_EXTERNALIZATION_ENABLED=true
LCM_LARGE_OUTPUT_EXTERNALIZATION_THRESHOLD_CHARS=12000
LCM_LARGE_OUTPUT_TRANSCRIPT_GC_ENABLED=false
LCM_CONTEXT_THRESHOLD=0.70
```

## Nightly cron prompt

Use a Hermes cron job that starts with token refresh, then runs maintenance:

```text
Run preflight token refresh first. Then run the Hermes memory stack nightly maintenance from the repo. Summarize failures only, and include report paths.
```

Example shell command for a local cron/script lane:

```bash
python scripts/memory_stack_maintenance.py --apply --workspace ~/my-hermes-workspace --hermes-home ~/.hermes --out reports/nightly-memory-stack.json
```

## Public-safety note

Do not publish your raw LCM database, private notes, session IDs, Telegram topic names, secrets, or local profile paths. Publish redacted reports and aggregate benchmark numbers only.

## License

MIT
