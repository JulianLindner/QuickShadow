import os
from qgis.core import QgsApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .QuickShadow_provider import QuickShadowProvider

# Get the folder of the current file
cmd_folder = os.path.dirname(__file__)

class QuickShadowPlugin(object):

    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.action = None

    def initGui(self):
        # 1. Register the processing tools
        self.provider = QuickShadowProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        # 2. Setup the Button
        icon_path = os.path.join(cmd_folder, 'icon.svg')
        
        # Use a system fallback icon if your svg isn't found
        if not os.path.exists(icon_path):
            icon = QgsApplication.getThemeIcon("/mActionFillShadow.svg")
        else:
            icon = QIcon(icon_path)

        self.action = QAction(
            icon, 
            "Create Cast Shadows", 
            self.iface.mainWindow()
        )
        
        self.action.triggered.connect(self.run_algorithm)

        # 3. Add to UI
        self.iface.addVectorToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("QuickShadow", self.action)
        
        # This will show a yellow bar if it actually reaches this point
        self.iface.messageBar().pushMessage("QuickShadow", "Plugin Initialized", level=0)

    def run_algorithm(self):
        import processing
        # Make sure this string is exactly "provider_id:algo_name"
        alg_id = "quickshadow:Create cast shadow"
        processing.execAlgorithmDialog(alg_id, {})

    def unload(self):
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
        if self.action:
            self.iface.removeVectorToolBarIcon(self.action)
            self.iface.removePluginMenu("QuickShadow", self.action)