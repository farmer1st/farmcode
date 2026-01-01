FARMER1ST SDLC WORKFLOW
Final Version — Program-Orchestrated, Monorepo, Git Worktrees, GitHub Comments

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                           FARMER1ST SDLC WORKFLOW                           │
│                                                                             │
│                            Program-Orchestrated                             │
│                          Monorepo + Git Worktrees                           │
│                      GitHub Comments for Communication                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

OVERVIEW
Key Principles

Program orchestrates, agents execute — Deterministic flow, no LLM routing decisions
GitHub is the source of truth — Issues, comments, PRs, labels track all state
Agents communicate via GitHub comments — Full transparency, audit trail
Git worktrees isolate work — Each feature gets its own worktree
Human approval gates — 4 checkpoints before merge
TDD implementation — Tests designed first, code loops until tests pass

Agents
HandleNameRoleGitHub Account@baronBaron HaussmannPM (orchestrator persona)farmer1st-baron@veuveVeuve ClicquotProduct Ownerfarmer1st-veuve@ducViollet-le-DucArchitectfarmer1st-duc@dedeAndré CitroënBackend Devfarmer1st-dede@daliSalvador DalíFrontend Devfarmer1st-dali@gusGustave EiffelDevOpsfarmer1st-gus@marieMarie MarvingtQAfarmer1st-marie@charlesCharles de GaulleSecurityfarmer1st-charles@louisLouis PasteurNetworkingfarmer1st-louis@maigretJules MaigretSREfarmer1st-maigret@jbJean-Baptiste ColbertFinOpsfarmer1st-jb
Each agent has their own GitHub App with gh CLI access.

COMMUNICATION PROTOCOL
GitHub Comments as Primary Channel
All agent communication happens via GitHub issue comments. Agents use gh CLI:
bash# Read issue
gh issue view $ISSUE_NUMBER

# Read comments
gh issue view $ISSUE_NUMBER --comments

# Post comment
gh issue comment $ISSUE_NUMBER --body "message"

# Update labels
gh issue edit $ISSUE_NUMBER --add-label "status:x" --remove-label "status:y"
Comment Format Convention
EmojiMeaningFormat✅Completion✅ {Task} complete. See \{path}`. @baron`❓Question❓ @{agent|human} Question: {question}💬Answer💬 @{agent} Answer: {answer}📝Status📝 Status: {what I'm doing}🚫Blocked🚫 Blocked: {reason}. Waiting on @{who}.🔍Clarification🔍 @{agent} Clarification needed: {details}
Orchestrator Notification Mechanism
The orchestrator polls for new comments:
pythonwhile issue_not_closed:
    new_comments = gh_get_comments(issue, since=last_check)
    
    for comment in new_comments:
        if is_completion_signal(comment):
            mark_agent_complete(comment.author)
        
        elif is_question(comment):
            target = extract_mention(comment)
            if target == "human":
                pause_for_human_input()
            elif target in AGENTS:
                dispatch(target, task="answer_question")
    
    sleep(poll_interval)  # 5-10 seconds
```

---

## LABELS

| Label | Meaning | Set By |
|-------|---------|--------|
| `status:new` | Issue created, worktree ready | Program |
| `status:specs-ready` | Architecture specs complete | Program |
| `status:plans-ready` | Implementation plans complete | Program |
| `status:tests-designed` | Test plan complete | Program |
| `status:implementing` | Agents writing code | Program |
| `status:in-review` | PR created, reviews in progress | Program |
| `status:approved` | All reviews passed | Program |
| `status:done` | Merged, deployed, cleaned up | Program |
| `blocked:clarification` | Waiting on human input | Program/Agent |
| `blocked:agent` | Waiting on another agent | Program/Agent |

---

## BRANCH & WORKTREE NAMING

### Branch Convention
```
{ISSUE}-{short-description}
```

**Rules:**
- Issue number first
- Lowercase only
- Alphanumeric + hyphens only (`a-z`, `0-9`, `-`)
- Max ~50 characters total
- Derived from issue title (slugified)

**Examples:**
```
123-add-user-authentication
456-survey-export-csv
789-deploy-redis-cluster
42-fix-login-timeout
```

### Directory Layout
```
~/Dev/farmer1st/github/
├── farmer1st-platform/              # Main repo (on main branch)
├── farmer1st-gitops/                # GitOps repo
├── farmer1st-ai-agents/             # Agent definitions
├── 123-add-user-authentication/     # Worktree for issue #123
│   └── .plans/123/
├── 456-survey-export-csv/           # Worktree for issue #456
│   └── .plans/456/
└── ...
```

---

## FOLDER STRUCTURE (per issue)
```
{ISSUE}-{short-description}/              # Worktree root
├── .plans/{ISSUE}/
│   ├── README.md                         # Issue summary, status checklist
│   ├── specs/                            # @duc's architecture specs
│   │   ├── backend.md                    # OpenAPI, DB DDL, events, services
│   │   ├── frontend.md                   # Component contracts, state, API calls
│   │   └── infra.md                      # K8s namespaces, Terraform, ArgoCD
│   ├── backend.md                        # @dede's implementation plan
│   ├── frontend.md                       # @dali's implementation plan
│   ├── infrastructure.md                 # @gus's implementation plan
│   ├── tests.md                          # @marie's test plan
│   └── reviews/
│       ├── backend-review.md             # @dede's review
│       ├── frontend-review.md            # @dali's review
│       ├── infrastructure-review.md      # @gus's review
│       └── tests-review.md               # @marie's review
├── src/                                  # Code changes
├── tests/                                # Test files
└── ...
```

---

## WORKFLOW PHASES
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   PHASE 1          PHASE 2        PHASE 3         PHASE 4                  │
│   Issue &          Architecture   Implementation  Test                      │
│   Worktree         & Specs        Plans           Design                    │
│   Creation                                                                  │
│      │                │               │               │                     │
│      ▼                ▼               ▼               ▼                     │
│   ┌─────┐         ┌─────┐         ┌─────┐         ┌─────┐                  │
│   │     │         │     │         │     │         │     │                  │
│   │  P  │────────▶│  S  │────────▶│  P  │────────▶│  T  │                  │
│   │     │         │     │         │     │         │     │                  │
│   └─────┘         └──┬──┘         └──┬──┘         └──┬──┘                  │
│                      │               │               │                      │
│                      ▼               ▼               ▼                      │
│                   ⛔ GATE 1      ⛔ GATE 2      ⛔ GATE 3                   │
│                   Human          Human          Human                       │
│                   Approval       Approval       Approval                    │
│                                                                             │
│                                                                             │
│   PHASE 5          PHASE 6        PHASE 7         PHASE 8                  │
│   Implementation   Create PR      Review          Merge &                   │
│   (TDD)                                           Cleanup                   │
│      │                │               │               │                     │
│      ▼                ▼               ▼               ▼                     │
│   ┌─────┐         ┌─────┐         ┌─────┐         ┌─────┐                  │
│   │     │         │     │         │     │         │     │                  │
│   │  I  │────────▶│ PR  │────────▶│  R  │────────▶│  M  │                  │
│   │     │         │     │         │     │         │     │                  │
│   └─────┘         └─────┘         └──┬──┘         └─────┘                  │
│                                      │                                      │
│                                      ▼                                      │
│                                   ⛔ GATE 4                                 │
│                                   Human                                     │
│                                   Approval                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: ISSUE & WORKTREE CREATION

**Trigger:** Human provides feature description to program

**Executor:** Program (attributed to @baron)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: ISSUE & WORKTREE CREATION                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT: Feature description from human                                     │
│                                                                             │
│  PROGRAM EXECUTES (as @baron):                                             │
│                                                                             │
│  1. Create GitHub Issue                                                    │
│     $ gh issue create \                                                    │
│         --title "Add user authentication" \                                │
│         --body "..." \                                                     │
│         --label "status:new"                                               │
│     → Returns: #123                                                        │
│                                                                             │
│  2. Derive branch name                                                     │
│     title = "Add user authentication"                                      │
│     slug = slugify(title) → "add-user-authentication"                      │
│     branch = "123-add-user-authentication"                                 │
│                                                                             │
│  3. Create branch from main                                                │
│     $ git branch 123-add-user-authentication main                          │
│                                                                             │
│  4. Create worktree (sibling directory)                                    │
│     $ git worktree add \                                                   │
│         ../123-add-user-authentication \                                   │
│         123-add-user-authentication                                        │
│                                                                             │
│  5. Create folder structure                                                │
│     $ cd ../123-add-user-authentication                                    │
│     $ mkdir -p .plans/123/specs .plans/123/reviews                         │
│                                                                             │
│  6. Create README.md                                                       │
│     .plans/123/README.md (see template below)                              │
│                                                                             │
│  7. Commit and push                                                        │
│     $ git add .plans/                                                      │
│     $ git commit -m "chore(123): initialize plans folder"                  │
│     $ git push -u origin 123-add-user-authentication                       │
│                                                                             │
│  8. Comment on issue                                                       │
│     $ gh issue comment 123 --body "..."                                    │
│                                                                             │
│     "Branch \`123-add-user-authentication\` created.                       │
│      Worktree ready at \`../123-add-user-authentication\`.                │
│                                                                             │
│      @duc Please design the architecture specs."                          │
│                                                                             │
│  OUTPUT:                                                                   │
│    - Issue #123 created                                                    │
│    - Branch: 123-add-user-authentication                                   │
│    - Worktree: ../123-add-user-authentication                              │
│    - Folder: .plans/123/ initialized                                       │
│    - Label: status:new                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
README.md Template
markdown# 123: Add user authentication

## GitHub
https://github.com/farmer1st/farmer1st-platform/issues/123

## Branch
`123-add-user-authentication`

## Status
- [ ] Architecture/specs (@duc)
- [ ] Backend plan (@dede)
- [ ] Frontend plan (@dali)
- [ ] Infrastructure plan (@gus)
- [ ] Test plan (@marie)
- [ ] Human approval: specs
- [ ] Human approval: plans
- [ ] Human approval: tests
- [ ] Implementation complete
- [ ] Reviews complete
- [ ] Human approval: merge
- [ ] Merged

## Summary
{Description from issue}

## Acceptance Criteria
{From issue}
```

---

## PHASE 2: ARCHITECTURE & SPECS

**Trigger:** Phase 1 complete

**Executor:** @duc (Claude CLI agent)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: ARCHITECTURE & SPECS                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ORCHESTRATOR DISPATCHES @duc:                                             │
│    - ISSUE_NUMBER=123                                                      │
│    - WORKTREE_PATH=../123-add-user-authentication                          │
│    - PHASE=specs                                                           │
│                                                                             │
│  @duc EXECUTES:                                                            │
│                                                                             │
│  1. Navigate to worktree                                                   │
│     $ cd $WORKTREE_PATH                                                    │
│                                                                             │
│  2. Read issue and comments                                                │
│     $ gh issue view $ISSUE_NUMBER                                          │
│     $ gh issue view $ISSUE_NUMBER --comments                               │
│                                                                             │
│  3. Post status update                                                     │
│     $ gh issue comment $ISSUE_NUMBER \                                     │
│         --body "📝 Status: Analyzing requirements and existing patterns." │
│                                                                             │
│  4. If clarification needed from human                                     │
│     $ gh issue comment $ISSUE_NUMBER \                                     │
│         --body "❓ @human Question: {question}"                            │
│     (Orchestrator pauses, waits for human response, then re-dispatches)   │
│                                                                             │
│  5. Create specs (based on what's needed)                                  │
│                                                                             │
│     .plans/123/specs/backend.md                                            │
│       - OpenAPI 3.x specification                                          │
│       - Database DDL (PostgreSQL)                                          │
│       - AsyncAPI for events                                                │
│       - Service names & namespaces                                         │
│                                                                             │
│     .plans/123/specs/frontend.md                                           │
│       - Component contracts                                                │
│       - State shape                                                        │
│       - API calls                                                          │
│       - UI/UX requirements                                                 │
│                                                                             │
│     .plans/123/specs/infra.md                                              │
│       - Kubernetes namespaces                                              │
│       - Terraform resources                                                │
│       - ArgoCD applications                                                │
│       - Secrets requirements                                               │
│                                                                             │
│  6. Commit and push                                                        │
│     $ git add .plans/123/specs/                                            │
│     $ git commit -m "docs(123): add architecture specs"                    │
│     $ git push                                                             │
│                                                                             │
│  7. Signal completion                                                      │
│     $ gh issue comment $ISSUE_NUMBER \                                     │
│         --body "✅ Specs complete. See \`.plans/123/specs/\`.             │
│                                                                             │
│         Created:                                                           │
│         - \`specs/backend.md\` - Auth service OpenAPI, JWT schema         │
│         - \`specs/frontend.md\` - Login component contracts               │
│         - \`specs/infra.md\` - Redis session store, K8s secrets          │
│                                                                             │
│         @baron Ready for human approval."                                  │
│                                                                             │
│  ORCHESTRATOR (as @baron):                                                 │
│                                                                             │
│  8. Update label                                                           │
│     $ gh issue edit 123 \                                                  │
│         --remove-label "status:new" \                                      │
│         --add-label "status:specs-ready"                                   │
│                                                                             │
│  9. Post approval request                                                  │
│     $ gh issue comment 123 --body \                                        │
│         "📋 **Specs ready for review.**                                   │
│                                                                             │
│          Please review:                                                    │
│          - \`.plans/123/specs/backend.md\`                                │
│          - \`.plans/123/specs/frontend.md\`                               │
│          - \`.plans/123/specs/infra.md\`                                  │
│                                                                             │
│          Reply **approved** to proceed."                                  │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════  │
│  ⛔ GATE 1: HUMAN APPROVAL                                                 │
│                                                                             │
│     Human reviews .plans/123/specs/*                                       │
│     Human comments: "approved" or requests changes                        │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 3: IMPLEMENTATION PLANS

**Trigger:** Human approves specs (Gate 1)

**Executors:** @dede, @dali, @gus (in parallel, based on which specs exist)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: IMPLEMENTATION PLANS                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ORCHESTRATOR determines which agents needed:                              │
│                                                                             │
│    specs/backend.md exists?  → dispatch @dede                              │
│    specs/frontend.md exists? → dispatch @dali                              │
│    specs/infra.md exists?    → dispatch @gus                               │
│                                                                             │
│  ORCHESTRATOR (as @baron) posts:                                           │
│    $ gh issue comment 123 --body \                                         │
│        "Specs approved. Moving to implementation planning.                 │
│                                                                             │
│         @dede Please write backend implementation plan.                    │
│         @dali Please write frontend implementation plan.                   │
│         @gus Please write infrastructure plan."                            │
│                                                                             │
│  ORCHESTRATOR dispatches agents IN PARALLEL:                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐         │   │
│  │  │    @dede      │   │    @dali      │   │    @gus       │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  │ Reads:        │   │ Reads:        │   │ Reads:        │         │   │
│  │  │ • specs/      │   │ • specs/      │   │ • specs/      │         │   │
│  │  │   backend.md  │   │   frontend.md │   │   infra.md    │         │   │
│  │  │ • existing    │   │ • existing    │   │ • gitops      │         │   │
│  │  │   backend     │   │   frontend    │   │   repo        │         │   │
│  │  │   code        │   │   code        │   │               │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  │ Writes:       │   │ Writes:       │   │ Writes:       │         │   │
│  │  │ .plans/123/   │   │ .plans/123/   │   │ .plans/123/   │         │   │
│  │  │  backend.md   │   │  frontend.md  │   │  infra.md     │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  └───────┬───────┘   └───────┬───────┘   └───────┬───────┘         │   │
│  │          │                   │                   │                 │   │
│  │          └───────────────────┴───────────────────┘                 │   │
│  │                              │                                     │   │
│  │                              ▼                                     │   │
│  │          Agents may ask each other questions via comments          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  AGENT INTERACTION EXAMPLE:                                                │
│                                                                             │
│    @dede posts:                                                            │
│      "❓ @duc Question: Should auth service use REST or GraphQL?"         │
│                                                                             │
│    Orchestrator sees @duc mentioned, dispatches @duc                       │
│                                                                             │
│    @duc posts:                                                             │
│      "💬 @dede Answer: GraphQL. Aligns with our BFF pattern."             │
│                                                                             │
│    @dede continues working...                                              │
│                                                                             │
│  EACH AGENT ON COMPLETION:                                                 │
│                                                                             │
│    $ git add .plans/123/{their-plan}.md                                    │
│    $ git commit -m "docs(123): add {domain} implementation plan"           │
│    $ git push                                                              │
│    $ gh issue comment $ISSUE_NUMBER \                                      │
│        --body "✅ {Domain} plan complete. See \`.plans/123/{file}\`.      │
│                @baron ready."                                              │
│                                                                             │
│  ORCHESTRATOR waits for all dispatched agents to complete                  │
│                                                                             │
│  ORCHESTRATOR (as @baron):                                                 │
│    $ gh issue edit 123 \                                                   │
│        --remove-label "status:specs-ready" \                               │
│        --add-label "status:plans-ready"                                    │
│                                                                             │
│    $ gh issue comment 123 --body \                                         │
│        "📋 **Implementation plans ready for review.**                     │
│                                                                             │
│         Please review:                                                     │
│         - \`.plans/123/backend.md\`                                       │
│         - \`.plans/123/frontend.md\`                                      │
│         - \`.plans/123/infrastructure.md\`                                │
│                                                                             │
│         Reply **approved** to proceed."                                   │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════  │
│  ⛔ GATE 2: HUMAN APPROVAL                                                 │
│                                                                             │
│     Human reviews .plans/123/*.md (excluding specs/ and reviews/)         │
│     Human comments: "approved" or requests changes                        │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 4: TEST DESIGN

**Trigger:** Human approves implementation plans (Gate 2)

**Executor:** @marie
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: TEST DESIGN                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ORCHESTRATOR (as @baron) posts:                                           │
│    $ gh issue comment 123 --body \                                         │
│        "Implementation plans approved. Moving to test design.              │
│                                                                             │
│         @marie Please write the test plan."                                │
│                                                                             │
│  ORCHESTRATOR dispatches @marie:                                           │
│    - ISSUE_NUMBER=123                                                      │
│    - WORKTREE_PATH=../123-add-user-authentication                          │
│    - PHASE=test_design                                                     │
│                                                                             │
│  @marie EXECUTES:                                                          │
│                                                                             │
│  1. Read all specs and plans                                               │
│     - .plans/123/specs/backend.md                                          │
│     - .plans/123/specs/frontend.md                                         │
│     - .plans/123/specs/infra.md                                            │
│     - .plans/123/backend.md                                                │
│     - .plans/123/frontend.md                                               │
│     - .plans/123/infrastructure.md                                         │
│                                                                             │
│  2. Read existing test patterns in monorepo                                │
│                                                                             │
│  3. Create test plan: .plans/123/tests.md                                  │
│                                                                             │
│     Contents:                                                              │
│     - Unit tests (backend + frontend)                                      │
│     - Integration tests (API endpoints, DB)                                │
│     - E2E tests (critical user flows)                                      │
│     - Edge cases                                                           │
│     - Coverage targets (80% minimum)                                       │
│     - Performance tests (if applicable)                                    │
│                                                                             │
│  4. Commit and push                                                        │
│     $ git add .plans/123/tests.md                                          │
│     $ git commit -m "docs(123): add test plan"                             │
│     $ git push                                                             │
│                                                                             │
│  5. Signal completion                                                      │
│     $ gh issue comment $ISSUE_NUMBER \                                     │
│         --body "✅ Test plan complete. See \`.plans/123/tests.md\`.       │
│                                                                             │
│                 Coverage:                                                  │
│                 - 12 unit tests (backend)                                  │
│                 - 8 unit tests (frontend)                                  │
│                 - 5 integration tests                                      │
│                 - 3 E2E flows                                              │
│                 - Target: 80% coverage                                     │
│                                                                             │
│                 @baron Ready for human approval."                          │
│                                                                             │
│  ORCHESTRATOR (as @baron):                                                 │
│    $ gh issue edit 123 \                                                   │
│        --remove-label "status:plans-ready" \                               │
│        --add-label "status:tests-designed"                                 │
│                                                                             │
│    $ gh issue comment 123 --body \                                         │
│        "📋 **Test plan ready for review.**                                │
│                                                                             │
│         Please review:                                                     │
│         - \`.plans/123/tests.md\`                                         │
│                                                                             │
│         Reply **approved** to proceed to implementation."                 │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════  │
│  ⛔ GATE 3: HUMAN APPROVAL                                                 │
│                                                                             │
│     Human reviews .plans/123/tests.md                                      │
│     Human comments: "approved" or requests changes                        │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 5: IMPLEMENTATION (TDD, PARALLEL)

**Trigger:** Human approves test plan (Gate 3)

**Executors:** @dede, @dali, @gus (in parallel, same agents who wrote plans)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 5: IMPLEMENTATION (TDD, PARALLEL)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ORCHESTRATOR (as @baron) posts:                                           │
│    $ gh issue comment 123 --body \                                         │
│        "Test plan approved. Starting implementation.                       │
│                                                                             │
│         @dede @dali @gus Begin implementing per your plans.               │
│         Follow TDD: write tests first, then code until tests pass."       │
│                                                                             │
│  ORCHESTRATOR dispatches agents IN PARALLEL:                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  All agents work in SAME worktree: ../123-add-user-authentication  │   │
│  │                                                                     │   │
│  │  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐         │   │
│  │  │ @dede + Claude│   │ @dali + Claude│   │ @gus + Claude │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  │ Reads:        │   │ Reads:        │   │ Reads:        │         │   │
│  │  │ • specs/      │   │ • specs/      │   │ • specs/      │         │   │
│  │  │   backend.md  │   │   frontend.md │   │   infra.md    │         │   │
│  │  │ • backend.md  │   │ • frontend.md │   │ • infra.md    │         │   │
│  │  │ • tests.md    │   │ • tests.md    │   │ • tests.md    │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  │ ┌───────────┐ │   │ ┌───────────┐ │   │ ┌───────────┐ │         │   │
│  │  │ │ TDD LOOP  │ │   │ │ TDD LOOP  │ │   │ │ TDD LOOP  │ │         │   │
│  │  │ │           │ │   │ │           │ │   │ │           │ │         │   │
│  │  │ │ 1. Write  │ │   │ │ 1. Write  │ │   │ │ 1. Write  │ │         │   │
│  │  │ │    test   │ │   │ │    test   │ │   │ │    test   │ │         │   │
│  │  │ │ 2. Run    │ │   │ │ 2. Run    │ │   │ │ 2. Run    │ │         │   │
│  │  │ │    (FAIL) │ │   │ │    (FAIL) │ │   │ │    (FAIL) │ │         │   │
│  │  │ │ 3. Write  │ │   │ │ 3. Write  │ │   │ │ 3. Write  │ │         │   │
│  │  │ │    code   │ │   │ │    code   │ │   │ │    code   │ │         │   │
│  │  │ │ 4. Run    │ │   │ │ 4. Run    │ │   │ │ 4. Run    │ │         │   │
│  │  │ │    test   │ │   │ │    test   │ │   │ │    test   │ │         │   │
│  │  │ │   ├─FAIL──┼─┼───┼─┼──►back   │ │   │ │   ├─FAIL─► │ │         │   │
│  │  │ │   │       │ │   │ │   to 3   │ │   │ │   │back   │ │         │   │
│  │  │ │   └─PASS──┼─┼───┼─┼──►next   │ │   │ │   └─PASS─► │ │         │   │
│  │  │ │     test  │ │   │ │   test   │ │   │ │     next   │ │         │   │
│  │  │ └───────────┘ │   │ └───────────┘ │   │ └───────────┘ │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  │ Stop hook     │   │ Stop hook     │   │ Stop hook     │         │   │
│  │  │ prevents exit │   │ prevents exit │   │ prevents exit │         │   │
│  │  │ until tests   │   │ until tests   │   │ until tests   │         │   │
│  │  │ pass          │   │ pass          │   │ pass          │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  └───────┬───────┘   └───────┬───────┘   └───────┬───────┘         │   │
│  │          │                   │                   │                 │   │
│  │          └───────────────────┴───────────────────┘                 │   │
│  │                              │                                     │   │
│  │                    All tests passing                               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  EACH AGENT commits as they go:                                            │
│    $ git add .                                                             │
│    $ git commit -m "feat(123): implement {component}"                      │
│    $ git push                                                              │
│                                                                             │
│  EACH AGENT posts status updates:                                          │
│    $ gh issue comment $ISSUE_NUMBER \                                      │
│        --body "📝 Status: Implementing auth service. 3/5 tests passing."  │
│                                                                             │
│  EACH AGENT ON COMPLETION:                                                 │
│    $ gh issue comment $ISSUE_NUMBER \                                      │
│        --body "✅ {Domain} implementation complete. All tests passing.    │
│                @baron ready."                                              │
│                                                                             │
│  ORCHESTRATOR waits for all agents to complete                             │
│                                                                             │
│  ORCHESTRATOR (as @baron):                                                 │
│    $ gh issue edit 123 \                                                   │
│        --remove-label "status:tests-designed" \                            │
│        --add-label "status:implementing"                                   │
│                                                                             │
│    $ gh issue comment 123 --body \                                         │
│        "Implementation complete. All tests passing. Creating PR."         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 6: CREATE PR

**Trigger:** All implementation agents complete

**Executor:** Program (attributed to @baron)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 6: CREATE PR                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PROGRAM EXECUTES (as @baron):                                             │
│                                                                             │
│  1. Create Pull Request                                                    │
│     $ gh pr create \                                                       │
│         --title "feat(123): Add user authentication" \                     │
│         --body "..." \                                                     │
│         --base main \                                                      │
│         --head 123-add-user-authentication \                               │
│         --label "status:in-review"                                         │
│                                                                             │
│     PR body includes:                                                      │
│       - Closes #123                                                        │
│       - Summary of changes                                                 │
│       - Link to .plans/123/                                                │
│       - Test coverage report                                               │
│                                                                             │
│  2. Update issue label                                                     │
│     $ gh issue edit 123 \                                                  │
│         --remove-label "status:implementing" \                             │
│         --add-label "status:in-review"                                     │
│                                                                             │
│  3. Comment on issue                                                       │
│     $ gh issue comment 123 --body \                                        │
│         "PR #456 created. Assigning reviewers.                            │
│                                                                             │
│          @dede @dali @gus @marie Please review against your plans."       │
│                                                                             │
│  OUTPUT:                                                                   │
│    - PR #456 created                                                       │
│    - Label: status:in-review                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 7: REVIEW

**Trigger:** PR created

**Executors:** Same agents who wrote plans (@dede, @dali, @gus, @marie)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 7: REVIEW                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ORCHESTRATOR dispatches reviewers:                                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐         │   │
│  │  │    @dede      │   │    @dali      │   │    @gus       │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  │ Reviews       │   │ Reviews       │   │ Reviews       │         │   │
│  │  │ against:      │   │ against:      │   │ against:      │         │   │
│  │  │ • specs/      │   │ • specs/      │   │ • specs/      │         │   │
│  │  │   backend.md  │   │   frontend.md │   │   infra.md    │         │   │
│  │  │ • backend.md  │   │ • frontend.md │   │ • infra.md    │         │   │
│  │  │ • python-     │   │ • react-      │   │               │         │   │
│  │  │   standards   │   │   standards   │   │               │         │   │
│  │  │               │   │               │   │               │         │   │
│  │  │ Writes:       │   │ Writes:       │   │ Writes:       │         │   │
│  │  │ reviews/      │   │ reviews/      │   │ reviews/      │         │   │
│  │  │ backend-      │   │ frontend-     │   │ infra-        │         │   │
│  │  │ review.md     │   │ review.md     │   │ review.md     │         │   │
│  │  └───────────────┘   └───────────────┘   └───────────────┘         │   │
│  │                                                                     │   │
│  │  ┌───────────────┐                                                 │   │
│  │  │    @marie     │                                                 │   │
│  │  │               │                                                 │   │
│  │  │ Reviews       │                                                 │   │
│  │  │ against:      │                                                 │   │
│  │  │ • tests.md    │                                                 │   │
│  │  │ • coverage    │                                                 │   │
│  │  │   targets     │                                                 │   │
│  │  │               │                                                 │   │
│  │  │ Writes:       │                                                 │   │
│  │  │ reviews/      │                                                 │   │
│  │  │ tests-        │                                                 │   │
│  │  │ review.md     │                                                 │   │
│  │  └───────────────┘                                                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  REVIEW VERDICTS:                                                          │
│    ✅ Approved                                                             │
│    ❌ Changes Requested                                                    │
│                                                                             │
│  EACH REVIEWER:                                                            │
│    $ git add .plans/123/reviews/{domain}-review.md                         │
│    $ git commit -m "docs(123): add {domain} review"                        │
│    $ git push                                                              │
│    $ gh issue comment $ISSUE_NUMBER \                                      │
│        --body "✅ Backend review complete. Approved.                      │
│                See \`.plans/123/reviews/backend-review.md\`."             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  REVIEW LOOP (if changes requested)                                 │   │
│  │                                                                     │   │
│  │  1. Reviewer posts:                                                 │   │
│  │     "❌ Changes requested. See \`reviews/backend-review.md\`."     │   │
│  │                                                                     │   │
│  │  2. Orchestrator collects all change requests                      │   │
│  │                                                                     │   │
│  │  3. Orchestrator dispatches relevant agents to fix:                │   │
│  │     "@dede Please address review feedback."                        │   │
│  │                                                                     │   │
│  │  4. Agent fixes, commits, pushes                                   │   │
│  │                                                                     │   │
│  │  5. Agent posts:                                                   │   │
│  │     "✅ Review feedback addressed. @dede please re-review."       │   │
│  │                                                                     │   │
│  │  6. Orchestrator re-dispatches reviewer                           │   │
│  │                                                                     │   │
│  │  7. Repeat until all reviewers approve                            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  WHEN ALL REVIEWERS APPROVE:                                               │
│                                                                             │
│  ORCHESTRATOR (as @baron):                                                 │
│    $ gh issue edit 123 \                                                   │
│        --remove-label "status:in-review" \                                 │
│        --add-label "status:approved"                                       │
│                                                                             │
│    $ gh issue comment 123 --body \                                         │
│        "All reviews passed. ✅                                            │
│                                                                             │
│         **Awaiting human approval to merge.**                             │
│                                                                             │
│         PR: #456                                                           │
│         Reviews:                                                           │
│         - @dede ✅                                                        │
│         - @dali ✅                                                        │
│         - @gus ✅                                                         │
│         - @marie ✅                                                       │
│                                                                             │
│         Reply **merge** to proceed."                                      │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════  │
│  ⛔ GATE 4: HUMAN APPROVAL                                                 │
│                                                                             │
│     Human reviews PR, review files                                        │
│     Human comments: "merge" or requests changes                           │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 8: MERGE & CLEANUP

**Trigger:** Human approves merge (Gate 4)

**Executor:** Program (attributed to @baron)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 8: MERGE & CLEANUP                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PROGRAM EXECUTES (as @baron):                                             │
│                                                                             │
│  1. Merge PR                                                               │
│     $ gh pr merge 456 \                                                    │
│         --squash \                                                         │
│         --subject "feat(123): Add user authentication (#456)"             │
│                                                                             │
│  2. ArgoCD auto-deploys to dev                                             │
│     (Detects change in main, syncs affected applications)                 │
│                                                                             │
│  3. Update issue label                                                     │
│     $ gh issue edit 123 \                                                  │
│         --remove-label "status:approved" \                                 │
│         --add-label "status:done"                                          │
│                                                                             │
│  4. Close issue                                                            │
│     $ gh issue close 123 \                                                 │
│         --comment "Merged and deployed to dev. 🎉                         │
│                                                                             │
│                    PR: #456                                                │
│                    Branch: \`123-add-user-authentication\`                │
│                    Deployed: dev environment                               │
│                                                                             │
│                    Très bien! Another successful delivery."               │
│                                                                             │
│  5. Remove worktree                                                        │
│     $ git worktree remove ../123-add-user-authentication                   │
│                                                                             │
│  6. Delete local branch (remote deleted by GitHub on merge)                │
│     $ git branch -d 123-add-user-authentication                            │
│                                                                             │
│  OUTPUT:                                                                   │
│    - PR merged to main                                                     │
│    - Issue closed                                                          │
│    - Worktree removed                                                      │
│    - Branch deleted                                                        │
│    - Deployed to dev                                                       │
│    - Label: status:done                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## SUMMARY TABLES

### Human Approval Gates

| Gate | Phase | What's Reviewed | Approval Command |
|------|-------|-----------------|------------------|
| **Gate 1** | After SPECS | `.plans/{issue}/specs/*.md` | Comment: "approved" |
| **Gate 2** | After PLANS | `.plans/{issue}/*.md` (plans) | Comment: "approved" |
| **Gate 3** | After TEST DESIGN | `.plans/{issue}/tests.md` | Comment: "approved" |
| **Gate 4** | After REVIEW | PR + all review files | Comment: "merge" |

### Who Does What

| Action | Executor | Attribution | Tool |
|--------|----------|-------------|------|
| Create GitHub issue | Program | @baron | `gh issue create` |
| Create branch | Program | — | `git branch` |
| Create worktree | Program | — | `git worktree add` |
| Create .plans folder | Program | — | filesystem |
| Update labels | Program | @baron | `gh issue edit` |
| Post orchestration comments | Program | @baron | `gh issue comment` |
| Write specs | @duc | @duc | Claude CLI + `gh` |
| Write implementation plans | @dede/@dali/@gus | themselves | Claude CLI + `gh` |
| Write test plan | @marie | @marie | Claude CLI + `gh` |
| Write code & tests | Agents + Claude | themselves | Claude CLI + `gh` |
| Write reviews | @dede/@dali/@gus/@marie | themselves | Claude CLI + `gh` |
| Create PR | Program | @baron | `gh pr create` |
| Merge PR | Program | @baron | `gh pr merge` |
| Close issue | Program | @baron | `gh issue close` |
| Remove worktree | Program | — | `git worktree remove` |
| Answer agent questions | Relevant agent | themselves | Claude CLI + `gh` |
| Route questions | @baron | @baron | Claude CLI (for complex routing) |

### Labels

| Label | Meaning | Set When |
|-------|---------|----------|
| `status:new` | Issue created, worktree ready | Phase 1 complete |
| `status:specs-ready` | Architecture specs complete | Phase 2 complete |
| `status:plans-ready` | Implementation plans complete | Phase 3 complete |
| `status:tests-designed` | Test plan complete | Phase 4 complete |
| `status:implementing` | Agents writing code | Phase 5 in progress |
| `status:in-review` | PR created, reviews in progress | Phase 6 complete |
| `status:approved` | All reviews passed | Phase 7 complete |
| `status:done` | Merged, deployed, cleaned up | Phase 8 complete |
| `blocked:clarification` | Waiting on human input | Anytime |
| `blocked:agent` | Waiting on another agent | Anytime |

### Comment Protocol

| Emoji | Type | Format | Used By |
|-------|------|--------|---------|
| ✅ | Completion | `✅ {Task} complete. See \`{path}\`. @baron` | All agents |
| ❓ | Question | `❓ @{agent\|human} Question: {question}` | All agents |
| 💬 | Answer | `💬 @{agent} Answer: {answer}` | All agents |
| 📝 | Status | `📝 Status: {what I'm doing}` | All agents |
| 🚫 | Blocked | `🚫 Blocked: {reason}. Waiting on @{who}.` | All agents |
| 📋 | Approval Request | `📋 **Ready for review.** ...` | @baron |
| 🎉 | Celebration | Merge complete message | @baron |

---

## ORCHESTRATOR STATE MACHINE
```
                              ┌─────────────┐
                              │    IDLE     │
                              └──────┬──────┘
                                     │ Human provides feature description
                                     ▼
                              ┌─────────────┐
                              │   PHASE_1   │ Create issue, branch, worktree
                              │   SETUP     │
                              └──────┬──────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │   PHASE_2   │ Dispatch @duc
                              │    SPECS    │◄─────────────────────┐
                              └──────┬──────┘                      │
                                     │                             │
                                     ▼                             │
                              ┌─────────────┐                      │
                              │   GATE_1    │ Wait for human       │
                              │   SPECS     │──── rejected ────────┘
                              └──────┬──────┘
                                     │ approved
                                     ▼
                              ┌─────────────┐
                              │   PHASE_3   │ Dispatch @dede/@dali/@gus
                              │    PLANS    │◄─────────────────────┐
                              └──────┬──────┘                      │
                                     │                             │
                                     ▼                             │
                              ┌─────────────┐                      │
                              │   GATE_2    │ Wait for human       │
                              │   PLANS     │──── rejected ────────┘
                              └──────┬──────┘
                                     │ approved
                                     ▼
                              ┌─────────────┐
                              │   PHASE_4   │ Dispatch @marie
                              │   TESTS     │◄─────────────────────┐
                              └──────┬──────┘                      │
                                     │                             │
                                     ▼                             │
                              ┌─────────────┐                      │
                              │   GATE_3    │ Wait for human       │
                              │   TESTS     │──── rejected ────────┘
                              └──────┬──────┘
                                     │ approved
                                     ▼
                              ┌─────────────┐
                              │   PHASE_5   │ Dispatch @dede/@dali/@gus
                              │    IMPL     │ (TDD loop until tests pass)
                              └──────┬──────┘
                                     │ all agents complete
                                     ▼
                              ┌─────────────┐
                              │   PHASE_6   │ Create PR
                              │  CREATE_PR  │
                              └──────┬──────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │   PHASE_7   │ Dispatch reviewers
                              │   REVIEW    │◄─────────────────────┐
                              └──────┬──────┘                      │
                                     │                             │
                                     ▼                             │
                              ┌─────────────┐                      │
                              │  REVIEW_    │ Changes requested?   │
                              │   CHECK     │──── yes ─────────────┘
                              └──────┬──────┘     (fix & re-review)
                                     │ all approved
                                     ▼
                              ┌─────────────┐
                              │   GATE_4    │ Wait for human
                              │   MERGE     │──── rejected ────────┐
                              └──────┬──────┘                      │
                                     │ approved                    │
                                     ▼                             │
                              ┌─────────────┐                      │
                              │   PHASE_8   │ Merge, cleanup       │
                              │   CLEANUP   │                      │
                              └──────┬──────┘                      │
                                     │                             │
                                     ▼                             │
                              ┌─────────────┐                      │
                              │    DONE     │                      │
                              └─────────────┘                      │
                                                                   │
                                     ┌─────────────────────────────┘
                                     │ (back to PHASE_7 for re-review)
                                     ▼