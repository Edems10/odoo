from ..static.constants import CourseConstants

class NotificationFactory:
    """Factory for creating notifications."""
    
    @staticmethod
    def _create_notification(title, message, notification_type='success'):
        """Base notification creation."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': notification_type,
            }
        }
    
    @staticmethod
    def create_enrollment_success(course_name):
        """Create enrollment success notification."""
        return NotificationFactory._create_notification(
            CourseConstants.Messages.ENROLLMENT_SUCCESS,
            f'You have been enrolled in "{course_name}"',
            'success'
        )
    
    @staticmethod
    def create_unenrollment_success(course_name):
        """Create unenrollment success notification."""
        return NotificationFactory._create_notification(
            CourseConstants.Messages.UNENROLLMENT_SUCCESS,
            f'You have been unenrolled from "{course_name}"',
            'info'
        )
