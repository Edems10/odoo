class CourseConstants:
    """Course-related constants and configuration."""

    class States:
        DRAFT = "draft"
        PUBLISHED = "published"
        CLOSED = "closed"
        ARCHIVED = "archived"

        ALL = [
            (DRAFT, "Draft"),
            (PUBLISHED, "Published - Open for Enrollment"),
            (CLOSED, "Published - Enrollment Closed"),
            (ARCHIVED, "Archived - Course Ended"),
        ]

    class Messages:
        ENROLLMENT_SUCCESS = "Enrollment Successful! 🎉"
        UNENROLLMENT_SUCCESS = "Unenrolled Successfully"
        TEACHER_CANNOT_ENROLL = "Teachers cannot enroll in their own courses."
        ALREADY_ENROLLED = "You are already enrolled in this course."
        NOT_ENROLLED = "You are not enrolled in this course."
        COURSE_NOT_ACCEPTING = "This course is not currently accepting enrollments."
        NEGATIVE_PRICE_ERROR = "Course price cannot be negative."
        CANNOT_PUBLISH_NEGATIVE = "Cannot publish course with negative price."

    class Security:
        TEACHER_GROUP = "online_course.group_online_course_teacher"
        STUDENT_GROUP = "online_course.group_online_course_student"
        ADMIN_GROUP = "base.group_system"

    DEFAULT_PRICE = 100.0
    MIN_PRICE = 0.0
