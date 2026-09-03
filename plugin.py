from pathlib import Path

from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtGui import QAction, QIcon
from qgis.PyQt.QtWidgets import QFileDialog, QMenu, QMessageBox, QToolButton


MENU_NAME = "&DMIKG STYLE"

STYLES = {
    "linjer": {
        "navn": "Linjer",
        "settings_key": "DMIKG_STYLE/linjer_qml"
    },
    "punkter": {
        "navn": "Punkter",
        "settings_key": "DMIKG_STYLE/punkter_qml"
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

        self.add_plugin_action(
            "Vælg QML til linjer...",
            lambda: self.choose_style("linjer")
        )

        self.add_plugin_action(
            "Vælg QML til punkter...",
            lambda: self.choose_style("punkter")
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
        settings_key = STYLES[style_type]["settings_key"]

        value = QSettings().value(
            settings_key,
            ""
        )

        return str(value).strip()

    def choose_style(self, style_type):
        style = STYLES[style_type]
        current_path = self.saved_style_path(style_type)

        if current_path:
            start_folder = str(Path(current_path).parent)
        else:
            start_folder = ""

        selected_path, _ = QFileDialog.getOpenFileName(
            self.iface.mainWindow(),
            f"Vælg QML-style til {style['navn'].lower()}",
            start_folder,
            "QGIS Layer Style (*.qml)"
        )

        if not selected_path:
            return False

        QSettings().setValue(
            style["settings_key"],
            selected_path
        )

        QMessageBox.information(
            self.iface.mainWindow(),
            "DMIKG STYLE",
            f"Stylefilen til {style['navn'].lower()} er gemt."
        )

        return True

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

        if not style_path:
            selected = self.choose_style(style_type)

            if not selected:
                return

            style_path = self.saved_style_path(style_type)

        if not Path(style_path).is_file():
            QMessageBox.warning(
                self.iface.mainWindow(),
                "DMIKG STYLE",
                f"Stylefilen blev ikke fundet:\n{style_path}"
            )
            return

        error_message, success = layer.loadNamedStyle(
            style_path
        )

        if not success:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "DMIKG STYLE",
                error_message
            )
            return

        layer.triggerRepaint()

        self.iface.messageBar().pushSuccess(
            "DMIKG STYLE",
            f"{style['navn']} er anvendt på {layer.name()}."
        )

