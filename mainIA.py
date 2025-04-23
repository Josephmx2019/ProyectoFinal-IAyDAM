from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from numpy import array, argmax
from os import environ
from tensorflow import keras, get_logger
from random import randint
import tensorflow as tf
from time import time

environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Desactiva todos los logs de TensorFlow
get_logger().setLevel('ERROR')  # Desactiva los logs de TensorFlow

# Configuración del juego
ANCHO = 10
ALTO = 20

# Variables globales
Tablero = [['.' for _ in range(ANCHO)] for _ in range(ALTO)]
Pieza = [[0 for _ in range(4)] for _ in range(4)]
x, y = 0, 0
puntaje = 0
pausado = False

# Sistema de velocidades mejorado
VELOCIDADES = {
    1: 0.5,   # Muy lento
    2: 1.0,   # Lento
    3: 1.5,   # Normal
    4: 2.0,   # Rápido
    5: 2.5,   # Muy rápido
    6: 3.0,   # Extremadamente rápido
    7: 3.5,   # Hiper rápido
    8: 4.0,   # Insano
    9: 4.5,   # Imposible
    10: 5.0   # Divino
}

nivel_velocidad = 3  # Comienza en velocidad normal
velocidad = VELOCIDADES[nivel_velocidad]

# Colores de las piezas
colores_piezas = {
    0: (1, 0, 0),  # Rojo
    1: (0, 1, 0),  # Verde
    2: (0, 0, 1),  # Azul
    3: (1, 1, 0),  # Amarillo
    4: (1, 0, 1)   # Magenta
}


# Agente de RL
class RLAgent:
    def __init__(self, estado_dim, accion_dim):
        self.estado_dim = estado_dim
        self.accion_dim = accion_dim
        self.model = self.construir_modelo()
        self.optimizer = keras.optimizers.Adam(learning_rate=0.001)

    def construir_modelo(self):
        inputs = tf.keras.layers.Input(shape=(self.estado_dim,))
        x = tf.keras.layers.Dense(64, activation="relu")(inputs)
        x = tf.keras.layers.Dense(64, activation="relu")(x)
        outputs = tf.keras.layers.Dense(self.accion_dim, activation="softmax")(x)
        return keras.Model(inputs, outputs)

    def tomar_decision(self, estado):
        estado = array(estado).reshape(1, -1)
        prob_acciones = self.model.predict(estado, verbose=0)
        return argmax(prob_acciones[0])


# Widget principal del juego
class TetrisWidget(Widget):
    def __init__(self, app, **kwargs):
        super(TetrisWidget, self).__init__(**kwargs)
        self.app = app
        self.generarPieza()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Clock.schedule_interval(self.update, 1.0 / velocidad)

        # Inicializar el agente de RL
        self.estado_dim = ANCHO * ALTO + 2  # Tablero + pieza actual + velocidad
        self.accion_dim = 5  # 5 acciones: -2, -1, 0, +1, +2 niveles de velocidad
        self.agente = RLAgent(self.estado_dim, self.accion_dim)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a':
            self.moverPieza(-1, 0)
        elif keycode[1] == 'd':
            self.moverPieza(1, 0)
        elif keycode[1] == 's':
            self.moverPieza(0, 1)
        elif keycode[1] == 'w':
            self.rotarPieza()
        elif keycode[1] == 'p':
            self.pausar_juego(None)  # Pausa con tecla 'p'
        return True

    def update(self, dt):
        if not pausado:  # Solo actualizar si el juego no está en pausa
            self.moverPieza(0, 1)
            self.dibujarTablero()
            self.ajustar_dificultad()

    # En la clase TetrisWidget, método ajustar_dificultad:
    def ajustar_dificultad(self):
        global nivel_velocidad, velocidad
        
        estado = self.obtener_estado()
        accion = self.agente.tomar_decision(estado)
        
        # Mapear la acción a un cambio en el nivel de velocidad (-2, -1, 0, +1, +2)
        cambio = accion - 2  # Esto convierte 0,1,2,3,4 en -2,-1,0,1,2
        
        nuevo_nivel = nivel_velocidad + cambio
        nuevo_nivel = max(1, min(10, nuevo_nivel))  # Cambiado de 5 a 10
        
        if nuevo_nivel != nivel_velocidad:
            nivel_velocidad = nuevo_nivel
            velocidad = VELOCIDADES[nivel_velocidad]
            
            # Actualizar la velocidad del juego
            Clock.unschedule(self.update)
            Clock.schedule_interval(self.update, 1.0 / velocidad)
            self.app.actualizar_velocidad(velocidad, nivel_velocidad)

    def obtener_estado(self):
        tablero_flat = [1 if cell == '#' else 0 for row in Tablero for cell in row]
        return tablero_flat + [self.tipoPieza, nivel_velocidad]

    def generarPieza(self):
        global x, y
        self.tipoPieza = randint(0, 4)  # Guardar el tipo de pieza generada

        for i in range(4):
            for j in range(4):
                Pieza[i][j] = 0
    
        if self.tipoPieza == 0:  # Cuadrado
            Pieza[1][1] = 1
            Pieza[1][2] = 1
            Pieza[2][1] = 1
            Pieza[2][2] = 1
        elif self.tipoPieza == 1:  # Linea
            Pieza[0][1] = 1
            Pieza[1][1] = 1
            Pieza[2][1] = 1
            Pieza[3][1] = 1
        elif self.tipoPieza == 2:  # L
            Pieza[0][1] = 1
            Pieza[1][1] = 1
            Pieza[2][1] = 1
            Pieza[2][2] = 1
        elif self.tipoPieza == 3:  # T
            Pieza[1][0] = 1
            Pieza[1][1] = 1
            Pieza[1][2] = 1
            Pieza[2][1] = 1
        elif self.tipoPieza == 4:  # Z
            Pieza[1][0] = 1
            Pieza[1][1] = 1
            Pieza[2][1] = 1
            Pieza[2][2] = 1
    
        x = ANCHO // 2 - 2
        y = 0

    def colisiona(self, nuevoX, nuevoY):
        for i in range(4):
            for j in range(4):
                if Pieza[i][j] == 1:
                    px = nuevoX + j
                    py = nuevoY + i
                    if py >= ALTO or px < 0 or px >= ANCHO or Tablero[py][px] != '.':
                        return True  # Colisión detectada
        return False  # No hay colisión

    def fijarPieza(self):
        global x, y
        for i in range(4):
            for j in range(4):
                if Pieza[i][j] == 1:
                    Tablero[y + i][x + j] = '#'

    def eliminarLineas(self):
        global puntaje
        fila = ALTO - 1
        lineas_eliminadas = 0  # Contador de líneas eliminadas

        while fila >= 0:
            completa = True
            for col in range(ANCHO):
                if Tablero[fila][col] == '.':
                    completa = False
                    break
        
            if completa:
                # Eliminar la línea y mover las líneas superiores hacia abajo
                for y in range(fila, 0, -1):
                    for x in range(ANCHO):
                        Tablero[y][x] = Tablero[y - 1][x]
                for x in range(ANCHO):
                    Tablero[0][x] = '.'
                lineas_eliminadas += 1  # Incrementar el contador de líneas eliminadas
            else:
                fila -= 1

        # Actualizar el puntaje
        if lineas_eliminadas > 0:
            puntaje += lineas_eliminadas * 100  # 100 puntos por cada línea eliminada
            self.app.actualizar_puntaje(puntaje)  # Llamar al método de la app para actualizar el Label

    def moverPieza(self, dx, dy):
        global x, y
        if not self.colisiona(x + dx, y + dy):
            x += dx
            y += dy
        elif dy == 1:
            self.fijarPieza()
            self.eliminarLineas()
            self.generarPieza()
            if self.colisiona(x, y):
                print("Game Over")
                exit(0)

    def rotarPieza(self):
        global x, y
        temp = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                temp[j][3 - i] = Pieza[i][j]
        if not self.colisiona(x, y):
            for i in range(4):
                for j in range(4):
                    Pieza[i][j] = temp[i][j]

    def dibujarTablero(self):
        self.canvas.clear()
        with self.canvas:
            # Dibujar fondo del tablero (gris oscuro)
            Color(0.15, 0.15, 0.15)
            Rectangle(pos=(0, 0), size=(ANCHO*30, ALTO*30))
            
            # Dibujar bordes del tablero (gris claro)
            Color(0.4, 0.4, 0.4)
            Rectangle(pos=(0, 0), size=(ANCHO*30, ALTO*30), width=1)
            
            # Dibujar todas las celdas
            for i in range(ALTO):
                for j in range(ANCHO):
                    # Verificar si es parte de la pieza actual
                    esPartePieza = False
                    for k in range(4):
                        for l in range(4):
                            if Pieza[k][l] == 1 and x + l == j and y + k == i:
                                esPartePieza = True
                    
                    if esPartePieza:
                        # Usar el color correspondiente al tipo de pieza (de colores_piezas)
                        color = colores_piezas[self.tipoPieza]
                        Color(*color)
                        Rectangle(pos=(j * 30 + 1, (ALTO - i - 1) * 30 + 1), size=(28, 28))
                        
                        # Borde más claro de la pieza actual
                        borde_color = [min(1.0, c + 0.3) for c in color]  # Aclarar el color
                        Color(*borde_color)
                        Rectangle(pos=(j * 30, (ALTO - i - 1) * 30), size=(30, 30), width=1)
                        
                    elif Tablero[i][j] == '#':
                        # Calcular altura relativa (0 = abajo, 1 = arriba)
                        altura_relativa = (ALTO - i) / ALTO
                        
                        # Zona de peligro (últimas 5 filas)
                        if i >= ALTO - 5:  # Últimas 5 filas
                            # Efecto parpadeante rojo/azul
                            if int(time() * 2) % 2 == 0:
                                Color(0.8, 0.2, 0.2)  # Rojo
                            else:
                                Color(0.2, 0.2, 0.8)  # Azul
                        else:
                            # Transición de color según altura
                            # Verde (abajo) -> Azul (arriba)
                            verde = max(0, 1 - (altura_relativa * 1.5))  # Disminuye
                            azul = min(1, altura_relativa * 1.3)        # Aumenta
                            
                            # Ajustar valores entre 0 y 1
                            verde = max(0.2, min(1, verde))  # Mínimo 0.2 de verde
                            azul = max(0.2, min(1, azul))    # Mínimo 0.2 de azul
                            
                            Color(0, verde, azul)
                        
                        # Dibujar bloque
                        Rectangle(pos=(j * 30 + 1, (ALTO - i - 1) * 30 + 1), size=(28, 28))
                        
                        # Borde del bloque (solo si no es zona de peligro)
                        if i < ALTO - 5:
                            brillo = min(1, verde + 0.3)
                            Color(brillo*0.5, brillo, brillo)
                            Rectangle(pos=(j * 30, (ALTO - i - 1) * 30), size=(30, 30), width=1)
            
            # Dibujar información del juego
            Color(0.9, 0.9, 0.9)
            Rectangle(pos=(ANCHO*30 + 10, ALTO*30 - 60), size=(180, 50))
            Label(text=f"Velocidad: {nivel_velocidad}\nPuntaje: {puntaje}", 
                pos=(ANCHO*30 + 15, ALTO*30 - 55),
                font_size='14sp')
    
    def pausar_juego(self, instance):
        global pausado
        pausado = not pausado  # Alternar entre pausado y no pausado
        if instance:  # Solo si se llama desde un botón
            instance.text = "Reanudar" if pausado else "Pausa"  # Cambiar el texto del botón


# Aplicación principal
class TetrisApp(App):
    def build(self):
        # Crear un BoxLayout vertical
        layout = BoxLayout(orientation='vertical')

        # Crear un Label para el puntaje y la velocidad
        self.puntaje_label = Label(text=f"Puntaje: {puntaje}", size_hint=(1, 0.1))
        self.velocidad_label = Label(text=f"Velocidad: Nivel {nivel_velocidad} ({velocidad:.2f})", size_hint=(1, 0.1))
        layout.add_widget(self.puntaje_label)
        layout.add_widget(self.velocidad_label)

        # Crear el widget del juego y añadirlo al layout
        self.game = TetrisWidget(self)
        self.game.size_hint = (1, 1)
        layout.add_widget(self.game)

        # Crear un BoxLayout horizontal para los botones
        button_layout = FloatLayout(size_hint=(1, 0.2))

        # Botones de movimiento
        btn_izquierda = Button(text="Izquierda", size_hint=(None, None), size=(100, 50), pos=(300, 50))
        btn_izquierda.bind(on_press=lambda instance: self.game.moverPieza(-1, 0))

        btn_derecha = Button(text="Derecha", size_hint=(None, None), size=(100, 50), pos=(550, 50))
        btn_derecha.bind(on_press=lambda instance: self.game.moverPieza(1, 0))

        btn_abajo = Button(text="Abajo", size_hint=(None, None), size=(100, 50), pos=(425, 50))
        btn_abajo.bind(on_press=lambda instance: self.game.moverPieza(0, 1))

        btn_rotar = Button(text="Rotar", size_hint=(None, None), size=(100, 50), pos=(425, 120))
        btn_rotar.bind(on_press=lambda instance: self.game.rotarPieza())

        btn_pausa = Button(text="Pausa", size_hint=(None, None), size=(100, 50), pos=(425, 0))
        btn_pausa.bind(on_press=lambda instance: self.game.pausar_juego(instance))

        # Botones para ajustar velocidad manualmente
        btn_mas_vel = Button(text="+ Velocidad", size_hint=(None, None), size=(120, 50), pos=(700, 120))
        btn_mas_vel.bind(on_press=lambda instance: self.cambiar_velocidad(1))

        btn_menos_vel = Button(text="- Velocidad", size_hint=(None, None), size=(120, 50), pos=(700, 50))
        btn_menos_vel.bind(on_press=lambda instance: self.cambiar_velocidad(-1))

        # Añadir los botones al layout horizontal
        button_layout.add_widget(btn_izquierda)
        button_layout.add_widget(btn_derecha)
        button_layout.add_widget(btn_abajo)
        button_layout.add_widget(btn_rotar)
        button_layout.add_widget(btn_pausa)
        button_layout.add_widget(btn_mas_vel)
        button_layout.add_widget(btn_menos_vel)

        # Añadir el layout de botones al layout principal
        layout.add_widget(button_layout)

        return layout

    def cambiar_velocidad(self, cambio):
        global nivel_velocidad, velocidad
        
        nuevo_nivel = nivel_velocidad + cambio
        nuevo_nivel = max(1, min(10, nuevo_nivel))  # Asegurar que esté entre 1 y 10
        
        if nuevo_nivel != nivel_velocidad:
            nivel_velocidad = nuevo_nivel
            velocidad = VELOCIDADES[nivel_velocidad]
            
            # Cancelar el intervalo actual
            Clock.unschedule(self.game.update)
            
            # Programar nuevo intervalo con la nueva velocidad
            Clock.schedule_interval(self.game.update, 1.0 / velocidad)
            
            # Actualizar la etiqueta de velocidad
            self.actualizar_velocidad(velocidad, nivel_velocidad)
            
            # Opcional: Mensaje de depuración
            print(f"Velocidad cambiada a nivel {nivel_velocidad} ({velocidad:.2f})")

    def actualizar_puntaje(self, nuevo_puntaje):
        self.puntaje_label.text = f"Puntaje: {nuevo_puntaje}"

    def actualizar_velocidad(self, nueva_velocidad, nivel):
        self.velocidad_label.text = f"Velocidad: Nivel {nivel} ({nueva_velocidad:.2f})"
    
if __name__ == '__main__':
    TetrisApp().run()