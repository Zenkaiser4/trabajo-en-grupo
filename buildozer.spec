[app]

# (str) Title of your application
title = Mi Espacio Ideal

# (str) Package name (CORREGIDO: Sin espacios y en minúsculas para evitar el fallo de compilación)
package.name = mi_espacio_ideal

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# CORREGIDO: Añadidas versiones estables de Kivy y KivyMD para que GitHub no use una rota
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow

# (str) Presplash of the application
# CORREGIDO: Cambiado de calcu.png a tu logo real para que no falle al buscar el archivo
presplash.filename = %(source.dir)s/logo_msj.png

# (str) Icon of the application
# CORREGIDO: Cambiado de calcu.png a tu logo real
icon.filename = %(source.dir)s/logo_msj.png

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (list) Permissions
# ¡MUY IMPORTANTE!: Permiso para que carguen las imágenes de los productos desde internet
android.permissions = INTERNET

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25c

# (int) Android NDK API to use.
android.ndk_api = 24

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (bool) Enable AndroidX support. (RECOMENDADO: Activado para compatibilidad con librerías modernas de Python/Android)
android.enable_androidx = True

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
