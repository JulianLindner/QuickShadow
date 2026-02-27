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
        pass

    def processAlgorithm(self, parameters, context, feedback):        
        feedback.pushInfo("Hello World!")
        
        return {}