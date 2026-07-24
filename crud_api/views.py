import json
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt


tasks = [
    {"id":1, "title":"Learn Django", "done":False},
    {"id":2, "title":"Build crud api", "done":False},
    {"id":3, "title":"Push to Github", "done":False}
]

@csrf_exempt
def task_list(request):
    #Reading the task
    if request.method == 'GET':
        return JsonResponse(tasks , safe=False)

    #Adding or Creating Task
    elif request.method == "POST":
        new_data = json.loads(request.body)
        title = new_data.get('title')
        
        if not title:
            return JsonResponse({"error": "Title is missing."}, status= 400)
 
        new_task = {
            "id": 4,
            "title": title,
            "done": False
        }

        #Adding global list and return output
        tasks.append(new_task)
        return JsonResponse(new_task,  status = 201)
    
@csrf_exempt
def task_detail(request, task_id):
    #Finding Task
    target_task = None
    for task in tasks:
        if task["id"] == task_id:
            target_task = task
            break

    # validation
    if not target_task:
        return JsonResponse({"error":"Task not found."}, status=404)

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