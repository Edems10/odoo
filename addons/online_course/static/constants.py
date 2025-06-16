# -*- coding: utf-8 -*-
from typing import List, Tuple, Final


class CourseConstants:
    """Course-related constants and configuration with type hints."""

    class States:
        """Course state constants."""

        DRAFT: Final[str] = "draft"
        PUBLISHED: Final[str] = "published"
        CLOSED: Final[str] = "closed"
        ARCHIVED: Final[str] = "archived"

        ALL: Final[List[Tuple[str, str]]] = [
            (DRAFT, "Draft"),
            (PUBLISHED, "Published - Open for Enrollment"),
            (CLOSED, "Published - Enrollment Closed"),
            (ARCHIVED, "Archived - Course Ended"),
        ]

    class Messages:
        """User-facing message constants."""

        ENROLLMENT_SUCCESS: Final[str] = "Enrollment Successful! 🎉"
        UNENROLLMENT_SUCCESS: Final[str] = "Unenrolled Successfully"
        TEACHER_CANNOT_ENROLL: Final[str] = (
            "Teachers cannot enroll in their own courses."
        )
        ALREADY_ENROLLED: Final[str] = "You are already enrolled in this course."
        NOT_ENROLLED: Final[str] = "You are not enrolled in this course."
        COURSE_NOT_ACCEPTING: Final[str] = (
            "This course is not currently accepting enrollments."
        )
        NEGATIVE_PRICE_ERROR: Final[str] = "Course price cannot be negative."
        CANNOT_PUBLISH_NEGATIVE: Final[str] = (
            "Cannot publish course with negative price."
        )

    class Security:
        """Security group constants."""

        TEACHER_GROUP: Final[str] = "online_course.group_online_course_teacher"
        STUDENT_GROUP: Final[str] = "online_course.group_online_course_student"
        ADMIN_GROUP: Final[str] = "base.group_system"

    DEFAULT_PRICE: Final[float] = 100.0
    MIN_PRICE: Final[float] = 0.0
