# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCourse(TransactionCase):

    def setUp(self):
        super(TestCourse, self).setUp()
        # Create a user to be a teacher and a student
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser@example.com',
        })

    def test_teacher_cannot_be_student(self):
        """Test that a teacher cannot be a student of the same course."""
        with self.assertRaises(ValidationError):
            self.env['online.course'].create({
                'name': 'Test Course for Constraint',
                'teacher_id': self.test_user.id,
                'student_ids': [(4, self.test_user.id)], # Add the teacher as a student
            })

    def test_course_creation(self):
        """Test basic course creation."""
        course = self.env['online.course'].create({
            'name': 'Introduction to Testing',
            'teacher_id': self.test_user.id,
        })
        self.assertEqual(course.name, 'Introduction to Testing')
        self.assertEqual(course.state, 'draft')
        
        
    def test_price_validation(self):
        """Test price validation constraints."""
        with self.assertRaises(ValidationError):
            self.env['online.course'].create({
                'name': 'Invalid Course',
                'teacher_id': self.test_user.id,
                'price': -100.0,  # Negative price should fail
            })

    def test_course_publish_workflow(self):
        """Test course publishing workflow."""
        course = self.env['online.course'].create({
            'name': 'Test Course',
            'teacher_id': self.test_user.id,
            'price': 50.0,
        })
        course.action_publish()
        self.assertEqual(course.state, 'published')

