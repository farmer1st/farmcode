# Data Flow

How data flows through the Farmer Code system.

## Workflow Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant AgentHub
    participant Baron

    User->>Orchestrator: Create workflow
    Orchestrator->>Orchestrator: Generate feature ID
    Orchestrator->>AgentHub: Invoke Baron (specify)
    AgentHub->>Baron: POST /invoke
    Baron->>Baron: Process with Claude SDK
    Baron-->>AgentHub: Specification result
    AgentHub->>AgentHub: Log to audit
    AgentHub-->>Orchestrator: Response
    Orchestrator-->>User: Workflow created
```

## Request/Response Models

### Workflow Creation

```json
// Request
{
  "workflow_type": "specify",
  "feature_description": "Add user authentication"
}

// Response
{
  "id": "uuid",
  "feature_id": "009-user-authentication",
  "status": "in_progress"
}
```

### Agent Invocation

```json
// Request to Agent Hub
{
  "workflow_type": "specify",
  "context": {
    "feature_description": "Add user authentication"
  }
}

// Response
{
  "success": true,
  "result": "...",
  "confidence": 85,
  "metadata": {
    "duration_ms": 1500
  }
}
```

## Session Context Flow

For multi-turn conversations:

```mermaid
sequenceDiagram
    participant User
    participant AgentHub
    participant Agent

    User->>AgentHub: Ask question (new)
    AgentHub->>AgentHub: Create session
    AgentHub->>Agent: Query with context
    Agent-->>AgentHub: Answer
    AgentHub-->>User: Answer + session_id

    User->>AgentHub: Follow-up (session_id)
    AgentHub->>AgentHub: Load session history
    AgentHub->>Agent: Query with full context
    Agent-->>AgentHub: Answer
    AgentHub-->>User: Answer
```

## Escalation Flow

When confidence is below threshold:

```mermaid
sequenceDiagram
    participant User
    participant AgentHub
    participant Agent
    participant Human

    User->>AgentHub: Ask question
    AgentHub->>Agent: Query
    Agent-->>AgentHub: Low confidence (60%)
    AgentHub->>AgentHub: Create escalation
    AgentHub-->>User: Pending human review

    Human->>AgentHub: Provide answer
    AgentHub->>AgentHub: Resolve escalation
    AgentHub-->>User: Final answer
```
