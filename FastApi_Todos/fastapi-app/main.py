from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os

app = FastAPI()

# To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# JSON 파일 경로
TODO_FILE = "todo.json"

# JSON 파일에서 To-Do 항목 로드
def load_todos():
    if os.path.exists(TODO_FILE):
        # Windows 기본 인코딩(cp949) 충돌을 피하기 위해 UTF-8(BOM 포함)로 읽습니다.
        with open(TODO_FILE, "r", encoding="utf-8-sig") as file:
            raw = file.read().strip()
            if not raw:
                return []
            return json.loads(raw)
    return []

# JSON 파일에 To-Do 항목 저장
def save_todos(todos):
    # 한글이 깨지지 않도록 UTF-8로 저장하고 ensure_ascii=False를 사용합니다.
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=4, ensure_ascii=False)

# To-Do 목록 조회
@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

# 신규 To-Do 항목 추가
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

# To-Do 항목 수정
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(updated_todo.dict())
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

# To-Do 항목 삭제
@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return {"message": "To-Do item deleted"}

# HTML 파일 서빙
@app.get("/", response_class=HTMLResponse)
def read_root():
    # 템플릿 파일도 UTF-8로 읽어 한글 깨짐을 방지합니다.
    with open("templates/index.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)
