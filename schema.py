# schema.py
import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy.orm import Session
from database import SessionLocal, ToDoDB


@strawberry.type
class ToDo:
    id: int
    title: str
    description: str
    completed: bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@strawberry.type
class Query:
    @strawberry.field
    def all_todos(self, info: Info) -> List[ToDo]:
        db: Session = next(get_db())
        return db.query(ToDoDB).all()

    @strawberry.field
    def get_todo_by_id(self, info: Info, id: int) -> Optional[ToDo]:
        db: Session = next(get_db())
        return db.query(ToDoDB).filter(ToDoDB.id == id).first()

    @strawberry.field
    def get_todo_by_title(self, info: Info, title: str) -> List[ToDo]:
        db: Session = next(get_db())
        return db.query(ToDoDB).filter(ToDoDB.title == title).all()

    @strawberry.field
    def get_todo_by_completed(self, info: Info, completed: bool) -> List[ToDo]:
        db: Session = next(get_db())
        return db.query(ToDoDB).filter(ToDoDB.completed == completed).all()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_todo(
            self, info: Info, title: str, description: str
    ) -> ToDo:
        db: Session = next(get_db())
        new_todo = ToDoDB(title=title, description=description, completed=False)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo

    @strawberry.mutation
    def update_todo(
            self, info: Info, id: int, title: Optional[str] = None,
            description: Optional[str] = None,
            completed: Optional[bool] = None
    ) -> Optional[ToDo]:
        db: Session = next(get_db())
        todo = db.query(ToDoDB).filter(ToDoDB.id == id).first()
        if todo:
            if title is not None:
                todo.title = title
            if description is not None:
                todo.description = description
            if completed is not None:
                todo.completed = completed
            db.commit()
            db.refresh(todo)
            return todo
        return None

    @strawberry.mutation
    def delete_todo(
            self, info: Info, id: int
    ) -> bool:
        db: Session = next(get_db())
        todo = db.query(ToDoDB).filter(ToDoDB.id == id).first()
        if todo:
            db.delete(todo)
            db.commit()
            return True
        return False


schema = strawberry.Schema(query=Query, mutation=Mutation)
