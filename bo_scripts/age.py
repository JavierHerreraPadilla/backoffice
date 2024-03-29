import requests
import sys
import json

__doc__ = """Returns the age of a name"""


names = sys.argv[1:]

def obtener_edad(nombre: str) -> str:
    """Returns the age of a name"""
    url = f"https://api.agify.io?name={nombre}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('age'):
                return data['age']
            else:
                return f"No se pudo determinar la edad para el nombre '{nombre}'."
        else:
            return f"Error al realizar la solicitud: {response.status_code}"
    except requests.RequestException as e:
        return f"Error de conexión: {e}"
    
def list_function(lst: list, letter: str) -> str:
    """test function to see if type list works"""
    return "Something"

if __name__ == "__main__":
    genders = {}
    for name in names:
        send = name.strip()
        age = obtener_edad(send)
        genders[send] = age
    print(genders)

