# tests/test_api.py

import os
import unittest
from datetime import date

from project import app, db
from project._config import basedir
from project.models import Task

TEST_DB = 'test.db'

class APITests(unittest.TestCase):

    ############################
    ### setup and teardown #####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ##############################
    ###### helper methods ########
    ##############################

    def add_tasks(self):
        db.session.add(
            Task(
                 "Run around in circles",
                 date(2015, 10, 22),
                 10,
                 date(2915, 10, 5),
                 1,
                 1
            )
        )
        db.session.commit()

        db.session.add(
            Task(
                 "Purchase Real Python",
                 date(2016, 2, 23),
                 10,
                 date(2016, 2, 7),
                 1,
                 1
                 )
            )
        db.session.commit()

    def task_dict(self):
        return dict(name = "Purchase Real Python Again",
        due_date = date(2016, 2, 23),
        priority = 10,
        posted_date = date(2016, 2, 7),
        status = 1,
        user_id = 1,
        task_id = 1)

    def bad_task_dict(self):
        return dict(
        due_date = date(2016, 2, 23),
        priority = 10,
        posted_date = date(2016, 2, 7),
        status = "qqqq",
        user_id = 1)
    ####################
    ### tests ##########
    ####################

    def test_collection_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks', follow_redirects = True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn('Run around in circles', response.data)
        self.assertIn('Purchase Real Python', response.data)

    def test_resource_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/2', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn('Purchase Real Python', response.data)
        self.assertNotIn('Run around in circles', response.data)

    def test_invalid_resource_endpoint_returns_error(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/209', follow_redirects=True)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn('Element does not exist', response.data)

    def test_process_aborts_if_task_doesnt_exist_when_adding(self):
        d = self.task_dict()
        response = self.app.put('/api/v1/tasks/209', data=d)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn('Element does not exist', response.data)

    def test_can_update_tasks_via_api_put(self):
        self.add_tasks()
        d = self.task_dict()
        response = self.app.put('/api/v1/tasks/1', data=d, follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn('Purchase Real Python Again', response.data)

    def test_can_post_tasks_via_api_post(self):
        d = dict(name = "Purchase Real Python Again",
        due_date = date(2016, 2, 23),
        priority = 10,
        posted_date = date(2016, 2, 7),
        status = 1,
        user_id = 1)
        response = self.app.post('/api/v1/tasks', data=d, follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn('Purchase Real Python Again', response.data)

    def test_can_delete_tasks_via_api_delete(self):
        self.add_tasks()
        response = self.app.delete('/api/v1/tasks/1', follow_redirects=True)
        self.assertIn('task id 1 deleted', response.data)
        response = self.app.get('/api/v1/tasks/1', follow_redirects=True)
        self.assertEquals(response.status_code, 404)
        self.assertIn('Element does not exist', response.data)

    if __name__ == "__main__":
        unittest.main()
