# Farm Code Backend Tests

Comprehensive test suite covering MVP functionality.

## Test Structure

### Unit Tests

**[test_state_machine.py](test_state_machine.py)** - State machine and phase transitions
- Phase advancement validation
- Agent completion tracking
- Human approval handling
- Status summary generation

**[test_state_store.py](test_state_store.py)** - State persistence
- Save/load operations
- State deletion
- Listing all states
- Phase history preservation

**[test_worktree_manager.py](test_worktree_manager.py)** - Git worktree operations
- Worktree creation with `.plans/` structure
- Branch naming (slugification)
- Worktree deletion
- Duplicate detection

**[test_github_poller.py](test_github_poller.py)** - GitHub comment monitoring
- Agent completion detection (✅)
- Human approval detection
- Timestamp filtering
- Agent handle extraction

**[test_phase_manager.py](test_phase_manager.py)** - Phase execution
- Phase 1 execution (setup)
- Phase 2 execution (specs)
- Gate 1 execution (approval)
- Phase validation

### Integration Tests

**[test_mvp_integration.py](test_mvp_integration.py)** - End-to-end MVP workflow
- Complete workflow: Create → Phase 2 → Gate 1 → Approval
- Agent dispatcher integration
- Polling loop with multiple features
- Manual gate approval

## Running Tests

### All Tests
```bash
cd apps/backend
pytest
```

### With Coverage
```bash
pytest --cov=farmcode --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_mvp_integration.py
```

### Specific Test
```bash
pytest tests/test_mvp_integration.py::test_mvp_workflow_end_to_end
```

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

## Test Coverage

The test suite covers:

### Phase 1 (Setup)
- ✅ GitHub issue creation
- ✅ Git branch creation
- ✅ Worktree creation
- ✅ `.plans/` folder structure
- ✅ README generation
- ✅ Auto-advance to Phase 2

### Phase 2 (Specs)
- ✅ Phase execution
- ✅ GitHub comment posting
- ✅ Agent dispatcher spawning
- ✅ Completion detection via polling
- ✅ Auto-advance to Gate 1

### Gate 1 (Approval)
- ✅ Approval request posting
- ✅ Human approval detection
- ✅ Manual approval via orchestrator
- ✅ Gate advancement

### Core Components
- ✅ State machine transitions
- ✅ State persistence (JSON)
- ✅ Git operations
- ✅ GitHub polling
- ✅ Agent handle extraction
- ✅ Multi-feature handling

## Test Fixtures

See [conftest.py](conftest.py) for shared fixtures:

- `temp_dir` - Temporary directory for test files
- `mock_config` - Test configuration with mock paths
- `state_store` - State store instance
- `mock_github_adapter` - Mocked GitHub API
- `mock_worktree_manager` - Mocked git operations
- `orchestrator` - Fully configured orchestrator

## Mocking Strategy

### GitHub Operations
GitHub API calls are mocked to avoid:
- Network requests during tests
- Rate limiting issues
- Dependency on GitHub availability

### Git Operations
Git push operations are mocked to avoid:
- Pushing to actual remote repositories
- Authentication requirements

### Agent Dispatch
Claude CLI spawning is mocked to avoid:
- Spawning actual Claude processes
- API costs during testing

## Test Data

Tests use realistic data:
- Issue numbers: 123, 456, etc.
- Repositories: `test-org/test-repo`
- Agent handles: `duc`, `baron`, `dede`
- Phases: Phase 1, Phase 2, Gate 1

## Continuous Integration

These tests are designed to run in CI/CD:
- No external dependencies required
- All GitHub/Git operations mocked
- Fast execution (< 5 seconds)
- Deterministic results

## Known Limitations

1. **MCP Server not tested in isolation** - MCP tools are tested via integration, not unit tests
2. **Agent CLI spawning mocked** - Actual Claude CLI execution not tested
3. **GitHub webhook integration not tested** - Only polling is tested
4. **Phase 3-8 not implemented** - Tests only cover MVP scope

## Future Test Additions

When implementing remaining phases:
- Phase 3-8 execution tests
- Multi-agent parallel execution
- Error recovery and retry logic
- Agent session resumption
- Webhook handlers
