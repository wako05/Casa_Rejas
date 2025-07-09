# run_app.py
import subprocess
import sys

# Este script se encarga de iniciar la aplicación Streamlit.
# Es útil para cuando se quiere ejecutar la aplicación de forma sencilla
# o para empaquetarla con PyInstaller.

def run_streamlit_app():
    """
    Ejecuta la aplicación Streamlit ubicada en ui.py.
    """
    try:
        # Llama a Streamlit para ejecutar el archivo ui.py
        # El comando es 'streamlit run' seguido del nombre del archivo de la UI.
        print("Iniciando la aplicación Streamlit...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "ui.py"])
    except FileNotFoundError:
        # Maneja el caso en que Streamlit no esté instalado o no se encuentre en el PATH
        print("Error: Streamlit no encontrado. Asegúrate de tenerlo instalado.")
        print("Puedes instalarlo con: pip install streamlit")
    except Exception as e:
        # Captura cualquier otra excepción durante la ejecución
        print(f"Ocurrió un error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    # Asegura que la función se ejecute solo cuando el script es llamado directamente
    run_streamlit_app()
