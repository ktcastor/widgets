"""
Este es un widget que te permite mostrar todas las notificaciónes que llegan de las apps
que tienes instaladas en tu distro linux

Tiene licencia GPLV3

Autora: su amiga cassíe :)
"""

# Importamos las librerias necesarias para el funcionamiento del script

#Librerias para la interfaz gáfica y funciones propias
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QLabel, QWidget, QVBoxLayout, QScrollArea, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QPoint, QTime, QRectF,pyqtSignal
from PyQt6.QtGui import QRegion, QPainterPath

#librerias que interacutan con procesos
import sys
import subprocess
import threading


# Clase que representa una notificación individual en el widget
class Notification(QFrame):
    def __init__(self, app_name: str, message: str, parent=None):
        super().__init__(parent)

        # Establecemos la información que tendra la notificación

        #Nombre de la app
        self.app_name = app_name
        
        #Mensaje
        self.message = message
        
        #La Hora que se activo la notificación
        self.time = QTime.currentTime().toString("HH:mm:ss")

        #Creamos unos estilos para la tarjeta de notificación
        self.setStyleSheet("""
            background-color: #ffe6f0;
            border: 1px solid #e6a6c9;
            border-radius: 10px;
            padding: 6px;
        """)

        # Le decimos a la notificación que no sobrepase los 250px de ancho
        self.setMaximumWidth(250)

        #Este codigo lo genero la IA
        #Según investigue es para que un widget se auto escale dinamicamente
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        # Layout interno de la notificación
        layout = QVBoxLayout(self)

        #Creamos una etiqueta para mostrar el nombre de la app y le añadimos un estilo
        self.appLabel = QLabel(f"📱 {self.app_name}", self)
        self.appLabel.setStyleSheet("font-weight: bold; color: #d63384;")
        layout.addWidget(self.appLabel)

        #Creamos una etiqueta para mostrar el mensaje de la notificación y le añadimos un estilo
        self.msgLabel = QLabel(self.message, self)
        self.msgLabel.setStyleSheet("color: black;")
        self.msgLabel.setWordWrap(True)
        layout.addWidget(self.msgLabel)

        #Creamos una etiqueta para mostrar la hora de la notificación y le añadimos un estilo
        self.timeLabel = QLabel(f"🕒 {self.time}", self)
        self.timeLabel.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(self.timeLabel)


# clase del widget que hereda de QMainWindow, que es la ventana principal de PyQt6
class Notifyme(QMainWindow):

   #Creamos una señal o evento que se va a ejecutar cuando ocurra una notificación
    newNotification = pyqtSignal(str, str)

    #Constructor del widget
    def __init__(self):
        super().__init__()

        # Titulo de la ventana
        self.setWindowTitle("Notifyme")
        # Tamaño personalizado de la ventana
        self.resize(300, 400)

        #Le decimos al widget que se muestre sin botoneray sin titulo y que se ejecute como una ventana de herramietas
        #Para que no se ejecute en la barra de tareas
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        
        #Le añadimos unos estilos al widget
        self.setStyleSheet("background-color: #FFC0CB")
        self.roundedCorners()

        # Variables para arrastrar la ventana
        self.hold = False
        self.position = QPoint()

        # Agregamos los widgets a la ventana
        self.widgets()

        #Nos conectamos a la señal o evento Nueva notficación y le pasamos nuestra notificación
        self.newNotification.connect(self.addNotification)

        #Esta función llama al proceso que captura las notificaciónes de las apps
        self.setupMonitor()

    # Evento que se ejecuta cuando se sujeta la ventana con el click izquiedo del ratón
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hold = True
            self.init_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    # Evento que se ejecuta cuando se mueve la ventana
    def mouseMoveEvent(self, event):
        if self.hold:
            self.move(event.globalPosition().toPoint() - self.init_position)
            event.accept()

    # Evento que se ejecuta cuando se deja de sostener la ventana
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hold = False
            event.accept()

    # Evento que se activa cuando damos clic derecho en la ventana
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        item = menu.addAction("Cerrar aplicación")
        action = menu.exec(event.globalPos())
        if action == item:
            QApplication.quit()

    # Función para esquinas redondeadas
    def roundedCorners(self, radius=10):
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # Evento que se ejecuta cuando se redimensiona un widget
    def resizeEvent(self, event):
        self.roundedCorners(15)
        super().resizeEvent(event)

    # Función que agrega widgets a la ventana
    def widgets(self):
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        self.setCentralWidget(widget)

        #MOstraremos un label con las notificaciones totales que tenemos actualmente
        self.titleLabel = QLabel("Tienes 0 notificaciones", widget)
        self.titleLabel.setStyleSheet("""
            font-size: 18px;
            font-family: Consolas;
            color: white;
            padding-left: 1px;
        """)
        layout.addWidget(self.titleLabel)

        # Área con scroll para mostrar notificaciones
        self.scrollArea = QScrollArea(widget)
        self.scrollArea.setFixedSize(300, 350)
        self.scrollArea.setWidgetResizable(True)

        self.scrollContent = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollArea.setWidget(self.scrollContent)

        layout.addWidget(self.scrollArea)

    #Esta función crea las notificaciones y las muestra en el layout con scroll
    def addNotification(self, app_name, message):
        notification = Notification(app_name, message, self.scrollContent)
        self.scrollLayout.addWidget(notification)
        count = self.scrollLayout.count()
        self.titleLabel.setText(f"Tienes {count} notificaciones")

    #FUnción que crea un proceso en el cual nos conectamos al dbus-monitor para optener en texto plano las notificaciones
    def setupMonitor(self):
        def monitor():
            proc = subprocess.Popen(
                ["dbus-monitor", "interface='org.freedesktop.Notifications'"],
                stdout=subprocess.PIPE,
                text=True
            )

            capture = False
            strings = []

            #Una  vez que capturemos la notificación la recorremos y la mostramos en el widget
            for line in proc.stdout:
                line = line.strip()

                if "member=Notify" in line:
                    capture = True
                    strings = []
                    continue

                if capture and line.startswith("string "):
                    print(line)
                    text = line.replace("string", "").strip().strip('"')
                    strings.append(text)

                if capture and len(strings) >= 5:
                    app_name = strings[0]
                    summary = strings[2] + " -> " + strings[3]
                    body = strings[4]
                    #Aquí ya no llamamos addNotification directo
                    # Enviamos señal al hilo principal
                    self.newNotification.emit(app_name, f"{summary}: {body}")
                    capture = False
                    strings = []

        threading.Thread(target=monitor, daemon=True).start()


# Este código se ejecuta si este script de python es el principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    notifyme = Notifyme()
    notifyme.show()
    sys.exit(app.exec())
