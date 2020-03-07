from flask import abort
from flask import Flask, jsonify
from flask import make_response
from flask import request

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'user1'
PASSWORD ='123'

HOST = '127.0.0.1'
PORT ='3306'
DATABASE = 'api'

SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
#'mysql+pymysql://user1:123@127.0.0.1:3306/api?charset=utf8'


app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)#创建
#映射到数据库中
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer,primary_key=True)#主键
    content = db.Column(db.String(200))
    status = db.Column(db.Boolean, default=True)
    addTime = db.Column(db.DateTime)
    stopTime = db.Column(db.DateTime)

#db.drop.all()
db.create_all()

#GET
@app.route('/api/v1.0/tasks', methods=['GET'])
def get_tasks():    #获取任务
    if request.args.get("status"):
        status = int(request.args.get("status"))
        print (request.args)
        if status == 1:
            a = Task.query.filter_by(status = 1).all()
            title = '已完成的任务'
            print ('已完成的任务',a)
        elif status == 0:
            title = '未完成的任务'
            a = Task.query.filter_by(status=0).all()
            print ('未完成的任务',a)
    else:
        title = '所有的任务'
        a = Task.query.all()
        print ('所有任务',a)

    ra = []
    for i in a:
        ra.append({"content": i.content,
                   "status": i.status,
                   "addTime": i.addTime,
                   "stopTime": i.stopTime
                   })
    return jsonify({'message': title, 'data': ra})

    # return jsonify([{'tasks': 'ok'}])

@app.route('/api/v1.0/tasks/count', methods=['GET'])
def get_task():
    if request.args.get("status"):
        status = int(request.args.get("status"))
        print (request.args)
        if status == 1:
            a = Task.query.filter_by(status = 1).count()
            title = '已完成的任务'
            print ('已完成的任务',a)
        elif status == 0:
            title = '未完成的任务'
            a = Task.query.filter_by(status=0).count()
            print ('未完成的任务',a)
    else:
        title = '所有的任务'
        a = Task.query.count()
        print ('所有任务',a)

    return jsonify({'message': title, 'status':'ok','data': {'数量':a}})

#404错误提示
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Not found'}), 404)


#POST
@app.route('/api/v1.0/newtasks', methods=['POST'])
def create_task():
    print (request.json)
    if not request.json or not 'content' in request.json:
        abort(400)
    task1 = Task(
        content= request.json['content'],
        status= request.json.get('status', ""),
        addTime= datetime.now())
    db.session.add(task1)
    db.session.commit()
    return jsonify({'status': 'ok'}), 201




# 修改指定任务的完成状态
# http://localhost:5000/api/v1.0/tasks/change
# {
#   "id":2,
#   "status":1
# }

@app.route('/api/v1.0/tasks/change', methods=['PUT'])
def update_task():
    if not request.json:
        print ('##1')
        abort(400)
    if 'id' in request.json and type(request.json['id']) != int or 'id' not in request.json:
        print ('##2')
        abort(400)
    if 'status' in request.json and type(request.json['status']) != int or 'status' not in request.json:
        print ('##3')
        abort(400)
    task_id = request.json['id']  # 获取到的任务id
    task_status = request.json['status']  # 获取到的任务状态
    a1 = Task.query.filter(Task.id == task_id).first()  #查询获取的id是否存在
    if not a1:
        abort(404)
    #将获取到的任务的状态改为获取到的状态
    a1.status = task_status
    if task_status == 1:    #任务状态变更为已完成，则表示该任务截止。添加任务截止时间
        a1.stopTime = datetime.now()
    db.session.commit()
    return jsonify({'status': 'ok'})

#更改所有任务的状态 {'status':1}
#http://localhost:5000/api/v1.0/tasks/changeall
# {'status':1}
@app.route('/api/v1.0/tasks/changeall', methods=['PUT'])
def update_all_task():
    if not request.json:
        print ('##1')
        abort(400)
    if 'status' in request.json and type(request.json['status']) != int or 'status' not in request.json:
        print ('##3')
        abort(400)
    task_status = request.json['status']  # 获取到的任务状态
    a1 = Task.query.all()  #查询获取的id是否存在
    if not a1:
        print('当前数据库没有任务')
        abort(404)
    #将获取到的任务的状态改为获取到的状态
    for i in a1:
        i.status = task_status
    db.session.commit()
    return jsonify({'status': 'ok'})


#DELETE

@app.route('/api/v1.0/tasks/delete', methods=['DELETE'])
def delete_task():
    if not request.args:
        print ('##1')
        abort(400)
    if 'status' in request.args  :
        task_status = request.args['status']
        a1 = Task.query.filter(Task.status == task_status).all()
    elif 'id'  in request.args :
        task_id = request.args['id']
        a1 = Task.query.filter(Task.id == task_id).all()
    elif 'all'  in request.args:
        a1 = Task.query.all()
    else:
        print ('参数错误')
        abort(404)

    if not a1:
        print ('没有该任务')
        abort(404)
    for i in a1:
        db.session.delete(i)

    db.session.commit()

    return jsonify({'status': 'ok'})



if __name__ == '__main__':
    app.run(debug=True)