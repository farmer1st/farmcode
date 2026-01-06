# Services Architecture

Farmer Code uses a microservices architecture with three main services and multiple agent services.

## Service Topology

```mermaid
graph TB
    subgraph "Core Services"
        ORC[Orchestrator<br/>:8001]
        HUB[Agent Hub<br/>:8000]
    end

    subgraph "Agent Services"
        BARON[Baron PM<br/>:8010]
        DUC[Duc Architecture<br/>:8011]
        MARIE[Marie Testing<br/>:8012]
    end

    ORC --> HUB
    HUB --> BARON
    HUB --> DUC
    HUB --> MARIE
```

## Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| Agent Hub | 8000 | Central coordination, routing, sessions |
| Orchestrator | 8001 | Workflow state machine |
| Baron | 8010 | PM agent (specify, plan, tasks) |
| Duc | 8011 | Architecture expert |
| Marie | 8012 | Testing expert |

## Communication Patterns

### Orchestrator → Agent Hub

The Orchestrator delegates all agent communication through Agent Hub:

```
POST /invoke/{agent_name}
POST /ask/{topic}
```

### Agent Hub → Agents

Agent Hub routes requests to the appropriate agent service:

```
POST /invoke  (to agent service)
GET /health   (health checks)
```

## Service Responsibilities

### Orchestrator

- Workflow state machine (specify → plan → tasks → implement)
- Feature ID generation
- Phase transitions and gates

### Agent Hub

- Request routing to agents
- Session management (multi-turn conversations)
- Confidence validation and escalation
- Audit logging

### Agent Services

- Stateless request processing
- Claude SDK integration
- Domain-specific expertise
