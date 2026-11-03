from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

app = FastAPI()

# Conexión a PostgreSQL con reintentos
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "tasks_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS,
                cursor_factory=RealDictCursor
            )
            return conn
        except psycopg2.OperationalError:
            time.sleep(2)

# Crear tabla al iniciar
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        completed BOOLEAN DEFAULT FALSE
    );
""")
conn.commit()

class TaskSchema(BaseModel):
    title: str
    completed: bool = False

@app.post("/tasks")
def create_task(task: TaskSchema):
    cursor.execute("INSERT INTO tasks (title, completed) VALUES (%s, %s) RETURNING *;", (task.title, task.completed))
    new_task = cursor.fetchone()
    conn.commit()
    return new_task

@app.get("/tasks")
def get_tasks():
    cursor.execute("SELECT * FROM tasks;")
    return cursor.fetchall()

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskSchema):
    cursor.execute("UPDATE tasks SET title = %s, completed = %s WHERE id = %s RETURNING *;", (task.title, task.completed, task_id))
    updated_task = cursor.fetchone()
    conn.commit()
    if not updated_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING *;", (task_id,))
    deleted_task = cursor.fetchone()
    conn.commit()
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"message": "Tarea eliminada exitosamente"}