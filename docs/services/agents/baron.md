# Baron (PM Agent)

Baron is the Product Management agent responsible for SpecKit workflows.

## Overview

| Property | Value |
|----------|-------|
| Port | 8010 |
| Role | Product Manager |
| Workflows | specify, plan, tasks, implement |

## Capabilities

Baron handles the core SpecKit workflows:

- **Specify**: Generate feature specifications from descriptions
- **Plan**: Create implementation plans from specifications
- **Tasks**: Generate task lists from plans
- **Implement**: Execute implementation tasks

## API

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "agent_name": "baron",
  "capabilities": {
    "workflow_types": ["specify", "plan", "tasks", "implement"]
  }
}
```

### Invoke

```
POST /invoke
```

Request:
```json
{
  "workflow_type": "specify",
  "context": {
    "feature_description": "Add user authentication with OAuth2"
  }
}
```

Response:
```json
{
  "success": true,
  "result": "# Feature Specification\n...",
  "confidence": 85,
  "metadata": {
    "duration_ms": 2500,
    "model": "claude-sonnet-4-20250514"
  }
}
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | Required |
| `BARON_PORT` | Service port | 8010 |
| `BARON_MODEL` | Claude model to use | claude-sonnet-4-20250514 |

## Source

- Location: `services/agents/baron/`
- README: [services/agents/baron/README.md](../../../services/agents/baron/README.md)
