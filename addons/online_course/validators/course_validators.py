from odoo import _
from ..static.constants import CourseConstants
from ..exception.exceptions import EnrollmentError, CourseStateError

class BaseValidator:
    """Base validator class."""
    
    def validate(self, course, user=None):
        """Override in subclasses."""
        raise NotImplementedError

class EnrollmentValidator:
    """Validates enrollment requirements."""
    
    def __init__(self):
        self.validators = [
            CourseStateValidator(),
            TeacherEnrollmentValidator(),
            DuplicateEnrollmentValidator(),
        ]
    
    def validate(self, course, user):
        """Run all enrollment validations."""
        for validator in self.validators:
            validator.validate(course, user)

class CourseStateValidator(BaseValidator):
    """Validates course state for enrollment."""
    
    def validate(self, course, user=None):
        if course.state != CourseConstants.States.PUBLISHED:
            raise EnrollmentError(_(CourseConstants.Messages.COURSE_NOT_ACCEPTING))

class TeacherEnrollmentValidator(BaseValidator):
    """Prevents teachers from enrolling in their own courses."""
    
    def validate(self, course, user):
        if user == course.teacher_id:
            raise EnrollmentError(_(CourseConstants.Messages.TEACHER_CANNOT_ENROLL))

class DuplicateEnrollmentValidator(BaseValidator):
    """Prevents duplicate enrollments."""
    
    def validate(self, course, user):
        if user in course.student_ids:
            raise EnrollmentError(_(CourseConstants.Messages.ALREADY_ENROLLED))

class PriceValidator(BaseValidator):
    """Validates course pricing."""
    
    def validate(self, course, user=None):
        if course.price < CourseConstants.MIN_PRICE:
            raise CourseStateError(_(CourseConstants.Messages.NEGATIVE_PRICE_ERROR))
