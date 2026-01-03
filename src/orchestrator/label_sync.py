"""Label Synchronization for orchestrator workflow.

This module provides functionality to synchronize GitHub issue labels
with the current workflow state.
"""

from typing import Any

from orchestrator.logger import logger
from orchestrator.models import OperationResult, OperationStatus, WorkflowState

# State to label mapping
STATE_LABEL_MAP: dict[WorkflowState, str] = {
    WorkflowState.IDLE: "status:new",
    WorkflowState.PHASE_1: "status:phase-1",
    WorkflowState.PHASE_2: "status:phase-2",
    WorkflowState.GATE_1: "status:awaiting-approval",
    WorkflowState.DONE: "status:done",
}

# Label colors (for creating labels if they don't exist)
LABEL_COLORS: dict[str, str] = {
    "status:new": "0052cc",  # Blue
    "status:phase-1": "fbca04",  # Yellow
    "status:phase-2": "f9a825",  # Orange
    "status:awaiting-approval": "7057ff",  # Purple
    "status:done": "0e8a16",  # Green
}

# Status label prefix for identification
STATUS_PREFIX = "status:"


class LabelSync:
    """Synchronizes GitHub issue labels with workflow state.

    The LabelSync class manages the application of status labels
    to GitHub issues based on the current workflow state. It ensures
    only one status label is present at a time.

    Attributes:
        _github: GitHub service for API operations.

    Example:
        >>> sync = LabelSync(github_service)
        >>> result = sync.sync_labels(123, WorkflowState.PHASE_2)
        >>> if result.status == OperationStatus.SUCCESS:
        ...     print("Labels synced successfully")
    """

    def __init__(self, github_service: Any) -> None:
        """Initialize the label sync.

        Args:
            github_service: GitHub service for API operations.
        """
        self._github = github_service

    def sync_labels(
        self,
        issue_number: int,
        current_state: WorkflowState,
    ) -> OperationResult:
        """Synchronize GitHub labels with current state.

        Removes old status labels and applies the label for the current state.

        Args:
            issue_number: GitHub issue number.
            current_state: Current workflow state.

        Returns:
            OperationResult indicating success/failure.
        """
        target_label = STATE_LABEL_MAP[current_state]
        errors: list[str] = []

        logger.info(
            f"Syncing labels for issue {issue_number}",
            extra={
                "context": {
                    "issue_number": issue_number,
                    "state": current_state.value,
                    "target_label": target_label,
                }
            },
        )

        # Remove old status labels
        try:
            existing_labels = self._github.get_issue_labels(issue_number)
            for label in existing_labels:
                label_name = getattr(label, "name", str(label))
                if label_name.startswith(STATUS_PREFIX) and label_name != target_label:
                    try:
                        self._github.remove_label(issue_number, label_name)
                        logger.info(
                            f"Removed label {label_name}",
                            extra={
                                "context": {
                                    "issue_number": issue_number,
                                    "label": label_name,
                                }
                            },
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to remove label {label_name}: {e}",
                            extra={"context": {"label": label_name, "error": str(e)}},
                        )
                        errors.append(f"Failed to remove {label_name}: {e}")
        except Exception as e:
            logger.warning(
                f"Failed to get existing labels: {e}",
                extra={"context": {"issue_number": issue_number, "error": str(e)}},
            )
            # Continue anyway - we'll still try to add the new label

        # Add current state label
        try:
            self._github.add_label(issue_number, target_label)
            logger.info(
                f"Added label {target_label}",
                extra={
                    "context": {
                        "issue_number": issue_number,
                        "label": target_label,
                    }
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to add label {target_label}: {e}",
                extra={"context": {"label": target_label, "error": str(e)}},
            )
            errors.append(f"Failed to add {target_label}: {e}")
            return OperationResult(
                status=OperationStatus.FAILURE,
                message=f"Failed to add label: {e}",
                details={"errors": errors},
            )

        if errors:
            return OperationResult(
                status=OperationStatus.PARTIAL,
                message="Labels synced with some errors",
                details={"errors": errors},
            )

        return OperationResult(
            status=OperationStatus.SUCCESS,
            message=f"Synced label to {target_label}",
            details={"label": target_label},
        )

    def ensure_labels_exist(self) -> OperationResult:
        """Ensure all status labels exist in the repository.

        Creates any missing status labels with appropriate colors.

        Returns:
            OperationResult indicating success/failure.
        """
        created = []
        errors = []

        for label_name, color in LABEL_COLORS.items():
            try:
                self._github.create_label(label_name, color)
                created.append(label_name)
            except Exception as e:
                # Label might already exist - that's OK
                if "already exists" not in str(e).lower():
                    errors.append(f"{label_name}: {e}")

        if errors:
            return OperationResult(
                status=OperationStatus.PARTIAL,
                message="Some labels could not be created",
                details={"created": created, "errors": errors},
            )

        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="All labels ensured",
            details={"labels": list(LABEL_COLORS.keys())},
        )
