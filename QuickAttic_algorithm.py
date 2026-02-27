from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString)

class QuickAtticAlgorithm(QgsProcessingAlgorithm):

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return QuickAtticAlgorithm()

    def name(self):
        return 'create_attic_layer'

    def displayName(self):
        return self.tr('Create Attic Layer')

    def group(self):
        return self.tr('Algorithms for Vector Polygon Layer')

    def groupId(self):
        return 'vector_polygon_scripts'

    def initAlgorithm(self, config=None):
        # Auch wenn wir nichts berechnen, braucht QGIS oft eine Definition
        pass

    def processAlgorithm(self, parameters, context, feedback):
        # Hier passiert die Magie
        print("Hello World")
        
        # In QGIS ist es sauberer, das Feedback-Objekt für Logs zu nutzen:
        feedback.pushInfo("Hello World aus dem Feedback-Log!")
        
        return {}