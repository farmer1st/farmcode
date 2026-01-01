# Farm Code MCP Server - Tool Specification

## Overview

The Farm Code MCP server provides issue tracker-agnostic tools for AI agents to communicate and track task progress. It runs embedded in the orchestrator and injects agent identity automatically.

## Agent Identity Injection

Each agent's Claude CLI process is configured with environment variables:
```bash
export FARMCODE_AGENT_HANDLE=dede
export FARMCODE_AGENT_GITHUB_APP_ID=123456
export FARMCODE_AGENT_GITHUB_PRIVATE_KEY_PATH=/path/to/key.pem
```

The MCP server reads these environment variables and automatically:
1. Authenticates as the agent's GitHub App
2. Posts comments/updates using the agent's identity
3. Includes agent handle in all operations

## MCP Tools

### 1. task_get_context

**Purpose**: Retrieve current task context (issue details, specs, plans, comments)

**Parameters**:
```json
{
  "issue_number": 123
}
```

**Returns**:
```json
{
  "issue": {
    "number": 123,
    "title": "Add user authentication",
    "body": "...",
    "labels": ["status:specs-ready"],
    "phase": "PHASE_3_PLANS",
    "worktree_path": "../123-add-user-authentication"
  },
  "specs": [
    {
      "path": ".plans/123/specs/backend.md",
      "content": "..."
    }
  ],
  "plans": [
    {
      "path": ".plans/123/backend.md",
      "content": "..."
    }
  ],
  "comments": [
    {
      "author": "baron",
      "created_at": "2025-01-01T10:00:00Z",
      "body": "@dede Please write backend implementation plan."
    }
  ]
}
```

**Usage by Agent**:
```
Agent: "Let me get the context for this task"
[Uses task_get_context tool with issue_number]
Agent: "I can see the backend spec requires JWT authentication..."
```

---

### 2. task_post_comment

**Purpose**: Post a comment to the issue thread

**Parameters**:
```json
{
  "issue_number": 123,
  "comment": "📝 Status: Analyzing requirements and existing patterns.",
  "comment_type": "status"
}
```

**Comment Types**:
- `status` - Progress update (📝)
- `completion` - Task complete (✅)
- `question` - Ask question (❓)
- `answer` - Answer question (💬)
- `blocked` - Signal blockage (🚫)
- `clarification` - Request clarification (🔍)

**Returns**:
```json
{
  "comment_id": 456789,
  "url": "https://github.com/farmer1st/platform/issues/123#issuecomment-456789"
}
```

**MCP Server automatically**:
- Prepends emoji based on comment_type
- Authenticates as the agent's GitHub App
- Posts with agent's identity

**Usage by Agent**:
```
Agent: "I'll post a status update"
[Uses task_post_comment with status type]
GitHub: "📝 Status: Analyzing requirements..." (posted by @farmcode-dede)
```

---

### 3. task_signal_complete

**Purpose**: Signal task completion to orchestrator

**Parameters**:
```json
{
  "issue_number": 123,
  "artifact_path": ".plans/123/backend.md",
  "summary": "Backend plan complete. See `.plans/123/backend.md`."
}
```

**Returns**:
```json
{
  "comment_id": 456790,
  "next_agent": "baron"
}
```

**MCP Server automatically**:
- Posts completion comment with ✅ emoji
- Includes artifact path and summary
- Tags @baron for orchestrator attention
- Commits and pushes artifact if in worktree

**GitHub Comment Format**:
```
✅ Backend plan complete. See `.plans/123/backend.md`.

@baron Ready for next phase.
```

**Usage by Agent**:
```
Agent: "I've completed the backend plan"
[Uses task_signal_complete]
Orchestrator: [Detects completion via polling, advances state machine]
```

---

### 4. task_ask_question

**Purpose**: Ask a question to another agent or human

**Parameters**:
```json
{
  "issue_number": 123,
  "target": "duc",
  "question": "Should auth service use REST or GraphQL?"
}
```

**Returns**:
```json
{
  "comment_id": 456791,
  "waiting_for": "duc"
}
```

**MCP Server automatically**:
- Posts question with ❓ emoji
- Tags the target (@duc or @human)
- Orchestrator detects mention and dispatches target agent

**GitHub Comment Format**:
```
❓ @duc Question: Should auth service use REST or GraphQL?
```

**Usage by Agent**:
```
Agent: "I need clarification from the architect"
[Uses task_ask_question with target="duc"]
Orchestrator: [Sees @duc mention, dispatches duc to answer]
@duc: [Posts answer using task_post_answer]
```

---

### 5. task_post_answer

**Purpose**: Answer a question from another agent

**Parameters**:
```json
{
  "issue_number": 123,
  "target": "dede",
  "answer": "GraphQL. Aligns with our BFF pattern."
}
```

**Returns**:
```json
{
  "comment_id": 456792
}
```

**GitHub Comment Format**:
```
💬 @dede Answer: GraphQL. Aligns with our BFF pattern.
```

---

### 6. task_signal_blocked

**Purpose**: Signal that agent is blocked and needs help

**Parameters**:
```json
{
  "issue_number": 123,
  "reason": "Missing database schema for users table",
  "waiting_for": "duc"
}
```

**Returns**:
```json
{
  "comment_id": 456793,
  "label_added": "blocked:agent"
}
```

**MCP Server automatically**:
- Posts blocked message with 🚫 emoji
- Adds `blocked:agent` or `blocked:clarification` label
- Tags the person/agent being waited on

**GitHub Comment Format**:
```
🚫 Blocked: Missing database schema for users table.

Waiting on @duc.
```

---

### 7. task_update_status

**Purpose**: Post a simple status update (convenience wrapper for task_post_comment)

**Parameters**:
```json
{
  "issue_number": 123,
  "status": "Implementing auth service. 3/5 tests passing."
}
```

**Returns**:
```json
{
  "comment_id": 456794
}
```

**GitHub Comment Format**:
```
📝 Status: Implementing auth service. 3/5 tests passing.
```

---

### 8. task_get_comments

**Purpose**: Retrieve recent comments (for checking answers to questions)

**Parameters**:
```json
{
  "issue_number": 123,
  "since": "2025-01-01T10:00:00Z",
  "from_agent": "duc"
}
```

**Returns**:
```json
{
  "comments": [
    {
      "id": 456792,
      "author": "duc",
      "created_at": "2025-01-01T10:15:00Z",
      "body": "💬 @dede Answer: GraphQL. Aligns with our BFF pattern."
    }
  ]
}
```

---

## Adapter Interface

All tools route through an adapter layer for issue tracker agnosticism:

```python
class IssueTrackerAdapter(Protocol):
    """Protocol for issue tracker adapters (GitHub, Jira, Linear)"""

    def get_issue_context(self, issue_id: str) -> IssueContext: ...
    def post_comment(self, issue_id: str, body: str, author_identity: str) -> str: ...
    def add_label(self, issue_id: str, label: str) -> None: ...
    def remove_label(self, issue_id: str, label: str) -> None: ...
    def get_comments(self, issue_id: str, since: datetime | None) -> list[Comment]: ...
```

### Current Adapters

**GitHubAdapter**:
- Uses GitHub App authentication (per agent)
- Uses `gh` CLI and PyGitHub
- Maps generic concepts to GitHub Issues/Comments/Labels

**Future Adapters** (placeholder):
- JiraAdapter (issues → Jira tickets)
- LinearAdapter (issues → Linear issues)

---

## MCP Server Configuration

The orchestrator embeds the MCP server and configures it per agent:

```python
# In orchestrator agent dispatcher
mcp_server = FarmCodeMCPServer(
    adapter=GitHubAdapter(
        repo="farmer1st/farmer1st-platform",
        agent_handle=agent_handle,
        app_id=app_id,
        private_key_path=key_path,
    )
)

# Spawn Claude CLI with MCP
subprocess.run([
    "claude",
    "--mcp", "farmcode",  # MCP server name
    "-p", user_message,
    # ... other args
], env={
    "FARMCODE_AGENT_HANDLE": agent_handle,
    "FARMCODE_MCP_SERVER_URL": mcp_server.url,
    # ... GitHub App credentials
})
```

---

## Example Agent Flow

**@dede writing backend plan**:

1. Orchestrator dispatches @dede to write backend plan
2. Claude CLI starts with `--mcp farmcode`
3. Agent uses `task_get_context(123)` to read specs
4. Agent posts status: `task_update_status("Analyzing backend spec...")`
5. Agent asks question: `task_ask_question(target="duc", question="...")`
6. Orchestrator sees @duc mention, dispatches @duc
7. @duc answers: `task_post_answer(target="dede", answer="...")`
8. @dede continues, writes plan to `.plans/123/backend.md`
9. Agent completes: `task_signal_complete(artifact_path=".../backend.md")`
10. Orchestrator detects ✅, advances phase

All communication visible in GitHub issue thread with full audit trail!
