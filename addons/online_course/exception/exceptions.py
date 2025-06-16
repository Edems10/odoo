# exceptions.py
from odoo.exceptions import ValidationError


class CourseException(ValidationError):
    """Base exception for course-related errors."""

    pass


class EnrollmentError(CourseException):
    """Exception for enrollment-related errors."""

    pass


class CourseSecurityError(CourseException):
    """Exception for security-related errors."""

    pass


class CourseStateError(CourseException):
    """Exception for state transition errors."""

    pass
