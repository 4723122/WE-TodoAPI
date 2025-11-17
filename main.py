from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

##2025/11/17 Tortoise追加
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from models import TodoItem ##2025/11/17 追加

app = FastAPI(title="TODO API", description="TODOリスト管理API", version="1.0.0")

#Pydanticモデルの定義 2025/11/17 追加
TodoItem_Pydantic = pydantic_model_creator(TodoItem)
TodoItemCreate_Pydantic = pydantic_model_creator(TodoItem,exclude=("id","completed"))
TodoItemUpdate_Pydantic = pydantic_model_creator(TodoItem, exclude=("id",))

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
def read_root():
    return {"message": "APIへようこそ!"}

#すべてのTODOアイテムを取得
@app.get("/todos", response_model=List[TodoItem_Pydantic])
async def get_all_todos():
    todos = await TodoItem.all()
    return todos

#特定のTODOアイテムを取得
@app.get("/todos/{todo_id}", response_model=TodoItem_Pydantic)
async def get_todo(todo_id: int):
    todo = await TodoItem.get(id=todo_id)
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="TODOアイテムが見つからない")


#新しいTodoをPOST　2025/11/10追加
@app.post("/todos", response_model=TodoItemCreate_Pydantic)
async def create_todo(res : TodoItemCreate_Pydantic):
    new_todo = await TodoItem.create(title=res.title, description=res.description)
    return new_todo

#TODOアイテムを削除 2025/11/10追加
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    todo = await TodoItem.get(id=todo_id)
    if todo:
        await todo.delete()
        return {"message": f"TODO'{todo.description}'を削除しました"}


#課題：PUT実装 2025/11/10追加##################
@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, req: TodoItemUpdate_Pydantic):#req:~ でJSONを変換して受け取る
    todo = await TodoItemUpdate_Pydantic.get(id=todo_id)
    if todo:
        todo.title = req.title
        todo.description = req.description
        todo.completed = req.completed
        await todo.save()
        return todo
    else:
        raise HTTPException(status_code=404, detail=f"ID{todo_id}が見つかりません")

