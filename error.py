#!/usr/bin/env python3


class MapValidationError(Exception):
    """Raised when a Map object fails its consistency checks."""
    pass


class ParserError(Exception):
    """Raised when the input file violates the expected format."""


class PathNotFoundError(Exception):
    """Raised when no valid path exists between two zones."""
