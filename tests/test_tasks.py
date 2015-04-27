# test.py

import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import Task, User

TEST_DB = 'test.db'

class AllTests(unittest.TestCase):

    #############################
    ##### setup and teardown ####
    #############################

        # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    # executed after to each test
    def tearDown(self):
        db.drop_all()


    # helper methods
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post('register/', data=dict(
                             name=name, email=email,
                             password=password,
                             confirm=confirm), follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

    def create_admin_user(self):
        new_user = User(name='Superman', email='admin@realpython.com', password=bcrypt.generate_password_hash('allpowerful'), role='admin')
        db.session.add(new_user)
        db.session.commit()

    def new_user1_login(self):
        self.create_user('Michael', 'mike@mike.com', 'python')
        self.login('Michael', 'python')

    def create_task(self):
        return self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date='02/05/2015',
            priority='1',
            posted_date='02/04/2015',
            status='1'
        ), follow_redirects=True)

    def create_task2(self):
        return self.app.post('add/', data=dict(
                name='Go to the bank again',
                due_date='02/05/2015',
                priority='1',
                posted_date='02/04/2014',
                status='1'
                ), follow_redirects=True)

    def goto_and_make_task(self):
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()

    def test_users_can_add_tasks(self):
        self.new_user1_login()
        self.app.get('tasks/', 'python')
        response = self.create_task()
        self.assertIn(
            'New entry was successfully posted. Thanks.', response.data
            )

    def test_logged_in_users_can_access_tasks_page(self):
        self.register(
                'Fletcher', "fletcher@realpython.com", 'python101', 'python101')
        self.login('Fletcher', 'python101')
        response = self.app.get("tasks/")
        self.assertEquals(response.status_code, 200)
        self.assertIn('Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn('You need to login first.', response.data)

    def test_users_can_complete_tasks(self):
        self.new_user1_login()
        self.goto_and_make_task()
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn('The task was marked as complete. Nice.', response.data)

    def test_users_can_delete_tasks(self):
        self.new_user1_login()
        self.goto_and_make_task()
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn('The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.new_user1_login()
        self.goto_and_make_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            'The task was marked as complete. Nice.', response.data
        )
        self.assertIn('You can only update tasks that belong to you.', response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.new_user1_login()
        self.goto_and_make_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn(
            'The task was marked as complete. Nice.', response.data
        )
        self.assertIn('You can only delete tasks that belong to you.', response.data)

    def test_admin_uesrs_can_complete_tasks_that_are_not_created_by_them(self):
        self.new_user1_login()
        self.goto_and_make_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn('You can only update tasks that belong to you.', response.data)

    def test_admin_uesrs_can_delete_tasks_that_are_not_created_by_them(self):
        self.new_user1_login()
        self.goto_and_make_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn('You can only delete tasks that belong to you.', response.data)

    def test_task_template_displays_logged_in_username(self):
        self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')
        self.login('Fletcher', 'python101')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'Fletcher', response.data)

    def test_task_template_displays_logged_in_username_second(self):
        self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        self.logout()
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn('Michael', response.data)

    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        response = self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        self.assertNotIn(b'Mark as complete', response.data)
        self.assertNotIn(b'Delete', response.data)

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'complete/2/', response.data)

    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/1/', response.data)
        self.assertIn(b'delete/1/', response.data)
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'delete/2/', response.data)

    def test_users_can_mark_complete_tasks_incomplete(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn(b'incomplete/1/', response.data)

    def test_marking_complete_tasks_incomplete_puts_them_back_open(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.app.get("complete/1/", follow_redirects=True)
        response = self.app.get("incomplete/1/", follow_redirects=True)
        self.assertIn(b'complete/1/', response.data)



if __name__ == "__main__":
    unittest.main()

