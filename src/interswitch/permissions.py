"""
Scope checking for API methods.
"""

import logging

logger = logging.getLogger("interswitch.auth")


class InsufficientActionsError(Exception):
    """
    Raised when the current token does not have permission to call an API.

    This means your Interswitch project was not configured with the required
    API. Go to the Interswitch Marketplace, open your project, and enable
    the missing API product.
    """

    def __init__(self, required_actions: list[str], available_actions: list[str]) -> None:
        self.required_actions = required_actions
        self.available_actions = available_actions

        if len(required_actions) == 1:
            scope_str = f"'{required_actions[0]}'"
        else:
            scope_str = " or ".join(f"'{s}'" for s in required_actions)

        self.message = (
            f"Your token does not have permission for this API. "
            f"Required: {scope_str}. "
            f"Go to the Interswitch Marketplace, open your project, "
            f"and enable the missing API product."
        )
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"InsufficientActionsError(required={self.required_actions!r})"


def check_api_actions(required: str | list[str], available: list[str]) -> None:
    """
    Check that at least one of the required scope actions is in available.

    Always OR logic — if any one of required is present, the check passes.
    If required is empty or None, the check is skipped.
    """
    if not required:
        return

    required_list = [required] if isinstance(required, str) else list(required)

    if any(action in available for action in required_list):
        logger.debug("Actions check passed (required=%s)", required_list)
        return

    logger.warning("Actions check failed. Required: %s. Available: %s", required_list, available)
    raise InsufficientActionsError(required_list, available)
