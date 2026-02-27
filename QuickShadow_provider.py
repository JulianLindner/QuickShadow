from qgis.core import QgsProcessingProvider
from .QuickShadow_algorithm import ShadowAlgorithm
from .QuickAttic_algorithm import AtticAlgorithm

class QuickShadowProvider(QgsProcessingProvider):
    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def loadAlgorithms(self):
        self.addAlgorithm(ShadowAlgorithm())
        self.addAlgorithm(AtticAlgorithm())

    def id(self):
        return 'quickshadow'

    def name(self):
        return 'QuickShadow'

    def icon(self):
        return QgsProcessingProvider.icon(self)