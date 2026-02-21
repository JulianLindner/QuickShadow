import processing

from qgis.PyQt import QtGui
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsApplication,
                       QgsProcessingUtils)
from qgis import utils


class QuickShadowAlgorithm(QgsProcessingAlgorithm):
    """
    QGIS Processing algorithm to generate simple ground shadow polygons from 
    input building polygons.
    """

    # Constants (Parameter Definitions)
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    DEFAULT_HEIGHT_FIELD_NAME = 'default_height_value'
    HEIGHT_FIELD = 'HEIGHT_FIELD'
    SHADOW_ANGLE = 'SHADOW_ANGLE' 
    SHADOW_LENGTH_FACTOR = 'SHADOW_LENGTH_FACTOR'

    def initAlgorithm(self, config):
        """
        Defines the inputs and outputs (parameters) of the algorithm.
        """

        # 1. Input Layer (Buildings)
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer (Buildings)'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # 2. Height Field
        self.addParameter(
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                self.tr('Height Field'),
                parentLayerParameterName=self.INPUT,
                optional=True, 
                defaultValue=self.DEFAULT_HEIGHT_FIELD_NAME, 
                type=QgsProcessingParameterField.Any
            )
        )

        # 3. Shadow Angle (Direction)
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SHADOW_ANGLE,
                self.tr('Shadow Angle (0-360 degrees clockwise from North)'),
                defaultValue=225.0, 
                minValue=0.0,
                maxValue=360.0
            )
        )
        
        # 4. Shadow Length Factor (Sun Altitude)
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SHADOW_LENGTH_FACTOR,
                self.tr('Shadow Length Factor (Length = Height * Factor)'),
                defaultValue=1.0,  
                minValue=0.1,
            )
        )

        # 5. Output Sink (Ground Shadows)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Ground Shadows')
            )
        )

# ----------------------------------------------------------------------
## Helper Methods for Process Algorithm
# ----------------------------------------------------------------------

    def _get_height_expression(self, parameters, context, feedback):
        """
        Determines the QGIS expression string for the building height value.
        Uses the selected field name or a default value of 1.0.
        """
        height_field_name = self.parameterAsString(parameters, self.HEIGHT_FIELD, context)
        
        # Check if a specific Height Field is selected
        if height_field_name and height_field_name != self.DEFAULT_HEIGHT_FIELD_NAME:
            # Enclose the field name for safe expression usage
            height_value_expression = f"coalesce(\"{height_field_name}\", 1.0)"
            feedback.pushInfo(f"Using field: {height_field_name} for shadow calculation.")
        else:
            # Use a default height if no field is provided
            height_value_expression = "1.0"
            feedback.pushInfo("No height field selected. Using a default height value of 1.0.")
            
        return height_value_expression

    def _run_geometry_by_expression(self, parameters, context, feedback, height_value_expression):
        """
        Constructs and executes the QGIS 'qgis:geometrybyexpression' algorithm 
        to create the raw shadow polygons.
        """
        shadow_angle = self.parameterAsDouble(parameters, self.SHADOW_ANGLE, context)
        shadow_factor = self.parameterAsDouble(parameters, self.SHADOW_LENGTH_FACTOR, context)

        # Calculate x and y offset (projection) from angle and factor
        # dx and dy calculate the extent of the shadow in map units.
        # QGIS trigonometry functions use radians.
        dx = f"-( {height_value_expression} * {shadow_factor}) * sin(radians({shadow_angle}))"
        dy = f"-( {height_value_expression} * {shadow_factor}) * cos(radians({shadow_angle}))"

        # Define the QGIS Geometry Expression:
        # segments_to_lines(@geometry): Converts the building polygon to its constituent line segments.
        # extrude(..., dx, dy): Extrudes each segment by the calculated x and y offset.
        # buffer(..., 0): Converts the extruded multi-line/surface into a valid polygon.
        # difference: Subtract the original building's footpring
        expression = f"""
            difference(
                    buffer(
                    extrude(
                        segments_to_lines(@geometry),
                        {dx},
                        {dy}
                    ),
                    0
                ),
                @geometry
            )
        """
              
        # Define the parameters for the 'Geometry by Expression' algorithm
        alg_params = {
            'INPUT': parameters[self.INPUT],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'EXPRESSION': expression,
            'OUTPUT_GEOMETRY': QgsProcessing.TypeVectorPolygon
        }
        
        feedback.pushInfo(f"Executing Geometry by Expression for ground shadows.")
        
        # Execute the built-in QGIS processing algorithm
        result_tuple = QgsApplication.processingRegistry().algorithmById('qgis:geometrybyexpression').run(
           alg_params,
           context,
           feedback
        )  
        
        # Check for execution success
        if result_tuple is None or 'OUTPUT' not in result_tuple[0]:
            feedback.reportError("Failed to execute 'Geometry by Expression' algorithm.", True)
            return None
        
        # Return the ID of the temporary output layer (raw shadows)
        return result_tuple[0]['OUTPUT']


    def _post_process_layer(self, output_layer):
        """
        Applies a basic grey symbology to the output layer for visual representation.
        """
        single_symbol_renderer = output_layer.renderer()
        symbol = single_symbol_renderer.symbol()
        
        # Set fill and stroke colour to a light grey for a shadow effect
        grey_color = QtGui.QColor.fromRgb(200, 200, 200)
        symbol.setColor(grey_color)
        symbol.symbolLayer(0).setStrokeColor(grey_color)
        
        # Refresh symbology in the QGIS interface (if running within QGIS GUI)
        output_layer.triggerRepaint()
        if utils.iface:
            utils.iface.layerTreeView().refreshLayerSymbology(output_layer.id())

# ----------------------------------------------------------------------
## Main Processing Method
# ----------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        """
        Main execution method for the QuickShadow algorithm.
        Calculates shadows and subtracts the original building footprints.
        """
       
        # Retrieve and validate input source layer
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            feedback.reportError("Could not load source layer for INPUT.", True)
            return {} 

        # Determine the height value expression
        height_value_expression = self._get_height_expression(parameters, context, feedback)
            
        # Run the 'Geometry by Expression' to get the "full" shadow shapes
        temp_shadow_id = self._run_geometry_by_expression(
            parameters, 
            context, 
            feedback, 
            height_value_expression
        )
        
        if temp_shadow_id is None:
            return {}
        
        final_temp_layer = QgsProcessingUtils.mapLayerFromString(temp_shadow_id, context)

        # Handle the Final Output Sink
        (sink_main, dest_id_main) = self.parameterAsSink(
            parameters, self.OUTPUT,
            context, final_temp_layer.fields(), final_temp_layer.wkbType(), final_temp_layer.sourceCrs()
        )
        
        if sink_main is None:
            return {}

        # Copy features from the difference result to the main output sink
        features_main = final_temp_layer.getFeatures()
        for feature in features_main:
            sink_main.addFeature(feature, QgsFeatureSink.FastInsert)

        # Apply basic styling
        output_layer_main = QgsProcessingUtils.mapLayerFromString(dest_id_main, context)
        if output_layer_main:
            self._post_process_layer(output_layer_main)

        return {self.OUTPUT: dest_id_main}
    
# ----------------------------------------------------------------------
## Metadata Methods
# ----------------------------------------------------------------------

    def name(self):
        return 'Create cast shadow'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Algorithms for Vector Polygon Layer'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return QuickShadowAlgorithm()