from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import logging
import time
from multiprocessing import Queue
from os import getenv
from prometheus_fastapi_instrumentator import Instrumentator
from logging_loki import LokiQueueHandler

app = FastAPI()

# --- 모니터링 설정 (Prometheus & Loki) ---

# 1. Prometheus 메트릭스 엔드포인트 설정 (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# 2. Loki 로그 핸들러 설정
# getenv를 통해 Docker Compose에 설정된 LOKI_ENDPOINT를 가져옵니다.
loki_url = getenv("LOKI_ENDPOINT", "http://loki:3100/loki/api/v1/push")

loki_logs_handler = LokiQueueHandler(
    Queue(-1),
    url=loki_url,
    tags={"application": "fastapi"},
    version="1",
)

# 3. 커스텀 액세스 로거 설정
custom_logger = logging.getLogger("custom.access")
custom_logger.setLevel(logging.INFO)
custom_logger.addHandler(loki_logs_handler)

# --- 미들웨어 설정 (로그 수집의 핵심) ---

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    모든 HTTP 요청을 가로채서 응답 시간과 상태 코드를 계산하고
    그 결과를 Loki 핸들러가 연결된 로거로 전송합니다.
    """
    start_time = time.time()
    
    # 다음 프로세스(엔드포인트 함수) 실행
    response = await call_next(request)
    
    # 응답 시간 계산
    duration = time.time() - start_time

    # 로그 메시지 포맷 구성 (IP - "METHOD PATH HTTP" STATUS DURATION)
    log_message = (
        f'{request.client.host} - "{request.method} {request.url.path} HTTP/1.1" '
        f'{response.status_code} {duration:.3f}s'
    )

    # Loki로 로그 전송
    custom_logger.info(log_message)

    return response

# --- 비즈니스 로직 (To-Do 모델 및 파일 처리) ---

class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

BASE_DIR = Path(__file__).resolve().parent
TODO_FILE = BASE_DIR / "todo.json"
INDEX_TEMPLATE = BASE_DIR / "templates" / "index.html"

def load_todos():
    if TODO_FILE.exists():
        try:
            content = TODO_FILE.read_text(encoding="utf-8-sig").strip()
            if not content:
                return []
            todos = json.loads(content)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=500,
                detail="Todo data file is not valid JSON",
            ) from exc
        return todos if isinstance(todos, list) else []
    return []

def save_todos(todos):
    TODO_FILE.write_text(json.dumps(todos, indent=4), encoding="utf-8")

def todo_to_dict(todo: TodoItem):
    return todo.model_dump() if hasattr(todo, "model_dump") else todo.dict()

# --- 엔드포인트 정의 ---

@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo_to_dict(todo))
    save_todos(todos)
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(todo_to_dict(updated_todo))
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found!!!_SJ")

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return {"message": "To-Do item deleted"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    if INDEX_TEMPLATE.exists():
        content = INDEX_TEMPLATE.read_text(encoding="utf-8")
        return HTMLResponse(content=content)
    return HTMLResponse(content="<h1>Index file not found</h1>", status_code=404)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)