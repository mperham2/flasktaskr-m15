# test.py

import os
import unittest

from views import app, db
from config import basedir
from models import User

TEST_DB = 'test.db'

class AllTests(unittest.TestCase):

    #############################
    ##### setup and teardown ####
    #############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # executed after each test
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
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def new_user1_login(self):
        self.create_user('Michael', 'mike@mike.com', 'python')
        self.login('Michael', 'python')

    def create_task(self):
        return self.app.post('add/', data=dict(
                name='Go to the bank',
                due_date='02/05/2014',
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

if __name__ == "__main__":
    unittest.main()

