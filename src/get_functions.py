import pathlib
import inspect 
import typing


__doc__ = """testing"""

python_modules = list(pathlib.Path("./bo_scripts/").glob("*.py"))


def main():
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
        # for para_name, param_obj in sig.parameters.items():
        #     print(para_name, param_obj.annotation)
            
    # funcs es una lista de listas. Cada lista interna -> ind 0: nombre del modulo o escript. ind 1: objeto funcion, 
        #ind 2: parametros y sus tipos de datos,
        # ind 3: tipo de dato del retorno 
    print(funcs)
    return funcs

