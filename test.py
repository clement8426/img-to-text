import sys
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PIL import ImageGrab  # Pour capturer la zone sélectionnée
import pytesseract  # Pour l'OCR

# Si nécessaire, configurez ici le chemin vers l'exécutable Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'  # Remplacez par le chemin correct

class SelectArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sélection de Zone")

        # Prend tous les écrans moins 1 pixel pour éviter le mode plein écran
        screen_geometry = QApplication.desktop().screenGeometry()
        self.setGeometry(screen_geometry.x(), screen_geometry.y(), screen_geometry.width() - 1, screen_geometry.height() - 1)

        self.setWindowFlag(Qt.FramelessWindowHint)  # Pas de bordure de fenêtre
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Variables pour la sélection
        self.start_point = None
        self.end_point = None
        self.selection_rect = None
        self.is_selecting = False

        # Interface centrée avec boutons et label
        self.info_label = QLabel("Cliquez sur Sélectionner pour démarrer la sélection", self)
        self.info_label.setAlignment(Qt.AlignCenter)

        self.select_button = QPushButton("Sélectionner")
        self.select_button.clicked.connect(self.start_selection)
        self.close_button = QPushButton("Fermer")
        self.close_button.clicked.connect(self.close_application)

        # Layout pour centrer les éléments
        self.layout = QVBoxLayout(self)
        self.layout.addStretch(1)
        self.layout.addWidget(self.info_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.select_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)

    def start_selection(self):
        # Démarre la sélection et rend la fenêtre transparente
        self.is_selecting = True
        self.setWindowOpacity(0.3)  # Rendre la fenêtre transparente
        self.hide_buttons()

    def mousePressEvent(self, event):
        # Début de la sélection au clic gauche
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        # Mise à jour du rectangle de sélection pendant le mouvement de la souris
        if self.start_point and self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        # Fin de la sélection au relâchement du clic gauche
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def paintEvent(self, event):
        # Dessiner le rectangle de sélection
        if self.start_point and self.end_point and self.is_selecting:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(0, 255, 0), 2, Qt.DashLine))
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            painter.drawRect(selection_rect)

    def hide_buttons(self):
        # Masquer les boutons et le label
        self.select_button.hide()
        self.close_button.hide()
        self.info_label.hide()

    def show_buttons(self):
        # Afficher les boutons et le label
        self.select_button.show()
        self.close_button.show()
        self.info_label.show()
        self.setWindowOpacity(1.0)  # Opacité à 100%
        self.is_selecting = False
        self.selection_rect = None  # Réinitialiser la sélection
        self.update()  # Rafraîchir l'affichage pour effacer le rectangle

    def keyPressEvent(self, event):
        # Gestion des touches Entrée et Échap
        if event.key() == Qt.Key_Return and self.is_selecting and self.selection_rect:
            self.extract_text_from_selection()  # Extraction de texte
            self.show_buttons()  # Réaffiche les boutons après extraction
        elif event.key() == Qt.Key_Escape:
            self.close_application()  # Fermer l'application avec Échap

    def extract_text_from_selection(self):
        # Capture la zone sélectionnée et extrait le texte avec Tesseract
        x = self.selection_rect.x()
        y = self.selection_rect.y()
        width = self.selection_rect.width()
        height = self.selection_rect.height()

        # Afficher les coordonnées de la sélection pour vérification
        print(f"Coordonnées de sélection: x={x}, y={y}, largeur={width}, hauteur={height}")

        # Capture la zone avec PIL et sauvegarde temporairement pour vérifier
        screen_capture = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        screen_capture.save("temp_capture.png")  # Sauvegarde temporaire pour vérification

        # Extraction du texte avec Tesseract
        extracted_text = pytesseract.image_to_string(screen_capture, lang='eng')  # Spécifiez la langue, par exemple, 'eng' pour anglais

        # Vérification du résultat dans la console
        print(f"Texte extrait :\n{extracted_text}")

        # Affiche le texte extrait dans le label et copie dans le presse-papiers
        self.info_label.setText(f"Texte extrait :\n{extracted_text}")
        QApplication.clipboard().setText(extracted_text)  # Copie dans le presse-papiers

    def close_application(self):
        # Ferme l'application
        self.close()

def main():
    app = QApplication(sys.argv)
    window = SelectArea()
    window.show()  # Affiche la fenêtre sans passer en mode plein écran
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
