from passlib.context import CryptContext
import pathlib
import inspect 
import typing
import importlib
from functools import partial
from datetime import datetime


USERS = dict()
TASKS = dict()
pwd_context = CryptContext(schemes="bcrypt")


def hash_pass(password: str) -> str:
    """hashes user password"""
    hashed_password = pwd_context.hash(password)
    return hashed_password


def verify_pass(plain_pass: str, hashed_pass: str) -> bool:
    """validates if user entered correct password to login"""
    return pwd_context.verify(plain_pass, hashed_pass)


def is_type_literal(type_obj)  -> bool:
    """checks if the type_obj annotation data type is Literal
    It is called type_obj because it comes from the inspect module which return the annotated data type.
    """
    if hasattr(type_obj, 'annotation'):
        obj_annotation_name = type_obj.annotation.__name__
        return obj_annotation_name == "Literal"
    elif hasattr(type_obj, "__name__"):
        return getattr(type_obj, "__name__") == "Literal"
    else:
        return False
    

def get_funtion_info() -> typing.List:
    """This function is in charge to load the module bo_scripts in which the backoffcie scripts resides.
    It returrns a list containing lists. Each list contains the subodule, the function, the arguments and teri types, 
    and the output and its type
    """
    def load_modules(path: str, extension: typing.Literal["py", "sh"]):
        assert pathlib.Path(path).exists(), "Path does not exist"
        scripts: typing.List[pathlib.PosixPath] = list(pathlib.Path("./bo_scripts/").glob(f"*.{extension}"))
        if not scripts:
            raise Exception(f"No scripts with extensio .{extension}", extension=extension)
        for scpt in scripts:
            #import statements
            exec(f"import bo_scripts.{scpt.stem}")
        
    load_modules("./bo_scripts/", "py")
    import bo_scripts # module where the scripts are comming from. It seems i have to load the individual scripts and the module
    members = inspect.getmembers(bo_scripts)
    submodules = [(name, obj) for name, obj in members if inspect.ismodule(obj) if name != "__init__"]
    funcs = list()

    for mod_name, mod_obj in submodules:
        members = inspect.getmembers(mod_obj)
        for _, member_obj in members:
            if inspect.isfunction(member_obj):
                funcs.append([mod_name, member_obj])

    for func in funcs:
        sig = inspect.signature(func[1])
        func.append(sig.parameters)
        func.append(sig.return_annotation)

    return funcs

def get_python_scripts():
    """Returns a genarator object containing the python scripts in a folder called /bo_scripts"""
    script_directory = pathlib.Path("./bo_scripts")

    python_scripts: typing.List[pathlib.PosixPath] = [scpt for scpt in script_directory.glob("*.py") if not scpt.name.startswith("__")]
    docs = []
    for script in python_scripts:
        module_absolute_path = script.absolute().__str__()
        specification = importlib.util.spec_from_file_location(script.name, module_absolute_path)
        imported_module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(imported_module)
        docs.append(imported_module.__doc__)  # module doc string
    script_info = enumerate(zip(docs, python_scripts))
    return script_info


def run_selected_function(job_id: int, func: typing.Callable, args: typing.Optional[typing.Dict]):
    """Function that runs the selected python function.
        Runs as a background task.
    """
    global TASKS
    args = {} if args is None else args
    assert isinstance(args, dict), "Parameters args must be a valid dict"
    func_result = partial(func, **args)()
    TASKS[job_id]["stdout"] = func_result
    TASKS[job_id]["stdout"] = None
    TASKS[job_id]["took"] = datetime.utcnow() - TASKS[job_id]["started"] 


def param_is_list(param_dict: typing.Dict)  -> typing.List:
    """checks if params of a function are List. If so appends them to a list and returns it."""
    is_list = []
    for param, param_type in param_dict.items():
        if param_type.annotation is typing.List:
            is_list.append(param)
    return is_list