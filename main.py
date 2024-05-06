from typing import Annotated

from fastapi import FastAPI, Depends, UploadFile, Body, Query
from fastapi.responses import HTMLResponse

from database import SessionLocal
from sensor_processor import process_sensor_file, process_sensor_data_from_string_strict, process_sensor_data_str_soft

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    content = """
    <body>
    <form action="/sensor/file/hex" enctype="multipart/form-data" method="post">
    <input name="file" type="file" multiple>
    <input type="submit">
    </form>
    </body>
        """
    return HTMLResponse(content=content)


@app.post("/sensor/file/hex")
async def sensor_data_from_hex_file(file: UploadFile,
                                    db: Annotated[SessionLocal, Depends(get_db)],
                                    mode: str = "soft"):
    return await process_sensor_file(file, db, mode)


@app.post("/sensor/hex")
async def sensor_data_from_hex_str(data: Annotated[str, Body(embed=True)],
                                   db: Annotated[SessionLocal, Depends(get_db)],
                                   mode: str = "soft"):
    match mode:
        case "soft":
            return await process_sensor_data_str_soft(data, db)
        case "strict":
            return await process_sensor_data_from_string_strict(data, db)
        case _:
            raise ValueError("Invalid mode")
