from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.status import *
import pyodbc
import json
import uvicorn

app = FastAPI()

server = 'bts-dm.database.windows.net'
database = 'bts-dm'
username = 'devmaks'
password = '121212Web'
driver= 'ODBC Driver 17 for SQL Server'
conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

def generate_task(cursor):
    for item in cursor:
        task = {
            'id': item.id,
            'type': item.type,
            'title': item.title,
            'description': item.description,
            'priority': item.priority,
            'status': item.status
        }
    return task;

def generate_tasks_list(cursor):
    tasksList = []
    for task in cursor:
        task = {
            'id' : task.id,
            'type' : task.type,
            'title' : task.title,
            'description' : task.description,
            'priority' : task.priority,
            'status' : task.status}
        tasksList.append(task)
    return tasksList;

@app.get("/tasks")
def get_tasks():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dbo.Tasks')
    tasksList = generate_tasks_list(cursor)
    return JSONResponse(json.dumps(tasksList), HTTP_200_OK)


@app.get("/task/{task_id}")
def get_task(task_id: int):
    cursor = conn.cursor()
    query = "SELECT * FROM dbo.Tasks WHERE id = %s" % task_id;
    cursor.execute(query)

    if cursor.rowcount == 0:
        return JSONResponse(status_code=HTTP_404_NOT_FOUND)
    
    task = generate_task(cursor)
    return JSONResponse(json.dumps(task), HTTP_200_OK)

@app.post("/create-task")
def create_task(taskType: str, taskTitle: str, taskDescription: str, taskPriority: int):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dbo.Tasks')
    tasksList = generate_tasks_list(cursor)

    if not tasksList:
        id = 1
    else:
        id = tasksList[-1]['id'] + 1

    cursor.execute("INSERT INTO dbo.Tasks(id, type, title, description, priority, status) VALUES (?, ?, ?, ?, ?, ?)", 
        id, taskType, taskTitle, taskDescription, taskPriority, 1)
    cursor.commit()

    return JSONResponse(status_code=HTTP_201_CREATED)

@app.post("/save-task/{task_id}")
def save_task(task_id: int, taskType: str, taskTitle: str, taskDescription: str, taskPriority: int, taskStatus: int):

    cursor = conn.cursor()
    cursor.execute("UPDATE Tasks SET type = ?, title = ?, description = ?, priority = ?, status = ? WHERE id = ?", 
        taskType, taskTitle, taskDescription, taskPriority, taskStatus, task_id)
    cursor.commit()

    return JSONResponse(status_code=HTTP_200_OK)