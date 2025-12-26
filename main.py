from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import datetime
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore

# Firebase and Firestore setup
app = FastAPI()
firestore_db = firestore.Client()
firebase_request_adapter = requests.Request()

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

# Firebase token validation
def validate_firebase_token(id_token):
    if not id_token:
        return None
    try:
        return google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    except ValueError:
        return None
    
# Validate the token and get user information
def is_user_creator(user_id, board_id):
    board_doc = firestore_db.collection("taskBoards").document(board_id).get()
    if board_doc.exists:
        return board_doc.to_dict().get("createdBy") == user_id
    return False

# Get the email of a user from their UID
def get_email_from_uid(uid):
    users_query = firestore_db.collection("users").where("user_id", "==", uid).limit(1).stream()
    for user in users_query:
        return user.id  
    return "Unknown"

# Check if a board has tasks
def board_has_tasks(board_id):
    tasks = firestore_db.collection("taskBoards").document(board_id).collection("tasks").stream()
    return len(list(tasks)) > 0

# Check if a board has non-owning users
def has_non_owning_users(board_id, user_id):
    users_query = firestore_db.collection("users").where("boards", "array_contains", board_id).stream()
    for user in users_query:
        if user.id != user_id:  
            return True
    return False

# Display the main page with boards and tasks
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    boards = []
    shared_boards = []
    if user_token:
        user_id = user_token.get("user_id")
        user_email = user_token.get("email")
        user_ref = firestore_db.collection("users").document(user_email)
        user_doc = user_ref.get()
        if not user_doc.exists:
            user_ref.set({"boards": [], "user_id": user_id})
        user_data = user_doc.to_dict() if user_doc.exists else {"boards": []}
        board_ids = user_data.get("boards", [])
        for board_id in board_ids:
            board_doc = firestore_db.collection("taskBoards").document(board_id).get()
            if board_doc.exists:
                board_data = board_doc.to_dict()
                creator_id = board_data.get("createdBy")
                creator_email = get_email_from_uid(creator_id)
                is_creator = creator_id == user_id
                board_info = {
                    "id": board_id,"title": board_data.get("title"),"description": board_data.get("description", ""),"is_creator": is_creator,"creator_email": creator_email,"tasks": []
                }
                task_docs = firestore_db.collection("taskBoards").document(board_id).collection("tasks").stream()
                for task in task_docs:
                    task_data = task.to_dict()
                    task_creator_email = get_email_from_uid(task_data.get("createdBy"))
                    board_info["tasks"].append({
                        "id": task.id,"title": task_data.get("title"),"due_date": task_data.get("due_date"),"completed": task_data.get("completed", False),"assignees": task_data.get("assignees", []),"creator_email": task_creator_email
                    })
                if is_creator:
                    boards.append(board_info)
                else:
                    shared_boards.append(board_info)
    return templates.TemplateResponse("main.html", {
        "request": request,"user_token": user_token,"boards": boards,"shared_boards": shared_boards
    })

#creation of a new board
@app.get("/create-board-form", response_class=HTMLResponse)
async def show_create_board_form(request: Request):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("create_board.html", {"request": request})

@app.post("/create-board", response_class=RedirectResponse)
async def create_board(request: Request, title: str = Form(...), description: str = Form(None)):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    user_id = user_token.get("user_id")
    user_email = user_token.get("email")
    try:
        user_ref = firestore_db.collection("users").document(user_email)
        user_doc = user_ref.get()
        if not user_doc.exists:
            user_ref.set({"boards": [], "user_id": user_id})
        board_ref = firestore_db.collection("taskBoards").document()
        board_ref.set({
            "title": title,"description": description,"createdBy": user_id,"createdAt": datetime.now()
        })
        user_ref.update({
            "boards": firestore.ArrayUnion([board_ref.id])
        })
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        print(f"Error creating board: {e}")
        return RedirectResponse("/create-board-form?error=creation_failed", status_code=303)

# Display a specific board and its tasks
@app.get("/board/{board_id}", response_class=HTMLResponse)
async def view_board(request: Request, board_id: str):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    user_email = user_token.get("email")
    user_id = user_token.get("user_id")
    user_doc = firestore_db.collection("users").document(user_email).get()
    if not user_doc.exists or board_id not in user_doc.to_dict().get("boards", []):
        return RedirectResponse("/", status_code=303)
    board_doc = firestore_db.collection("taskBoards").document(board_id).get()
    if not board_doc.exists:
        return RedirectResponse("/", status_code=303)
    board_data = board_doc.to_dict()
    is_creator = board_data.get("createdBy") == user_id
    members = []
    users_query = firestore_db.collection("users").where("boards", "array_contains", board_id).stream()
    for user in users_query:
        user_data = user.to_dict()
        user_data["email"] = user.id
        members.append(user_data)
    tasks = []
    total_tasks = 0
    completed_tasks = 0
    tasks_query = firestore_db.collection("tasks").where("boardId", "==", board_id).stream()
    for task in tasks_query:
        task_data = task.to_dict()
        task_data["id"] = task.id

        completed_at = task_data.get("completedAt")
        task_data["completed_at"] = (
            completed_at.to_datetime() if hasattr(completed_at, "to_datetime") else completed_at
        )
        task_data["creator_email"] = get_email_from_uid(task_data.get("createdBy"))
        tasks.append(task_data)
        total_tasks += 1
        if task_data.get("completed"):
            completed_tasks += 1
    active_tasks = total_tasks - completed_tasks
    return templates.TemplateResponse("board.html", {
        "request": request,"user_token": user_token,"board": {"id": board_id, **board_data, "is_creator": is_creator},"members": members,"tasks": tasks,"user_email": user_email,"total_tasks": total_tasks,"completed_tasks": completed_tasks,"active_tasks": active_tasks
    })

# Add a user to a board
@app.post("/board/{board_id}/add-user", response_class=RedirectResponse)
async def add_user(request: Request, board_id: str, email: str = Form(...)):
    user_token = validate_firebase_token(request.cookies.get("token"))
    if not user_token:
        return RedirectResponse("/", status_code=303)
    board_doc = firestore_db.collection("taskBoards").document(board_id).get()
    if not board_doc.exists or board_doc.to_dict().get("createdBy") != user_token.get("user_id"):
        return RedirectResponse(f"/board/{board_id}?error=not_creator", status_code=303)
    # Check if the user already has the board
    try:
        user_ref = firestore_db.collection("users").document(email)
        user_ref.update({
            "boards": firestore.ArrayUnion([board_id])
        })
        return RedirectResponse(f"/board/{board_id}", status_code=303)
    except Exception as e:
        print(f"Error adding user: {e}")
        return RedirectResponse(f"/board/{board_id}?error=add_user_failed", status_code=303)

@app.post("/board/{board_id}/add-task", response_class=RedirectResponse)
async def add_task(request: Request,board_id: str,title: str = Form(...),due_date: str = Form(...),assignees: Optional[List[str]] = Form(None)
):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    # Validate the token and get user information
    user_id = user_token.get("user_id")
    user_email = user_token.get("email")
    user_ref = firestore_db.collection("users").document(user_email)
    if not user_ref.get().exists:
        user_ref.set({"boards": [], "user_id": user_id})
    if assignees is None:
        assignees = []
    tasks = firestore_db.collection("tasks").where("boardId", "==", board_id).stream()
    # Check if the task title already exists in the board
    for task in tasks:
        if task.to_dict().get("title") == title:
            return RedirectResponse(f"/board/{board_id}?error=task_exists", status_code=303)
    try:
        firestore_db.collection("tasks").add({
            "boardId": board_id,"title": title,"due_date": due_date,"createdBy": user_id,"createdAt": datetime.now(),"completed": False,"assignees": assignees
        })
        return RedirectResponse(f"/board/{board_id}", status_code=303)
    except Exception as e:
        print(f"Error adding task: {e}")
        return RedirectResponse(f"/board/{board_id}?error=task_failed", status_code=303)

# Toggle task completion status
@app.post("/board/{board_id}/task/{task_id}/toggle", response_class=RedirectResponse)
async def toggle_task(request: Request, board_id: str, task_id: str):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    try:
        task_ref = firestore_db.collection("tasks").document(task_id)
        task_doc = task_ref.get()        
        if not task_doc.exists:
            return RedirectResponse(f"/board/{board_id}?error=task_not_found", status_code=303)           
        current_status = task_doc.to_dict().get("completed", False)
        update_data = {
            "completed": not current_status,"updatedAt": datetime.now()
        }        
        if not current_status:
            update_data["completedAt"] = datetime.now()
        else:
            update_data["completedAt"] = None      
        task_ref.update(update_data)       
        return RedirectResponse(f"/board/{board_id}", status_code=303)
    except Exception as e:
        print(f"Error toggling task: {e}")
        return RedirectResponse(f"/board/{board_id}?error=toggle_failed", status_code=303)

# Edit task details
@app.post("/board/{board_id}/task/{task_id}/edit", response_class=RedirectResponse)
async def edit_task(request: Request, board_id: str, task_id: str, title: str = Form(...), due_date: str = Form(...), assignees: List[str] = Form(...)):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    try:
        task_ref = firestore_db.collection("tasks").document(task_id)
        task_ref.update({
            "title": title,"due_date": due_date,"assignees": assignees,"updatedAt": datetime.now()
        })
        return RedirectResponse(f"/board/{board_id}", status_code=303)
    except Exception as e:
        print(f"Error editing task: {e}")
        return RedirectResponse(f"/board/{board_id}?error=edit_failed", status_code=303)

# Delete a task
@app.post("/board/{board_id}/task/{task_id}/delete", response_class=RedirectResponse)
async def delete_task(request: Request, board_id: str, task_id: str):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    # Validate the token and get user information
    try:
        firestore_db.collection("tasks").document(task_id).delete()
        return RedirectResponse(f"/board/{board_id}", status_code=303)
    except Exception as e:
        print(f"Error deleting task: {e}")
        return RedirectResponse(f"/board/{board_id}?error=delete_failed", status_code=303)

# Rename a board by creator
@app.post("/board/{board_id}/rename", response_class=RedirectResponse)
async def rename_board(request: Request, board_id: str, new_title: str = Form(...)):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    board_doc = firestore_db.collection("taskBoards").document(board_id).get()
    if not board_doc.exists or board_doc.to_dict().get("createdBy") != user_token.get("user_id"):
        return RedirectResponse(f"/board/{board_id}?error=not_creator", status_code=303)
    firestore_db.collection("taskBoards").document(board_id).update({"title": new_title})
    return RedirectResponse(f"/board/{board_id}", status_code=303)

# Deletion of a board by creator
@app.post("/board/{board_id}/delete", response_class=RedirectResponse)
async def delete_board(request: Request, board_id: str):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    board_ref = firestore_db.collection("taskBoards").document(board_id)
    board_doc = board_ref.get()
    # Check if the user is the creator of the board
    # and if the board has tasks or non-owning users
    if not board_doc.exists or board_doc.to_dict().get("createdBy") != user_token.get("user_id"):
        return RedirectResponse(f"/board/{board_id}?error=not_creator", status_code=303)
    tasks_query = firestore_db.collection("tasks").where("boardId", "==", board_id).limit(1).get()
    if len(tasks_query) > 0:
        return RedirectResponse(f"/board/{board_id}?error=board_has_tasks", status_code=303)
    users_query = firestore_db.collection("users").where("boards", "array_contains", board_id).stream()
    for user in users_query:
        if user.id != user_token.get("email"):
            return RedirectResponse(f"/board/{board_id}?error=board_has_members", status_code=303)
    try:
        board_ref.delete()
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        print(f"Error deleting board: {e}")
        return RedirectResponse("/", status_code=303)

# Remove a user from a board by creator
@app.post("/board/{board_id}/remove-user", response_class=RedirectResponse)
async def remove_user_from_board(request: Request, board_id: str, emails: List[str] = Form(...)):
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=303)
    board_doc = firestore_db.collection("taskBoards").document(board_id).get()
    # Check if the user is the creator of the board
    # and if the board has tasks or non-owning users
    if not board_doc.exists or board_doc.to_dict().get("createdBy") != user_token.get("user_id"):
        return RedirectResponse(f"/board/{board_id}?error=not_creator", status_code=303)
    try:
        for email in emails:
            firestore_db.collection("users").document(email).update({
                "boards": firestore.ArrayRemove([board_id])
            })
            tasks_query = firestore_db.collection("tasks").where("boardId", "==", board_id).stream()
            for task in tasks_query:
                task_data = task.to_dict()
                assignees = task_data.get("assignees", [])
                if email in assignees:
                    assignees.remove(email)
                    firestore_db.collection("tasks").document(task.id).update({
                        "assignees": assignees
                    })
        return RedirectResponse(f"/board/{board_id}", status_code=303)
    except Exception as e:
        print(f"Error removing user(s): {e}")
        return RedirectResponse(f"/board/{board_id}?error=remove_user_failed", status_code=303)