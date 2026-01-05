# SpecKit Workflow Guide

**Quick Reference for Feature Development with SpecKit**

Version: 1.0.0
Last Updated: 2026-01-03

---

## Table of Contents

1. [Understanding the Hierarchy](#understanding-the-hierarchy)
2. [File Organization](#file-organization)
3. [SpecKit Commands](#speckit-commands)
4. [Complete Workflow](#complete-workflow)
5. [Where to Find Information](#where-to-find-information)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Understanding the Hierarchy

SpecKit organizes work into a clear hierarchy:

```
Roadmap (strategic plan, quarters/months)
  │
  └─► Feature (large deliverable, 2-8 weeks)
       │   - Has unique ID: NNN-short-name (e.g., 001-github-integration-core)
       │   - Has dedicated branch: NNN-short-name
       │   - Has specs directory: specs/NNN-short-name/
       │   - Has spec.md, plan.md, tasks.md
       │
       └─► User Story (user-facing functionality, 2-5 days)
            │   - Priority: P1 (critical), P2 (important), P3 (nice-to-have)
            │   - Label: US1, US2, US3...
            │   - Defined in spec.md
            │   - Each gets its own phase in tasks.md
            │
            └─► Task (single unit of work, 15min-2 hours)
                 - ID: T001, T002, T003...
                 - Defined in tasks.md
                 - Exact file paths and actions
                 - Can be parallel [P] or sequential
```

### Key Relationships

- **Feature → User Stories**: 1 feature contains 3-8 user stories
- **User Story → Tasks**: 1 user story contains 5-20 tasks
- **Task → Files**: 1 task typically affects 1-3 files

---

## File Organization

### Repository Structure

```
farmer-code/
├── .specify/                    # SpecKit infrastructure
│   ├── memory/
│   │   └── constitution.md      # Project standards (v1.4.0)
│   ├── templates/               # Templates for spec, plan, tasks
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   └── tasks-template.md
│   └── scripts/                 # SpecKit automation scripts
│       └── bash/
│           ├── create-new-feature.sh
│           ├── setup-plan.sh
│           ├── check-prerequisites.sh
│           └── update-agent-context.sh
│
├── specs/                       # All feature specifications
│   └── NNN-feature-name/        # One directory per feature
│       ├── spec.md              # WHAT & WHY (business requirements)
│       ├── plan.md              # HOW (technical design)
│       ├── tasks.md             # DETAILED STEPS (implementation tasks)
│       ├── research.md          # Technical decisions & research
│       ├── data-model.md        # Entities, fields, relationships
│       ├── quickstart.md        # Integration scenarios
│       ├── contracts/           # API specifications
│       │   ├── openapi.yaml     # REST API contracts
│       │   └── *.contract.md    # Individual endpoint contracts
│       └── checklists/          # Quality gates
│           ├── requirements.md  # Spec quality checklist
│           ├── ux.md            # UX checklist (if applicable)
│           ├── security.md      # Security checklist (if applicable)
│           └── test.md          # Test coverage checklist (if applicable)
│
├── docs/                        # User-facing documentation
│   ├── user-journeys/           # End-to-end user workflows
│   │   ├── JOURNEYS.md          # Journey registry (all journeys)
│   │   ├── README.md            # Journey documentation guide
│   │   └── ORC-*.md             # Individual journey files
│   └── architecture/            # System architecture docs
│
├── references/                  # Development references
│   ├── speckit-guide.md         # This file
│   ├── sdlc-workflow.md         # 8-phase SDLC reference
│   └── feature-breakdown.md     # Example feature breakdown
│
├── src/                         # Implementation code
│   └── module_name/
│       ├── README.md            # Module documentation
│       ├── service.py
│       ├── models.py
│       └── ...
│
└── tests/                       # Test suites
    ├── contract/                # Public API tests
    ├── integration/             # Component integration tests
    ├── e2e/                     # End-to-end journey tests
    └── conftest.py              # Shared fixtures + journey reporting
```

### Feature Directory Structure

Each feature gets a directory: `specs/NNN-short-name/`

**Example**: `specs/001-github-integration-core/`

```
specs/001-github-integration-core/
├── spec.md              # Business requirements (WHAT & WHY)
├── plan.md              # Technical design (HOW)
├── tasks.md             # Implementation tasks (DETAILED STEPS)
├── research.md          # Technical research & decisions
├── data-model.md        # Database entities & relationships
├── quickstart.md        # Integration & test scenarios
├── contracts/           # API contracts
│   ├── issues.contract.md
│   └── comments.contract.md
└── checklists/          # Quality gates
    ├── requirements.md  # Spec completeness
    └── test.md          # Test coverage
```

---

## SpecKit Commands

SpecKit provides 9 commands for the development workflow:

### Core Workflow Commands (use in order)

| Command | Purpose | Input | Output | When to Use |
|---------|---------|-------|--------|-------------|
| `/speckit.specify [description]` | Create feature specification | Natural language feature description | `spec.md` + new branch | Starting a new feature |
| `/speckit.clarify` | Ask clarification questions | Unclear requirements in spec | Updated `spec.md` | After `/specify` if spec has [NEEDS CLARIFICATION] markers |
| `/speckit.plan` | Generate technical plan | `spec.md` | `plan.md` + `research.md` + `data-model.md` + `contracts/` | After spec is complete |
| `/speckit.tasks` | Generate task list | `spec.md` + `plan.md` | `tasks.md` | After plan is complete |
| `/speckit.implement` | Execute tasks | `tasks.md` | Implemented code | After tasks are generated |

### Supporting Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/speckit.checklist [domain]` | Create quality checklists | After `/specify` or `/plan` to ensure quality gates |
| `/speckit.analyze` | Check cross-artifact consistency | After `/tasks` before `/implement` |
| `/speckit.constitution` | Update project constitution | When adding new standards or principles |
| `/speckit.taskstoissues` | Convert tasks to GitHub issues | After `/tasks` to create trackable issues |

---

## Complete Workflow

### Step-by-Step Feature Development

#### 1. Start New Feature

```bash
/speckit.specify Add user authentication with OAuth2
```

**What happens:**
- Generates feature ID (e.g., `002-user-auth`)
- Creates branch: `002-user-auth`
- Creates directory: `specs/002-user-auth/`
- Creates `spec.md` with:
  - User stories (P1, P2, P3)
  - Functional requirements
  - Success criteria
  - User scenarios
  - May have [NEEDS CLARIFICATION] markers

**Output:**
```
✅ Created branch: 002-user-auth
✅ Created spec: specs/002-user-auth/spec.md
✅ Ready for: /speckit.clarify (if needed) or /speckit.plan
```

#### 2. Clarify Requirements (if needed)

```bash
/speckit.clarify
```

**What happens:**
- Scans `spec.md` for [NEEDS CLARIFICATION] markers
- Asks up to 3 targeted questions
- Updates `spec.md` with your answers
- Removes all [NEEDS CLARIFICATION] markers

**Skip this if:** Spec has no [NEEDS CLARIFICATION] markers

#### 3. Generate Technical Plan

```bash
/speckit.plan
```

**What happens:**
- Reads `spec.md` and `constitution.md`
- Generates technical architecture
- Creates multiple files:
  - `plan.md` - Tech stack, architecture, phases
  - `research.md` - Technical decisions
  - `data-model.md` - Database entities
  - `contracts/` - API specifications
  - `quickstart.md` - Integration scenarios

**Output:**
```
✅ Created plan: specs/002-user-auth/plan.md
✅ Generated research: specs/002-user-auth/research.md
✅ Generated data model: specs/002-user-auth/data-model.md
✅ Generated contracts: specs/002-user-auth/contracts/
✅ Ready for: /speckit.tasks
```

#### 4. Generate Task List

```bash
/speckit.tasks
```

**What happens:**
- Reads all design documents (`spec.md`, `plan.md`, `data-model.md`, `contracts/`)
- Organizes tasks by user story (P1, P2, P3)
- Creates dependency-ordered task list
- Marks parallelizable tasks with [P]

**Output:**
```
✅ Created tasks: specs/002-user-auth/tasks.md
✅ Total tasks: 45
   - Setup: 5 tasks
   - User Story 1 (P1): 12 tasks
   - User Story 2 (P1): 8 tasks
   - User Story 3 (P2): 15 tasks
   - Polish: 5 tasks
✅ Parallel opportunities: 18 tasks
✅ Ready for: /speckit.analyze or /speckit.implement
```

#### 5. Implement Tasks

```bash
/speckit.implement
```

**What happens:**
- Reads `tasks.md` and all design documents
- Executes tasks phase by phase
- Marks completed tasks as [X]
- Follows TDD approach (tests before code)
- Reports progress after each task

**Process:**
1. Setup phase (project structure, dependencies)
2. Foundational phase (shared components)
3. User Story phases (P1 → P2 → P3)
4. Polish phase (optimization, documentation)

**Output:**
```
✅ Phase 1 (Setup): 5/5 tasks completed
✅ Phase 2 (US1): 12/12 tasks completed
⏳ Phase 3 (US2): 3/8 tasks in progress...
```

---

## Where to Find Information

### "Where is...?"

| What You Need | Where to Find It | File/Location |
|---------------|------------------|---------------|
| **Feature ID** | Branch name or specs directory | `git branch` or `ls specs/` |
| **Business requirements** | Specification file | `specs/NNN-name/spec.md` |
| **User stories** | Specification file | `specs/NNN-name/spec.md` → User Stories section |
| **User story priorities** | Specification file | `specs/NNN-name/spec.md` → User Stories (P1, P2, P3) |
| **Technical design** | Implementation plan | `specs/NNN-name/plan.md` |
| **Tech stack** | Implementation plan | `specs/NNN-name/plan.md` → Technology Stack section |
| **Database schema** | Data model file | `specs/NNN-name/data-model.md` |
| **API contracts** | Contracts directory | `specs/NNN-name/contracts/*.contract.md` |
| **Technical decisions** | Research file | `specs/NNN-name/research.md` |
| **Task list** | Tasks file | `specs/NNN-name/tasks.md` |
| **Task status** | Tasks file | `specs/NNN-name/tasks.md` → Check `[X]` marks |
| **User journeys** | Journey registry | `docs/user-journeys/JOURNEYS.md` |
| **Journey details** | Journey files | `docs/user-journeys/ORC-*.md` |
| **Project standards** | Constitution | `.specify/memory/constitution.md` |
| **Module documentation** | Module README | `src/module_name/README.md` |

### "How do I...?"

| Task | Command/Action |
|------|----------------|
| **Start a new feature** | `/speckit.specify [description]` |
| **See all features** | `ls specs/` or `git branch` |
| **Check current feature** | `git branch --show-current` |
| **Switch to feature** | `git checkout NNN-feature-name` |
| **See user stories** | Read `specs/NNN-name/spec.md` |
| **See task progress** | Read `specs/NNN-name/tasks.md` (count `[X]` marks) |
| **See what's next** | Read `tasks.md` → find first `[ ]` (unchecked) task |
| **Check tech stack** | Read `specs/NNN-name/plan.md` |
| **Check standards** | Read `.specify/memory/constitution.md` |
| **Run tests** | `uv run pytest` |
| **Run journey tests** | `uv run pytest -m journey` |

---

## Common Patterns

### Pattern 1: Starting Fresh

```bash
# 1. Describe feature
/speckit.specify Add real-time notifications with WebSockets

# 2. Wait for spec generation
# (SpecKit creates branch, spec.md)

# 3. Review spec.md, clarify if needed
/speckit.clarify

# 4. Generate plan
/speckit.plan

# 5. Generate tasks
/speckit.tasks

# 6. Implement
/speckit.implement
```

### Pattern 2: Resuming Work

```bash
# 1. Switch to feature branch
git checkout 003-notifications

# 2. Check progress
cat specs/003-notifications/tasks.md | grep -E '\[[ X]\]'

# 3. Continue implementation
/speckit.implement
```

### Pattern 3: Adding User Story Mid-Feature

```bash
# 1. Update spec.md manually (add new user story)

# 2. Regenerate tasks
/speckit.tasks

# 3. Continue implementation
/speckit.implement
```

### Pattern 4: Quality Check Before Implementation

```bash
# 1. After generating tasks
/speckit.tasks

# 2. Run consistency check
/speckit.analyze

# 3. If issues found, fix and regenerate
# Edit spec.md or plan.md
/speckit.tasks

# 4. Implement when ready
/speckit.implement
```

---

## Troubleshooting

### Common Issues

#### "I forgot which feature I'm working on"

```bash
# Check current branch
git branch --show-current

# Output: 002-user-auth
# This is your feature ID
```

#### "Where are my user stories?"

```bash
# Open the spec file for current feature
# Example: specs/002-user-auth/spec.md
# Look for "User Stories" section
cat specs/$(git branch --show-current)/spec.md
```

#### "What tasks are left?"

```bash
# Find uncompleted tasks
# [ ] = not done, [X] = done
cat specs/$(git branch --show-current)/tasks.md | grep '\[ \]'
```

#### "I need to see the tech stack"

```bash
# Open plan.md for current feature
cat specs/$(git branch --show-current)/plan.md
# Look for "Technology Stack" section
```

#### "Where is the API documentation?"

```bash
# Check contracts directory
ls specs/$(git branch --show-current)/contracts/

# Read a specific contract
cat specs/$(git branch --show-current)/contracts/issues.contract.md
```

#### "I want to check my test coverage"

```bash
# Run all tests with coverage
uv run pytest --cov=src --cov-report=html

# Run journey tests only
uv run pytest -m journey -v

# Open coverage report
open htmlcov/index.html
```

#### "SpecKit says 'NEEDS CLARIFICATION' - what do I do?"

```bash
# Run clarify command
/speckit.clarify

# It will ask you questions and update spec.md automatically
```

#### "How do I know if I'm following standards?"

```bash
# Read the constitution
cat .specify/memory/constitution.md

# Key sections:
# - Principle I: Test-First Development
# - Principle II: Thin Client Architecture
# - Principle V: Security-First Development
```

---

## Quick Reference Card

### SpecKit Workflow (4 Commands)

1. **Specify** → Creates `spec.md` (business requirements)
2. **Plan** → Creates `plan.md` + research + data model + contracts
3. **Tasks** → Creates `tasks.md` (detailed task list)
4. **Implement** → Executes tasks, writes code

### File Locations

- **Business**: `specs/NNN-name/spec.md`
- **Technical**: `specs/NNN-name/plan.md`
- **Tasks**: `specs/NNN-name/tasks.md`
- **Standards**: `.specify/memory/constitution.md`
- **Journeys**: `docs/user-journeys/`

### Task Markers

- `[ ]` - Not started
- `[X]` - Completed
- `[P]` - Can run in parallel
- `[US1]` - User Story 1 task
- `T001` - Task ID

### Priority Levels

- **P1** - Critical (MVP, must have)
- **P2** - Important (post-MVP)
- **P3** - Nice to have (future)

---

## Additional Resources

- **Constitution**: `.specify/memory/constitution.md` - Project standards
- **SDLC Reference**: `references/sdlc-workflow.md` - 8-phase workflow
- **Journey Guide**: `docs/user-journeys/README.md` - User journey documentation
- **Templates**: `.specify/templates/` - Spec, plan, tasks templates

---

**Last Updated**: 2026-01-03
**Version**: 1.0.0
