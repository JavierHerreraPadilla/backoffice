import asyncio
import json
from datetime import datetime
from .. import oauth2
from fastapi import HTTPException, status, Request, Depends, Form, APIRouter, Body
from fastapi.background import BackgroundTasks
from .user import User
from random import randint
from fastapi.responses import RedirectResponse
from ..utils import TASKS
from typing import Dict

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


def process_script_input(script_data: str) -> list:
    """process de incoming data entered by the client to run the script"""
    data_list = script_data.replace("\r\n", ",").split(",")
    if len(data_list) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="could not process client data")
    data_list = [data_point.strip() for data_point in data_list if data_point not in ["", " ", "\n"]]
    return data_list


@router.post("/run-function", response_model=Dict)
async def run_function(request: Request):
    form_data = await request.form()
    form_data = dict(form_data)
    form_data.pop("submit")
    return form_data

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