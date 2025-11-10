from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="TODO API", description="TODOリスト管理API", version="1.0.0")

class TodoItem(BaseModel):
    id: int
    title: str #やることのタイトル
    description: Optional[str] = None #やることの詳細説明
    completed: bool = False #完了状態

#POSTリクエスト用class 2025/11/10追加
class TodoItemCreateSchema(BaseModel):
    title: str
    description: Optional[str] = None

#PUTリクエスト用class 2025/11/10追加############################
class TodoItemPUT(BaseModel):
    title: str #やることのタイトル
    description: Optional[str] = None #やることの詳細説明
    completed: bool = False #完了状態

todos = [
    TodoItem(id=1, title="牛乳とパンを買う", description="牛乳は低温殺菌じゃないとだめ", completed=False),
    TodoItem(id=2, title="Pythonの勉強", description="30分勉強する", completed=True),
    TodoItem(id=3, title="30分のジョギング", description="", completed=False),
    TodoItem(id=4, title="技術書を読む", description="", completed=False),
    TodoItem(id=5, title="夕食の準備", description="カレーを作る", completed=True)
]


@app.get("/")
def read_root():
    return {"message": "APIへようこそ!"}

#すべてのTODOアイテムを取得
@app.get("/todos", response_model=List[TodoItem])
def get_all_todos(query: Optional[str] = None):
    if query:
        resuls: List[TodoItem] = []
        for todo in todos:
            if query.lower() in todo.title.lower():
                resuls.append(todo)
            if query.lower() in todo.description.lower():
                resuls.append(todo)
        return resuls
    else:
        return todos

#特定のTODOアイテムを取得
@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="TODOアイテムが見つからない")


#新しいTodoをPOST　2025/11/10追加
@app.post("/todos", response_model=TodoItem)
def create_todo(req : TodoItemCreateSchema):
    #新しいIDを生成
    new_id = max([todo.id for todo in todos], default=0) + 1
    #新しいTODOアイテムを作成
    new_todo = TodoItem(id=new_id, title=req.title, description=req.description, completed=False)
    #リストに追加
    todos.append(new_todo)

    return new_todo

#TODOアイテムを削除 2025/11/10追加
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for i,todo in enumerate(todos):
        if todo.id == todo_id:
            deleted_todo = todos.pop(i)
            return {"message": f"TODO'{deleted_todo.description}'を削除しました"}
        raise HTTPException(status_code=404, detail=f"ID{todo_id}が見つかりません")


#課題：PUT実装 2025/11/10追加##################
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, req: TodoItemPUT):#req:~ でJSONを変換して受け取る
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            todo.title = req.title
            todo.description = req.description
            todo.completed = req.completed
            return todo
    raise HTTPException(status_code=404, detail=f"ID{todo_id}が見つかりません")

