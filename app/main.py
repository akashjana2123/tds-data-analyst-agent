# app/main.py
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import os, tempfile, time, asyncio
from .utils.fileops import create_temp_dir, save_upload_file, cleanup_dir
from .workers import run_pipeline
from .config import API_TIMEOUT_SECONDS

app = FastAPI(title="TDS Data Analyst Agent")

@app.post("/api/")
async def analyze(request: Request, files: Optional[List[UploadFile]] = None):
    """
    Accepts a multipart POST. questions.txt MUST be present. Additional files optional.
    The evaluation calls: curl "https://app.example.com/api/" -F "questions.txt=@question.txt" -F "image.png=@image.png" -F "data.csv=@data.csv"
    We'll accept any set of files and return JSON (within ~3 minutes).
    """
    # collect uploaded files
    form = await request.form()
    # find questions.txt
    if "questions.txt" not in form:
        raise HTTPException(status_code=400, detail="questions.txt is required in the multipart body.")
    qfile = form["questions.txt"]
    # Prepare temp dir to save attachments
    tempdir = create_temp_dir(prefix="tda_")
    saved = {}
    try:
        # save every uploaded file to disk
        for key, value in form.multi_items():
            # value may be UploadFile or str; we handle upload file types
            try:
                if hasattr(value, "filename") and value.filename:
                    dest = os.path.join(tempdir, os.path.basename(value.filename))
                    await value.seek(0)
                    # use read() to write
                    with open(dest, "wb") as f:
                        while True:
                            chunk = await value.read(1024*64)
                            if not chunk:
                                break
                            f.write(chunk)
                    saved[value.filename] = dest
            except Exception:
                # ignore non-file fields
                pass
        # read questions.txt content (string)
        await qfile.seek(0)
        qtext = (await qfile.read()).decode("utf-8")
        # run pipeline with timeout (API_TIMEOUT_SECONDS defined in env/config)
        try:
            result = await asyncio.wait_for(run_pipeline(qtext, saved, API_TIMEOUT_SECONDS), timeout=API_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Processing timed out (exceeded allowed time).")
        return JSONResponse(content=result)
    finally:
        # cleanup uploaded files
        try:
            cleanup_dir(tempdir)
        except Exception:
            pass

# root health
@app.get("/")
async def root():
    return {"status":"ok", "info":"TDS Data Analyst Agent API. POST to /api/ with questions.txt"}
