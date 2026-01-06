# API Contracts

OpenAPI specifications for Farmer Code services.

## Contract Files

Full OpenAPI specs are in `specs/008-services-architecture/contracts/`:

- [orchestrator.yaml](../../specs/008-services-architecture/contracts/orchestrator.yaml)
- [agent-hub.yaml](../../specs/008-services-architecture/contracts/agent-hub.yaml)
- [agent-service.yaml](../../specs/008-services-architecture/contracts/agent-service.yaml)

## Orchestrator API

### Create Workflow

```
POST /workflows
```

Request:
```json
{
  "workflow_type": "specify",
  "feature_description": "Add user authentication"
}
```

Response:
```json
{
  "id": "uuid",
  "feature_id": "009-user-authentication",
  "workflow_type": "specify",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Workflow

```
GET /workflows/{id}
```

### Advance Workflow

```
POST /workflows/{id}/advance
```

## Agent Hub API

### Ask Expert

```
POST /ask/{topic}
```

Request:
```json
{
  "question": "What auth method should we use?",
  "context": "Building a web app",
  "feature_id": "009-auth"
}
```

Response:
```json
{
  "answer": "...",
  "confidence": 85,
  "status": "resolved",
  "session_id": "uuid"
}
```

### Invoke Agent

```
POST /invoke/{agent_name}
```

Request:
```json
{
  "workflow_type": "specify",
  "context": {
    "feature_description": "..."
  }
}
```

### Sessions

```
POST /sessions           # Create session
GET /sessions/{id}       # Get session
DELETE /sessions/{id}    # Close session
```

### Escalations

```
GET /escalations/{id}           # Get escalation
POST /escalations/{id}          # Respond to escalation
```

## Agent Service API

All agents implement this interface.

### Health

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
  "context": {}
}
```

Response:
```json
{
  "success": true,
  "result": "...",
  "confidence": 85,
  "metadata": {
    "duration_ms": 1500
  }
}
```
