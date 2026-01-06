# API Reference

Interactive API documentation for all Farmer Code services.

## Core Services

| Service | Port | Description |
|---------|------|-------------|
| [Orchestrator](orchestrator.md) | 8000 | Workflow state machine |
| [Agent Hub](agent-hub.md) | 8001 | Agent routing & sessions |

## Agent Services

| Agent | Port | Description |
|-------|------|-------------|
| [Baron](agents/baron.md) | 8002 | PM agent (specify, plan, tasks) |
| [Duc](agents/duc.md) | 8003 | Architecture expert |
| [Marie](agents/marie.md) | 8004 | Testing expert |

## Regenerating Docs

```bash
./scripts/generate-api-docs.sh
```
