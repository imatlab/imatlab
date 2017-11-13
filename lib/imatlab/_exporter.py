from pathlib import Path

from nbconvert.exporters.html import TemplateExporter
from traitlets import default


class MatlabExporter(TemplateExporter):

    @default("file_extension")
    def _file_extension_default(self):
        return ".m"

    @default("template_path")
    def _template_path_default(self):
        return [str(Path(__file__).with_name("resources"))]

    @default("template_file")
    def _template_file_default(self):
        return "matlab"

    @default("output_mimetype")
    def _output_mimetype_default(self):
        return "text/x-matlab"
