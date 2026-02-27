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
        # Register the processing tools
        self.provider = QuickShadowProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        # Setup the Button
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

        # Add to UI
        self.iface.addVectorToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("QuickShadow", self.action)
        
        self.iface.messageBar().pushMessage("QuickShadow", "Plugin Initialized", level=0)

    def run_algorithm(self):
        import processing
        alg_id = "quickshadow:Create cast shadow"
        processing.execAlgorithmDialog(alg_id, {})

    def unload(self):
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
        if self.action:
            self.iface.removeVectorToolBarIcon(self.action)
            self.iface.removePluginMenu("QuickShadow", self.action)