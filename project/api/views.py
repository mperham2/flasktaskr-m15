# project/api/views.py

from functools import wraps
from datetime import date, datetime
from flask import flash, redirect, jsonify, session, url_for, Blueprint, make_response, abort, request
from flask.ext.restful import reqparse, abort, Resource, Api
from project import app, db
from project.models import Task

#######################
##### config   ########
#######################

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

#######################
### helper functions ###
#######################

# def login_required(test):
#     @wraps(test)
#     def wrap(*args, **kwargs):
#         if 'logged_in' in session:
#             return test(*args, **kwargs)
#         else:
#             flash('You need to login first.')
#             return redirect(url_for('users.login'))
#     return wrap

#######################
### routes ###
#######################

class TaskListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('task_id', type=int, help="that's some bullshit")
        self.reqparse.add_argument('name', type=str, required=True,
help="Name cannot be blank!")
        self.reqparse.add_argument('due_date', type=str)
        self.reqparse.add_argument('priority', type=int)
        self.reqparse.add_argument('status', type=int, help="that's some bullshit")
        super(TaskListAPI, self).__init__()

    def get(self):
        results = db.session.query(Task).limit(10).offset(0).all()
        json_results = []
        for result in results:
            data = {
                'task_id': result.task_id,
                'task name': result.name,
                'due date': str(result.due_date),
                'priority': result.priority,
                'posted date': str(result.posted_date),
                'status': result.status,
                'user id': result.user_id
                }
            json_results.append(data)

        return jsonify(items=json_results)

    def post(self):
        args = self.reqparse.parse_args()
        app.logger.debug(args)
        result = args
        new_task = Task(
            args['name'],
            datetime.strptime(args['due_date'], "%Y-%m-%d"),
            args['priority'],
            datetime.utcnow(),
            args['status'],
            '1'
        )
        db.session.add(new_task)
        db.session.commit()
        code = 200
        return make_response(jsonify(result), code)

class TaskAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('task_id', type=int)
        self.reqparse.add_argument('name', type=str)
        self.reqparse.add_argument('due_date', type=str)
        self.reqparse.add_argument('priority', type=str)
        self.reqparse.add_argument('status', type=int, help="that's some bullshit")
        super(TaskAPI, self).__init__()

    def get(self, task_id):
        result = db.session.query(Task).filter_by(task_id=task_id).first()
        if result:
            result = {
                'task_id': result.task_id,
                'task name': result.name,
                'due date': str(result.due_date),
                'priority': result.priority,
                'posted date': str(result.posted_date),
                'status': result.status,
                'user id': result.user_id
            }
            code = 200
        else:
            result = {"error": "Element does not exist"}
            code = 404
        return make_response(jsonify(result), code)

    def delete(self, task_id):
        task = db.session.query(Task).filter_by(task_id=task_id)
        if task.first():
            task.delete()
            db.session.commit()
            result = {"result": "task id {} deleted".format(task_id)}
            code = 200
        else:
            result = {"error": "Element does not exist"}
            code = 404
        return make_response(jsonify(result), code)

    def put(self, task_id):
        new_id = task_id
        result = db.session.query(Task).filter_by(task_id=new_id)
        if result.first():
            args = self.reqparse.parse_args()
            app.logger.debug("the parsed args are: ")
            app.logger.debug(args)
            for key, value in args.iteritems():
                if key == 'due_date':
                    value = datetime.strptime(value, "%Y-%m-%d")
                result.update({key: value})
            db.session.commit()
            task = result.first()
            result = {
                'task_id': task.task_id,
                'task name': task.name,
                'due date': str(task.due_date),
                'priority': task.priority,
                'posted date': str(task.posted_date),
                'status': task.status,
                'user id': task.user_id
            }
            code = 200
        else:
            result = {"error": "Element does not exist"}
            code = 404
        return make_response(jsonify(result), code)

##
## Actually setup the Api resource routing here
##

api.add_resource(TaskAPI, '/api/v1/tasks/<int:task_id>', endpoint='task')
api.add_resource(TaskListAPI, '/api/v1/tasks', endpoint='tasks')

