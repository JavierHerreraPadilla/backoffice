import asyncio
import json
from datetime import datetime
from .. import oauth2
from fastapi import HTTPException, status, Request, Depends, Form, APIRouter, Body
from fastapi.background import BackgroundTasks
from .user import User
from random import randint
from fastapi.responses import RedirectResponse
from ..utils import TASKS, param_is_list
from typing import Dict
from .get import FUNCS
from functools import partial
import typing


router = APIRouter(
    tags=["post-routes"]
    )


async def bash_script_asincrono(command: list, job_id: int):
    """asynconously runs the bash script"""
    global TASKS
    proceso = await asyncio.create_subprocess_shell(
        " ".join(command), 
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proceso.communicate()
    # modifica stdout de bytes a str y se cambia comilla simple por comilla doble para poder serializar
    stdout = stdout.decode("utf-8").replace("\n", "").replace("'", "\"")
    stdout = json.loads(stdout)
    TASKS[job_id]["stdout"] = stdout
    TASKS[job_id]["stderr"] = stderr
    TASKS[job_id]["took"] = datetime.utcnow() - TASKS[job_id]["started"] 


def process_script_input(script_data: str) -> typing.List:
    """process de incoming data entered by the client to run the script"""
    data_list = script_data.replace("\r\n", ",").split(",")
    if len(data_list) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="could not process client data")
    data_list = [data_point.strip() for data_point in data_list if data_point not in ["", " ", "\n"]]
    return data_list


def run_selected_function(job_id: int, func: typing.Callable, args: typing.Optional[typing.Dict]):
    global TASKS
    args = {} if args is None else args
    assert isinstance(args, dict), "Parameters args must be a valid dict"
    try:
        func_result = partial(func, **args)()
        TASKS[job_id]["stdout"] = func_result
        TASKS[job_id]["stderr"] = None
        TASKS[job_id]["took"] = datetime.utcnow() - TASKS[job_id]["started"] 
    except Exception as e:
        TASKS[job_id]["stdout"] = None
        TASKS[job_id]["stderr"] = e.args
        TASKS[job_id]["took"] = datetime.utcnow() - TASKS[job_id]["started"] 




@router.post("/run-function", response_model=Dict)
async def run_function(request: Request, background_task: BackgroundTasks):
    form_data = await request.form()
    form_data = dict(form_data)
    form_data.pop("submit")
    script_index = int(form_data.pop("script_index"))
    if script_index > len(FUNCS) - 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="function not found")
    function_info = FUNCS[script_index]
    list_params = param_is_list(param_dict=dict(function_info[2]))
    for list_param in list_params:
        form_data[list_param] = process_script_input(form_data.get(list_param))

    function_to_run = function_info[1]
    # result = partial(function_to_run, **form_data)() # runs the function with its arguments
    # there's no need change the str types received from the form since the functions all will only make http requests using strings
    job_id = randint(0, 9999)
    stdout, stderr = "pending", "pending"
    TASKS[job_id] = {
                    "job_id": job_id,
                    # "user": user.email,
                    "started": datetime.utcnow(),
                    "payload": form_data, 
                    "stdout": stdout,
                    "stderr": stderr
                    }
    background_task.add_task(run_selected_function, job_id, function_to_run, form_data)
    print(form_data)
    print(function_info)
    return RedirectResponse(url=f"/get-job/{job_id}")

@router.post("/")
async def post_root(request: Request, background_task: BackgroundTasks, data: str = Form(...), 
                    script_name: str = Form(...), user: User = Depends(oauth2.get_current_user)):
    data_list = process_script_input(data)
    instruction = ["python", f"bo_scripts/{script_name}"]
    instruction.extend(data_list)
    job_id = randint(0, 9999)
    stdout, stderr = "pending", "pending"
    TASKS[job_id] = {
                    "job_id": job_id,
                    "user": user.email,
                    "started": datetime.utcnow(),
                    "payload": data_list, 
                    "stdout": stdout,
                    "stderr": stderr
                    }
    background_task.add_task(bash_script_asincrono, instruction, job_id)
    # stdout, stderr = await bash_script_asincrono(command=instruction)

    # return TASKS[job_id]
    return RedirectResponse(url=f"/get-job/{job_id}")


@router.post("/get-job/{job_id}")
def get_job_post(job_id: int):
    job = TASKS.get(job_id) 
    return job