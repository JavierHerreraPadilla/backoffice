import requests
import sys
import json

__doc__ = "Returns the gender of a name TEST"


names = sys.argv[1:]

def obtener_genero(nombre: str) -> tuple:
    url = f"https://api.genderize.io?name={nombre}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('gender'):
                return data['gender']
            else:
                return f"No se pudo determinar el género para el nombre '{nombre}'."
        else:
            return f"Error al realizar la solicitud: {response.status_code}"
    except requests.RequestException as e:
        return f"Error de conexión: {e}"

if __name__ == "__main__":
    genders = {}
    for name in names:
        send = name.strip()
        gender = obtener_genero(send)
        genders[send] = gender
    print(genders)

