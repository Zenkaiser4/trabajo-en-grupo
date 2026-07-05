[app]

# (str) Title of your application
title = Mi Espacio Ideal

# (str) Package name
package.name = miespacioideal

# (str) Package domain (needed for android packaging)
package.domain = org.regalos

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas

# (str) Application versioning (method 1)
# Se cambia a 1.0.2 para obligar a GitHub Actions a ignorar la caché corrupta anterior
version = 1.0.4

# (list) Application requirements
# CORREGIDO: Se añade 'plyer' al final para que la app no se rompa al buscar el selector de archivos
requirements = python3, kivy==2.3.1, kivymd==1.2.0, pillow, urllib3, certifi, openssl, requests, plyer

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# =============================================================================
# Android specific configuration
# =============================================================================

# (list) Permissions
# CRÍTICO: Permiso de internet para descargar el catálogo de imágenes externas
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 26b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (str) Android architecture to build for.
# Mantenemos únicamente arm64-v8a para evitar que GitHub Actions se quede sin RAM o tiempo límite
android.archs = arm64-v8a

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Type of builds to run (debug or release)
android.build_mode = debug

# =============================================================================
# Buildozer sections
# =============================================================================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
