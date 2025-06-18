from .lib import *
from .marc21 import *

__version__ = "0.5.0"
__all__ = ["MarcException", "MarcDto", "SubField", "MarcField", "get_dictionary", "add_additional_fields_to_list"] + \
          ["add_field_to_list", "switch_repeatability_of_field", "switch_type_of_field"] + \
          ["add_additional_subfield_to_field_in_list", "from_iso2709", "to_iso2709"] + \
          ["from_marcxml", "to_marcxml"]