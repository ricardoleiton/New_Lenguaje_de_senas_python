"""Entrada de compatibilidad para la interfaz gráfica.

La implementación principal vive en el paquete ``gui``.

Ejecutar:

    .\\.venv\\Scripts\\python.exe gui_app.py
"""

from gui import App


if __name__ == "__main__":
    App().mainloop()
