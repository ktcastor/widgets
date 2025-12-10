"""
Widget que muestra un reloj digítal en pantalla

Este programa esta desarrollado en python y tiene licencia GPLV3

Autora: Su querida amiga Cassie :)
"""

# Importamos las librerias necesarias para el funcionamiento del script
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu,QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer, QTime, QRectF
from PyQt6.QtGui import QRegion,QPainterPath
import sys

# clase del widget que hereda de QMainWindow, que es la ventana principal de PyQt6
class MiniClock(QMainWindow):

    # Definimos su constructor
    def __init__(self):
        super().__init__()

        # Titulo de la ventana
        self.setWindowTitle("MiniClock")
        # Tamaño personalizado de la ventana
        self.resize(300, 100)

        # Con esta línea le estamos diciendo que se active como una ventana de herramientas del sistema
        # Pero no como una aplicación normal, por lo que no se va a ver en la barra de tareas.
        # y también le estamos quitando la cavezera y sus botoneras, para darle ese efecto de widget
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)

        #Le agregamos algunos estilos a la ventana
        self.setStyleSheet("background-color: #FFC0CB")
        self.roundedCorners()

        # Variable que nos indicará si estamos sujetando la ventana
        self.hold = False
        # Optenemos la posiciónes de la ventana con este objeto QPoint
        self.position = QPoint()

        #Agregamos los widgets a la ventana
        self.widgets()

    # Evento que se ejecuta cuando se sujeta la ventana con el click izquiedo del ratón
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Cambiamos el valor de la variable hold a True, porque estamos sujetando la ventana
            self.hold = True

            # Optenemos su pocición inicial
            self.init_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

            # Le indicamos a pyQt6 que este evento ya se completo
            event.accept()

    # Evento que se ejecuta cuando se mueve la ventana
    def mouseMoveEvent(self, event):
        # Verificamos que se este sujetando la ventana
        if self.hold:
            # Movemos la ventana
            self.move(event.globalPosition().toPoint() - self.init_position)

            # Le indicamos a pyQt6 que este evento ya se completo
            event.accept()

    # Evento que se ejecuta cuando se deja de sostener la ventana
    def mouseReleaseEvent(self, event):
        # Verificamos que ya no precionemos el click izquierdo
        if event.button() == Qt.MouseButton.LeftButton:
            # Cambiamos el valor de sujetar a false
            self.hold = False
            # Le indicamos a pyQt6 que este evento ya se completo
            event.accept()

    # Evento que se activa cuando damos clic derecho en la ventana
    def contextMenuEvent(self, event):
        # Creamos un menú que se activa dando clic derecho
        menu = QMenu(self)

        # Agregamos un item al menú, en este caso cerrar la aplicación
        item = menu.addAction("Cerrar aplicación")

        # Mostramos el menú en la posición donde se de clic derecho en la ventana y retornamos el item que seleciono
        action = menu.exec(event.globalPos())

        # Verificamos que la acion a realizar sea igual al item que seleccionamos
        if action == item:
            # Cerramos la aplicación
            QApplication.quit()


    #Función que agrega widgets a la ventana
    def widgets(self):

        #Cramos un widget principal
        widget = QWidget(self)

        #Cramos un layout vertical el cual va estar dentro del widget que acabamos de crear
        layout = QVBoxLayout(widget)

        #Le decimos a la aplicación que este es el widget que tiene que mostrar en el centro de la ventana
        self.setCentralWidget(widget)

        #Creamos una etiqueta la cual mostrara el reloj de la aplicación
        self.clockLabel = QLabel("00:00:00",self)

        #Establecemos algunos estilos para nuestra etiqueta
        self.clockLabel.setStyleSheet("""
            font-size: 48px;
            font-family: Consolas;
            color: white;
            padding-left: 8px;
        """)

        #Añadimos la etiqueta al layout vertical
        layout.addWidget(self.clockLabel)

        #Creamos un temporizador de pyqt6
        self.timer = QTimer(self) 
        #Le añadimos la función que tiene que ejecutar cuando se complete el tiempo que vamos a establecer
        self.timer.timeout.connect(self.updateTime)
        #Definimos que el timpo para que se ejecute la función sea de 1 segundo
        self.timer.start(1000)


    #Función que actualizará el reloj de la aplicación
    def updateTime(self):

        #Obtenemos la hora acutal del sistema y la convertimos a string
        hour = QTime.currentTime().toString("HH:mm:ss")

        #mostramos la nueva hora en el label
        self.clockLabel.setText(hour)

    #Función que redondea los bordes de la pantalla
    
    #Este codigo lo genero la IA
    def roundedCorners(self,radius=10):
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)  # esquinas redondeadas
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    #Evento que se ejecuta cuando se redimenciona un widget
    def resizeEvent(self, event):
        # Reaplicar bordes redondeados al cambiar tamaño
        self.roundedCorners(15)
        super().resizeEvent(event)



# Este código se ejecuta si este script de python es el principal
if __name__ == "__main__":
    # Creamos una aplicación de pyQtb
    app = QApplication(sys.argv)

    # Creamos una instancia de la ventana a mostrar en la aplicación
    miniclock = MiniClock()

    # Mostramos la ventana
    miniclock.show()

    # Esta línea es para que se activen los eventos propios de pyqt6 y se ejecute la aplicación en bucle
    sys.exit(app.exec())
