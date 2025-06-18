import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

# local imports
from .marcException import MarcSubfieldException, MarcUnknownFieldTypeException, MarcSubfieldNotRepeatableException

@dataclass(init=False, eq=True, order=True)
class SubField:
    """
    The SubField class represents a subfield in the MARC (Machine-Readable Cataloging) data format. It stores information about the tag, repeatability, description, and value of the subfield.
    """
    tag: str
    repeatable: bool
    description: str = ''
    value: str = ''

    def __init__(self, tag: str = '', repeatable: bool = True, description: str = '', value: str = 'dummy'):
        if tag == '' or value == '':
            raise MarcSubfieldException(tag='', subfield=tag, value=value, reason='')

        self.tag = tag
        self.repeatable = repeatable
        self.description = description
        self.value = value

    def __repr__(self, show_description: bool = False) -> str:
        tag = getattr(self, 'tag', '<?>')
        value = getattr(self, 'value', '<?>')
        description = getattr(self, 'description', '')
        if show_description and description:
            return f'{tag} [{description}] {value}'
        return f'{tag}{value}'

    def __copy__(self):
        return SubField(self.tag, self.repeatable, self.description, self.value)

    def __len__(self):
        return len(self.tag) + len(self.value)

    def __json__(self):
        return {
            'tag': self.tag,
            'description': self.description,
            'value': self.value
        }

    def __xml__(self, root : ET.Element):
        sf = ET.SubElement(root, 'subfield', code=self.tag, description=self.description)
        sf.text = self.value

        return sf


@dataclass(init=False)
class MarcField:
    """
    The MarcField class represents a field in the MARC (Machine-Readable Cataloging) data format. It stores information about the tag, type, repeatability, description, indicators, data, and subfields of the field.
    """
    tag: str
    type: str
    repeatable: bool
    description: str
    has_indicators: bool
    indicators: str
    data: str
    subfields: list[SubField] = field(default_factory=list)

    def __init__(self, tag: str, fieldtype: str, repeatable: bool = False, description: str = 'not supplied',
                 has_indicators: bool = True,
                 indicators: str = '  ',
                 data: str = '  ',
                 subfields: Optional[list[SubField]] = None) -> None:
        self.tag = tag
        self.type = fieldtype
        self.repeatable = repeatable
        self.description = description
        self.data = data
        self.indicators = indicators
        self.subfields = []
        if subfields is not None:
            for sf in subfields:
                self.subfields.append(sf)

        if self.type == 'c':
            self.has_indicators = False
        elif self.type == 'd':
            self.has_indicators = has_indicators
        else:
            raise MarcUnknownFieldTypeException(tag=tag, type=fieldtype, reason='')

    def __del__(self):
        if self.type == 'c':
            del self.data
        else:
            del self.indicators
            for sf in self.subfields:
                del sf
            del self.subfields

        del self.tag
        del self.type
        del self.repeatable
        del self.description

    def __copy__(self):
        mf = MarcField(self.tag,
                       self.type,
                       self.repeatable,
                       self.description,
                       self.has_indicators,
                       '  ',
                       '',
                       []
                       )

        if mf.type == 'c':
            mf.data = self.data
        else:
            mf.indicators = self.indicators
            mf.subfields = [sf.__copy__() for sf in self.subfields]

        return mf

    def __json__(self):
        if self.type == 'c':
            return {
                'tag': self.tag,
                'type': self.type,
                'description': self.description
            }
        else:
            return {
                'tag': self.tag,
                'type': self.type,
                'description': self.description,
                'has_indicators': self.has_indicators,
                'indicators': self.indicators,
                'subfields': [sf.__json__() for sf in self.subfields]
            }

    def add_SubField(self, new_sf: SubField =None, tag: str ='', repeatable: bool =False, description :str =''):
        """
        The add_SubField method is used to add a new subfield to the MarcField object. It checks if the subfield is repeatable and if a subfield with the same tag already exists. If the subfield is not repeatable and a subfield with the same tag already exists, it raises a MarcException. Otherwise, it appends the new subfield to the list of subfields in the MarcField object.
        :param new_sf:  The new subfield to be added to the MarcField object
        :return:  Updated MarcField object with the new subfield added.
        """
        if new_sf is None:
            if tag == '':
                raise MarcSubfieldException(tag=self.tag, subfield='', value='', reason='')

            new_sf = SubField(tag, repeatable, description)

        if not new_sf.repeatable:
            for sf in self.subfields:
                if sf.tag == new_sf.tag:
                    raise MarcSubfieldNotRepeatableException(subfield=new_sf.tag, tag=self.tag, extra_reason='')

        self.subfields.append(new_sf)

        return self


    def set_indicators(self, indicators: str = '  '):
        """
        The set_indicators method is used to set the value of the indicators attribute in the MarcField class.
        :param indicators:  indicators (optional): A string representing the indicators for the field. Default value is two spaces (' ').
        :return: None
        """
        self.indicators = indicators

    def is_subfield_present(self, tag: str) -> bool:
        """
        Check if a subfield with the given tag is present.

        Args:
            tag (str): The tag to search for.

        Returns:
            bool: True if a subfield with the given tag is present, False otherwise.
        """
        if tag is None or tag == '':
            return False

        if self.subfields is None or self.subfields == []:
            return False

        for sf in self.subfields:
            if sf.tag == tag:
                return True

        return False

    def get_subfields(self) -> list[SubField]:
        """
        Return the subfields of the object.

        If the type of the object is 'd', return the list of subfields.
        Otherwise, return an empty list.
        """
        if self.type == 'd' and self.subfields:
            return self.subfields
        else:
            return []
