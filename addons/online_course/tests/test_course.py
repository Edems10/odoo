# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestCourse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestCourse, cls).setUpClass()
        cls.teacher = cls.env["res.users"].create({
            "name": "Teacher User",
            "login": "teacher@example.com",
        })
        cls.student1 = cls.env["res.users"].create({
            "name": "Student One",
            "login": "student1@example.com",
        })
        
    def test_course_creation(self):
        """Test basic course creation."""
        course = self.env["online.course"].create({
            "name": "Python Basics",
            "teacher_id": self.teacher.id,
        })
        self.assertEqual(course.name, "Python Basics")
        self.assertEqual(course.state, "draft")

    def test_teacher_cannot_be_student(self):
        """Test constraint: teacher cannot be enrolled as student."""
        course = self.env["online.course"].create({
            "name": "Test Course",
            "teacher_id": self.teacher.id,
        })
        
        with self.assertRaises(ValidationError):
            course.write({
                "student_ids": [(4, self.teacher.id)]
            })

    def test_student_enrollment(self):
        """Test adding students to course."""
        course = self.env["online.course"].create({
            "name": "Web Development",
            "teacher_id": self.teacher.id,
        })
        
        # Add student
        course.write({
            "student_ids": [(4, self.student1.id)]
        })
        self.assertEqual(len(course.student_ids), 1)
        self.assertIn(self.student1, course.student_ids)

    def test_course_name_required(self):
        """Test that course name is required."""
        with self.assertRaises(Exception):
            with self.env.cr.savepoint():
                self.env["online.course"].create({
                    "teacher_id": self.teacher.id,
                    # Missing name should cause error
                })

