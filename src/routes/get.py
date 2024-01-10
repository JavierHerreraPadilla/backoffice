from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pathlib import Path, PosixPath
from fastapi.templating import Jinja2Templates
import importlib
from ..utils import USERS
from ..utils import TASKS
from . import user
from ..get_functions import main

FUNCS = main()

router = APIRouter(
    tags=["get-routes"]
)

templates = Jinja2Templates(directory="./src/templates")

script_directory = Path("../bo_scripts")

def get_python_scripts():
    script_directory = Path("./bo_scripts")

    python_scripts: List[PosixPath] = [scpt for scpt in script_directory.glob("*.py") if not scpt.name.startswith("__")]
    docs = []
    for script in python_scripts:
        module_absolute_path = script.absolute().__str__()
        specification = importlib.util.spec_from_file_location(script.name, module_absolute_path)
        imported_module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(imported_module)
        docs.append(imported_module.__doc__)  # module doc string
    script_info = enumerate(zip(docs, python_scripts))
    return script_info

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    scripts = get_python_scripts()
    print("####", FUNCS[2][1]("3", "prd"))
    return templates.TemplateResponse("index.html", {"request": request, "scripts": list(scripts)})


@router.get("/users", response_model=Dict)
async def get_users():
    return USERS


@router.get("/script/{item_id}")
async def read_item(item_id: int, request: Request, script_name: str):
    bash_scripts = script_directory.glob("*.py")
    return templates.TemplateResponse("form.html", {"request": request, "script": script_name})


@router.get("/get-job/{job_id}")
def get_job(job_id: int):
    job = TASKS.get(job_id) 
    return job


@router.get("/users/{user_id}", response_model=user.User)
async def get_user_info(user_id: int):
    user: user.User = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user {user_id} does not exist")
    return {"user_id": user_id, "email": user.email}