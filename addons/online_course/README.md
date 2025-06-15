# Online Course Management Module

This module allows for the management of online courses, teachers, and students within Odoo.

## Features

-   Create and manage courses with details like price, teacher, and description.
-   Assign students to courses.
-   Workflow for courses: Draft, Published, Archived.
-   Kanban view with color-coding for course status.
-   Smart button on the User form to quickly see courses taught by them.

## Installation

1.  Place this module directory (`online_course`) into your Odoo addons path.
2.  Restart the Odoo server.
3.  Navigate to **Apps** in your Odoo instance.
4.  Click on **Update Apps List**.
5.  Search for "Online Courses" and click **Install**.

## Running Tests

To run the unit tests for this module, start your Odoo server with the following command:

```
docker-compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d test_db --test-tags /online_course --stop-after-init -i online_course
```

