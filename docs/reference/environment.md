# Environment Variables

All environment variables used by Farmer Code services.

## Required Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | All agents | Claude API key |

## Service Ports

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_HUB_PORT` | 8000 | Agent Hub service port |
| `ORCHESTRATOR_PORT` | 8001 | Orchestrator service port |
| `BARON_PORT` | 8010 | Baron agent port |
| `DUC_PORT` | 8011 | Duc agent port |
| `MARIE_PORT` | 8012 | Marie agent port |

## Service URLs

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_HUB_URL` | http://agent-hub:8000 | Agent Hub URL (for Orchestrator) |
| `ORCHESTRATOR_URL` | http://orchestrator:8001 | Orchestrator URL |
| `BARON_URL` | http://baron:8010 | Baron agent URL |
| `DUC_URL` | http://duc:8011 | Duc agent URL |
| `MARIE_URL` | http://marie:8012 | Marie agent URL |

## Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | sqlite:///./data/app.db | Database connection string |

## Agent Hub

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFIDENCE_THRESHOLD` | 80 | Min confidence for auto-accept |
| `AUDIT_LOG_PATH` | ./logs/audit.jsonl | Audit log file path |
| `SESSION_TIMEOUT_MINUTES` | 60 | Session expiry time |

## Agents

| Variable | Default | Description |
|----------|---------|-------------|
| `BARON_MODEL` | claude-sonnet-4-20250514 | Claude model for Baron |
| `DUC_MODEL` | claude-sonnet-4-20250514 | Claude model for Duc |
| `MARIE_MODEL` | claude-sonnet-4-20250514 | Claude model for Marie |

## GitHub Integration

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | - | GitHub personal access token |
| `GITHUB_APP_ID` | - | GitHub App ID (if using App) |
| `GITHUB_PRIVATE_KEY` | - | GitHub App private key |

## Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | INFO | Logging level |
| `LOG_FORMAT` | json | Log format (json/text) |

## Example .env File

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional - GitHub
GITHUB_TOKEN=ghp_...

# Optional - Override ports
# AGENT_HUB_PORT=8000
# ORCHESTRATOR_PORT=8001

# Optional - Override models
# BARON_MODEL=claude-opus-4-20250514
```
