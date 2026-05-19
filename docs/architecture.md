# Architecture

Hermes memory works best as a routing problem, not as one giant context window.

## Layers

### Raw transcript

LCM records the exact conversation. This is the source of truth when the user asks what happened earlier, what was said before compression, or where a decision came from.

### Durable memory

Native memory stores compact facts that should survive sessions: preferences, stable environment facts, project conventions, and lessons.

### Wiki/search layer

QMD or a Markdown wiki stores docs, reports, project notes, and long-lived knowledge. Use it for facts that are too big or too structured for native memory.

### Entity graph

The graph links names, projects, files, and topics across docs and transcripts. It should boost retrieval. It should not replace raw sources.

### Hybrid router

The router fuses ranked lists with Reciprocal Rank Fusion and source priors. Conversation-history queries should boost raw transcript results. Durable-fact queries should boost docs and native memory.

### Focus brief

A focus brief is a task-local retrieval packet. It gives the agent a short cited context block without polluting canonical memory or the compaction DAG.

### Regression checks

Memory fails quietly. The harness checks whether known queries still retrieve the expected source types and hints.

### Maintenance

Nightly maintenance updates indexes, runs health checks, writes reports, and flags contradictions or stale config.
