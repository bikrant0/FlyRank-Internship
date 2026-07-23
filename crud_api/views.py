import json
from django.http import JsonResponse
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
