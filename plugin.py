from pathlib import Path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QAction, QIcon
from qgis.PyQt.QtWidgets import QMenu, QMessageBox, QToolButton


MENU_NAME = "&DMIKG STYLE"

STYLES = {
    "linjer": {
        "navn": "Linjer",
        "path": r"C:\Users\x189777\Documents\QML\DMIKG_LINJE_STYLE.qml"
    },
    "punkter": {
        "navn": "Punkter",
        "path": r"C:\Users\x189777\Documents\QML\DMIKG_PUNKT_STYLE.qml"
    }
}


class DmikgStyle:

    def __init__(self, iface):
        self.iface = iface
        self.button = None
        self.toolbar_action = None
        self.plugin_actions = []

    def initGui(self):
        self.button = QToolButton(self.iface.mainWindow())
        self.button.setText("DMIKG STYLE")
        self.button.setToolTip("DMIKG STYLE")
        self.button.setIcon(
            QIcon(str(Path(__file__).parent / "icon.ico"))
        )

        self.button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )

        self.button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup
        )

        menu = QMenu(self.button)

        linjer_action = QAction("Linjer", self.button)
        punkter_action = QAction("Punkter", self.button)

        linjer_action.triggered.connect(
            lambda: self.apply_style("linjer")
        )

        punkter_action.triggered.connect(
            lambda: self.apply_style("punkter")
        )

        menu.addAction(linjer_action)
        menu.addAction(punkter_action)

        self.button.setMenu(menu)

        self.toolbar_action = self.iface.addToolBarWidget(
            self.button
        )

    def add_plugin_action(self, text, function):
        action = QAction(text, self.iface.mainWindow())
        action.triggered.connect(function)

        self.iface.addPluginToMenu(
            MENU_NAME,
            action
        )

        self.plugin_actions.append(action)

    def unload(self):
        if self.toolbar_action is not None:
            self.iface.removeToolBarIcon(
                self.toolbar_action
            )

        if self.button is not None:
            self.button.deleteLater()

        for action in self.plugin_actions:
            self.iface.removePluginMenu(
                MENU_NAME,
                action
            )
            action.deleteLater()

    def saved_style_path(self, style_type):
        return STYLES[style_type]["path"]

    def apply_style(self, style_type):
        style = STYLES[style_type]
        layer = self.iface.activeLayer()
    
        if layer is None:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "DMIKG STYLE",
                "Markér først et lag i Lag-panelet."
            )
            return
    
        style_path = self.saved_style_path(style_type)
    
        if not Path(style_path).is_file():
            QMessageBox.critical(
                self.iface.mainWindow(),
                "DMIKG STYLE",
                f"QML-filen kunne ikke findes:\n\n{style_path}\n\n"
                "Kontrollér at fællesdrevet er tilgængeligt."
            )
            return
    
        error_message, success = layer.loadNamedStyle(style_path)
    
        if not success:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "DMIKG STYLE",
                f"QML-filen blev fundet, men kunne ikke indlæses:\n\n"
                f"{error_message}"
            )
            return
    
        layer.triggerRepaint()
    
        self.iface.messageBar().pushSuccess(
            "DMIKG STYLE",
            f"{style['navn']} er anvendt på {layer.name()}."
        )
    
