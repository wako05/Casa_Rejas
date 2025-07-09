# run_app.py
import sys
import os

# Importa la función principal de Streamlit directamente.
# Si esta importación falla, PyInstaller no ha empaquetado Streamlit correctamente.
# La excepción será capturada por el bloque try-except general.
from streamlit.web.cli import main as streamlit_main

def run_streamlit_app():
    """
    Ejecuta la aplicación Streamlit ubicada en ui.py directamente.
    """
    # Guarda los argumentos originales
    original_argv = sys.argv

    try:
        # Configura sys.argv para que Streamlit lo interprete correctamente
        # El primer elemento es el nombre del script (run_app.py),
        # el segundo es "run" (el subcomando de streamlit),
        # y el tercero es la ruta a tu archivo ui.py.
        # Es importante que 'ui.py' sea accesible, por lo que usamos su ruta relativa.
        script_path = os.path.join(os.path.dirname(__file__), "ui.py")
        sys.argv = ["streamlit", "run", script_path]

        print(f"Iniciando la aplicación Streamlit desde: {script_path}...")
        
        # Llama directamente a la función principal de Streamlit
        # Ahora usamos 'streamlit_main' que debería estar correctamente importada
        streamlit_main()

    except Exception as e:
        # Captura cualquier excepción durante la ejecución de la aplicación Streamlit
        print(f"Ocurrió un error al iniciar la aplicación: {e}")
    finally:
        # Restaura sys.argv a su estado original para evitar efectos secundarios
        sys.argv = original_argv

if __name__ == "__main__":
    # Asegura que la función se ejecute solo cuando el script es llamado directamente
    run_streamlit_app()
