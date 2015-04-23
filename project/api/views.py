# project/api/views.py

from functools import wraps
from flask import flash, redirect, jsonify, session, url_for, Blueprint, make_response, abort
from flask.ext.restful import reqparse, abort, Resource, Api
from project import app, db
from project.models import Task

#######################
##### config   ########
#######################

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)


###########################
##### reqparse formats ####
###########################

# parser = reqparse.RequestParser()
# parser.add_argument('task_id', type=int)
# parser.add_argument('name', type=str)
# parser.add_argument('due_date', type=str)
# parser.add_argument('priority', type=int)
# parser.add_argument('status', type=int)

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

# def open_tasks():
#     return db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())

# def closed_tasks():
#     return db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())

# def abort_if_task_doesnt_exist(task_id):
#     result = db.session.query(Task).filter_by(task_id=task_id).first()
#     if not result:
#         abort(404, message="Element does not exist")

def abort_if_doesnt_exist(task_id):
    result = db.session.query(Task).filter_by(task_id=task_id).first()
    if result:
        return result
    else:
        abort(404, message="Element does not exist")

#######################
### routes ###
#######################

class TaskListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('task_id', type=int, location = 'json')
        self.reqparse.add_argument('name', type=str, location = 'json')
        self.reqparse.add_argument('due_date', location = 'json')
        self.reqparse.add_argument('priority', type=int, location = 'json')
        self.reqparse.add_argument('status', type=int, location = 'json')
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
        error = None
        args = parser.parse_args()
        new_task = Task(
            args['name'],
            args['due_date'],
            args['priority'],
            datetime.datetime.utcnow(),
            args['status'],
            args['user_id']
        )
        db.session.add(new_task)
        db.session.commit()
        # code = 200
        # else:
        #     result = {"error": error}
        #     code = 404
        return make_response(jsonify(result), code)

class TaskAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('task_id', type=int, location = 'json')
        self.reqparse.add_argument('name', type=str, location = 'json')
        self.reqparse.add_argument('due_date', location = 'json')
        self.reqparse.add_argument('priority', type=int, location = 'json')
        self.reqparse.add_argument('status', type=int, location = 'json')
        super(TaskAPI, self).__init__()

    def get(self, task_id):
        result = abort_if_doesnt_exist(task_id)
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
        result = abort_if_doesnt_exist(task_id)
        if result:
            task = db.session.query(Task).filter_by(task_id=task_id).first()
            task.delete()
            db.session.commit()
            code = 200
        else:
            result = {"error": "Element does not exist"}
            code = 404
        return make_response(jsonify(result), code)

    def put(self, task_id):
        result = abort_if_doesnt_exist(task_id)
        if result:
            task = db.session.query(Task).filter_by(task_id=task_id).first()
            if len(task) == 0:
                abort(404)
            args = parser.parse_args()
            for key, value in args.iteritems():
                task.update({key: value})
            db.session.commit()
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

