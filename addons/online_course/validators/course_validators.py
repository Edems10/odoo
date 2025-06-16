# -*- coding: utf-8 -*-
from typing import List, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from odoo import _
from odoo.exceptions import ValidationError

if TYPE_CHECKING:
    from ..models.res_users import ResUsers
    from ..models.course import Course

from ..static.constants import CourseConstants


class BaseValidator(ABC):
    """Abstract base validator class"""

    @abstractmethod
    def validate(self, course: "Course", user: Optional["ResUsers"] = None) -> None:
        """
        Override in subclasses to implement validation logic.

        Args:
            course: The course to validate.
            user: Optional user for validation context.

        Raises:
            ValidationError: If validation fails.
        """
        raise NotImplementedError


class EnrollmentValidator:
    """Validates enrollment requirements"""

    def __init__(self) -> None:
        """Initialize enrollment validator with all required validators."""
        self.validators: List[BaseValidator] = [
            CourseStateValidator(),
            TeacherEnrollmentValidator(),
            DuplicateEnrollmentValidator(),
        ]

    def validate(self, course: "Course", user: "ResUsers") -> None:
        """
        Run all enrollment validations.

        Args:
            course: The course to validate enrollment for.
            user: The user attempting to enroll.

        Raises:
            ValidationError: If any validation fails.
        """
        validator: BaseValidator
        for validator in self.validators:
            validator.validate(course, user)


class CourseStateValidator(BaseValidator):
    """Validates course state for enrollment."""

    def validate(self, course: "Course", user: Optional["ResUsers"] = None) -> None:
        """
        Validate that course is in correct state for enrollment.

        Args:
            course: The course to validate.
            user: Optional user (not used in this validator).

        Raises:
            ValidationError: If course is not accepting enrollments.
        """
        if course.state != CourseConstants.States.PUBLISHED:
            raise ValidationError(_(CourseConstants.Messages.COURSE_NOT_ACCEPTING))


class TeacherEnrollmentValidator(BaseValidator):
    """Prevents teachers from enrolling in their own courses."""

    def validate(self, course: "Course", user: Optional["ResUsers"] = None) -> None:
        """
        Validate that teacher is not trying to enroll in their own course.

        Args:
            course: The course to validate.
            user: The user attempting to enroll.

        Raises:
            ValidationError: If teacher attempts to enroll in own course.
        """
        if user and user == course.teacher_id:
            raise ValidationError(_(CourseConstants.Messages.TEACHER_CANNOT_ENROLL))


class DuplicateEnrollmentValidator(BaseValidator):
    """Prevents duplicate enrollments."""

    def validate(self, course: "Course", user: Optional["ResUsers"] = None) -> None:
        """
        Validate that user is not already enrolled.

        Args:
            course: The course to validate.
            user: The user attempting to enroll.

        Raises:
            ValidationError: If user is already enrolled.
        """
        if user and user in course.student_ids:
            raise ValidationError(_(CourseConstants.Messages.ALREADY_ENROLLED))


class PriceValidator(BaseValidator):
    """Validates course pricing"""

    def validate(self, course: "Course", user: Optional["ResUsers"] = None) -> None:
        """
        Validate course pricing.

        Args:
            course: The course to validate pricing for.
            user: Optional user (not used in this validator).

        Raises:
            ValidationError: If price is invalid.
        """
        if course.price < CourseConstants.MIN_PRICE:
            raise ValidationError(_(CourseConstants.Messages.NEGATIVE_PRICE_ERROR))


class UnenrollmentValidator:
    """Validates unenrollment requirements."""

    def __init__(self) -> None:
        """Initialize unenrollment validator."""
        self.validators: List[BaseValidator] = [
            EnrollmentExistsValidator(),
        ]

    def validate(self, course: "Course", user: "ResUsers") -> None:
        """
        Run all unenrollment validations.

        Args:
            course: The course to validate unenrollment for.
            user: The user attempting to unenroll.

        Raises:
            ValidationError: If any validation fails.
        """
        validator: BaseValidator
        for validator in self.validators:
            validator.validate(course, user)


class EnrollmentExistsValidator(BaseValidator):
    """Validates that user is actually enrolled before allowing unenrollment."""

    def validate(self, course: "Course", user: Optional["ResUsers"] = None) -> None:
        """
        Validate that user is enrolled in the course.

        Args:
            course: The course to validate.
            user: The user attempting to unenroll.

        Raises:
            ValidationError: If user is not enrolled.
        """
        if user and user not in course.student_ids:
            raise ValidationError(_(CourseConstants.Messages.NOT_ENROLLED))
