from flask import Flask, render_template, request, redirect, url_for, jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# named after name of file
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jlf:myPassword@localhost:5432/todoapp'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

##childe
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

##parent table
class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    #childen name = db.relationship('Childclass', backref='customized parent reference'))
    todos = db.relationship('Todo', backref='todoparent', lazy=True)
    

# db.create_all()
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
        # body['completed'] = todo.completed
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        return jsonify(body)

# route that complete an item
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

# route that delete an item
@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

# route the page to the list_id
@app.route('/todolists/<todolist_id>')
def get_todo_list(todolist_id):
    return render_template('index.html', 
    data=Todo.query.filter_by(todolist_id=todolist_id).order_by('id').all())
    # return render_template('index.html', data=Todo.query.all())

# route that listens to homepage
@app.route('/')
def index():
    return redirect(url_for('get_todo_list'), todolist_id = 1)

if __name__ == '__main__': 
   app.run(host="127.0.0.1")