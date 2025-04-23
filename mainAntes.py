from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from random import randint

ANCHO = 10
ALTO = 20

Tablero = [['.' for _ in range(ANCHO)] for _ in range(ALTO)]
Pieza = [[0 for _ in range(4)] for _ in range(4)]
x, y = 0, 0
puntaje = 0  # Variable para almacenar el puntaje

class TetrisWidget(Widget):
    def __init__(self, app, **kwargs):
        super(TetrisWidget, self).__init__(**kwargs)
        self.app = app  # Guardar la referencia a la instancia de TetrisApp
        self.generarPieza()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Clock.schedule_interval(self.update, 1.0 / 2.0)  # Actualiza cada 0.5 segundos

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
        return True

    def update(self, dt):
        self.moverPieza(0, 1)
        self.dibujarTablero()

    def generarPieza(self):
        global x, y
        tipoPieza = randint(0, 4)

        for i in range(4):
            for j in range(4):
                Pieza[i][j] = 0
    
        if tipoPieza == 0:  # Cuadrado
            Pieza[1][1] = 1
            Pieza[1][2] = 1
            Pieza[2][1] = 1
            Pieza[2][2] = 1
        elif tipoPieza == 1:  # Linea
            Pieza[0][1] = 1
            Pieza[1][1] = 1
            Pieza[2][1] = 1
            Pieza[3][1] = 1
        elif tipoPieza == 2:  # L
            Pieza[0][1] = 1
            Pieza[1][1] = 1
            Pieza[2][1] = 1
            Pieza[2][2] = 1
        elif tipoPieza == 3:  # T
            Pieza[1][0] = 1
            Pieza[1][1] = 1
            Pieza[1][2] = 1
            Pieza[2][1] = 1
        elif tipoPieza == 4:  # Z
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
            for i in range(ALTO):
                for j in range(ANCHO):
                    esPartePieza = False
                    for k in range(4):
                        for l in range(4):
                            if Pieza[k][l] == 1 and x + l == j and y + k == i:
                                esPartePieza = True
            
                    if esPartePieza:
                        Color(1, 0, 0)  # Color rojo para la pieza actual
                    elif Tablero[i][j] == '#':
                        Color(0, 1, 0)  # Color verde para las piezas fijadas
                    else:
                        Color(1, 1, 1)  # Color blanco para el fondo
                    Rectangle(pos=(j * 30, (ALTO - i - 1) * 30), size=(30, 30))

class TetrisApp(App):
    def build(self):
        # Crear un BoxLayout vertical
        layout = BoxLayout(orientation='vertical')

        # Crear un Label para el puntaje
        self.puntaje_label = Label(text=f"Puntaje: {puntaje}", size_hint=(1, 0.1))
        layout.add_widget(self.puntaje_label)

        # Crear el widget del juego y añadirlo al layout
        self.game = TetrisWidget(self)  # Pasar la referencia de TetrisApp a TetrisWidget
        self.game.size_hint = (1, 1)  # Ajustar el tamaño del widget del juego
        layout.add_widget(self.game)

        # Crear un BoxLayout horizontal para los botones
        button_layout = FloatLayout(size_hint=(1, 0.1))

        btn_izquierda = Button(text="Izquierda", size_hint=(None, None), size=(100, 50), pos=(300, 200))
        btn_izquierda.bind(on_press=lambda instance: self.game.moverPieza(-1, 0))

        btn_derecha = Button(text="Derecha", size_hint=(None, None), size=(100, 50), pos=(550, 200))
        btn_derecha.bind(on_press=lambda instance: self.game.moverPieza(1, 0))

        btn_abajo = Button(text="Abajo", size_hint=(None, None), size=(100, 50), pos=(425, 200))
        btn_abajo.bind(on_press=lambda instance: self.game.moverPieza(0, 1))

        btn_rotar = Button(text="Rotar", size_hint=(None, None), size=(100, 50), pos=(425, 275))
        btn_rotar.bind(on_press=lambda instance: self.game.rotarPieza())

        # Añadir los botones al layout horizontal
        button_layout.add_widget(btn_izquierda)
        button_layout.add_widget(btn_derecha)
        button_layout.add_widget(btn_abajo)
        button_layout.add_widget(btn_rotar)

        # Añadir el layout de botones al layout principal
        layout.add_widget(button_layout)

        return layout

    def actualizar_puntaje(self, nuevo_puntaje):
        # Actualizar el texto del Label del puntaje
        self.puntaje_label.text = f"Puntaje: {nuevo_puntaje}"

if __name__ == '__main__':
    TetrisApp().run()