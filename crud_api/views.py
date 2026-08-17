import json
import sqlite3
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt

def init_db():
    #Connecting to SQLite
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    # Creating table if it doesn't exits.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    ''')

    # Checking if table is empty
    cursor.execute('SELECT COUNT(*) FROM tasks')
    count = cursor.fetchone()[0]


    if count == 0:
        example_tasks = [
            ("Learn Django", 0),
            ("Build crud api", 0),
            ("Push to Github", 0)
        ]

        # (?,?) prevents SQL injection hackers.
        cursor.executemany('''
            INSERT INTO tasks ( title, done) VALUES (?, ?)
        ''', example_tasks)
        conn.commit()

    conn.close()

init_db()

@csrf_exempt
def task_list(request):
    #Reading the task
    if request.method == 'GET':
        conn = sqlite3.connect('tasks.db')

        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Executing raw SQL query to get every task.
        cursor.execute('SELECT * FROM tasks')
        rows = cursor.fetchall()

        # Translating SQL row into Python List of dictionaries.
        tasks_list = []
        for row in rows:
            tasks_list.append({
                "id" : row["id"],
                "title" : row["title"],
                "done" : bool(row["done"]) #Converts 0/1 integer back to True/False
            })

        conn.close()
        return JsonResponse(tasks_list, safe=False)

    

    #Adding or Creating Task
    elif request.method == "POST":
        new_data = json.loads(request.body)
        title = new_data.get('title')

        # Validatinf: missing title returns 400
        if not title:
            return JsonResponse({"error": "Title is missing."}, status= 404)

        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO tasks(title, done) VALUES (?,?)', (title, False))

        # Sving the changes.
        conn.commit()

        # Get tje ID that Sqlite automatically created for us
        new_id = cursor.lastrowid
        conn.close()

        # Return 201 Created response.        
        new_task = {
            "id": new_id,
            "title": title,
            "done": False
        }

        return JsonResponse(new_task,  status = 201)
    
@csrf_exempt
def task_detail(request, task_id):
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return JsonResponse({"error": "Task not found."}, status = 404)

    # Translate the SQL row into a dictionary
    task = {
        "id" : row["id"],
        "title" : row["title"],
        "done" : bool(row["done"])
    }

    if request.method == 'DELETE':
        tasks.remove(target_task)
        return JsonResponse({}, status = 204)


    elif request.method == 'PUT':
        new_data = json.loads(request.body)
        new_title = new_data.get("title", target_task["title"])

        if not new_title:
            return JsonResponse({"error":"Title cannot be empty."},  status=400)
        
        target_task["title"] = new_title
        target_task["done"] = new_data.get("done", target_task["done"])

        return JsonResponse(target_task, status=200)

#Adding Swagger UI
def openapi_schema(request):
    schema = {
        "openapi": "3.0.0",
        "info": {"title": "Task CRUD API", "version": "1.0.0"},
        "paths": {
            "/tasks/": {
                "get": {
                    "summary": "List all tasks", 
                    "responses": {"200": {"description": "OK"}}
                },
                "post": {
                    "summary": "Create a task",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string", "example": "Learn Swagger UI"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "Created"}, "400": {"description": "Bad Request"}}
                }
            },
            "/tasks/{task_id}/": {
                "put": {
                    "summary": "Update a task",
                    "parameters": [{"name": "task_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string", "example": "Updated task title"},
                                        "done": {"type": "boolean", "example": True}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}, "404": {"description": "Not Found"}}
                },
                "delete": {
                    "summary": "Delete a task",
                    "parameters": [{"name": "task_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"204": {"description": "No Content"}, "404": {"description": "Not Found"}}
                }
            }
        }
    }
    return JsonResponse(schema)

def docs(request):
    # This serves the Swagger UI web page
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Swagger UI</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
        <script>
            window.onload = () => {
                window.ui = SwaggerUIBundle({
                    url: '/openapi.json',  // Points to the schema view we just made
                    dom_id: '#swagger-ui',
                });
            };
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)