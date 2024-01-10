from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from typing import Dict
from fastapi.templating import Jinja2Templates
from ..utils import TASKS, USERS, get_funtion_info, get_python_scripts, is_type_literal
from . import user
import pathlib

FUNCS = get_funtion_info()

router = APIRouter(
    tags=["get-routes"]
)

templates = Jinja2Templates(directory="./src/templates")

script_directory = pathlib.Path("./bo_scripts")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    scripts = get_python_scripts()
    # this is fucked up list cpmprehension
    function_info = [
                        {
                         "script_id": FUNCS.index(func),
                         "name": func[1].__name__, 
                         "doc": func[1].__doc__,
                         "params": {
                                    param_name:param_type.annotation.__name__ 
                                    if not is_type_literal(param_type) 
                                    else [param_type.annotation.__name__] + list(param_type.annotation.__args__ )
                                    for param_name, param_type in func[2].items()
                                    },
                         "output": func[3].__name__ if not is_type_literal(func[3]) else [func[3].__name__] + list(func[3].__args__)
                         } 
                         for func in FUNCS 
                     ]
    
    return templates.TemplateResponse("index.html", {"request": request, 
                                                     "scripts": list(scripts), 
                                                     "func_info": function_info})


@router.get("/function/{function_id}")
def render_function(function_id: int, request: Request):
    if function_id > len(FUNCS) - 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="function not found")
    function: list = FUNCS[function_id]
    function_info: dict =  {
        "id": function_id,
        "name":function[0],
        "params":{
                    param_name:param_type.annotation.__name__ 
                    if not is_type_literal(param_type) 
                    else [param_type.annotation.__name__] + list(param_type.annotation.__args__ )
                    for param_name, param_type in function[2].items()
                    },
        "output": function[3].__name__ if not is_type_literal(function[3]) else [function[3].__name__] + list(function[3].__args__)
    }
    return templates.TemplateResponse("function.html", 
                                      {"request": request,
                                      "function": function_info}
                                      )


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