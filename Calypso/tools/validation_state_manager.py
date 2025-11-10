#!/usr/bin/env python3
"""
Validation State Manager for Calypso Project

Manages validation state across retry attempts.
Tracks validation results, retry counts, and feedback for each page.

State files: page_artifacts/page_XX/validation_state.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class ValidationStateManager:
    """Manage validation state for pages."""

    def __init__(self, chapter: int, page: int):
        """Initialize state manager for a specific page."""
        self.chapter = chapter
        self.page = page
        self.state_file = self._get_state_file_path()
        self.state = self._load_state()

    def _get_state_file_path(self) -> Path:
        """Get path to validation state file."""
        base_dir = Path(__file__).parent.parent
        chapter_str = f"{self.chapter:02d}"
        state_file = (
            base_dir / "output" / f"chapter_{chapter_str}" /
            "page_artifacts" / f"page_{self.page}" / "validation_state.json"
        )
        return state_file

    def _load_state(self) -> Dict:
        """Load existing state or create new."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'chapter': self.chapter,
                'page': self.page,
                'created_at': datetime.now().isoformat(),
                'status': 'new',
                'stage': None,
                'attempts': [],
                'last_result': None,
                'retry_count': 0,
                'max_retries': 3,
                'validation_scores': {
                    'text_coverage': None,
                    'html_structure': None,
                    'visual_similarity': None
                }
            }

    def _save_state(self):
        """Save current state to file."""
        self.state['updated_at'] = datetime.now().isoformat()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_retry_count(self) -> int:
        """Get current retry count."""
        return self.state.get('retry_count', 0)

    def get_max_retries(self) -> int:
        """Get max retry limit."""
        return self.state.get('max_retries', 3)

    def can_retry(self) -> bool:
        """Check if page can be retried."""
        return self.get_retry_count() < self.get_max_retries()

    def increment_retry(self) -> int:
        """Increment retry count and return new count."""
        self.state['retry_count'] = self.get_retry_count() + 1
        self._save_state()
        return self.state['retry_count']

    def record_attempt(self, stage: str, status: str, scores: Dict, issues: List[str]):
        """Record a validation attempt."""
        attempt = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'attempt_number': self.get_retry_count(),
            'status': status,
            'scores': scores,
            'issues': issues
        }

        self.state['attempts'].append(attempt)
        self.state['stage'] = stage
        self.state['last_result'] = attempt

        # Update validation scores
        if scores:
            for key, value in scores.items():
                if value is not None:
                    self.state['validation_scores'][key] = value

        self._save_state()

    def mark_passed(self, stage: str):
        """Mark page as passed at a stage."""
        self.state['status'] = 'passed'
        self.state['stage'] = stage
        self.state['passed_at'] = datetime.now().isoformat()
        self._save_state()

    def mark_failed(self, stage: str, reason: str):
        """Mark page as failed at a stage."""
        self.state['status'] = 'failed'
        self.state['stage'] = stage
        self.state['failed_at'] = datetime.now().isoformat()
        self.state['failure_reason'] = reason
        self._save_state()

    def mark_blocked(self, stage: str, reason: str):
        """Mark page as blocked (max retries exceeded)."""
        self.state['status'] = 'blocked'
        self.state['stage'] = stage
        self.state['blocked_at'] = datetime.now().isoformat()
        self.state['block_reason'] = reason
        self._save_state()

    def get_status(self) -> str:
        """Get current status."""
        return self.state.get('status', 'new')

    def get_validation_scores(self) -> Dict:
        """Get all validation scores."""
        return self.state.get('validation_scores', {})

    def get_last_attempt(self) -> Optional[Dict]:
        """Get information from last attempt."""
        attempts = self.state.get('attempts', [])
        return attempts[-1] if attempts else None

    def get_feedback_summary(self) -> str:
        """Get summary of all feedback from failed attempts."""
        attempts = self.state.get('attempts', [])
        failed_attempts = [a for a in attempts if a['status'] != 'passed']

        if not failed_attempts:
            return "No failed attempts"

        feedback_lines = []
        for i, attempt in enumerate(failed_attempts, 1):
            feedback_lines.append(f"\nAttempt {i} ({attempt['stage']} stage):")

            if attempt['issues']:
                for issue in attempt['issues']:
                    feedback_lines.append(f"  • {issue}")

            scores = attempt.get('scores', {})
            if scores:
                for score_name, score_value in scores.items():
                    if score_value is not None:
                        feedback_lines.append(f"  {score_name}: {score_value}%")

        return "\n".join(feedback_lines)

    def reset(self):
        """Reset state for a fresh attempt."""
        self.state = {
            'chapter': self.chapter,
            'page': self.page,
            'created_at': self.state['created_at'],
            'status': 'new',
            'stage': None,
            'attempts': [],
            'last_result': None,
            'retry_count': 0,
            'max_retries': 3,
            'validation_scores': {
                'text_coverage': None,
                'html_structure': None,
                'visual_similarity': None
            }
        }
        self._save_state()

    def to_dict(self) -> Dict:
        """Export state as dictionary."""
        return self.state.copy()

    def print_summary(self):
        """Print human-readable summary."""
        print(f"\n{'='*80}")
        print(f"Validation Status: Chapter {self.chapter}, Page {self.page}")
        print(f"{'='*80}")

        print(f"Status: {self.get_status()}")
        print(f"Retries: {self.get_retry_count()}/{self.get_max_retries()}")

        scores = self.get_validation_scores()
        if any(v is not None for v in scores.values()):
            print(f"\nValidation Scores:")
            for key, value in scores.items():
                if value is not None:
                    print(f"  {key}: {value}%")

        last_attempt = self.get_last_attempt()
        if last_attempt:
            print(f"\nLast Attempt:")
            print(f"  Stage: {last_attempt['stage']}")
            print(f"  Status: {last_attempt['status']}")

            if last_attempt['issues']:
                print(f"  Issues:")
                for issue in last_attempt['issues']:
                    print(f"    • {issue}")

        print(f"{'='*80}\n")


def main():
    """Test/demo the state manager."""
    if len(sys.argv) < 3:
        print("Usage: python3 validation_state_manager.py <chapter> <page> [action]")
        print("Actions: status, reset, summary")
        sys.exit(1)

    chapter = int(sys.argv[1])
    page = int(sys.argv[2])
    action = sys.argv[3] if len(sys.argv) > 3 else "status"

    manager = ValidationStateManager(chapter, page)

    if action == "status":
        print(json.dumps(manager.to_dict(), indent=2))
    elif action == "summary":
        manager.print_summary()
    elif action == "reset":
        manager.reset()
        print(f"Reset validation state for chapter {chapter}, page {page}")
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == '__main__':
    main()
