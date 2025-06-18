import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

from marc21.lib.marcDictionary import MarcDictionary
from marc21.lib.marcException import (MarcException,
                                      MarcInvalidTagException,
                                      MarcInvalidSubfieldException,
                                      MarcSubfieldNotRepeatableException)
from marc21.lib.marcFields import SubField, MarcField

marc_dict = MarcDictionary()

# Constants
FIELD_TERMINATOR = b'\x1E'
RECORD_TERMINATOR = b'\x1D'
SUBFIELD_DELIMITER = b'\x1F'
LEADER_LENGTH = 24
DIRECTORY_ENTRY_LENGTH = 12

def add_field_to_list(field: MarcField) -> None:
    marc_dict.add_field_to_list(field=field)


def add_additional_fields_to_list(fields: list[MarcField]) -> None:
    marc_dict.add_additional_fields_to_list(fields=fields)


def add_additional_subfield_to_field_in_list(tag: str, subfield: SubField) -> None:
    marc_dict.add_additional_subfield_to_field_in_list(tag=tag, subfield=subfield)

def switch_type_of_field(tag: str):
    marc_dict.switch_type_of_field(tag)


def switch_repeatability_of_field(tag: str):
    marc_dict.switch_repeatability_of_field(tag)


def get_dictionary(verbose: bool = False, tag:str = ''):
    return marc_dict.get_dictionary(verbose, show_tag=tag)


@dataclass(init=False, eq=True, order=True)
class BaseField:
    tag: str
    description: str
    field_type: str
    field_separator: str
    subfield_separator: str

    def __init__(self, tag: str, description: str, field_type: str):
        self.tag = tag
        self.description = description
        self.field_type = field_type
        self.field_separator = '^^'
        self.subfield_separator = '^_'

    def __len__(self):
        return 0

    def __del__(self):
        del self.tag
        del self.description
        del self.field_type
        del self.field_separator
        del self.subfield_separator

    def set_separators(self, field_separator: str, subfield_separator: str):
        self.field_separator = field_separator
        self.subfield_separator = subfield_separator


# class for control fields (tag 000 - 009)
@dataclass(eq=True, order=True)
class CField(BaseField):
    data: str

    def __init__(self, tag: str, description: str, data: str):
        super().__init__(tag, description.strip(), 'c')
        if tag == '' or data == '':
            raise MarcException('Tag and data cannot be empty for CField')

        valid = marc_dict.validate_field(tag=tag, fieldtype='c')

        if not valid:
            raise MarcInvalidTagException(tag, 'as a CField')

        self.data = data
        self.field_type = 'c'

    def __del__(self):
        super().__del__()

    def __repr__(self, show_description: bool = False, extra_space: bool = False) -> str:
        msg: list[str] = []
        separator: str = ' ' if extra_space else ''

        if show_description:
            msg.append(f"{self.field_separator}{self.tag} [{self.description}]{separator}")
        else:
            msg.append(f"{self.field_separator}{self.tag}{separator}")

        msg.append(self.data)

        return self.subfield_separator.join(msg)

    def __len__(self):
        return len(self.tag) + len(self.data)

    def __json__(self):
        return {
            'tag': self.tag,
            'data': self.data
        }

    def __xml__(self, record: ET.Element):
        cf = ET.SubElement(record,'controlfield', tag=self.tag)
        cf.text = self.data
        return cf

@dataclass(eq=True, order=True)
class DField(BaseField):
    indicators: str
    subfields: list[SubField]

    def __init__(self, tag: str, description: str, indicators: str, subfields: list[SubField]):
        super().__init__(tag, description.strip(), 'd')
        if tag == '':
            raise MarcException('Tag cannot be empty for DField')

        valid = marc_dict.validate_field(tag=tag, fieldtype='d')

        if not valid:
            raise MarcInvalidTagException(tag, 'as a DField')

        self.indicators = indicators
        self.subfields = subfields.copy()
        self.field_type = 'd'

    def __del__(self):
        super().__del__()


    def __repr__(self, show_description: bool = False, extra_space: bool = False) -> str:
        msg: list[str] = []
        indicator: str = self.indicators if self.indicators else '  '
        separator: str = ' ' if extra_space else ''

        if show_description:
            msg.append(f'{self.field_separator}{self.tag}{separator}[{self.description}]{indicator}')
        else:
            msg.append(f'{self.field_separator}{self.tag}{separator}{indicator}')

        for s in self.subfields:
            msg.append(s.__repr__(show_description))

        return self.subfield_separator.join(msg)

    def __len__(self):
        return len(self.tag) + len(self.indicators) + sum(len(sf) for sf in self.subfields)

    def addSubField(self, tag: str, value: str):
        repeatable: bool = True
        valid_sf: list[SubField] = marc_dict.get_valid_subfields_for_field(tag=self.tag)
        new_sf: Optional[SubField] = None

        for sf in valid_sf:
            if sf.tag == tag:
                new_sf = sf.__copy__()
                repeatable = sf.repeatable
                new_sf.value = value
                break

        if new_sf is not None:
            if not repeatable:
                found = [sf for sf in self.subfields if sf.tag == tag]

                if len(found) > 0:
                    raise MarcSubfieldNotRepeatableException(tag, self.tag, '')

            self.subfields.append(new_sf)
        else:
            raise MarcInvalidSubfieldException(tag, self.tag, '')

        return self

    def __json__(self):
        return {
            'tag': self.tag,
            'indicators': self.indicators,
            'subfields': [sf.__json__() for sf in self.subfields]
        }

    def __xml__(self, record: ET.Element):
        df = ET.SubElement(record, 'datafield', tag = self.tag, ind1 = self.indicators[0], ind2 = self.indicators[1])

        for sf in self.subfields:
            sf.__xml__(df)

        return df

    def set_indicators(self, indicators: str):
        self.indicators = indicators

@dataclass
class MarcDto:
    _cfields: list[CField] = field(default_factory=list)
    _dfields: list[DField] = field(default_factory=list)
    _field_separator: str = ' '
    _subfield_separator: str = ' '
    extra_space: bool = False

    def __init__(self, field_separator: str = '', subfield_separator: str = '', extra_space: bool = False):
        self._field_separator = field_separator or ' '
        self._subfield_separator = subfield_separator or ' '
        self.extra_space = extra_space
        self._cfields = []
        self._dfields = []

    def __del__(self):
        for cf in self._cfields:
            del cf
        del self._cfields

        for df in self._dfields:
            del df
        del self._dfields

    def __repr__(self, show_description: bool = False) -> str:
        msg: list[str] = [f.__repr__(show_description, self.extra_space) for f in self._cfields] + [f.__repr__(show_description, self.extra_space) for f in
                                                                                  self._dfields]
        msg.sort()

        return '\n'.join(msg)

    def to_string(self, show_description: bool = False) -> str:
        msg: list[str] = [f.__repr__(show_description, self.extra_space) for f in self._cfields] + [f.__repr__(show_description, self.extra_space) for f in
                                                                                  self._dfields]
        msg.sort()

        return '\n'.join(msg)

    def __len__(self, count_characters: bool = False) -> int:
        if count_characters:
            return sum([len(f) for f in self._cfields]) + sum([len(f) for f in self._dfields])
        else:
            return len(self._cfields) + len(self._dfields)

    def __json__(self):
        jslist = []
        for cf in self._cfields:
            jslist.append(cf.__json__())
        for df in self._dfields:
            jslist.append(df.__json__())

        jslist.sort(key=lambda x: x['tag'])

        return json.dumps(jslist)

    def __xml__(self):
        root = ET.Element('collection', xmlns = 'http://www.loc.gov/MARC21/slim')

        record = ET.SubElement(root, 'record')
        leader = ET.SubElement(record, 'leader')
        leader.text = '00000np a 4500'

        for cf in self._cfields:
            cf.__xml__(record)
        for df in self._dfields:
            df.__xml__(record)

        # tree = ET.ElementTree(root)

        return ET.tostring(root, encoding='unicode', method='xml', xml_declaration=True)

    def from_text(self, text: str):
        lfs = len(self._field_separator)
        for line in text.split('\n'):
            if line.startswith('#'):
                continue
            elif line.startswith(self._field_separator):
                line = line[lfs:]
                tag = line[0:3]
                line = line[3:]

                mf = self.create_field(tag, indicators=line[0:2], data=line[2:], subfields=[])

                if mf is None:
                    raise MarcException('Unknown tag \'%s\' encountered on line \'%s\'' % (tag, line))

                if mf.field_type == 'd':
                    line = line[2:]

                    if line[0] == self._subfield_separator:
                        line = line[1:]

                    for subfield in line.split(self._subfield_separator):
                        if len(subfield) > 2:
                            mf.addSubField(subfield[0], subfield[1:])
                        else:
                            raise MarcException("Invalid subfield '%s' in line '%s'" % (subfield, line))

                self.insert_field(mf)
            else:
                raise MarcException('Line \'%s\' does not start with field separator \'%s\'' % (line, self._field_separator))

        return self

    def set_separators(self, field_separator: str, subfield_separator: str) -> object:
        if field_separator == '' or subfield_separator == '':
            return

        self._field_separator = field_separator
        self._subfield_separator = subfield_separator

        for cf in self._cfields:
            cf.set_separators(field_separator, subfield_separator)
        for df in self._dfields:
            df.set_separators(field_separator, subfield_separator)


    def as_list(self, show_description: bool = False) -> list[str]:
        msg: list[str] = ([f.__repr__(show_description, self.extra_space) for f in self._cfields]
                       +  [f.__repr__(show_description, self.extra_space) for f in self._dfields])
        msg.sort()

        return msg

    def __create_cfield(self, tag: str, description: str, data: str) -> CField:
        cf = CField(tag=tag, description=description, data=data)
        cf.set_separators(self._field_separator, self._subfield_separator)
        return cf


    def __create_dfield(self, tag: str, definition: MarcField, indicators: str,
                        subfields: list[SubField]) -> DField:
        if indicators != '':
            field_indicators = indicators
        else:
            field_indicators = definition.indicators

        subs: list[SubField] = []
        for s in subfields:
            for d in definition.subfields:
                if d.tag == s.tag:
                    sf = d
                    sf.value = s.value
                    subs.append(sf)

        df = DField(tag=tag, description=definition.description, indicators=field_indicators, subfields=subs)
        df.set_separators(self._field_separator, self._subfield_separator)
        return df

    def create_field(self, tag: str, indicators: str = '', data: str = '',
                     subfields=None) -> CField | DField:

        if subfields is None:
            subfields = []

        definition = marc_dict.find_definition_for_field(tag=tag)

        if not definition:
            raise MarcException('Attempt to add non-existing field \'%s\'' % tag)

        if not definition.repeatable and self.is_tag_present(tag):
            raise MarcException('Attempt to add non-repeatable field \'%s\' more than once' % tag)

        if definition.type == 'c':
            return self.__create_cfield(tag, definition.description, data)
        else:
            return self.__create_dfield(tag, definition, indicators, subfields)

    def insert_field(self, marc_field: CField | DField):
        match marc_field.field_type:
            case 'c':
                if marc_field not in self._cfields:
                    self._cfields.append(marc_field)

            case 'd':
                if marc_field not in self._dfields:
                    self._dfields.append(marc_field)

    def is_tag_present(self, tag: str) -> bool:
        all_fields: list[BaseField] = self._dfields + self._cfields

        for f in all_fields:
            if f.tag == tag:
                return True

        return False

    def perform_filter(self, tag_present: str, tag_remove: str):
        if tag_present == '' or tag_remove == '':
            return

        if tag_present == tag_remove:
            return

        if self.is_tag_present(tag_present) and self.is_tag_present(tag_remove):
            new_dfields: list[DField] = [f for f in self._dfields if f.tag != tag_remove]

            self._dfields = new_dfields

        return self

def load_marc21_from_text(text: str, field_separator: str = '', subfield_separator: str = '') -> MarcDto:
    dto = MarcDto(field_separator=field_separator, subfield_separator=subfield_separator)

    return dto.from_text(text)

def from_iso2709(data: bytes, extra_space:bool = False) -> MarcDto:
    if not data.endswith(RECORD_TERMINATOR):
        raise ValueError("Record does not end with ISO 2709 record terminator (0x1D).")

    leader = data[:LEADER_LENGTH].decode('utf-8')
    try:
        record_length = int(leader[0:5])
        base_address = int(leader[12:17])
    except ValueError:
        raise ValueError("Invalid leader: cannot extract record length or base address.")

    directory_data = data[LEADER_LENGTH:base_address]  # ends with FIELD_TERMINATOR
    field_data = data[base_address:-1]  # exclude RECORD_TERMINATOR

    if not directory_data.endswith(FIELD_TERMINATOR):
        raise ValueError("Directory does not end with field terminator (0x1E).")

    dto = MarcDto(extra_space=extra_space)
    pos = 0
    while pos + DIRECTORY_ENTRY_LENGTH <= len(directory_data):
        entry = directory_data[pos:pos + DIRECTORY_ENTRY_LENGTH]
        tag = entry[0:3].decode('utf-8')
        length = int(entry[3:7].decode('utf-8'))
        offset = int(entry[7:12].decode('utf-8'))
        field_bytes = field_data[offset:offset + length - 1]  # exclude 0x1E

        # Decide if it's control field or data field
        if tag < '010':  # Control field (000-009)
            value = field_bytes.decode('utf-8')
            try:
                fld = dto.create_field(tag=tag, data=value)
                dto.insert_field(fld)
            except MarcInvalidTagException:
                pass  # unknown field, skip
        else:
            indicators = field_bytes[:2].decode('utf-8')
            subfields_raw = field_bytes[2:].split(SUBFIELD_DELIMITER)[1:]  # first split is empty

            subfields: list[SubField] = []
            for raw in subfields_raw:
                if len(raw) == 0:
                    continue
                code = chr(raw[0])
                value = raw[1:].decode('utf-8')
                try:
                    sf = SubField(tag=code, value=value)  # repeatable doesn't matter at runtime
                    subfields.append(sf)
                except Exception:
                    continue

            try:
                fld = dto.create_field(tag=tag, indicators=indicators, subfields=subfields)
                dto.insert_field(fld)
            except MarcInvalidTagException:
                pass  # skip unknown fields

        pos += DIRECTORY_ENTRY_LENGTH

    return dto


def to_iso2709(dto: MarcDto) -> bytes:
    fields_data = b''
    directory = b''
    current_position = 0

    for field in dto._cfields + dto._dfields:
        tag = field.tag.encode('utf-8')

        if isinstance(field, CField):
            content = field.data.encode('utf-8')
        elif isinstance(field, DField):
            content = field.indicators.encode('utf-8')
            for sf in field.subfields:
                content += SUBFIELD_DELIMITER + sf.tag.encode('utf-8') + sf.value.encode('utf-8')
        else:
            continue  # skip unknown

        content += FIELD_TERMINATOR
        length = len(content)
        fields_data += content

        directory += tag.ljust(3, b' ')  # tag
        directory += f"{length:0>4}".encode('utf-8')  # field length
        directory += f"{current_position:0>5}".encode('utf-8')  # starting position
        current_position += length

    directory += FIELD_TERMINATOR
    base_address = LEADER_LENGTH + len(directory)
    record_length = base_address + len(fields_data) + 1  # +1 for RECORD_TERMINATOR

    leader = bytearray(' ' * LEADER_LENGTH, 'utf-8')
    leader[0:5] = f"{record_length:05}".encode('utf-8')
    leader[12:17] = f"{base_address:05}".encode('utf-8')
    leader[20] = ord(' ')  # entry map default
    leader[21] = ord(' ')  # entry map default

    return bytes(leader) + directory + fields_data + RECORD_TERMINATOR


def from_marcxml(xml_string: str, extra_space:bool = False) -> MarcDto:
    dto = MarcDto(extra_space=extra_space)
    tree = ET.fromstring(xml_string)

    ns = {'marc': 'http://www.loc.gov/MARC21/slim'}
    record = tree.find('marc:record', ns)
    if record is None:
        raise ValueError("No MARC record found in XML")

    for field in record:
        tag = field.attrib.get('tag')
        if field.tag.endswith('controlfield'):
            value = field.text or ''
            dto.insert_field(dto.create_field(tag=tag, data=value))
        elif field.tag.endswith('datafield'):
            ind1 = field.attrib.get('ind1', ' ')
            ind2 = field.attrib.get('ind2', ' ')
            indicators = ind1 + ind2
            subfields = []
            for sub in field.findall('marc:subfield', ns):
                code = sub.attrib.get('code')
                value = sub.text or ''
                if code:
                    subfields.append(SubField(tag=code, value=value))
            dto.insert_field(dto.create_field(tag=tag, indicators=indicators, subfields=subfields))

    return dto

def to_marcxml(dto: MarcDto) -> str:
    return dto.__xml__()

