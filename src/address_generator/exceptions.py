"""Custom exception types."""


class AddressGeneratorError(Exception):
    """Base exception for project-specific failures."""


class ConfigurationError(AddressGeneratorError):
    """Raised when configuration input is malformed or incomplete."""


class ExplorerApiError(AddressGeneratorError):
    """Raised when an external explorer returns an invalid response."""
