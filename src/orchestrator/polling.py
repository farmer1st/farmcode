"""Signal Polling for orchestrator workflow.

This module provides polling functionality to detect completion signals
in GitHub issue comments.
"""

import time
from typing import Any

from orchestrator.errors import PollTimeoutError
from orchestrator.logger import logger
from orchestrator.models import PollResult, SignalType

# Signal patterns
AGENT_COMPLETE_PATTERN = "✅"  # Checkmark emoji
HUMAN_APPROVAL_PATTERN = "approved"  # Case-insensitive


class SignalPoller:
    """Polls GitHub issue comments for completion signals.

    The SignalPoller periodically checks issue comments for specific
    signals indicating agent completion or human approval.

    Attributes:
        _github: GitHub service for API operations.

    Example:
        >>> poller = SignalPoller(github_service)
        >>> result = poller.poll_for_signal(
        ...     issue_number=123,
        ...     signal_type=SignalType.AGENT_COMPLETE,
        ...     timeout_seconds=300,
        ... )
        >>> if result.detected:
        ...     print(f"Signal found in comment {result.comment_id}")
    """

    def __init__(self, github_service: Any) -> None:
        """Initialize the signal poller.

        Args:
            github_service: GitHub service for API operations.
        """
        self._github = github_service

    def poll_for_signal(
        self,
        issue_number: int,
        signal_type: SignalType,
        timeout_seconds: int = 3600,
        interval_seconds: int = 30,
        raise_on_timeout: bool = False,
    ) -> PollResult:
        """Poll for a completion signal in issue comments.

        Args:
            issue_number: GitHub issue number.
            signal_type: Type of signal to poll for.
            timeout_seconds: Maximum time to poll (default 1 hour).
            interval_seconds: Time between polls (default 30s).
            raise_on_timeout: Whether to raise PollTimeoutError on timeout.

        Returns:
            PollResult with detection status.

        Raises:
            PollTimeoutError: If timeout reached and raise_on_timeout is True.
        """
        start_time = time.time()
        poll_count = 0

        logger.info(
            f"Starting poll for {signal_type.value}",
            extra={
                "context": {
                    "issue_number": issue_number,
                    "signal_type": signal_type.value,
                    "timeout_seconds": timeout_seconds,
                }
            },
        )

        while True:
            poll_count += 1
            elapsed = time.time() - start_time

            # Check for timeout
            if elapsed >= timeout_seconds:
                if raise_on_timeout:
                    raise PollTimeoutError(
                        f"Signal {signal_type.value} not detected after {timeout_seconds}s"
                    )
                return PollResult(
                    detected=False,
                    signal_type=signal_type,
                    poll_count=poll_count,
                )

            # Check for signal
            result = self._check_for_signal(issue_number, signal_type)
            if result.detected:
                logger.info(
                    f"Signal {signal_type.value} detected",
                    extra={
                        "context": {
                            "issue_number": issue_number,
                            "comment_id": result.comment_id,
                            "poll_count": poll_count,
                        }
                    },
                )
                return PollResult(
                    detected=True,
                    signal_type=signal_type,
                    comment_id=result.comment_id,
                    comment_body=result.comment_body,
                    comment_author=result.comment_author,
                    poll_count=poll_count,
                )

            # Wait before next poll (unless timeout imminent)
            remaining = timeout_seconds - elapsed
            sleep_time = min(interval_seconds, max(0, remaining - 0.1))
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _check_for_signal(
        self,
        issue_number: int,
        signal_type: SignalType,
    ) -> PollResult:
        """Check issue comments for a specific signal.

        Args:
            issue_number: GitHub issue number.
            signal_type: Type of signal to look for.

        Returns:
            PollResult indicating if signal was found.
        """
        try:
            comments = self._github.get_issue_comments(issue_number)

            for comment in comments:
                body = comment.body or ""
                author = getattr(comment.user, "login", "unknown")

                if self._matches_signal(body, signal_type):
                    return PollResult(
                        detected=True,
                        signal_type=signal_type,
                        comment_id=comment.id,
                        comment_body=body,
                        comment_author=author,
                    )

        except Exception as e:
            logger.warning(
                f"Error checking comments for issue {issue_number}: {e}",
                extra={"context": {"issue_number": issue_number, "error": str(e)}},
            )

        return PollResult(
            detected=False,
            signal_type=signal_type,
        )

    def _matches_signal(self, body: str, signal_type: SignalType) -> bool:
        """Check if comment body matches the signal pattern.

        Args:
            body: Comment body text.
            signal_type: Type of signal to match.

        Returns:
            True if body matches the signal pattern.
        """
        if signal_type == SignalType.AGENT_COMPLETE:
            return AGENT_COMPLETE_PATTERN in body
        elif signal_type == SignalType.HUMAN_APPROVAL:
            return HUMAN_APPROVAL_PATTERN in body.lower()
        return False
