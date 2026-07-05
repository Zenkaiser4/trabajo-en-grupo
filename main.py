import os
import webbrowser
from kivy.utils import platform

# --- CONFIGURACIÓN GRÁFICA INTELIGENTE Y SOLUCIÓN SSL ---
if platform == 'win':
    from kivy.config import Config
    Config.set('graphics', 'width', '360')
    Config.set('graphics', 'height', '640')
    Config.set('graphics', 'resizable', False)
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
elif platform == 'android':
    try:
        import certifi
        os.environ['SSL_CERT_FILE'] = certifi.where()
    except Exception:
        pass

from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.switch import Switch
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivymd.uix.card import MDCard
from kivy.graphics import Color, Line, Rectangle, PushMatrix, PopMatrix, Rotate, Ellipse
from kivy.graphics import StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.carousel import Carousel
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from plyer import filechooser

URL_NUEVO_LOGO = "logo_msj.png"

class LabelClickable(ButtonBehavior, Label):
    pass

class BotonBarra(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

# --- COMPONENTE DE LOGO REDONDO ---
class LogoRedondoCircular(BoxLayout):
    def __init__(self, source_url, size_pixels=60, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (size_pixels, size_pixels)
        
        self.imagen = AsyncImage(
            source=source_url,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        
        self._angulo = 0
        
        with self.canvas.before:
            StencilPush()
            self.ellipse_mask = Ellipse(size=self.size, pos=self.pos)
            StencilUse()
            PushMatrix()
            self.rotacion = Rotate(angle=0, axis=(0, 0, 1))
            
        with self.canvas.after:
            PopMatrix()
            StencilUnUse()
            self.ellipse_mask_clear = Ellipse(size=self.size, pos=self.pos)
            StencilPop()
            
        self.add_widget(self.imagen)
        self.bind(pos=self._actualizar_todo, size=self._actualizar_todo)

    def _actualizar_todo(self, *args):
        self.ellipse_mask.pos = self.pos
        self.ellipse_mask.size = self.size
        self.ellipse_mask_clear.pos = self.pos
        self.ellipse_mask_clear.size = self.size
        self.imagen.pos = self.pos
        self.imagen.size = self.size
        self.rotacion.origin = self.center

    def iniciar_giro(self, velocidad=1.5):
        Clock.schedule_interval(lambda dt: self._girar(velocidad), 1 / 60)

    def _girar(self, velocidad):
        self._angulo = (self._angulo + velocidad) % 360
        self.rotacion.angle = self._angulo

# --- TARJETA DE PRODUCTO OPTIMIZADA (2 POR FILA) ---
class ProductCard(ButtonBehavior, BoxLayout):
    def __init__(self, image_url, product_name, **kwargs):
        super().__init__(**kwargs)
        self.image_url = image_url
        self.product_name = product_name
        self.orientation = 'vertical'
        self.padding = 8
        self.spacing = 6
        self.size_hint_x = 0.5

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            Color(0.85, 0.80, 0.75, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)

        self.bind(size=self._update_canvas, pos=self._update_canvas)

        self.foto_layout = AnchorLayout(anchor_x='right', anchor_y='top', size_hint_y=0.75)
        
        self.foto = AsyncImage(
            source=image_url,
            allow_stretch=True,
            keep_ratio=True
        )
        
        self.btn_corazon = MDIconButton(
            icon="heart-outline",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.1, 0.1, 1),
            icon_size="24sp",
        )
        app = MDApp.get_running_app()
        if app and hasattr(app, 'favoritos') and any(f['name'] == self.product_name for f in app.favoritos):
            self.btn_corazon.icon = "heart"

        self.foto_layout.add_widget(self.foto)
        self.foto_layout.add_widget(self.btn_corazon)
        self.add_widget(self.foto_layout)

        self.nombre_label = Label(
            text=product_name,
            color=(0.3, 0.2, 0.1, 1),
            size_hint_y=0.25,
            font_size='14sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        self.nombre_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - 10, None)))
        self.add_widget(self.nombre_label)

    def _update_canvas(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def on_touch_down(self, touch):
        if self.btn_corazon.collide_point(*touch.pos):
            self.toggle_favorito()
            return True
        return super().on_touch_down(touch)

    def toggle_favorito(self):
        app = MDApp.get_running_app()
        es_favorito = any(f['name'] == self.product_name for f in app.favoritos)
        
        if es_favorito:
            app.favoritos = [f for f in app.favoritos if f['name'] != self.product_name]
        else:
            app.favoritos.append({'url': self.image_url, 'name': self.product_name})
        
        for screen in app.root.screens:
            self._update_cards_in_widget(screen, app.favoritos)
            
        if app.root.current == 'favoritos':
            app.root.get_screen('favoritos').on_enter()

    def _update_cards_in_widget(self, widget, favorites_list):
        if isinstance(widget, ProductCard):
            if any(f['name'] == widget.product_name for f in favorites_list):
                widget.btn_corazon.icon = "heart"
            else:
                widget.btn_corazon.icon = "heart-outline"
        
        if hasattr(widget, 'children'):
            for child in widget.children:
                self._update_cards_in_widget(child, favorites_list)

    def on_release(self):
        app = MDApp.get_running_app()
        pantalla_detalle = app.root.get_screen('detalle_producto')
        pantalla_detalle.actualizar_producto(self.image_url, self.product_name, app.root.current)
        app.root.transition.direction = "left"
        app.root.current = 'detalle_producto'


# --- PANTALLAS DE CLIENTE ---

class PantallaDetalleProducto(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pantalla_anterior = 'principal'
        self.cantidad = 1

        layout_principal = BoxLayout(orientation="vertical")

        self.barra_superior = MDTopAppBar(title="Detalle del Producto", elevation=3, size_hint_y=0.10, md_bg_color="#856C50")
        self.barra_superior.left_action_items = [["arrow-left", lambda x: self.regresar()]]
        layout_principal.add_widget(self.barra_superior)

        scroll_contenido = ScrollView(size_hint=(1, 0.90))
        box_contenido = BoxLayout(orientation="vertical", padding=15, spacing=15, size_hint_y=None)
        box_contenido.bind(minimum_height=box_contenido.setter('height'))

        self.foto_producto = AsyncImage(size_hint_y=None, height=220, allow_stretch=True, keep_ratio=True)
        box_contenido.add_widget(self.foto_producto)

        self.nombre_producto = MDLabel(text="", halign="center", font_style="H5", theme_text_color="Custom", text_color="#C0392B", bold=True, size_hint_y=None, height=40)
        box_contenido.add_widget(self.nombre_producto)

        layout_cantidad = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=10, padding=[40, 0, 40, 0])
        btn_menos = MDRaisedButton(text="-", md_bg_color="#856C50", on_release=self.restar_cantidad)
        self.lbl_cantidad = MDLabel(text=str(self.cantidad), halign="center", font_style="H6")
        btn_mas = MDRaisedButton(text="+", md_bg_color="#856C50", on_release=self.sumar_cantidad)
        
        layout_cantidad.add_widget(btn_menos)
        layout_cantidad.add_widget(self.lbl_cantidad)
        layout_cantidad.add_widget(btn_mas)
        box_contenido.add_widget(layout_cantidad)

        lbl_seccion_extras = MDLabel(text="Sumar al regalo:", font_style="Subtitle1", bold=True, theme_text_color="Custom", text_color="#856C50", size_hint_y=None, height=25)
        box_contenido.add_widget(lbl_seccion_extras)

        box_funda = BoxLayout(orientation="horizontal", size_hint_y=None, height=35)
        self.chk_funda = CheckBox(size_hint_x=0.15, color=(0.52, 0.42, 0.31, 1))
        lbl_funda = MDLabel(text="Funda de regalo", size_hint_x=0.85)
        box_funda.add_widget(self.chk_funda)
        box_funda.add_widget(lbl_funda)
        box_contenido.add_widget(box_funda)

        box_choc = BoxLayout(orientation="horizontal", size_hint_y=None, height=35)
        self.chk_choc = CheckBox(size_hint_x=0.15, color=(0.52, 0.42, 0.31, 1))
        lbl_choc = MDLabel(text="Chocolates", size_hint_x=0.85)
        box_choc.add_widget(self.chk_choc)
        box_choc.add_widget(lbl_choc)
        box_contenido.add_widget(box_choc)

        box_tarjeta = BoxLayout(orientation="horizontal", size_hint_y=None, height=35)
        self.chk_tarjeta = CheckBox(size_hint_x=0.15, color=(0.52, 0.42, 0.31, 1))
        self.chk_tarjeta.bind(active=self.toggle_campo_mensaje)
        lbl_tarjeta = MDLabel(text="Tarjeta personalizada", size_hint_x=0.85)
        box_tarjeta.add_widget(self.chk_tarjeta)
        box_tarjeta.add_widget(lbl_tarjeta)
        box_contenido.add_widget(box_tarjeta)

        self.txt_mensaje_tarjeta = MDTextField(
            hint_text="Escribe el mensaje para tu tarjeta aqui...",
            mode="rectangle",
            disabled=True,
            size_hint_y=None,
            height=80,
            multiline=True
        )
        box_contenido.add_widget(self.txt_mensaje_tarjeta)

        btn_agregar = MDRaisedButton(
            text="Agregar al carrito de compras",
            md_bg_color=(0.52, 0.42, 0.31, 1),
            pos_hint={'center_x': 0.5},
            size_hint_y=None,
            height=50,
            on_release=self.agregar_al_carrito
        )
        box_contenido.add_widget(btn_agregar)

        scroll_contenido.add_widget(box_contenido)
        layout_principal.add_widget(scroll_contenido)
        self.add_widget(layout_principal)

    def toggle_campo_mensaje(self, checkbox, value):
        self.txt_mensaje_tarjeta.disabled = not value
        if not value:
            self.txt_mensaje_tarjeta.text = ""

    def actualizar_producto(self, url, nombre, anterior):
        self.foto_producto.source = url
        self.nombre_producto.text = nombre
        self.pantalla_anterior = anterior
        self.cantidad = 1
        self.lbl_cantidad.text = str(self.cantidad)
        self.chk_funda.active = False
        self.chk_choc.active = False
        self.chk_tarjeta.active = False
        self.txt_mensaje_tarjeta.text = ""

    def sumar_cantidad(self, instance):
        self.cantidad += 1
        self.lbl_cantidad.text = str(self.cantidad)

    def regresar(self):
        self.manager.transition.direction = "right"
        self.manager.current = self.pantalla_anterior

    def agregar_al_carrito(self, instance):
        self.manager.transition.direction = "left"
        self.manager.current = 'carrito'

    def restar_cantidad(self, instance):
        if self.cantidad > 1:
            self.cantidad -= 1
            self.lbl_cantidad.text = str(self.cantidad)


# --- LOGIN ---
class PantallaLogin(Screen):
    def ingresar(self, instance):
        usuario = self.txt_usuario.text.strip()
        clave = self.txt_clave.text.strip()
        app = MDApp.get_running_app()

        if usuario in app.usuarios and app.usuarios[usuario]["clave"] == clave:
            rol = app.usuarios[usuario]["rol"]
            self.txt_usuario.text = ""
            self.txt_clave.text = ""
            self.lbl_resultado.text = ""

            if rol == "admin":
                self.manager.current = 'admin_principal'
            else:
                self.manager.current = 'principal'
        else:
            self.lbl_resultado.text = "Datos incorrectos, ingrese nuevamente por favor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.txt_usuario = MDTextField(hint_text="Usuario")
        self.txt_clave = MDTextField(hint_text="Contrasena", password=True)

        box_botones = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=50)
        boton_ingresar = MDRaisedButton(text="Ingresar", size_hint_x=0.5, md_bg_color=(0.52, 0.42, 0.31, 1))
        boton_ingresar.bind(on_release=self.ingresar)
        
        boton_registro = MDRaisedButton(text="Registrarse", size_hint_x=0.5, md_bg_color=(0.4, 0.3, 0.2, 1))
        boton_registro.bind(on_release=lambda x: setattr(self.manager, 'current', 'registro'))

        box_botones.add_widget(boton_ingresar)
        box_botones.add_widget(boton_registro)

        contenedor_logo_login = AnchorLayout(size_hint_y=None, height=160)
        self.imagen_logo = LogoRedondoCircular(source_url=URL_NUEVO_LOGO, size_pixels=130)
        contenedor_logo_login.add_widget(self.imagen_logo)

        self.lbl_resultado = MDLabel(text="", halign="center", theme_text_color="Error")

        layout.add_widget(self.txt_usuario)
        layout.add_widget(self.txt_clave)
        layout.add_widget(box_botones)
        layout.add_widget(contenedor_logo_login)
        layout.add_widget(self.lbl_resultado)

        self.add_widget(layout)


class PantallaRegistro(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        contenedor_logo = AnchorLayout(size_hint_y=None, height=130)
        self.imagen_logo = LogoRedondoCircular(source_url=URL_NUEVO_LOGO, size_pixels=100)
        contenedor_logo.add_widget(self.imagen_logo)

        self.txt_nuevo_usuario = MDTextField(hint_text="Nuevo Usuario")
        self.txt_correo = MDTextField(hint_text="Correo Electronico")
        self.txt_nueva_clave = MDTextField(hint_text="Contrasena", password=True)

        self.lbl_resultado = MDLabel(text="", halign="center", theme_text_color="Error")

        box_botones = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=50)
        btn_volver = MDRaisedButton(text="Volver", size_hint_x=0.5, md_bg_color="#C0392B")
        btn_volver.bind(on_release=self.volver_login)
        
        btn_registrar = MDRaisedButton(text="Crear Cuenta", size_hint_x=0.5, md_bg_color="#856C50")
        btn_registrar.bind(on_release=self.registrar_usuario)

        box_botones.add_widget(btn_volver)
        box_botones.add_widget(btn_registrar)

        layout.add_widget(contenedor_logo)
        layout.add_widget(self.txt_nuevo_usuario)
        layout.add_widget(self.txt_correo)
        layout.add_widget(self.txt_nueva_clave)
        layout.add_widget(self.lbl_resultado)
        layout.add_widget(box_botones)

        self.add_widget(layout)

    def volver_login(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = "login"

    def registrar_usuario(self, instance):
        usr = self.txt_nuevo_usuario.text.strip()
        correo = self.txt_correo.text.strip()
        clave = self.txt_nueva_clave.text.strip()

        if not usr or not correo or not clave:
            self.lbl_resultado.theme_text_color = "Error"
            self.lbl_resultado.text = "Todos los campos son obligatorios"
            return

        app = MDApp.get_running_app()
        if usr in app.usuarios:
            self.lbl_resultado.theme_text_color = "Error"
            self.lbl_resultado.text = "El usuario ya existe, intenta con otro"
            return

        app.usuarios[usr] = {"clave": clave, "rol": "cliente", "correo": correo}
        self.lbl_resultado.theme_text_color = "Custom"
        self.lbl_resultado.text_color = (0, 0.5, 0, 1)
        self.lbl_resultado.text = "Cuenta creada. Volviendo al login..."
        
        self.txt_nuevo_usuario.text = ""
        self.txt_correo.text = ""
        self.txt_nueva_clave.text = ""
        Clock.schedule_once(lambda dt: self.volver_login(None), 1.5)


# --- PANTALLA PRINCIPAL (2 EN 2 ESPACIADO) ---
class Principal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout_principal = BoxLayout(orientation="vertical", padding=[12, 0, 12, 12], spacing=10)

        contenedor_iconos = MDTopAppBar(title="", elevation=3, size_hint_y=0.12, md_bg_color="#856C50")
        fila_logos = BoxLayout(orientation="horizontal", padding=[10, 0, 10, 0], spacing=10)

        btn_fb = MDIconButton(icon="facebook", theme_icon_color="Custom", icon_color=(1, 1, 1, 1), pos_hint={'center_y': 0.5})
        btn_fb.bind(on_release=lambda x: webbrowser.open("https://www.facebook.com/profile.php?id=61590789510847"))
        
        btn_ig = MDIconButton(icon="instagram", theme_icon_color="Custom", icon_color=(1, 1, 1, 1), pos_hint={'center_y': 0.5})
        btn_ig.bind(on_release=lambda x: webbrowser.open("https://www.instagram.com/mi.espacioideal/"))
        
        btn_wa = MDIconButton(icon="whatsapp", theme_icon_color="Custom", icon_color=(1, 1, 1, 1), pos_hint={'center_y': 0.5})
        btn_wa.bind(on_release=lambda x: webbrowser.open("https://wa.me/qr/CSW5OMPYZLREI1"))
        
        btn_gm = MDIconButton(icon="google-maps", theme_icon_color="Custom", icon_color=(1, 1, 1, 1), pos_hint={'center_y': 0.5})
        btn_gm.bind(on_release=lambda x: webbrowser.open("https://www.google.com/maps/search/?api=1&query=Mi+Espacio+Ideal"))

        fila_logos.add_widget(BoxLayout(size_hint_x=0.1))
        fila_logos.add_widget(btn_fb)
        fila_logos.add_widget(btn_ig)
        fila_logos.add_widget(btn_wa)
        fila_logos.add_widget(btn_gm)
        fila_logos.add_widget(BoxLayout(size_hint_x=0.1))
        
        contenedor_iconos.add_widget(fila_logos)
        layout_principal.add_widget(contenedor_iconos)
        
        fila_titulo = BoxLayout(orientation="horizontal", size_hint_y=0.16, spacing=10)
        contenedor_logo_fijo = AnchorLayout(size_hint_x=0.30, anchor_x='center', anchor_y='center')
        
        self.logo_widget = LogoRedondoCircular(source_url=URL_NUEVO_LOGO, size_pixels=90)
        self.logo_widget.iniciar_giro(velocidad=1.5)
        contenedor_logo_fijo.add_widget(self.logo_widget)
        fila_titulo.add_widget(contenedor_logo_fijo)

        label_titulo = MDLabel(
            text="Mi Espacio Ideal",
            halign="left",
            theme_text_color="Custom",
            text_color="#C0392B",
            font_style="H5",
            bold=True,
            size_hint_x=0.70
        )
        fila_titulo.add_widget(label_titulo)
        layout_principal.add_widget(fila_titulo)

        self.txt_buscar = MDTextField(
            hint_text=" Buscar el regalo ideal",
            mode="round",
            pos_hint={'center_x': 0.5},
            size_hint_y=0.07
        )
        self.txt_buscar.bind(text=self.filtrar_productos)
        layout_principal.add_widget(self.txt_buscar)

        titulo1 = Label(
            text="Lo Más Vendido",
            font_size='18sp',
            bold=True,
            color=(0.80, 0.10, 0.05, 1),
            size_hint_y=0.06
        )
        layout_principal.add_widget(titulo1)

        self.mi_carousel = Carousel(direction='right', loop=True, size_hint_y=0.46) 
        layout_principal.add_widget(self.mi_carousel)
        Clock.schedule_interval(self.avanzar_carrusel, 4)

        barra = BoxLayout(orientation="horizontal", size_hint_y=0.13, spacing=5, padding=[5, 2, 5, 2])
        nav_iconos = [
            ("Inicio",      "home"),
            ("Categorias",  "apps"),
            ("Favoritos",   "heart"),
            ("Carrito",     "cart"),
            ("Perfil",      "account"),
        ]

        for texto, icono_nombre in nav_iconos:
            contenedor_boton = BotonBarra()
            contenedor_boton.bind(on_release=lambda inst, t=texto: self.cambiar_pantalla(t))

            icono = MDIconButton(
                icon=icono_nombre, 
                theme_icon_color="Custom", 
                icon_color=(0.52, 0.35, 0.15, 1), 
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint_y=0.65
            )
            icono.disabled = True 
            
            etiqueta = Label(text=texto, font_size='11sp', bold=True, color=(0.52, 0.35, 0.15, 1), size_hint_y=0.35)
            contenedor_boton.add_widget(icono)
            contenedor_boton.add_widget(etiqueta)
            barra.add_widget(contenedor_boton)

        layout_principal.add_widget(barra)
        self.add_widget(layout_principal)

    def on_enter(self):
        self.txt_buscar.text = ""
        self.filtrar_productos(None, "")

    def filtrar_productos(self, instance, texto):
        self.mi_carousel.clear_widgets()
        app = MDApp.get_running_app()
        texto = (texto or "").strip().lower()

        if texto == "":
            prods = app.productos
        else:
            prods = [p for p in app.productos if texto in p["nombre"].lower()]

        if not prods:
            lbl = MDLabel(
                text="No se encontraron productos.",
                theme_text_color="Custom",
                text_color="#856C50",
                halign="center",
                font_style="Subtitle1",
                bold=True
            )
            self.mi_carousel.add_widget(lbl)
            return

        for i in range(0, len(prods), 2):
            fila = BoxLayout(orientation='horizontal', spacing=14, padding=[8, 2, 8, 2])
            grupo = prods[i:i+2]
            for p in grupo:
                fila.add_widget(ProductCard(p["url"], p["nombre"]))
            for _ in range(2 - len(grupo)):
                fila.add_widget(Label(size_hint_x=0.5))
            self.mi_carousel.add_widget(fila)

    def avanzar_carrusel(self, dt):
        self.mi_carousel.load_next()

    def cambiar_pantalla(self, nombre_boton):
        self.manager.transition.direction = "left"
        if nombre_boton == "Perfil":
            self.manager.current = 'perfil'
        elif nombre_boton == "Categorias":
            self.manager.current = 'categories'
        elif nombre_boton == "Favoritos":
            self.manager.current = 'favoritos'
        elif nombre_boton == "Carrito":
            self.manager.current = 'carrito'
        elif nombre_boton == "Inicio":
            self.manager.current = 'principal'


# --- CATEGORÍAS ---
class PantallaCategorias(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout_principal = BoxLayout(orientation="vertical")

        barra_superior = MDTopAppBar(title="Más Productos", elevation=3, size_hint_y=0.12, md_bg_color="#856C50")
        layout_principal.add_widget(barra_superior)

        fila_switch = BoxLayout(orientation="horizontal", size_hint_y=0.08, padding=[10, 0, 10, 0])
        label_switch = MDLabel(text="Activar modo especial", theme_text_color="Custom", text_color="#856C50", font_style="Subtitle1", bold=True)
        self.switch_cat = Switch(active=False, pos_hint={'center_y': 0.5}, size_hint_x=None, width=60)
        fila_switch.add_widget(label_switch)
        fila_switch.add_widget(self.switch_cat)
        layout_principal.add_widget(fila_switch)

        scroll = ScrollView(size_hint=(1, 1))
        self.grid_productos = GridLayout(cols=2, spacing=14, padding=12, size_hint_y=None)
        self.grid_productos.bind(minimum_height=self.grid_productos.setter('height'))
        scroll.add_widget(self.grid_productos)
        layout_principal.add_widget(scroll)

        box_btn = BoxLayout(size_hint_y=0.1, padding=10)
        btn_regresar = MDRaisedButton(text="Regresar al inicio", md_bg_color="#856C50", pos_hint={'center_x': 0.5})
        btn_regresar.bind(on_press=lambda x: setattr(self.manager, 'current', 'principal'))
        box_btn.add_widget(btn_regresar)
        layout_principal.add_widget(box_btn)

        self.add_widget(layout_principal)

    def on_enter(self):
        self.grid_productos.clear_widgets()
        app = MDApp.get_running_app()
        for p in app.productos:
            prod = ProductCard(p["url"], p["nombre"])
            prod.size_hint_y = None
            prod.height = 240  
            prod.size_hint_x = 1
            self.grid_productos.add_widget(prod)


# --- FAVORITOS ---
class Favoritos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout_favoritos = BoxLayout(orientation="vertical")

        self.barra_superior = MDTopAppBar(title="Mis Favoritos", elevation=3, size_hint_y=0.12, md_bg_color="#856C50")
        self.layout_favoritos.add_widget(self.barra_superior)

        self.scroll = ScrollView(size_hint=(1, 0.74))
        self.grid = GridLayout(cols=2, spacing=14, padding=12, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout_favoritos.add_widget(self.scroll)

        barra_regresar = BoxLayout(orientation="horizontal", size_hint_y=0.14, padding=10)
        btn_volver = BotonBarra()
        
        icon_v = MDIconButton(icon="home", theme_icon_color="Custom", icon_color=(0.4, 0.3, 0.2, 1), pos_hint={'center_x': 0.5})
        icon_v.disabled = True
        btn_volver.add_widget(icon_v)
        btn_volver.add_widget(Label(text="Volver al Inicio", font_size=16, color=(0.4, 0.3, 0.2, 1), bold=True))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'principal'))

        barra_regresar.add_widget(btn_volver)
        self.layout_favoritos.add_widget(barra_regresar)
        self.add_widget(self.layout_favoritos)

    def on_enter(self):
        self.grid.clear_widgets()
        app = MDApp.get_running_app()
        
        if not app.favoritos:
            lbl = MDLabel(
                text="No tienes productos en Favoritos aún.",
                halign="center", theme_text_color="Custom",
                text_color="#856C50", font_style="Subtitle1", size_hint_y=None, height=100
            )
            self.grid.add_widget(lbl)
        else:
            for fav in app.favoritos:
                prod = ProductCard(fav['url'], fav['name'])
                prod.size_hint_y = None
                prod.height = 240
                prod.size_hint_x = 1
                self.grid.add_widget(prod)


# --- CARRITO (MENÚ VISIBLE Y ESPACIADO COMPLETO) ---
class PantallaCarrito(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metodo_pago = ""
        self.ruta_comprobante = None

        layout_principal = BoxLayout(orientation="vertical")
        barra_superior = MDTopAppBar(title="Mi Carrito", elevation=3, size_hint_y=0.12, md_bg_color="#856C50")
        layout_principal.add_widget(barra_superior)

        scroll = ScrollView(size_hint=(1, 0.74))
        layout_carrito = BoxLayout(orientation="vertical", padding=20, spacing=18, size_hint_y=None)
        layout_carrito.bind(minimum_height=layout_carrito.setter('height'))

        avatar_layout = AnchorLayout(size_hint_y=None, height=100, anchor_x='center', anchor_y='center')
        self.foto_carrito = LogoRedondoCircular(source_url=URL_NUEVO_LOGO, size_pixels=80)
        avatar_layout.add_widget(self.foto_carrito)
        layout_carrito.add_widget(avatar_layout)

        self.txt_direccion = MDTextField(text="Av. Central 123", hint_text="Dirección de Envío", mode="round", size_hint_y=None, height=50)
        self.txt_nota = MDTextField(text="Dejar en portería", hint_text="Nota especial", mode="round", size_hint_y=None, height=50)
        layout_carrito.add_widget(self.txt_direccion)
        layout_carrito.add_widget(self.txt_nota)

        fila_switch = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, padding=[10, 0, 10, 0])
        label_switch = MDLabel(text="¿Agregar envoltura de regalo?", theme_text_color="Custom", text_color="#856C50", font_style="Subtitle1", bold=True)
        self.switch_regalo = Switch(active=True, pos_hint={'center_y': 0.5}, size_hint_x=None, width=60)
        fila_switch.add_widget(label_switch)
        fila_switch.add_widget(self.switch_regalo)
        layout_carrito.add_widget(fila_switch)

        lbl_titulo_pago = MDLabel(text="Método de Pago:", theme_text_color="Custom", text_color="#856C50", font_style="Subtitle1", bold=True, size_hint_y=None, height=40)
        layout_carrito.add_widget(lbl_titulo_pago)

        self.btn_desplegable_pago = MDRaisedButton(text="Seleccionar Método", md_bg_color="#856C50", size_hint_x=1, on_release=lambda x: self.menu_pago.open())
        layout_carrito.add_widget(self.btn_desplegable_pago)

        menu_items = [
            {
                "viewclass": "OneLineListItem", 
                "text": "Tarjeta de Crédito/Débito", 
                "text_color": (0.2, 0.1, 0, 1),
                "on_release": lambda x="Tarjeta de Crédito/Débito": self.seleccionar_pago(x)
            },
            {
                "viewclass": "OneLineListItem", 
                "text": "PayPal", 
                "text_color": (0.2, 0.1, 0, 1),
                "on_release": lambda x="PayPal": self.seleccionar_pago(x)
            },
            {
                "viewclass": "OneLineListItem", 
                "text": "Transferencia Bancaria", 
                "text_color": (0.2, 0.1, 0, 1),
                "on_release": lambda x="Transferencia Bancaria": self.seleccionar_pago(x)
            },
            {
                "viewclass": "OneLineListItem", 
                "text": "Efectivo", 
                "text_color": (0.2, 0.1, 0, 1),
                "on_release": lambda x="Efectivo": self.seleccionar_pago(x)
            },
        ]
        
        self.menu_pago = MDDropdownMenu(
            caller=self.btn_desplegable_pago, 
            items=menu_items, 
            width_mult=4,
            background_color=(1, 1, 1, 1) 
        )

        self.contenedor_datos_pago = BoxLayout(orientation="vertical", size_hint_y=None, height=0, spacing=15, padding=[0, 10, 0, 10])
        layout_carrito.add_widget(self.contenedor_datos_pago)

        self.lbl_metodo_seleccionado = MDLabel(text="Ningún método seleccionado", theme_text_color="Custom", text_color="#856C50", halign="center", font_style="Caption", size_hint_y=None, height=30)
        layout_carrito.add_widget(self.lbl_metodo_seleccionado)

        btn_procesar = MDRaisedButton(text="Procesar Pedido", md_bg_color="#856C50", pos_hint={'center_x': 0.5}, size_hint_y=None, height=50, on_press=self.procesar_pedido)
        layout_carrito.add_widget(btn_procesar)

        scroll.add_widget(layout_carrito)
        layout_principal.add_widget(scroll)

        barra_retorno = BoxLayout(orientation="horizontal", size_hint_y=0.14, spacing=10, padding=5)
        btn_inicio = BotonBarra()
        btn_inicio.bind(on_release=lambda x: setattr(self.manager, 'current', 'principal'))
        ic1 = MDIconButton(icon="home", theme_icon_color="Custom", icon_color=(0.4, 0.3, 0.2, 1), pos_hint={'center_x': 0.5})
        ic1.disabled = True
        btn_inicio.add_widget(ic1)
        btn_inicio.add_widget(Label(text="Inicio", font_size='13sp', color=(0.4, 0.3, 0.2, 1), bold=True, size_hint_y=0.35))

        btn_carr = BotonBarra()
        ic2 = MDIconButton(icon="cart", theme_icon_color="Custom", icon_color=(0.6, 0.1, 0.1, 1), pos_hint={'center_x': 0.5})
        ic2.disabled = True
        btn_carr.add_widget(ic2)
        btn_carr.add_widget(Label(text="Carrito", font_size='13sp', color=(0.6, 0.1, 0.1, 1), bold=True, size_hint_y=0.35))

        barra_retorno.add_widget(btn_inicio)
        barra_retorno.add_widget(BoxLayout())
        barra_retorno.add_widget(btn_carr)
        layout_principal.add_widget(barra_retorno)

        self.add_widget(layout_principal)

    def seleccionar_pago(self, metodo):
        self.metodo_pago = metodo
        self.btn_desplegable_pago.text = metodo
        self.menu_pago.dismiss()
        self.lbl_metodo_seleccionado.text = f"Método seleccionado: {metodo}"
        self.contenedor_datos_pago.clear_widgets()
        
        if metodo == "Tarjeta de Crédito/Débito":
            self.contenedor_datos_pago.height = 140
            self.txt_num_tarjeta = MDTextField(hint_text="Número de Tarjeta (16 dígitos)", mode="round", size_hint_y=None, height=50)
            box_horizontal = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=50)
            self.txt_fecha_exp = MDTextField(hint_text="MM/AA", mode="round")
            self.txt_cvv = MDTextField(hint_text="CVV", mode="round", password=True)
            box_horizontal.add_widget(self.txt_fecha_exp)
            box_horizontal.add_widget(self.txt_cvv)
            self.contenedor_datos_pago.add_widget(self.txt_num_tarjeta)
            self.contenedor_datos_pago.add_widget(box_horizontal)
        elif metodo == "Transferencia Bancaria":
            self.contenedor_datos_pago.height = 200
            self.ruta_comprobante = None
            lbl_datos_banco = MDLabel(
                text="Banco: Pichincha\nNúmero de cuenta: 2213116852\nCédula: 1752775922",
                theme_text_color="Custom", text_color="#856C50", halign="center", font_style="Body1", bold=True, size_hint_y=None, height=90
            )
            self.contenedor_datos_pago.add_widget(lbl_datos_banco)
            btn_subir_comprobante = MDRaisedButton(text="Abrir Galería / Archivos", md_bg_color="#856C50", size_hint_x=1, height=50, on_release=self.abrir_selector_comprobante)
            self.contenedor_datos_pago.add_widget(btn_subir_comprobante)
            self.lbl_comprobante = MDLabel(text="Ningún comprobante seleccionado", theme_text_color="Custom", text_color="#856C50", halign="center", font_style="Caption", size_hint_y=None, height=30)
            self.contenedor_datos_pago.add_widget(self.lbl_comprobante)
        else:
            self.contenedor_datos_pago.height = 70
            self.txt_cantidad = MDTextField(hint_text="Monto a pagar", mode="round", size_hint_y=None, height=50)
            self.contenedor_datos_pago.add_widget(self.txt_cantidad)

    def abrir_selector_comprobante(self, *args):
        filechooser.open_file(title="Selecciona el comprobante", filters=[("Imágenes", "*.png", "*.jpg", "*.jpeg")], on_selection=self._comprobante_seleccionado)

    def _comprobante_seleccionado(self, selection):
        if selection:
            self.ruta_comprobante = selection[0]
            self.lbl_comprobante.text = f"Comprobante: {os.path.basename(self.ruta_comprobante)}"

    def procesar_pedido(self, instance):
        if self.metodo_pago == "":
            dialog = MDDialog(title="Atención", text="Por favor selecciona un método de pago.")
        else:
            envoltura = "Sí" if self.switch_regalo.active else "No"
            detalles = ""
            if self.metodo_pago == "Tarjeta de Crédito/Débito":
                num = self.txt_num_tarjeta.text
                terminacion = num[-4:] if len(num) >= 4 else "****"
                detalles = f"Tarjeta terminada en: {terminacion}"
            elif self.metodo_pago == "Transferencia Bancaria":
                detalles = f"Comprobante: {os.path.basename(self.ruta_comprobante)}" if self.ruta_comprobante else "Sin comprobante"
            else:
                detalles = f"Monto: {self.txt_cantidad.text}"
                
            dialog = MDDialog(
                title="Pedido Confirmado",
                text=f"Dirección: {self.txt_direccion.text}\nNota: {self.txt_nota.text}\nEnvoltura: {envoltura}\nMétodo: {self.metodo_pago}\n{detalles}"
            )
        dialog.open()


# --- PERFIL ---
class PantallaPerfil(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout_perfil = BoxLayout(orientation="vertical", padding=20, spacing=10)

        barra_superior = MDTopAppBar(title="Mi Perfil", elevation=3, size_hint_y=0.12, md_bg_color="#856C50")
        layout_perfil.add_widget(barra_superior)

        avatar_layout = AnchorLayout(size_hint_y=0.25, anchor_x='center', anchor_y='center')
        avatar_container = AnchorLayout(anchor_x='right', anchor_y='bottom', size_hint=(None, None), size=(90, 90))
        self.foto_perfil = LogoRedondoCircular(source_url=URL_NUEVO_LOGO, size_pixels=90)
        
        btn_camara = MDIconButton(
            icon="camera", theme_icon_color="Custom", icon_color=(1, 1, 1, 1),
            md_bg_color=[133/255.0, 108/255.0, 80/255.0, 1], icon_size="18sp",
            on_release=self.abrir_selector_foto
        )
        avatar_container.add_widget(self.foto_perfil)
        avatar_container.add_widget(btn_camara)
        avatar_layout.add_widget(avatar_container)
        layout_perfil.add_widget(avatar_layout)

        self.txt_nombre = MDTextField(text="Usuario Registrado", hint_text="Nombre Completo", mode="round", size_hint_y=0.08)
        self.txt_correo = MDTextField(text="correo@email.com", hint_text="Correo Electrónico", mode="round", size_hint_y=0.08)
        layout_perfil.add_widget(self.txt_nombre)
        layout_perfil.add_widget(self.txt_correo)

        fila_switch = BoxLayout(orientation="horizontal", size_hint_y=0.07, padding=[10, 0, 10, 0])
        label_switch = MDLabel(text="Activar Notificaciones", theme_text_color="Custom", text_color="#856C50", font_style="Subtitle1", bold=True)
        self.switch_notif = Switch(active=True, pos_hint={'center_y': 0.5}, size_hint_x=None, width=60)
        fila_switch.add_widget(label_switch)
        fila_switch.add_widget(self.switch_notif)
        layout_perfil.add_widget(fila_switch)

        btn_guardar = MDRaisedButton(text="Guardar Cambios", md_bg_color="#856C50", pos_hint={'center_x': 0.5}, size_hint_y=0.07, on_press=self.guardar_datos)
        btn_cerrar_sesion = MDRaisedButton(text="Cerrar Sesión", md_bg_color="#C0392B", pos_hint={'center_x': 0.5}, size_hint_y=0.07, on_release=self.cerrar_sesion)
        
        layout_perfil.add_widget(btn_guardar)
        layout_perfil.add_widget(btn_cerrar_sesion)

        barra_retorno = BoxLayout(orientation="horizontal", size_hint_y=0.14, spacing=10, padding=5)
        btn_inicio = BotonBarra()
        btn_inicio.bind(on_release=lambda x: setattr(self.manager, 'current', 'principal'))
        ic3 = MDIconButton(icon="home", theme_icon_color="Custom", icon_color=(0.4, 0.3, 0.2, 1), pos_hint={'center_x': 0.5})
        ic3.disabled = True
        btn_inicio.add_widget(ic3)
        btn_inicio.add_widget(Label(text="Inicio", font_size='13sp', color=(0.4, 0.3, 0.2, 1), bold=True, size_hint_y=0.35))

        btn_perf = BotonBarra()
        ic4 = MDIconButton(icon="account", theme_icon_color="Custom", icon_color=(0.6, 0.1, 0.1, 1), pos_hint={'center_x': 0.5})
        ic4.disabled = True
        btn_perf.add_widget(ic4)
        btn_perf.add_widget(Label(text="Perfil", font_size='13sp', color=(0.6, 0.1, 0.1, 1), bold=True, size_hint_y=0.35))

        barra_retorno.add_widget(btn_inicio)
        barra_retorno.add_widget(BoxLayout())
        barra_retorno.add_widget(btn_perf)
        layout_perfil.add_widget(barra_retorno)

        self.add_widget(layout_perfil)

    def abrir_selector_foto(self, *args):
        filechooser.open_file(title="Selecciona una imagen", filters=[("Imágenes", "*.png", "*.jpg", "*.jpeg")], on_selection=self._foto_seleccionada)

    def _foto_seleccionada(self, selection):
        if selection:
            self.foto_perfil.imagen.source = selection[0]

    def guardar_datos(self, instance):
        dialog = MDDialog(title="Perfil Actualizado", text="Tus datos se guardaron con éxito.")
        dialog.open()

    def cerrar_sesion(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = "login"


# --- VISTAS ADMINISTRADOR ---
class AdminPrincipal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        barra_superior = MDTopAppBar(title="Panel de Administrador", elevation=3, md_bg_color="#856C50")
        layout.add_widget(barra_superior)
        
        box = BoxLayout(orientation="vertical", padding=30, spacing=30)
        lbl_bienvenida = MDLabel(text="Bienvenido, Administrador", font_style="H5", halign="center", theme_text_color="Custom", text_color="#856C50", size_hint_y=0.2)
        box.add_widget(lbl_bienvenida)
        
        btn_inv = MDRaisedButton(text="Gestionar Inventario", size_hint_x=1, height=60, md_bg_color="#856C50", on_release=self.ir_inventario)
        btn_salir = MDRaisedButton(text="Cerrar Sesión", size_hint_x=1, height=60, md_bg_color="#C0392B", on_release=self.cerrar_sesion)
        
        box.add_widget(btn_inv)
        box.add_widget(btn_salir)
        box.add_widget(BoxLayout(size_hint_y=0.4))
        layout.add_widget(box)
        self.add_widget(layout)
        
    def ir_inventario(self, instance):
        self.manager.transition.direction = "left"
        self.manager.current = "admin_inventario"
        
    def cerrar_sesion(self, instance):
        self.manager.transition.direction = "right"
        self.manager.current = "login"


class PantallaAdminInventario(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout_principal = BoxLayout(orientation="vertical")
        
        self.barra_superior = MDTopAppBar(title="Inventario", elevation=3, md_bg_color="#856C50")
        self.barra_superior.left_action_items = [["arrow-left", lambda x: self.regresar()]]
        layout_principal.add_widget(self.barra_superior)
        
        scroll = ScrollView()
        self.lista_productos = BoxLayout(orientation="vertical", padding=10, spacing=15, size_hint_y=None)
        self.lista_productos.bind(minimum_height=self.lista_productos.setter('height'))
        scroll.add_widget(self.lista_productos)
        layout_principal.add_widget(scroll)
        
        btn_agregar = MDFloatingActionButton(icon="plus", md_bg_color="#856C50", pos_hint={"right": 0.95}, on_release=self.mostrar_dialogo_agregar)
        box_inferior = AnchorLayout(size_hint_y=None, height=80, anchor_x="right", anchor_y="center", padding=15)
        box_inferior.add_widget(btn_agregar)
        layout_principal.add_widget(box_inferior)
        self.add_widget(layout_principal)
        
    def on_enter(self):
        self.refrescar_lista()
        
    def refrescar_lista(self):
        self.lista_productos.clear_widgets()
        app = MDApp.get_running_app()
        
        lbl = MDLabel(text="Edita el stock y nombres:", font_style="Subtitle1", bold=True, size_hint_y=None, height=40, theme_text_color="Custom", text_color="#856C50")
        self.lista_productos.add_widget(lbl)
        
        for p in app.productos:
            tarjeta = MDCard(orientation="horizontal", size_hint_y=None, height=130, padding=10, spacing=15, elevation=2, radius=[15, 15, 15, 15])
            img = AsyncImage(source=p["url"], size_hint_x=0.30, allow_stretch=True, keep_ratio=True)
            
            caja_inputs = BoxLayout(orientation="vertical", size_hint_x=0.45, spacing=5)
            txt_nom = MDTextField(text=p["nombre"], hint_text="Nombre", size_hint_y=0.5, font_size="13sp")
            txt_stock = MDTextField(text=str(p["stock"]), hint_text="Stock", size_hint_y=0.5, font_size="13sp")
            caja_inputs.add_widget(txt_nom)
            caja_inputs.add_widget(txt_stock)
            
            caja_botones = BoxLayout(orientation="vertical", size_hint_x=0.25, spacing=10)
            btn_guardar = MDRaisedButton(text="Guardar", md_bg_color="#856C50", size_hint=(1, 0.5), font_size="11sp")
            btn_guardar.bind(on_release=lambda instance, prod=p, n=txt_nom, s=txt_stock: self.guardar_cambio(prod, n.text, s.text))
            
            btn_eliminar = MDRaisedButton(text="Borrar", md_bg_color="#C0392B", size_hint=(1, 0.5), font_size="11sp")
            btn_eliminar.bind(on_release=lambda instance, prod=p: self.eliminar_producto(prod))
            
            caja_botones.add_widget(btn_guardar)
            caja_botones.add_widget(btn_eliminar)
            
            tarjeta.add_widget(img)
            tarjeta.add_widget(caja_inputs)
            tarjeta.add_widget(caja_botones)
            self.lista_productos.add_widget(tarjeta)
            
    def guardar_cambio(self, prod_dict, nuevo_nombre, nuevo_stock):
        app = MDApp.get_running_app()
        nombre_anterior = prod_dict["nombre"]
        try:
            nuevo_stock_int = int(nuevo_stock)
            prod_dict["nombre"] = nuevo_nombre
            prod_dict["stock"] = nuevo_stock_int
            
            for fav in app.favoritos:
                if fav['name'] == nombre_anterior:
                    fav['name'] = nuevo_nombre
                    
            d = MDDialog(title="Éxito", text="Producto actualizado.")
            d.open()
            self.refrescar_lista()
        except ValueError:
            d = MDDialog(title="Error", text="El stock debe ser entero.")
            d.open()
            
    def eliminar_producto(self, prod_dict):
        app = MDApp.get_running_app()
        app.favoritos = [f for f in app.favoritos if f['name'] != prod_dict['nombre']]
        app.productos.remove(prod_dict)
        self.refrescar_lista()
        
    def mostrar_dialogo_agregar(self, instance):
        contenido = BoxLayout(orientation="vertical", spacing=15, padding=[10, 20, 10, 10], size_hint_y=None, height=250)
        txt_url = MDTextField(hint_text="URL de la imagen", mode="rectangle")
        txt_nom = MDTextField(hint_text="Nombre del producto", mode="rectangle")
        txt_stock = MDTextField(hint_text="Cantidad de Stock", mode="rectangle")
        
        contenido.add_widget(txt_url)
        contenido.add_widget(txt_nom)
        contenido.add_widget(txt_stock)
        
        box_btn = BoxLayout(size_hint_y=None, height=50, spacing=15)
        btn_cancelar = MDRaisedButton(text="Cancelar", md_bg_color="#C0392B", size_hint_x=0.5)
        btn_agregar = MDRaisedButton(text="Agregar", md_bg_color="#856C50", size_hint_x=0.5)
        box_btn.add_widget(btn_cancelar)
        box_btn.add_widget(btn_agregar)
        contenido.add_widget(box_btn)
        
        popup = Popup(title="Agregar Nuevo Producto", content=contenido, size_hint=(0.9, 0.6))
        btn_cancelar.bind(on_release=popup.dismiss)
        
        def confirmar(x):
            app = MDApp.get_running_app()
            try:
                stk = int(txt_stock.text)
                app.productos.append({"url": txt_url.text, "nombre": txt_nom.text, "stock": stk})
                self.refrescar_lista()
                popup.dismiss()
            except ValueError:
                d = MDDialog(title="Error", text="El stock debe ser numérico.")
                d.open()
                
        btn_agregar.bind(on_release=confirmar)
        popup.open()
        
    def regresar(self):
        self.manager.transition.direction = "right"
        self.manager.current = "admin_principal"


# --- BASE DE DATOS LOCAL ---
class MiApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.favoritos = []
        self.usuarios = {
            "Hola123": {"clave": "1701", "rol": "admin", "correo": "admin@tienda.com"},
            "AppRegalos": {"clave": "17112025", "rol": "cliente", "correo": "usuario@tienda.com"}
        }
        self.productos = [
            {"url": "https://tussorpresas.com/wp-content/uploads/2024/01/globos-personalizados-cumpleanos.jpg", "nombre": "Globos", "stock": 10},
            {"url": "https://i.ebayimg.com/images/g/AWsAAeSwdwxpcx6p/s-l1600.webp", "nombre": "Peluches", "stock": 15},
            {"url": "https://dulceobsesion.com/upload/1737523855cuadro_mi_mejor-regalo_A1.jpg", "nombre": "Cuadros", "stock": 5},
            {"url": "https://floreriacdmx.com.mx/cdn/shop/files/image_d200dda6-618e-4a87-9a4c-71bc42e26411.heic?v=1691775242&width=493", "nombre": "Flores eternas", "stock": 20},
            {"url": "https://chokolat.com.ec/wp-content/uploads/2025/07/IMG_4666-scaled-1.jpg", "nombre": "Cajas con dulces", "stock": 30},
            {"url": "https://static.wixstatic.com/media/802169_044abc1d71a44b248d0eb4d4f566c9b9~mv2.png/v1/fill/w_551,h_551,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/802169_044abc1d71a44b248d0eb4d4f566c9b9~mv2.png", "nombre": "Peluches premium", "stock": 8}
        ]

    def build(self):
        SC = ScreenManager()
        SC.add_widget(PantallaLogin(name='login'))
        SC.add_widget(PantallaRegistro(name='registro'))
        SC.add_widget(Principal(name='principal'))
        SC.add_widget(PantallaDetalleProducto(name='detalle_producto'))
        SC.add_widget(PantallaCategorias(name='categories'))
        SC.add_widget(Favoritos(name='favoritos'))
        SC.add_widget(PantallaCarrito(name='carrito'))
        SC.add_widget(PantallaPerfil(name='perfil'))
        SC.add_widget(AdminPrincipal(name='admin_principal'))
        SC.add_widget(PantallaAdminInventario(name='admin_inventario'))

        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Brown'
        SC.current = 'login'
        return SC

if __name__ == '__main__':
    MiApp().run()
