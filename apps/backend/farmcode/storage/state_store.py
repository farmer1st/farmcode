"""State persistence for feature workflow tracking."""

from __future__ import annotations

from pathlib import Path

from farmcode.models.state import FeatureState


class StateStore:
    """Manages persistence of feature states to JSON files."""

    def __init__(self, storage_dir: Path | None = None):
        """Initialize state store.

        Args:
            storage_dir: Directory for state files. Defaults to ~/.farmcode
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".farmcode"

        self.storage_dir = storage_dir / "features"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, issue_number: int) -> Path:
        """Get file path for an issue's state.

        Args:
            issue_number: GitHub issue number

        Returns:
            Path to JSON file
        """
        return self.storage_dir / f"{issue_number}.json"

    def save(self, state: FeatureState) -> None:
        """Save feature state to JSON file.

        Args:
            state: Feature state to save
        """
        file_path = self._get_file_path(state.issue_number)
        file_path.write_text(state.model_dump_json(indent=2))

    def load(self, issue_number: int) -> FeatureState | None:
        """Load feature state from JSON file.

        Args:
            issue_number: GitHub issue number

        Returns:
            Feature state if found, None otherwise
        """
        file_path = self._get_file_path(issue_number)

        if not file_path.exists():
            return None

        return FeatureState.model_validate_json(file_path.read_text())

    def delete(self, issue_number: int) -> bool:
        """Delete feature state file.

        Args:
            issue_number: GitHub issue number

        Returns:
            True if file was deleted, False if it didn't exist
        """
        file_path = self._get_file_path(issue_number)

        if file_path.exists():
            file_path.unlink()
            return True

        return False

    def list_all(self) -> list[FeatureState]:
        """List all active feature states.

        Returns:
            List of all feature states sorted by issue number
        """
        states = []

        for file_path in self.storage_dir.glob("*.json"):
            try:
                state = FeatureState.model_validate_json(file_path.read_text())
                states.append(state)
            except Exception:
                # Skip invalid files
                continue

        # Sort by issue number
        return sorted(states, key=lambda s: s.issue_number)

    def exists(self, issue_number: int) -> bool:
        """Check if state exists for an issue.

        Args:
            issue_number: GitHub issue number

        Returns:
            True if state file exists
        """
        return self._get_file_path(issue_number).exists()
