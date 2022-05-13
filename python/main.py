import os
import logging
import pathlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello, world!"}


@app.get("/items")
def response():
    dbname = "/Users/ando/GitHub/mercari-build-training-2022/db/mercari.sqlite3"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("SELECT items.name, items.category FROM items")
    items = cur.fetchall()
    cur.close()
    json = {"items": [dict(zip(["name", "category"], item)) for item in items]}
    return json


@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...)):
    logger.info(f"Receive item: {name} Receive category: {category}")
    dbname = "/Users/ando/GitHub/mercari-build-training-2022/db/mercari.sqlite3"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("SELECT items.id FROM items")
    items = cur.fetchall()
    if not items:
        new_id = 0
    else:
        new_id = max(sum(items, ())) + 1
    sql = f"INSERT INTO items(id, name, category) values({new_id}, '{name}', '{category}')"
    cur.execute(sql)
    conn.commit()
    cur.close()
    # cur.execute(f"INSERT INTO items(id, name, category) values({new_id}, {name}, {category})")
    return {"message": f"item received: {name}"}


@app.get("/search")
def search_item(keyword: str):
    dbname = "/Users/ando/GitHub/mercari-build-training-2022/db/mercari.sqlite3"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute(
        f"SELECT items.name, items.category FROM items WHERE items.name == '{keyword}'"
    )
    items = cur.fetchall()
    cur.close()
    json = {"items": [dict(zip(["name", "category"], item)) for item in items]}
    return json


@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
