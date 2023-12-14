import json
from dataclasses import dataclass, field
from typing import Optional
from marc21.lib.marcException import MarcException
from marc21.lib.marcFields import SubField, MarcField
from marc21.lib.marcDictionary import MarcDictionary

marc_dict = MarcDictionary()


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
            raise MarcException('Tag %s is not defined as a CField' % tag)

        self.data = data
        self.field_type = 'c'

    def __del__(self):
        super().__del__()

    def __repr__(self, show_description: bool = False) -> str:
        msg: list[str] = []

        if show_description:
            msg.append('%s%s [%s]' % (self.field_separator, self.tag, self.description))
        else:
            msg.append('%s%s' % (self.field_separator, self.tag))

        msg.append(self.data)

        return self.subfield_separator.join(msg)

    def __json__(self):
        return {
            'tag': self.tag,
            'data': self.data
        }


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
            raise MarcException('Tag %s is not defined as a DField' % tag)

        self.indicators = indicators
        self.subfields = subfields.copy()
        self.field_type = 'd'

    def __del__(self):
        super().__del__()


    def __repr__(self, show_description: bool = False) -> str:
        msg: list[str] = []

        if show_description:
            msg.append('%s%s [%s]%s' % (self.field_separator, self.tag, self.description, self.indicators))
        else:
            msg.append('%s%s%s' % (self.field_separator, self.tag, self.indicators))

        for s in self.subfields:
            msg.append(s.__repr__(show_description))

        return self.subfield_separator.join(msg)

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
                    raise MarcException(
                        'Non repeatable subfield \'$%s\' tried to be added more than once to field \'%s\'' % (
                        tag, self.tag))

            self.subfields.append(new_sf)
        else:
            raise MarcException('Subfield \'%s\' is not defined for field \'%s\'' % (tag, self.tag))

        return self

    def __json__(self):
        return {
            'tag': self.tag,
            'indicators': self.indicators,
            'subfields': [sf.__json__() for sf in self.subfields]
        }


@dataclass
class MarcDto:
    _cfields: list[CField] = field(default_factory=list)
    _dfields: list[DField] = field(default_factory=list)
    _field_separator: str = ' '
    _subfield_separator: str = ' '

    def __init__(self):
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
        msg: list[str] = [f.__repr__(show_description) for f in self._cfields] + [f.__repr__(show_description) for f in
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

    def set_separators(self, field_separator: str, subfield_separator: str):
        if field_separator == '' or subfield_separator == '':
            return

        self._field_separator = field_separator
        self._subfield_separator = subfield_separator

        for cf in self._cfields:
            cf.set_separators(field_separator, subfield_separator)
        for df in self._dfields:
            df.set_separators(field_separator, subfield_separator)


    def as_list(self, show_description: bool = False) -> list[str]:
        msg: list[str] = [f.__repr__(show_description) for f in self._cfields] + [f.__repr__(show_description) for f in
                                                                                  self._dfields]
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
