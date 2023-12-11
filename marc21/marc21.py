import json
from dataclasses import dataclass, field


class MarcException(Exception):
    """
    The MarcException class is a custom exception class that is used to raise exceptions specific to the MARC (Machine-Readable Cataloging) data format.
    """
    reason: str

    def __init__(self, reason: str):
        if str == '':
            self.reason = 'Unknown reason'
        else:
            self.reason = reason

    def __del__(self):
        del self.reason

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
        if tag == '':
            raise MarcException('Subfield without a tag encountered')

        if value == '':
            raise MarcException('Subfield without value encountered')

        self.tag = tag
        self.repeatable = repeatable
        self.description = description
        self.value = value

    def __repr__(self, show_description: bool = False):
        if show_description:
            return '%s [%s] %s' % (self.tag, self.description, self.value)
        else:
            return '%s%s' % (self.tag, self.value)

    def __copy__(self):
        return SubField(self.tag, self.repeatable, self.description, self.value)

    def __del__(self):
        del self.tag
        del self.repeatable
        del self.description
        del self.value


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

    def __init__(self, tag: str, type: str, repeatable: bool = False, description: str = 'not supplied',
                 has_indicators: bool = True,
                 indicators: str = '  ',
                 data: str = '  ',
                 subfields: list[SubField] = []) -> object:
        self.tag = tag
        self.type = type
        self.repeatable = repeatable
        self.description = description

        if self.type == 'c':
            self.data = data
            self.has_indicators = False
        elif self.type == 'd':
            self.has_indicators = has_indicators
            self.indicators = indicators
            self.subfields = subfields
        else:
            raise MarcException('Field \'%s\' has unknown type \'%s\'' % (tag, type))

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
        del self.has_indicators


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

    def add_SubField(self, new_sf: SubField=None, tag: str='', repeatable: bool=False, description:str=''):
        """
        The add_SubField method is used to add a new subfield to the MarcField object. It checks if the subfield is repeatable and if a subfield with the same tag already exists. If the subfield is not repeatable and a subfield with the same tag already exists, it raises a MarcException. Otherwise, it appends the new subfield to the list of subfields in the MarcField object.        
        :param new_sf:  The new subfield to be added to the MarcField object
        :return:  Updated MarcField object with the new subfield added.
        """
        if new_sf is None:
            if tag == '':
                raise MarcException('Insufficient data supplied to create a new subfield for tag %s' % self.tag)

            new_sf = SubField(tag, repeatable, description)

        if not new_sf.repeatable:
            for sf in self.subfields:
                if sf.tag == new_sf.tag:
                    raise MarcException('Non-repeatable subfield %s repeated for tag %s' % (new_sf.tag, self.tag))

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

        if self.subfields is None:
            return False

        for sf in self.subfields:
            if sf.tag == tag:
                return True

        return False

"""
Create the FIELDS list and fill it with the standard MARCFields, with for datafields the allowed subfields
"""
FIELDS: list[MarcField] = [
    MarcField('001', 'c', False, 'Control Number', False, '', '', []),
    MarcField('003', 'c', False, 'Control Number Identifier', False, '', '', []),
    MarcField('005', 'c', False, 'Date and Time of Latest Transaction', False, '', '', []),
    MarcField('006', 'c', False, 'Fixed-Length Data Elements - Additional Material Characteristics', False, '', '', []),
    MarcField('007', 'c', False, 'Physical Description Fixed Field-General Information', False, '', '', []),
    MarcField('008', 'c', False, 'Fixed-Length Data Elements', False, '', '', []),
    MarcField('010', 'd', False, 'Library of Congress Control Number', True, '  ', '', [
        SubField('a', False, 'LC control number'),
        SubField('b', True, 'NUCMC control number'),
        SubField('z', True, 'Cancelled/Invalid LC control number'),
        SubField('8', True, 'Field Link and Sequence number')
    ]),
    MarcField('013', 'd', True, 'Patent Control Information', True, '  ', '', [
        SubField('a', False, 'Number'),
        SubField('b', True, 'Country'),
        SubField('c', True, 'Type of number'),
        SubField('d', True, 'Date'),
        SubField('e', True, 'Status'),
        SubField('f', True, 'Party of document'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('015', 'd', True, 'National Bibliography Number', True, '  ', '', [
        SubField('a', False, 'National Bibliography number'),
        SubField('q', True, 'Qualifying information'),
        SubField('z', True, 'Cancelled/Invalid national bibliography number'),
        SubField('2', False, 'Source'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('017', 'd', True, 'Copyright or legal deposit number', True, '  ', '', [
        SubField('a', False, 'Copyright or legal deposit number'),
        SubField('b', True, 'Assigning agency'),
        SubField('d', True, 'Date'),
        SubField('i', True, 'Display Text'),
        SubField('z', True, 'Cancelled/Invalid Copyright or legal deposit number'),
        SubField('2', False, 'Source'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('018', 'd', False, 'Copyright Article-Fee Code ', True, '  ', '', [
        SubField('a', False, 'Copyright article-fee code'),
        SubField('6', True, 'Linkage')
    ]),
    MarcField('020', 'd', True, 'International Standard Book Number ', True, '  ', '', [
        SubField('a', False, 'International Standard Book Number'),
        SubField('c', True, 'Terms of availability'),
        SubField('q', True, 'Qualifying information'),
        SubField('z', True, 'Canceled/invalid ISBN'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('022', 'd', True, 'International Standard Serial Number ', True, '  ', '', [
        SubField('a', False, 'International Standard Serial Number'),
        SubField('l', True, 'ISSN-L'),
        SubField('m', True, 'Canceled ISSN-L'),
        SubField('y', True, 'Incorrect ISSN'),
        SubField('z', True, 'Canceled ISSN'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('024', 'd', True, 'Other Standard Identifier ', True, '  ', '', [
        SubField('a', False, 'Standard number or code'),
        SubField('c', True, 'Terms of availability'),
        SubField('d', True, 'Additional codes following the standard number or code'),
        SubField('q', True, 'Qualifying information'),
        SubField('z', True, 'Canceled/invalid standard number or code'),
        SubField('2', True, 'Source of number or code'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('025', 'd', True, 'Overseas Acquisition Number ', True, '  ', '', [
        SubField('a', False, 'Overseas acquisition number'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('026', 'd', True, 'Fingerprint Identifier ', True, '  ', '', [
        SubField('a', False, 'First and second groups of characters'),
        SubField('b', True, 'Third and fourth groups of characters'),
        SubField('c', True, 'Date'),
        SubField('d', True, 'Number of volume or part'),
        SubField('e', True, 'Unparsed fingerprint'),
        SubField('2', False, 'Source'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('027', 'd', True, 'Standard Technical Report Number ', True, '  ', '', [
        SubField('a', False, 'Standard technical report number'),
        SubField('q', True, 'Qualifying information'),
        SubField('z', True, 'Canceled/invalid number'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('028', 'd', True, 'Publisher or Distributor Number ', True, '  ', '', [
        SubField('a', False, 'Publisher or distributor number'),
        SubField('b', True, 'Source'),
        SubField('q', True, 'Qualifying information'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('030', 'd', True, 'CODEN Designation ', True, '  ', '', [
        SubField('a', False, 'CODEN'),
        SubField('z', True, 'Canceled/invalid CODEN'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('031', 'd', True, 'Musical Incipits Information ', True, '  ', '', [
        SubField('a', False, 'Number of work'),
        SubField('b', True, 'Number of movement'),
        SubField('c', True, 'Number of excerpt'),
        SubField('d', True, 'Caption or heading'),
        SubField('e', True, 'Role'),
        SubField('g', True, 'Clef'),
        SubField('m', True, 'Voice/instrument'),
        SubField('n', True, 'Key signature'),
        SubField('o', True, 'Time signature'),
        SubField('p', True, 'Musical notation'),
        SubField('q', True, 'General note'),
        SubField('r', True, 'Key or mode'),
        SubField('s', True, 'Coded validity note'),
        SubField('t', True, 'Text incipit'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('y', True, 'Link text'),
        SubField('z', True, 'Public note'),
        SubField('2', True, 'System code'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('032', 'd', True, 'Postal Registration Number ', True, '  ', '', [
        SubField('a', False, 'Postal registration number'),
        SubField('b', True, 'Source agency assigning number'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('033', 'd', True, 'Date/Time and Place of an Event ', True, '  ', '', [
        SubField('a', False, 'Formatted date/time'),
        SubField('b', True, 'Geographic classification area code'),
        SubField('c', True, 'Geographic classification subarea code'),
        SubField('p', True, 'Place of event'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of term'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('034', 'd', True, 'Coded Cartographic Mathematical Data ', True, '  ', '', [
        SubField('a', False, 'Category of scale'),
        SubField('b', True, 'Constant ratio linear horizontal scale'),
        SubField('c', True, 'Constant ratio linear vertical scale'),
        SubField('d', True, 'Coordinates - westernmost longitude'),
        SubField('e', True, 'Coordinates - easternmost longitude'),
        SubField('f', True, 'Coordinates - northernmost latitude'),
        SubField('g', True, 'Coordinates - southernmost latitude'),
        SubField('h', True, 'Angular scale'),
        SubField('j', True, 'Declination - northern limit'),
        SubField('k', True, 'Declination - southern limit'),
        SubField('m', True, 'Right ascension - eastern limit'),
        SubField('n', True, 'Right ascension - western limit'),
        SubField('p', True, 'Equinox'),
        SubField('r', True, 'Distance from earth'),
        SubField('s', True, 'G-ring latitude'),
        SubField('t', True, 'G-ring longitude'),
        SubField('x', True, 'Beginning date'),
        SubField('y', True, 'Ending date'),
        SubField('z', True, 'Name of extraterrestrial body'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('035', 'd', True, 'System Control Number ', True, '  ', '', [
        SubField('a', False, 'System control number'),
        SubField('z', True, 'Canceled/invalid control number'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'),
    ]),
    MarcField('036', 'd', True, 'Original Study Number for Computer Data Files ', True, '  ', '', [
        SubField('a', False, 'Original study number'),
        SubField('b', True, 'Source agency assigning number'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('037', 'd', True, 'Source of Acquisition ', True, '  ', '', [
        SubField('a', False, 'Stock number'),
        SubField('b', True, 'Source of stock number/acquisition'),
        SubField('c', True, 'Terms of availability'),
        SubField('f', True, 'Form of issue'),
        SubField('g', True, 'Additional format characteristics'),
        SubField('n', True, 'Note'),
        SubField('3', True, 'Materials specified'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('038', 'd', False, 'Record Content Licensor ', True, '  ', '', [
        SubField('a', False, 'Record content licensor'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('040', 'd', False, 'Cataloging Source ', True, '  ', '', [
        SubField('a', False, 'Original cataloging agency'),
        SubField('b', True, 'Language of cataloging'),
        SubField('c', True, 'Transcribing agency'),
        SubField('d', True, 'Modifying agency'),
        SubField('e', True, 'Description conventions'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('041', 'd', True, 'Language Code ', True, '  ', '', [
        SubField('a', False, 'Language code of text/sound track or separate title'),
        SubField('b', True, 'Language code of summary or abstract'),
        SubField('d', True, 'Language code of sung or spoken text'),
        SubField('e', True, 'Language code of librettos'),
        SubField('f', True, 'Language code of table of contents'),
        SubField('g', True, 'Language code of accompanying material other than librettos and transcripts'),
        SubField('h', True, 'Language code of original'),
        SubField('i', True, 'Language code of intertitles'),
        SubField('j', True, 'Language code of subtitles'),
        SubField('k', True, 'Language code of intermediate translations'),
        SubField('m', True, 'Language code of original accompanying materials other than librettos'),
        SubField('n', True, 'Language code of original libretto'),
        SubField('p', True, 'Language code of captions'),
        SubField('q', True, 'Language code of accessible audio'),
        SubField('r', True, 'Language code of accessible visual language (non-textual)'),
        SubField('t', True, 'Language code of accompanying transcripts for audiovisual materials'),
        SubField('2', True, 'Source of code'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('042', 'd', False, 'Authentication Code ', True, '  ', '', [
        SubField('a', False, 'Authentication code')]),
    MarcField('043', 'd', True, 'Geographic Area Code ', True, '  ', '', [
        SubField('a', False, 'Geographic area code'),
        SubField('b', True, 'Local GAC code'),
        SubField('c', True, 'ISO code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of local code'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('044', 'd', False, 'Country of Publishing/Producing Entity Code ', True, '  ', '', [
        SubField('a', False, 'MARC country code'),
        SubField('b', True, 'Local subentity code'),
        SubField('c', True, 'ISO country code'),
        SubField('2', True, 'Source of local subentity code'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('045', 'd', False, 'Time Period of Content ', True, '  ', '', [
        SubField('a', False, 'Time period code'),
        SubField('b', True, 'Formatted 9999 B.C. through C.E. time period'),
        SubField('c', True, 'Formatted pre-9999 B.C. time period'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('046', 'd', True, 'Special Coded Dates ', True, '  ', '', [
        SubField('a', False, 'Type of date code'),
        SubField('b', True, 'Date 1, B.C.E. date'),
        SubField('c', True, 'Date 1, C.E. date'),
        SubField('d', True, 'Date 2, B.C.E. date'),
        SubField('e', True, 'Date 2, C.E. date'),
        SubField('j', True, 'Date resource modified'),
        SubField('k', True, 'Beginning or single date created'),
        SubField('l', True, 'Ending date created'),
        SubField('m', True, 'Beginning of date valid'),
        SubField('n', True, 'End of date valid'),
        SubField('o', True, 'Single or starting date for aggregated content'),
        SubField('p', True, 'Ending date for aggregated content'),
        SubField('x', True, 'Nonpublic note'),
        SubField('z', True, 'Public note'),
        SubField('2', True, 'Source of date'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('047', 'd', True, 'Form of Musical Composition Code ', True, '  ', '', [
        SubField('a', False, 'Form of musical composition code'),
        SubField('2', True, 'Source of code'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('048', 'd', True, 'Number of Musical Instruments or Voices Codes ', True, '  ', '', [
        SubField('a', False, 'Performer or ensemble'),
        SubField('b', True, 'Soloist'),
        SubField('2', True, 'Source of code'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('050', 'd', True, 'Library of Congress Call Number ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('051', 'd', True, 'Library of Congress Copy, Issue, Offprint Statement ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('c', True, 'Copy information'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('052', 'd', True, 'Geographic Classification ', True, '  ', '', [
        SubField('a', False, 'Geographic classification area code'),
        SubField('b', True, 'Geographic classification subarea code'),
        SubField('d', True, 'Populated place name'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Code source'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('055', 'd', True, 'Classification Numbers Assigned in Canada ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of call/class number'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('060', 'd', True, 'National Library of Medicine Call Number ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('061', 'd', True, 'National Library of Medicine Copy Statement ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('c', True, 'Copy information'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('066', 'd', False, 'Character Sets Present ', True, '  ', '', [
        SubField('a', False, 'Primary G0 character set'),
        SubField('b', True, 'Primary G1 character set'),
        SubField('c', True, 'Alternate G0 or G1 character set')
    ]),
    MarcField('070', 'd', True, 'National Agricultural Library Call Number ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('071', 'd', True, 'National Agricultural Library Copy Statement ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('c', True, 'Copy information'),
        SubField('8', True, 'Field link and sequence number'),
    ]),
    MarcField('072', 'd', True, 'Subject Category Code ', True, '  ', '', [
        SubField('a', False, 'Subject category code'),
        SubField('x', True, 'Subject category code subdivision'),
        SubField('2', False, 'Source'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('074', 'd', True, 'GPO Item Number ', True, '  ', '', [
        SubField('a', False, 'GPO item number'),
        SubField('z', True, 'Canceled/invalid GPO item number'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('080', 'd', True, 'Universal Decimal Classification Number ', True, '  ', '', [
        SubField('a', False, 'Universal Decimal Classification number'),
        SubField('b', True, 'Item number'),
        SubField('x', True, 'Common auxiliary subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Edition identifier'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('082', 'd', True, 'Dewey Decimal Classification Number ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('m', True, 'Standard or optional designation'),
        SubField('q', True, 'Assigning agency'),
        SubField('2', True, 'Edition information'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('083', 'd', True, 'Additional Dewey Decimal Classification Number ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('c', True, 'Classification number--Ending number of span'),
        SubField('m', True, 'Standard or optional designation'),
        SubField('q', True, 'Assigning agency'),
        SubField('y', True, 'Table sequence number for internal subarrangement or add table'),
        SubField('z', True, 'Table identification'),
        SubField('2', True, 'Edition information'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('084', 'd', True, 'Other Classification Number ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('b', True, 'Item number'),
        SubField('q', True, 'Assigning agency'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Number source'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('085', 'd', True, 'Synthesized Classification Number Components ', True, '  ', '', [
        SubField('a', False, 'Number where instructions are found-single number or beginning number of span'),
        SubField('b', True, 'Base number'),
        SubField('c', True, 'Classification number-ending number of span'),
        SubField('f', True, 'Facet designator'),
        SubField('r', True, 'Root number'),
        SubField('s', True, 'Digits added from classification number in schedule or external table'),
        SubField('t', True, 'Digits added from internal subarrangement or add table'),
        SubField('u', True, 'Number being analyzed'),
        SubField('v', True, 'Number in internal subarrangement or add table where instructions are found'),
        SubField('w', True, 'Table identification-Internal subarrangement or add table'),
        SubField('y', True, 'Table sequence number for internal subarrangement or add table'),
        SubField('z', True, 'Table identification'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('086', 'd', True, 'Government Document Classification Number ', True, '  ', '', [
        SubField('a', False, 'Classification number'),
        SubField('z', True, 'Canceled/invalid classification number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Number source'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('088', 'd', True, 'Report Number ', True, '  ', '', [
        SubField('a', False, 'Report number'),
        SubField('z', True, 'Canceled/invalid report number'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('090', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('091', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('092', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('093', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('094', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('095', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('096', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('097', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('098', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('099', 'd', True, 'Local Call Numbers', True, '  ', '', []),
    MarcField('100', 'd', False, 'Main Entry - Personal Name', True, '  ', '', [
        SubField('a', False, 'Personal name'),
        SubField('b', True, 'Numeration'),
        SubField('c', True, 'Titles and words associated with a name'),
        SubField('d', True, 'Dates associated with a name'),
        SubField('e', True, 'Relator term'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('j', True, 'Attribution qualifier'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', True, 'Fuller form of name'),
        SubField('t', True, 'Title of a work'),
        SubField('u', True, 'Affiliation'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('4', True, 'Relationship'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('110', 'd', False, 'Main Entry - Corporate Name ', True, '  ', '', [
        SubField('a', False, 'Corporate name or jurisdiction name as entry element'),
        SubField('b', True, 'Subordinate unit'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Relator term'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('t', True, 'Title of a work'),
        SubField('u', True, 'Affiliation'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('4', True, 'Relationship'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('111', 'd', False, 'Main Entry - Meeting Name ', True, '  ', '', [
        SubField('a', False, 'Meeting name or jurisdiction name as entry element'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Subordinate unit'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('j', True, 'Relator term'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', True, 'Name of meeting following jurisdiction name entry element'),
        SubField('t', True, 'Title of a work'),
        SubField('u', True, 'Affiliation'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('4', True, 'Relationship'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('130', 'd', False, 'Main Entry - Uniform Title ', True, '  ', '', [
        SubField('a', False, 'Uniform title'),
        SubField('d', True, 'Date of treaty signing'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', True, 'Medium'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', True, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', True, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', True, 'Title of a work'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('210', 'd', True, 'Abbreviated Title ', True, '  ', '', [
        SubField('a', False, 'Abbreviated title'),
        SubField('b', True, 'Qualifying information'),
        SubField('2', False, 'Source'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('222', 'd', True, 'Key Title ', True, '  ', '', [
        SubField('a', False, 'Key title'),
        SubField('b', True, 'Qualifying information'), SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('240', 'd', False, 'Uniform Title ', True, '  ', '', [
        SubField('a', False, 'Uniform title'),
        SubField('d', True, 'Date of treaty signing'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', True, 'Medium'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', True, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', True, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('242', 'd', True, 'Translation of Title by Cataloging Agency ', True, '  ', '', [
        SubField('a', False, 'Title'),
        SubField('b', True, 'Remainder of title'),
        SubField('c', True, 'Statement of responsibility, etc.'),
        SubField('h', True, 'Medium'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('y', True, 'Language code of translated title'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('243', 'd', False, 'Collective Uniform Title ', True, '  ', '', [
        SubField('a', False, 'Uniform title'),
        SubField('d', True, 'Date of treaty signing'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', True, 'Medium'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', True, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', True, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('245', 'd', False, 'Title Statement ', True, '  ', '', [
        SubField('a', False, 'Title'),
        SubField('b', True, 'Remainder of title'),
        SubField('c', True, 'Statement of responsibility, etc.'),
        SubField('f', True, 'Inclusive dates'),
        SubField('g', True, 'Bulk dates'),
        SubField('h', True, 'Medium'),
        SubField('k', True, 'Form'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('s', True, 'Version'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('246', 'd', True, 'Varying Form of Title ', True, '  ', '', [
        SubField('a', False, 'Title proper/short title'),
        SubField('b', True, 'Remainder of title'),
        SubField('f', True, 'Date or sequential designation'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', True, 'Medium'),
        SubField('i', True, 'Display text'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('247', 'd', True, 'Former Title ', True, '  ', '', [
        SubField('a', False, 'Title'),
        SubField('b', True, 'Remainder of title'),
        SubField('f', True, 'Date or sequential designation'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', True, 'Medium'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('x', True, 'International Standard Serial Number'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('250', 'd', True, 'Edition Statement ', True, '  ', '', [
        SubField('a', False, 'Edition statement'),
        SubField('b', True, 'Remainder of edition statement'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('251', 'd', True, 'Version Information ', True, '  ', '', [
        SubField('a', False, 'Version'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('254', 'd', False, 'Musical Presentation Statement ', True, '  ', '', [
        SubField('a', False, 'Musical presentation statement'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('255', 'd', True, 'Cartographic Mathematical Data ', True, '  ', '', [
        SubField('a', False, 'Statement of scale'),
        SubField('b', True, 'Statement of projection'),
        SubField('c', True, 'Statement of coordinates'),
        SubField('d', True, 'Statement of zone'),
        SubField('e', True, 'Statement of equinox'),
        SubField('f', True, 'Outer G-ring coordinate pairs'),
        SubField('g', True, 'Exclusion G-ring coordinate pairs'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('256', 'd', False, 'Computer File Characteristics ', True, '  ', '', [
        SubField('a', False, 'Computer file characteristics'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('257', 'd', True, 'Country of Producing Entity ', True, '  ', '', [
        SubField('a', False, 'Country of producing entity'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('258', 'd', True, 'Philatelic Issue Data ', True, '  ', '', [
        SubField('a', False, 'Issuing jurisdiction'),
        SubField('b', True, 'Denomination'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('260', 'd', True, 'Publication, Distribution, etc. ', True, '  ', '', [
        SubField('a', False, 'Place of publication, distribution, etc.'),
        SubField('b', True, 'Name of publisher, distributor, etc.'),
        SubField('c', True, 'Date of publication, distribution, etc.'),
        SubField('e', True, 'Place of manufacture'),
        SubField('f', True, 'Manufacturer'),
        SubField('g', True, 'Date of manufacture'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number (Imprint)')
    ]),
    MarcField('263', 'd', False, 'Projected Publication Date ', True, '  ', '', [
        SubField('a', False, 'Projected publication date'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('264', 'd', True, 'Production, Publication, Distribution, Manufacture, and Copyright Notice ', True, '  ',
              '', [
                  SubField('a', False, 'Place of production, publication, distribution, manufacture'),
                  SubField('b', True, 'Name of producer, publisher, distributor, manufacturer'),
                  SubField('c', True,
                           'Date of production, publication, distribution, manufacture, or copyright notice'),
                  SubField('3', True, 'Materials specified'),
                  SubField('6', True, 'Linkage'),
                  SubField('7', True, 'Data provenance'),
                  SubField('8', True, 'Field link and sequence number')
              ]),
    MarcField('270', 'd', True, 'Address ', True, '  ', '', [
        SubField('a', False, 'Address'),
        SubField('b', True, 'City'),
        SubField('c', True, 'State or province'),
        SubField('d', True, 'Country'),
        SubField('e', True, 'Postal code'),
        SubField('f', True, 'Terms preceding attention name'),
        SubField('g', True, 'Attention name'),
        SubField('h', True, 'Attention position'),
        SubField('i', True, 'Type of address'),
        SubField('j', True, 'Specialized telephone number'),
        SubField('k', True, 'Telephone number'),
        SubField('l', True, 'Fax number'),
        SubField('m', True, 'Electronic mail address'),
        SubField('n', True, 'TDD or TTY number'),
        SubField('p', True, 'Contact person'),
        SubField('q', True, 'Title of contact person'),
        SubField('r', True, 'Hours'),
        SubField('z', True, 'Public note'),
        SubField('4', True, 'Relationship'),
        SubField('6', True, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('300', 'd', False, 'Physical Description ', False, '  ', '', [
        SubField('a', True, 'Extent'),
        SubField('b', False, 'Other physical details'),
        SubField('c', True, 'Dimensions'),
        SubField('e', False, 'Accompanying material'),
        SubField('f', True, 'Type of unit'),
        SubField('g', True, 'Size of unit'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('306', 'd', True, 'Playing Time ', False, '  ', '', [
        SubField('a', True, 'Playing time'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('307', 'd', True, 'Hours, etc. ', False, '  ', '', [
        SubField('a', True, 'Playing time'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('310', 'd', True, 'Current Publication Frequency ', False, '  ', '', [
        SubField('a', False, 'Current publication frequency'),
        SubField('b', False, 'Date of current publication frequency'),
        SubField('0', False, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('321', 'd', True, 'Former Publication Frequency ', False, '  ', '', [
        SubField('a', False, 'Former publication frequency'),
        SubField('b', False, 'Dates of former publication frequency'),
        SubField('0', False, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('334', 'd', True, 'Mode of Issuance ', False, '  ', '', [
        SubField('a', False, 'Mode of issuance term'),
        SubField('b', False, 'Mode of issuance code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('335', 'd', True, 'Extension Plan ', False, '  ', '', [
        SubField('a', False, 'Extension plan term'),
        SubField('b', False, 'Extension plan code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('336', 'd', True, 'Content Type ', False, '  ', '', [
        SubField('a', True, 'Content type term'),
        SubField('b', True, 'Content type code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('337', 'd', True, 'Media Type ', False, '  ', '', [
        SubField('a', True, 'Media type term'),
        SubField('b', True, 'Media type code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('338', 'd', True, 'Carrier Type ', False, '  ', '', [
        SubField('a', True, 'Carrier type term'),
        SubField('b', True, 'Carrier type code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('340', 'd', True, 'Physical Medium ', False, '  ', '', [
        SubField('a', True, 'Material base and configuration'),
        SubField('b', True, 'Dimensions'),
        SubField('c', True, 'Materials applied to surface'),
        SubField('d', True, 'Information recording technique'),
        SubField('e', True, 'Support'),
        SubField('f', True, 'Reduction ratio value'),
        SubField('g', True, 'Color content'),
        SubField('h', True, 'Location within medium'),
        SubField('i', True, 'Technical specifications of medium'),
        SubField('j', True, 'Generation'),
        SubField('k', True, 'Layout'),
        SubField('l', True, 'Binding'),
        SubField('m', True, 'Book format'),
        SubField('n', True, 'Font size'),
        SubField('o', True, 'Polarity'),
        SubField('p', True, 'Illustrative content'),
        SubField('q', True, 'Reduction ratio designator'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('341', 'd', True, 'Accessibility Content ', False, '  ', '', [
        SubField('a', False, 'Content access mode'),
        SubField('b', True, 'Textual assistive features'),
        SubField('c', True, 'Visual assistive features'),
        SubField('d', True, 'Auditory assistive features'),
        SubField('e', True, 'Tactile assistive features'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('342', 'd', True, 'Geospatial Reference Data ', False, '  ', '', [
        SubField('a', False, 'Name'),
        SubField('b', False, 'Coordinate units or distance units'),
        SubField('c', False, 'Latitude resolution'),
        SubField('d', False, 'Longitude resolution'),
        SubField('e', True, 'Standard parallel or oblique line latitude'),
        SubField('f', True, 'Oblique line longitude'),
        SubField('g', False, 'Longitude of central meridian or projection center'),
        SubField('h', False, 'Latitude of projection center or projection origin'),
        SubField('i', False, 'False easting'),
        SubField('j', False, 'False northing'),
        SubField('k', False, 'Scale factor'),
        SubField('l', False, 'Height of perspective point above surface'),
        SubField('m', False, 'Azimuthal angle'),
        SubField('n', False, 'Azimuth measure point longitude or straight vertical longitude from pole'),
        SubField('o', False, 'Landsat number and path number'),
        SubField('p', False, 'Zone identifier'),
        SubField('q', False, 'Ellipsoid name'),
        SubField('r', False, 'Semi-major axis'),
        SubField('s', False, 'Denominator of flattening ratio'),
        SubField('t', False, 'Vertical resolution'),
        SubField('u', False, 'Vertical encoding method'),
        SubField('v', False, 'Local planar, local, or other projection or grid description'),
        SubField('w', False, 'Local planar or local georeference information'),
        SubField('2', False, 'Reference method used'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('343', 'd', True, 'Planar Coordinate Data ', False, '  ', '', [
        SubField('a', False, 'Planar coordinate encoding method'),
        SubField('b', False, 'Planar distance units'),
        SubField('c', False, 'Abscissa resolution'),
        SubField('d', False, 'Ordinate resolution'),
        SubField('e', False, 'Distance resolution'),
        SubField('f', False, 'Bearing resolution'),
        SubField('g', False, 'Bearing units'),
        SubField('h', False, 'Bearing reference direction'),
        SubField('i', False, 'Bearing reference meridian'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('344', 'd', True, 'Sound Characteristics ', False, '  ', '', [
        SubField('a', True, 'Type of recording'),
        SubField('b', True, 'Recording medium'),
        SubField('c', True, 'Playing speed'),
        SubField('d', True, 'Groove characteristic'),
        SubField('e', True, 'Track configuration'),
        SubField('f', True, 'Tape configuration'),
        SubField('g', True, 'Configuration of playback channels'),
        SubField('h', True, 'Special playback characteristics'),
        SubField('i', True, 'Sound content'),
        SubField('j', True, 'Original capture and storage technique'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('345', 'd', True, 'Moving Image Characteristics ', False, '  ', '', [
        SubField('a', True, 'Presentation format'),
        SubField('b', True, 'Projection speed'),
        SubField('c', True, 'Aspect ratio value'),
        SubField('d', True, 'Aspect ratio designator'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('346', 'd', True, 'Video Characteristics ', False, '  ', '', [
        SubField('a', True, 'Video format'),
        SubField('b', True, 'Broadcast standard'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('347', 'd', True, 'Digital File Characteristics ', False, '  ', '', [
        SubField('a', True, 'File type'),
        SubField('b', True, 'Encoding format'),
        SubField('c', True, 'File size'),
        SubField('d', True, 'Resolution'),
        SubField('e', True, 'Regional encoding'),
        SubField('f', True, 'Encoded bitrate'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('348', 'd', True, 'Notated Music Characteristics ', False, '  ', '', [
        SubField('a', True, 'Format of notated music term'),
        SubField('b', True, 'Format of notated music code'),
        SubField('c', True, 'Form of musical notation term'),
        SubField('d', True, 'Form of musical notation code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number'), ]),
    MarcField('351', 'd', True, 'Organization and Arrangement of Materials ', False, '  ', '', [
        SubField('a', True, 'Organization'),
        SubField('b', True, 'Arrangement'),
        SubField('c', False, 'Hierarchical level'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'),
    ]),
    MarcField('352', 'd', True, 'Digital Graphic Representation ', False, '  ', '', [
        SubField('a', False, 'Direct reference method'),
        SubField('b', True, 'Object type'),
        SubField('c', True, 'Object count'),
        SubField('d', False, 'Row count'),
        SubField('e', False, 'Column count'),
        SubField('f', False, 'Vertical count'),
        SubField('g', False, 'VPF topology level'),
        SubField('i', False, 'Indirect reference description'),
        SubField('q', False, 'Format of the digital image'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('353', 'd', True, 'Supplementary Content Characteristics ', False, '  ', '', [
        SubField('a', True, 'Supplementary content term'),
        SubField('b', True, 'Supplementary content code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('355', 'd', True, 'Security Classification Control ', False, '  ', '', [
        SubField('a', False, 'Security classification'),
        SubField('b', True, 'Handling instructions'),
        SubField('c', True, 'External dissemination information'),
        SubField('d', False, 'Downgrading or declassification event'),
        SubField('e', False, 'Classification system'),
        SubField('f', False, 'Country of origin code'),
        SubField('g', False, 'Downgrading date'),
        SubField('h', False, 'Declassification date'),
        SubField('j', True, 'Authorization'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('357', 'd', True, 'Originator Dissemination Control ', False, '  ', '', [
        SubField('a', False, 'Originator control term'),
        SubField('b', True, 'Originating agency'),
        SubField('c', True, 'Authorized recipients of material'),
        SubField('g', True, 'Other restrictions'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'),
    ]),
    MarcField('361', 'd', True, 'Structured Ownership and Custodial History ', False, '  ', '', [
        SubField('a', False, 'Name'),
        SubField('f', True, 'Ownership and custodial history evidence term'),
        SubField('k', False, 'Formatted date'),
        SubField('l', False, 'Date'),
        SubField('o', True, 'Type of ownership and custodial history information'),
        SubField('s', False, 'Shelf mark of copy described'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('x', True, 'Nonpublic note'),
        SubField('y', False, 'Identifier of the copy described'),
        SubField('z', True, 'Public note'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('362', 'd', True, 'Dates of Publication and/or Sequential Designation ', False, '  ', '', [
        SubField('a', False, 'Dates of publication and/or sequential designation'),
        SubField('z', False, 'Source of information'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('363', 'd', True, 'Normalized Date and Sequential Designation ', False, '  ', '', [
        SubField('a', False, 'First level of enumeration'),
        SubField('b', False, 'Second level of enumeration'),
        SubField('c', False, 'Third level of enumeration'),
        SubField('d', False, 'Fourth level of enumeration'),
        SubField('e', False, 'Fifth level of enumeration'),
        SubField('f', False, 'Sixth level of enumeration'),
        SubField('g', False, 'Alternative numbering scheme, first level of enumeration'),
        SubField('h', False, 'Alternative numbering scheme, second level of enumeration'),
        SubField('i', False, 'First level of chronology'),
        SubField('j', False, 'Second level of chronology'),
        SubField('k', False, 'Third level of chronology'),
        SubField('l', False, 'Fourth level of chronology'),
        SubField('m', False, 'Alternative numbering scheme, chronology'),
        SubField('u', False, 'First level textual designation'),
        SubField('v', False, 'First level of chronology, issuance'),
        SubField('x', True, 'Nonpublic note'),
        SubField('z', True, 'Public note'),
        SubField('6', False, 'Linkage'),
        SubField('8', False, 'Field link and sequence number')]),
    MarcField('365', 'd', True, 'Trade Price ', False, '  ', '', [
        SubField('a', False, 'Price type code'),
        SubField('b', False, 'Price amount'),
        SubField('c', False, 'Currency code'),
        SubField('d', False, 'Unit of pricing'),
        SubField('e', False, 'Price note'),
        SubField('f', False, 'Price effective from'),
        SubField('g', False, 'Price effective until'),
        SubField('h', False, 'Tax rate 1'),
        SubField('i', False, 'Tax rate 2'),
        SubField('j', False, 'ISO country code'),
        SubField('k', False, 'MARC country code'),
        SubField('m', False, 'Identification of pricing entity'),
        SubField('2', False, 'Source of price type code'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('366', 'd', True, 'Trade Availability Information ', False, '  ', '',
              [SubField('a', False, 'Publishers\' compressed title identification'),
               SubField('b', False, 'Detailed date of publication'),
               SubField('c', False, 'Availability status code'),
               SubField('d', False, 'Expected next availability date'),
               SubField('e', False, 'Note'),
               SubField('f', False, 'Publisher\'s discount category'),
               SubField('g', False, 'Date made out of print'),
               SubField('j', False, 'ISO country code'),
               SubField('k', False, 'MARC country code'),
               SubField('m', False, 'Identification of agency'),
               SubField('2', False, 'Source of availability status code'),
               SubField('6', False, 'Linkage'),
               SubField('8', True, 'Field link and sequence number')]),
    MarcField('370', 'd', True, 'Associated Place ', True, '  ', '', [
        SubField('c', True, 'Associated country'),
        SubField('f', True, 'Other associated place'),
        SubField('g', True, 'Place of origin of work or expression'),
        SubField('i', True, 'Relationship information'),
        SubField('s', True, 'Start period'),
        SubField('t', True, 'End period'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('v', True, 'Source of information'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of term'),
        SubField('3', True, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('377', 'd', True, 'Associated Language ', True, '  ', '', [
        SubField('a', False, 'Language code'),
        SubField('l', True, 'Language term'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', True, 'Materials specified'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('380', 'd', True, 'Form of Work ', False, '  ', '', [
        SubField('a', True, 'Form of work'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('381', 'd', True, 'Other Distinguishing Characteristics of Work or Expression ', False, '  ', '', [
        SubField('a', True, 'Other distinguishing characteristic'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('v', True, 'Source of information'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number'),
    ]),
    MarcField('382', 'd', True, 'Medium of Performance ', False, '  ', '', [
        SubField('a', True, 'Medium of performance'),
        SubField('b', True, 'Soloist'),
        SubField('d', True, 'Doubling instrument'),
        SubField('e', True, 'Number of ensembles of the same type'),
        SubField('n', True, 'Number of performers of the same medium'),
        SubField('p', True, 'Alternative medium of performance'),
        SubField('r', False, 'Total number of individuals performing alongside ensembles'),
        SubField('s', False, 'Total number of performers'),
        SubField('t', False, 'Total number of ensembles'),
        SubField('v', True, 'Note'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('383', 'd', True, 'Numeric Designation of Musical Work ', False, '  ', '', [
        SubField('a', True, 'Serial number'),
        SubField('b', True, 'Opus number'),
        SubField('c', True, 'Thematic index number'),
        SubField('d', False, 'Thematic index code'),
        SubField('e', False, 'Publisher associated with opus number'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('384', 'd', True, 'Key ', False, '  ', '', [
        SubField('a', False, 'Key'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('385', 'd', True, 'Audience Characteristics ', False, '  ', '', [
        SubField('a', True, 'Audience term'),
        SubField('b', True, 'Audience code'),
        SubField('m', False, 'Demographic group term'),
        SubField('n', False, 'Demographic group code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('386', 'd', True, 'Creator/Contributor Characteristics ', False, '  ', '', [
        SubField('a', True, 'Creator/contributor term'),
        SubField('b', True, 'Creator/contributor code'),
        SubField('i', True, 'Relationship information'),
        SubField('m', False, 'Demographic group term'),
        SubField('n', False, 'Demographic group code'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('387', 'd', True, 'Representative Expression Characteristics ', False, '  ', '', [
        SubField('a', True, 'Aspect ratio of representative expression'),
        SubField('b', True, 'Color content of representative expression'),
        SubField('c', True, 'Content type of representative expression'),
        SubField('d', True, 'Date of capture of representative expression'),
        SubField('e', True, 'Date of representative expression'),
        SubField('f', True, 'Duration of representative expression'),
        SubField('g', True, 'Intended audience of representative expression'),
        SubField('h', True, 'Language of representative expression'),
        SubField('i', True, 'Place of capture of representative expression'),
        SubField('j', True, 'Projection of cartographic content of representative expression'),
        SubField('k', True, 'Scale of representative expression'),
        SubField('l', True, 'Script of representative expression'),
        SubField('m', True, 'Sound content of representative expression'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('388', 'd', True, 'Time Period of Creation ', False, '  ', '', [
        SubField('a', True, 'Time period of creation term'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('500', 'd', True, 'General Note ', False, '  ', '', [
        SubField('a', False, 'General note'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('501', 'd', True, 'With Note ', False, '  ', '', [
        SubField('a', False, 'With note'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('502', 'd', True, 'Dissertation Note ', False, '  ', '', [
        SubField('a', False, 'Dissertation note'),
        SubField('b', False, 'Degree type'),
        SubField('c', False, 'Name of granting institution'),
        SubField('d', False, 'Year degree granted'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('o', True, 'Dissertation identifier'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('504', 'd', True, 'Bibliography, etc. Note ', False, '  ', '', [
        SubField('a', False, 'Bibliography, etc. note'),
        SubField('b', False, 'Number of references'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('505', 'd', True, 'Formatted Contents Note ', False, '  ', '', [
        SubField('a', False, 'Formatted contents note'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('r', True, 'Statement of responsibility'),
        SubField('t', True, 'Title'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('506', 'd', True, 'Restrictions on Access Note ', False, '  ', '', [
        SubField('a', False, 'Formatted contents note'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('r', True, 'Statement of responsibility'),
        SubField('t', True, 'Title'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('507', 'd', True, 'Scale Note for Visual Materials ', False, '  ', '', [
        SubField('a', False, 'Representative fraction of scale note'),
        SubField('b', False, 'Remainder of scale note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('508', 'd', True, 'Creation/Production Credits Note ', False, '  ', '', [
        SubField('a', False, 'Creation/production credits note'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('510', 'd', True, 'Citation/References Note ', False, '  ', '', [
        SubField('a', False, 'Name of source'),
        SubField('b', False, 'Coverage of source'),
        SubField('c', False, 'Location within source'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('511', 'd', True, 'Participant or Performer Note ', False, '  ', '', [
        SubField('a', False, 'Participant or performer note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('513', 'd', True, 'Type of Report and Period Covered Note ', False, '  ', '', [
        SubField('a', False, 'Type of report'),
        SubField('b', False, 'Period covered'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('514', 'd', True, 'Data Quality Note ', False, '  ', '', [
        SubField('a', False, 'Attribute accuracy report'),
        SubField('b', True, 'Attribute accuracy value'),
        SubField('c', True, 'Attribute accuracy explanation'),
        SubField('d', False, 'Logical consistency report'),
        SubField('e', False, 'Completeness report'),
        SubField('f', False, 'Horizontal position accuracy report'),
        SubField('g', True, 'Horizontal position accuracy value'),
        SubField('h', True, 'Horizontal position accuracy explanation'),
        SubField('i', False, 'Vertical positional accuracy report'),
        SubField('j', True, 'Vertical positional accuracy value'),
        SubField('k', True, 'Vertical positional accuracy explanation'),
        SubField('m', False, 'Cloud cover'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('z', True, 'Display note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('515', 'd', True, 'Numbering Peculiarities Note ', False, '  ', '', [
        SubField('a', False, 'Numbering peculiarities note'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('516', 'd', True, 'Type of Computer File or Data Note ', False, '  ', '', [
        SubField('a', False, 'Type of computer file or data note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('518', 'd', True, 'Date/Time and Place of an Event Note ', False, '  ', '', [
        SubField('a', False, 'Date/time and place of an event note'),
        SubField('d', True, 'Date of event'),
        SubField('o', True, 'Other event information'),
        SubField('p', True, 'Place of event'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('520', 'd', True, 'Summary, etc. ', False, '  ', '', [
        SubField('a', False, 'Summary, etc.'),
        SubField('b', False, 'Expansion of summary note'),
        SubField('c', False, 'Assigning source'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('2', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('521', 'd', True, 'Target Audience Note ', False, '  ', '', [
        SubField('a', True, 'Target audience note'),
        SubField('b', False, 'Source'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('522', 'd', True, 'Geographic Coverage Note ', False, '  ', '', [
        SubField('a', False, 'Geographic coverage note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('524', 'd', True, 'Preferred Citation of Described Materials Note ', False, '  ', '', [
        SubField('a', False, 'Preferred citation of described materials note'),
        SubField('2', False, 'Source of schema used'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('525', 'd', True, 'Supplement Note ', False, '  ', '', [
        SubField('a', False, 'Supplement note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('526', 'd', True, 'Study Program Information Note ', False, '  ', '', [
        SubField('a', False, 'Program name'),
        SubField('b', False, 'Interest level'),
        SubField('c', False, 'Reading level'),
        SubField('d', False, 'Title point value'),
        SubField('i', False, 'Display text'),
        SubField('x', True, 'Nonpublic note'),
        SubField('z', True, 'Public note'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'),
    ]),
    MarcField('530', 'd', True, 'Additional Physical Form available Note ', False, '  ', '', [
        SubField('a', False, 'Additional physical form available note'),
        SubField('b', False, 'Availability source'),
        SubField('c', False, 'Availability conditions'),
        SubField('d', False, 'Order number'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('532', 'd', True, 'Accessibility Note ', False, '  ', '', [
        SubField('a', False, 'Summary of accessibility'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('533', 'd', True, 'Reproduction Note ', False, '  ', '', [
        SubField('a', False, 'Type of reproduction'),
        SubField('b', True, 'Place of reproduction'),
        SubField('c', True, 'Agency responsible for reproduction'),
        SubField('d', False, 'Date of reproduction'),
        SubField('e', False, 'Physical description of reproduction'),
        SubField('f', True, 'Series statement of reproduction'),
        SubField('m', True, 'Dates and/or sequential designation of issues reproduced'),
        SubField('n', True, 'Note about reproduction'),
        SubField('y', True, 'Data provenance'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Fixed-length data elements of reproduction'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('534', 'd', True, 'Original Version Note ', False, '  ', '', [
        SubField('a', False, 'Main entry of original'),
        SubField('b', False, 'Edition statement of original'),
        SubField('c', False, 'Publication, distribution, etc. of original'),
        SubField('e', False, 'Physical description, etc. of original'),
        SubField('f', True, 'Series statement of original'),
        SubField('k', True, 'Key title of original'),
        SubField('l', False, 'Location of original'),
        SubField('m', False, 'Material specific details'),
        SubField('n', True, 'Note about original'),
        SubField('o', True, 'Other resource identifier'),
        SubField('p', False, 'Introductory phrase'),
        SubField('t', False, 'Title statement of original'),
        SubField('x', True, 'International Standard Serial Number'),
        SubField('z', True, 'International Standard Book Number'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('535', 'd', True, 'Location of Originals/Duplicates Note ', False, '  ', '', [
        SubField('a', False, 'Custodian'),
        SubField('b', True, 'Postal address'),
        SubField('c', True, 'Country'),
        SubField('d', True, 'Telecommunications address'),
        SubField('g', False, 'Repository location code'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('536', 'd', True, 'Funding Information Note ', False, '  ', '', [
        SubField('a', False, 'Text of note'),
        SubField('b', True, 'Contract number'),
        SubField('c', True, 'Grant number'),
        SubField('d', True, 'Undifferentiated number'),
        SubField('e', True, 'Program element number'),
        SubField('f', True, 'Project number'),
        SubField('g', True, 'Task number'),
        SubField('h', True, 'Work unit number'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('538', 'd', True, 'System Details Note ', False, '  ', '', [
        SubField('a', False, 'System details note'),
        SubField('i', False, 'Display text'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('3', False, 'Materials specified'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('540', 'd', True, 'Terms Governing Use and Reproduction Note ', False, '  ', '', [
        SubField('a', False, 'Terms governing use and reproduction'),
        SubField('b', False, 'Jurisdiction'),
        SubField('c', False, 'Authorization'),
        SubField('d', False, 'Authorized users'),
        SubField('f', True, 'Use and reproduction rights'),
        SubField('g', True, 'Availability date'),
        SubField('q', False, 'Supplying agency'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('541', 'd', True, 'Immediate Source of Acquisition Note ', False, '  ', '', [
        SubField('a', False, 'Source of acquisition'),
        SubField('b', False, 'Address'),
        SubField('c', False, 'Method of acquisition'),
        SubField('d', False, 'Date of acquisition'),
        SubField('e', False, 'Accession number'),
        SubField('f', False, 'Owner'),
        SubField('h', False, 'Purchase price'),
        SubField('n', True, 'Extent'),
        SubField('o', True, 'Type of unit'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('542', 'd', True, 'Information Relating to Copyright Status ', False, '  ', '', [
        SubField('a', False, 'Personal creator'),
        SubField('b', False, 'Personal creator death date'),
        SubField('c', False, 'Corporate creator'),
        SubField('d', True, 'Copyright holder'),
        SubField('e', True, 'Copyright holder contact information'),
        SubField('f', True, 'Copyright statement'),
        SubField('g', False, 'Copyright date'),
        SubField('h', True, 'Copyright renewal date'),
        SubField('i', False, 'Publication date'),
        SubField('j', False, 'Creation date'),
        SubField('k', True, 'Publisher'), SubField('l', False, 'Copyright status'),
        SubField('m', False, 'Publication status'),
        SubField('n', True, 'Note'),
        SubField('o', False, 'Research date'),
        SubField('p', True, 'Country of publication or creation'),
        SubField('q', False, 'Supplying agency'),
        SubField('r', False, 'Jurisdiction of copyright assessment'),
        SubField('s', False, 'Source of information'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('544', 'd', True, 'Location of Other Archival Materials Note ', False, '  ', '', [
        SubField('a', True, 'Custodian'),
        SubField('b', True, 'Address'),
        SubField('c', True, 'Country'),
        SubField('d', True, 'Title'),
        SubField('e', True, 'Provenance'),
        SubField('n', True, 'Note'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('545', 'd', True, 'Biographical or Historical Data ', False, '  ', '', [
        SubField('a', False, 'Biographical or historical data'),
        SubField('b', False, 'Expansion'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('546', 'd', True, 'Language Note ', False, '  ', '', [
        SubField('a', False, 'Language note'),
        SubField('b', True, 'Information code or alphabet'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('547', 'd', True, 'Former Title Complexity Note ', False, '  ', '', [
        SubField('a', False, 'Former title complexity note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('550', 'd', True, 'Issuing Body Note ', False, '  ', '', [
        SubField('a', False, 'Issuing body note'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('552', 'd', True, 'Entity and Attribute Information Note ', False, '  ', '', [
        SubField('a', False, 'Entity type label'),
        SubField('b', False, 'Entity type definition and source'),
        SubField('c', False, 'Attribute label'),
        SubField('d', False, 'Attribute definition and source'),
        SubField('e', True, 'Enumerated domain value'),
        SubField('f', True, 'Enumerated domain value definition and source'),
        SubField('g', False, 'Range domain minimum and maximum'),
        SubField('h', False, 'Codeset name and source'),
        SubField('i', False, 'Unrepresentable domain'),
        SubField('j', False, 'Attribute units of measurement and resolution'),
        SubField('k', False, 'Beginning and ending date of attribute values'),
        SubField('l', False, 'Attribute value accuracy'),
        SubField('m', False, 'Attribute value accuracy explanation'),
        SubField('n', False, 'Attribute measurement frequency'),
        SubField('o', True, 'Entity and attribute overview'),
        SubField('p', True, 'Entity and attribute detail citation'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('z', True, 'Display note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('555', 'd', True, 'Cumulative Index/Finding Aids Note ', False, '  ', '', [
        SubField('a', False, 'Cumulative index/finding aids note'),
        SubField('b', True, 'Availability source'),
        SubField('c', False, 'Degree of control'),
        SubField('d', False, 'Bibliographic reference'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('556', 'd', True, 'Information About Documentation Note ', False, '  ', '', [
        SubField('a', False, 'Information about documentation note'),
        SubField('z', True, 'International Standard Book Number'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('561', 'd', True, 'Ownership and Custodial History ', False, '  ', '', [
        SubField('a', False, 'History'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('562', 'd', True, 'Copy and Version Identification Note ', False, '  ', '', [
        SubField('a', True, 'Identifying markings'),
        SubField('b', True, 'Copy identification'),
        SubField('c', True, 'Version identification'),
        SubField('d', True, 'Presentation format'),
        SubField('e', True, 'Number of copies'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('563', 'd', True, 'Binding Information ', False, '  ', '', [
        SubField('a', False, 'Binding note'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('565', 'd', True, 'Case File Characteristics Note ', False, '  ', '', [
        SubField('a', False, 'Number of cases/variables'),
        SubField('b', True, 'Name of variable'),
        SubField('c', True, 'Unit of analysis'),
        SubField('d', True, 'Universe of data'),
        SubField('e', True, 'Filing scheme or code'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('567', 'd', True, 'Methodology Note ', False, '  ', '', [
        SubField('a', False, 'Methodology note'),
        SubField('b', True, 'Controlled term'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('580', 'd', True, 'Linking Entry Complexity Note ', False, '  ', '', [
        SubField('a', False, 'Linking entry complexity note'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('581', 'd', True, 'Publications About Described Materials Note ', False, '  ', '', [
        SubField('a', False, 'Publications about described materials note'),
        SubField('z', True, 'International Standard Book Number'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('583', 'd', True, 'Action Note ', False, '  ', '', [
        SubField('a', False, 'Action'),
        SubField('b', True, 'Action identification'),
        SubField('c', True, 'Time/date of action'),
        SubField('d', True, 'Action interval'),
        SubField('e', True, 'Contingency for action'),
        SubField('f', True, 'Authorization'),
        SubField('h', True, 'Jurisdiction'),
        SubField('i', True, 'Method of action'),
        SubField('j', True, 'Site of action'),
        SubField('k', True, 'Action agent'),
        SubField('l', True, 'Status'),
        SubField('n', True, 'Extent'),
        SubField('o', True, 'Type of unit'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('x', True, 'Nonpublic note'),
        SubField('z', True, 'Public note'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('584', 'd', True, 'Accumulation and Frequency of Use Note ', False, '  ', '', [
        SubField('a', True, 'Accumulation'),
        SubField('b', True, 'Frequency of use'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('585', 'd', True, 'Exhibitions Note ', False, '  ', '', [
        SubField('a', False, 'Exhibitions note'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number'),
    ]),
    MarcField('586', 'd', True, 'Awards Note ', False, '  ', '', [
        SubField('a', False, 'Awards note'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('588', 'd', True, 'Source of Description, Etc. Note ', False, '  ', '', [
        SubField('a', False, 'Source of description note'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('590', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('591', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('592', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('593', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('594', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('595', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('596', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('597', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('598', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('599', 'd', True, 'Local Notes', False, '  ', '', []),
    MarcField('600', 'd', True, 'Subject Added Entry - Personal Name ', False, '  ', '', [
        SubField('a', False, 'Personal name'),
        SubField('b', False, 'Numeration'),
        SubField('c', True, 'Titles and other words associated with a name'),
        SubField('d', False, 'Dates associated with a name'),
        SubField('e', True, 'Relator term'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('j', True, 'Attribution qualifier'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', False, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', False, 'Fuller form of name'),
        SubField('r', False, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('u', False, 'Affiliation'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('610', 'd', True, 'Subject Added Entry - Corporate Name ', False, '  ', '', [
        SubField('a', False, 'Corporate name or jurisdiction name as entry element'),
        SubField('b', True, 'Subordinate unit'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Relator term'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('o', False, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', False, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('u', False, 'Affiliation'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('611', 'd', True, 'Subject Added Entry - Meeting Name ', False, '  ', '', [
        SubField('a', False, 'Meeting name or jurisdiction name as entry element'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Subordinate unit'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('j', True, 'Relator term'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', False, 'Name of meeting following jurisdiction name entry element'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('u', False, 'Affiliation'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('630', 'd', True, 'Subject Added Entry - Uniform Title ', False, '  ', '', [
        SubField('a', False, 'Uniform title'),
        SubField('d', True, 'Date of treaty signing'),
        SubField('e', True, 'Relator term'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', False, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', False, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('647', 'd', True, 'Subject Added Entry - Named Event ', False, '  ', '', [
        SubField('a', False, 'Named event'),
        SubField('c', True, 'Location of named event'),
        SubField('d', False, 'Date of named event'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('648', 'd', True, 'Subject Added Entry - Chronological Term ', False, '  ', '', [
        SubField('a', False, 'Chronological term'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('650', 'd', True, 'Subject Added Entry - Topical Term ', False, '  ', '', [
        SubField('a', False, 'Topical term or geographic name entry element'),
        SubField('b', False, 'Topical term following geographic name entry element'),
        SubField('c', False, 'Location of event'),
        SubField('d', False, 'Active dates'),
        SubField('e', True, 'Relator term'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('4', True, 'Relationship'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('651', 'd', True, 'Subject Added Entry - Geographic Name ', False, '  ', '', [
        SubField('a', False, 'Geographic name'),
        SubField('e', True, 'Relator term'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('4', True, 'Relationship'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('653', 'd', True, 'Index Term - Uncontrolled ', False, '  ', '', [
        SubField('a', True, 'Uncontrolled term'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('654', 'd', True, 'Subject Added Entry - Faceted Topical Terms ', False, '  ', '', [
        SubField('a', True, 'Focus term'),
        SubField('b', True, 'Non-focus term'),
        SubField('c', True, 'Facet/hierarchy designation'),
        SubField('e', True, 'Relator term'),
        SubField('v', True, 'Form subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('655', 'd', True, 'Index Term - Genre/Form ', False, '  ', '', [
        SubField('a', False, 'Genre/form data or focus term'),
        SubField('b', True, 'Non-focus term'),
        SubField('c', True, 'Facet/hierarchy designation'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('656', 'd', True, 'Index Term - Occupation ', False, '  ', '', [
        SubField('a', False, 'Occupation'),
        SubField('k', False, 'Form'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('657', 'd', True, 'Index Term - Function ', False, '  ', '', [
        SubField('a', False, 'Function'),
        SubField('v', True, 'Form subdivision'),
        SubField('x', True, 'General subdivision'),
        SubField('y', True, 'Chronological subdivision'),
        SubField('z', True, 'Geographic subdivision'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('658', 'd', True, 'Index Term - Curriculum Objective ', False, '  ', '', [
        SubField('a', False, 'Main curriculum objective'),
        SubField('b', True, 'Subordinate curriculum objective'),
        SubField('c', False, 'Curriculum code'),
        SubField('d', False, 'Correlation factor'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term or code'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('662', 'd', True, 'Subject Added Entry - Hierarchical Place Name ', False, '  ', '', [
        SubField('a', True, 'Country or larger entity'),
        SubField('b', False, 'First-order political jurisdiction'),
        SubField('c', True, 'Intermediate political jurisdiction'),
        SubField('d', False, 'City'),
        SubField('e', True, 'Relator term'),
        SubField('f', True, 'City subsection'),
        SubField('g', True, 'Other nonjurisdictional geographic region and feature'),
        SubField('h', True, 'Extraterrestrial area'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('688', 'd', True, 'Subject Added Entry - Type of Entity Unspecified ', False, '  ', '', [
        SubField('a', False, 'Name, title, or term'),
        SubField('e', True, 'Relator term'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of name, title, or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('690', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('691', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('692', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('693', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('694', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('695', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('696', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('697', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('698', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('699', 'd', True, 'Local Subject Access Fields ', False, '  ', '', []),
    MarcField('700', 'd', True, 'Added Entry - Personal Name ', True, '  ', '', [
        SubField('a', False, 'Personal name'),
        SubField('b', True, 'Numeration'),
        SubField('c', True, 'Titles and other words associated with a name'),
        SubField('d', True, 'Dates associated with a name'),
        SubField('e', True, 'Relator term'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', True, 'Medium'),
        SubField('i', True, 'Relationship information'),
        SubField('j', True, 'Attribution qualifier'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', True, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', True, 'Fuller form of name'),
        SubField('r', True, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', True, 'Title of a work'),
        SubField('u', True, 'Affiliation'),
        SubField('x', True, 'International Standard Serial Number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('3', True, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('710', 'd', True, 'Added Entry - Corporate Name ', True, '  ', '', [
        SubField('a', False, 'Corporate name or jurisdiction name as entry element'),
        SubField('b', True, 'Subordinate unit'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Relator term'),
        SubField('f', True, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', True, 'Medium'),
        SubField('i', True, 'Relationship information'),
        SubField('k', True, 'Form subheading'),
        SubField('l', True, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('o', True, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', True, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', True, 'Title of a work'),
        SubField('u', True, 'Affiliation'),
        SubField('x', True, 'International Standard Serial Number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('3', True, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', True, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')
    ]),
    MarcField('711', 'd', True, 'Added Entry - Meeting Name ', False, '  ', '', [
        SubField('a', False, 'Meeting name or jurisdiction name as entry element'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Subordinate unit'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('i', True, 'Relationship information'),
        SubField('j', True, 'Relator term'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', False, 'Name of meeting following jurisdiction name entry element'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('u', False, 'Affiliation'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', True, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('720', 'd', True, 'Added Entry - Uncontrolled Name ', False, '  ', '', [
        SubField('a', False, 'Name'),
        SubField('e', True, 'Relator term'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('4', True, 'Relationship'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('730', 'd', True, 'Added Entry - Uniform Title ', False, '  ', '', [
        SubField('a', False, 'Uniform title'),
        SubField('d', True, 'Date of treaty signing'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('i', True, 'Relationship information'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', False, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', False, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('740', 'd', True, 'Added Entry - Uncontrolled Related/Analytical Title ', False, '  ', '', [
        SubField('a', False, 'Uncontrolled related/analytical title'),
        SubField('h', False, 'Medium'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('751', 'd', True, 'Added Entry - Geographic Name ', False, '  ', '', [
        SubField('a', False, 'Geographic name'),
        SubField('e', True, 'Relator term'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', True, 'Data provenance'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('752', 'd', True, 'Added Entry - Hierarchical Place Name ', False, '  ', '', [
        SubField('a', True, 'Country or larger entity'),
        SubField('b', False, 'First-order political jurisdiction'),
        SubField('c', True, 'Intermediate political jurisdiction'),
        SubField('d', False, 'City'),
        SubField('e', True, 'Relator term'),
        SubField('f', True, 'City subsection'),
        SubField('g', True, 'Other nonjurisdictional geographic region and feature'),
        SubField('h', True, 'Extraterrestrial area'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('753', 'd', True, 'System Details Access to Computer Files ', False, '  ', '', [
        SubField('a', False, 'Make and model of machine'),
        SubField('b', False, 'Programming language'),
        SubField('c', False, 'Operating system'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of term'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('754', 'd', True, 'Added Entry - Taxonomic Identification ', False, '  ', '', [
        SubField('a', True, 'Taxonomic name'),
        SubField('c', True, 'Taxonomic category'),
        SubField('d', True, 'Common or alternative name'),
        SubField('x', True, 'Non-public note'),
        SubField('z', True, 'Public note'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of taxonomic identification'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('758', 'd', True, 'Resource Identifier ', False, '  ', '', [
        SubField('a', False, 'Label'),
        SubField('i', True, 'Relationship information'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('760', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('761', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('762', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('763', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('764', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('765', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('766', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('767', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('768', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('769', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('770', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('771', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('772', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('773', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('774', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('775', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('776', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('777', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('778', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('779', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('780', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('781', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('782', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('783', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('784', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('785', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('786', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('787', 'd', True, 'Linking Entry Fields - General Information', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('788', 'd', True, 'Parallel Description in Another Language of Cataloging ', False, '  ', '', [
        SubField('a', False, 'Main entry heading'),
        SubField('b', False, 'Edition'),
        SubField('c', False, 'Qualifying information'),
        SubField('d', False, 'Place, publisher, and date of publication'),
        SubField('g', True, 'Related parts'),
        SubField('h', False, 'Physical description'),
        SubField('i', True, 'Relationship information'),
        SubField('l', True, 'Data provenance'),
        SubField('m', False, 'Material-specific details'),
        SubField('n', True, 'Note'),
        SubField('o', True, 'Other item identifier'),
        SubField('s', False, 'Uniform title'),
        SubField('t', False, 'Title'),
        SubField('w', True, 'Record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', False, 'CODEN designation'),
        SubField('4', True, 'Relationship'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('800', 'd', True, 'Series Added Entry - Personal Name ', False, '  ', '', [
        SubField('a', False, 'Personal name'),
        SubField('b', False, 'Numeration'),
        SubField('c', True, 'Titles and other words associated with a name'),
        SubField('d', False, 'Dates associated with a name'),
        SubField('e', True, 'Relator term'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('j', True, 'Attribution qualifier'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', False, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', False, 'Fuller form of name'),
        SubField('r', False, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('u', False, 'Affiliation'),
        SubField('v', False, 'Volume/sequential designation'),
        SubField('w', True, 'Bibliographic record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', True, 'Data provenance'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('810', 'd', True, 'Series Added Entry - Corporate Name ', False, '  ', '', [
        SubField('a', False, 'Corporate name or jurisdiction name as entry element'),
        SubField('b', True, 'Subordinate unit'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Relator term'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('o', False, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', False, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('u', False, 'Affiliation'),
        SubField('v', False, 'Volume/sequential designation'),
        SubField('w', True, 'Bibliographic record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', True, 'Data provenance'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('811', 'd', True, 'Series Added Entry - Meeting Name ', False, '  ', '', [
        SubField('a', False, 'Meeting name or jurisdiction name as entry element'),
        SubField('c', True, 'Location of meeting'),
        SubField('d', True, 'Date of meeting or treaty signing'),
        SubField('e', True, 'Subordinate unit'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('j', True, 'Relator term'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('n', True, 'Number of part/section/meeting'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('q', False, 'Name of meeting following jurisdiction name entry element'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('u', False, 'Affiliation'),
        SubField('v', False, 'Volume/sequential designation'),
        SubField('w', True, 'Bibliographic record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', True, 'Data provenance'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('4', True, 'Relationship'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('830', 'd', True, 'Series Added Entry - Uniform Title ', False, '  ', '', [
        SubField('a', False, 'Uniform title'),
        SubField('d', True, 'Date of treaty signing'),
        SubField('f', False, 'Date of a work'),
        SubField('g', True, 'Miscellaneous information'),
        SubField('h', False, 'Medium'),
        SubField('k', True, 'Form subheading'),
        SubField('l', False, 'Language of a work'),
        SubField('m', True, 'Medium of performance for music'),
        SubField('n', True, 'Number of part/section of a work'),
        SubField('o', False, 'Arranged statement for music'),
        SubField('p', True, 'Name of part/section of a work'),
        SubField('r', False, 'Key for music'),
        SubField('s', True, 'Version'),
        SubField('t', False, 'Title of a work'),
        SubField('v', False, 'Volume/sequential designation'),
        SubField('w', True, 'Bibliographic record control number'),
        SubField('x', False, 'International Standard Serial Number'),
        SubField('y', True, 'Data provenance'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source of heading or term'),
        SubField('3', False, 'Materials specified'),
        SubField('5', True, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Control subfield')]),
    MarcField('841', 'd', True, 'Holdings Coded Data Values ', False, '  ', '', []),
    MarcField('842', 'd', True, 'Textual Physical Form Designator ', False, '  ', '', []),
    MarcField('843', 'd', True, 'Reproduction Note ', False, '  ', '', []),
    MarcField('844', 'd', True, 'Name of Unit ', False, '  ', '', []),
    MarcField('845', 'd', True, 'Terms Governing Use and Reproduction ', False, '  ', '', []),
    MarcField('850', 'd', True, 'Holding Institution ', False, '  ', '', [
        SubField('a', True, 'Holding institution'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('852', 'd', True, 'Location ', False, '  ', '', [
        SubField('a', False, 'Location'),
        SubField('b', True, 'Sublocation or collection'),
        SubField('c', True, 'Shelving location'),
        SubField('d', True, 'Former shelving location'),
        SubField('e', True, 'Address'),
        SubField('f', True, 'Coded location qualifier'),
        SubField('g', True, 'Non-coded location qualifier'),
        SubField('h', False, 'Classification part'),
        SubField('i', True, 'Item part'),
        SubField('j', False, 'Shelving control number'),
        SubField('k', True, 'Call number prefix'),
        SubField('l', False, 'Shelving form of title'),
        SubField('m', True, 'Call number suffix'),
        SubField('n', False, 'Country code'),
        SubField('p', False, 'Piece designation'),
        SubField('q', False, 'Piece physical condition'),
        SubField('s', True, 'Copyright article-fee code'),
        SubField('t', False, 'Copy number'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('x', True, 'Nonpublic note'),
        SubField('z', True, 'Public note'),
        SubField('2', False, 'Source of classification or shelving scheme'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', False, 'Sequence number')]),
    MarcField('853', 'd', True, 'Captions and Pattern - Basic Bibliographic Unit ', False, '  ', '', []),
    MarcField('854', 'd', True, 'Captions and Pattern - Supplementary Material ', False, '  ', '', []),
    MarcField('855', 'd', True, 'Captions and Pattern - Indexes ', False, '  ', '', []),
    MarcField('856', 'd', True, 'Electronic Location and Access ', False, '  ', '', [
        SubField('a', True, 'Host name'),
        SubField('c', True, 'Compression information'),
        SubField('d', True, 'Path'),
        SubField('e', True, 'Data provenance'),
        SubField('f', True, 'Electronic name'),
        SubField('g', True, 'Persistent identifier'),
        SubField('h', True, 'Non-functioning Uniform Resource Identifier'),
        SubField('l', True, 'Standardized information governing access'),
        SubField('m', True, 'Contact for access assistance'),
        SubField('n', True, 'Terms governing access'),
        SubField('o', False, 'Operating system'),
        SubField('p', False, 'Port'),
        SubField('q', True, 'Electronic format type'),
        SubField('r', True, 'Standardized information governing use and reproduction'),
        SubField('s', True, 'File size'),
        SubField('t', True, 'Terms governing use and reproduction'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('v', True, 'Hours access method available'),
        SubField('w', True, 'Record control number'),
        SubField('x', True, 'Nonpublic note'),
        SubField('y', True, 'Link text'),
        SubField('z', True, 'Public note'),
        SubField('2', False, 'Access method'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Access status'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('857', 'd', True, 'Electronic Archive Location and Access ', False, '  ', '', [
        SubField('b', False, 'Name of archiving agency'),
        SubField('c', False, 'Name of Web archive or digital archive repository'),
        SubField('d', False, 'Date range of archived material'),
        SubField('e', True, 'Data provenance'),
        SubField('f', False, 'Archive completeness'),
        SubField('g', True, 'Persistent identifier'),
        SubField('h', True, 'Non-functioning Uniform Resource Identifier'),
        SubField('l', True, 'Standardized information governing access'),
        SubField('m', True, 'Contact for access assistance'),
        SubField('n', True, 'Terms governing access'),
        SubField('q', True, 'Electronic format type'),
        SubField('r', True, 'Standardized information governing use and reproduction'),
        SubField('s', True, 'File size'),
        SubField('t', True, 'Terms governing use and reproduction'),
        SubField('u', True, 'Uniform Resource Identifier'),
        SubField('x', True, 'Nonpublic note'),
        SubField('y', True, 'Link text'),
        SubField('z', True, 'Public note'),
        SubField('2', False, 'Access method'),
        SubField('3', False, 'Materials specified'),
        SubField('5', False, 'Institution to which field applies'),
        SubField('6', False, 'Linkage'),
        SubField('7', False, 'Access status'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('863', 'd', True, 'Enumeration and Chronology - Basic Bibliographic Unit ', False, '  ', '', []),
    MarcField('864', 'd', True, 'Enumeration and Chronology - Supplementary Material ', False, '  ', '', []),
    MarcField('865', 'd', True, 'Enumeration and Chronology - Indexes ', False, '  ', '', []),
    MarcField('866', 'd', True, 'Textual Holdings - Basic Bibliographic Unit ', False, '  ', '', []),
    MarcField('867', 'd', True, 'Textual Holdings - Supplementary Material ', False, '  ', '', []),
    MarcField('868', 'd', True, 'Textual Holdings - Indexes ', False, '  ', '', []),
    MarcField('876', 'd', True, 'Item Information - Basic Bibliographic Unit ', False, '  ', '', []),
    MarcField('877', 'd', True, 'Item Information - Supplementary Material ', False, '  ', '', []),
    MarcField('878', 'd', True, 'Item Information - Indexes ', False, '  ', '', []),
    MarcField('880', 'd', True, 'Alternate Graphic Representation ', False, '  ', '', []),
    MarcField('881', 'd', True, 'Manifestation Statements ', False, '  ', '', [
        SubField('a', True, 'Manifestation statement, high-level/general'),
        SubField('b', True, 'Manifestation identifier statement'),
        SubField('c', True, 'Manifestation title and responsibility statement'),
        SubField('d', True, 'Manifestation edition statement'),
        SubField('e', True, 'Manifestation production statement'),
        SubField('f', True, 'Manifestation publication statement'),
        SubField('g', True, 'Manifestation distribution statement'),
        SubField('h', True, 'Manifestation manufacture statement'),
        SubField('i', True, 'Manifestation copyright statement'),
        SubField('j', True, 'Manifestation frequency statement'),
        SubField('k', True, 'Manifestation designation of sequence statement'),
        SubField('l', True, 'Manifestation series statement'),
        SubField('m', True, 'Manifestation dissertation statement'),
        SubField('n', True, 'Manifestation regional encoding statement'),
        SubField('3', False, 'Materials specified'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('882', 'd', True, 'Replacement Record Information ', False, '  ', '', [
        SubField('a', True, 'Replacement title'),
        SubField('i', True, 'Explanatory text'),
        SubField('w', True, 'Replacement bibliographic record control number'),
        SubField('6', False, 'Linkage'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('883', 'd', True, 'Metadata Provenance ', False, '  ', '', [
        SubField('a', False, 'Creation process'),
        SubField('c', False, 'Confidence value'),
        SubField('d', False, 'Creation date'),
        SubField('q', False, 'Assigning or generating agency'),
        SubField('x', False, 'Validity end date'),
        SubField('u', False, 'Uniform Resource Identifier'),
        SubField('w', True, 'Bibliographic record control number'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('8', True, 'Field link and sequence number')]),
    MarcField('884', 'd', True, 'Description Conversion Information ', False, '  ', '', [
        SubField('a', False, 'Conversion process'),
        SubField('g', False, 'Conversion date'),
        SubField('k', False, 'Identifier of source metadata'),
        SubField('q', False, 'Conversion agency'),
        SubField('u', True, 'Uniform Resource Identifier')]),
    MarcField('885', 'd', True, 'Matching Information ', False, '  ', '', [
        SubField('a', False, 'Matching information'),
        SubField('b', False, 'Status of matching and its checking'),
        SubField('c', False, 'Confidence value'),
        SubField('d', False, 'Generation date'),
        SubField('w', True, 'Record control number'),
        SubField('x', True, 'Nonpublic note'),
        SubField('z', True, 'Public note'),
        SubField('0', True, 'Authority record control number or standard number'),
        SubField('1', True, 'Real World Object URI'),
        SubField('2', False, 'Source'),
        SubField('5', False, 'Institution to which field applies')]),
    MarcField('886', 'd', True, 'Foreign MARC Information Field ', False, '  ', '', [
        SubField('a', False, 'Tag of the foreign MARC field'),
        SubField('b', False, 'Content of the foreign MARC field'),
        SubField('2', False, 'Source of data')]),
    MarcField('887', 'd', True, 'Non-MARC Information Field ', False, '  ', '', [
        SubField('a', False, 'Content of non-MARC field'),
        SubField('2', False, 'Source of data')])
]


def add_field_to_list(field: MarcField) -> None:
    """
    Adds the given field to the FIELDS list.
    
    Args:
        field (MarcField): The field to be added.
    """
    if field is None:
        return
    FIELDS.append(field)


def add_additional_fields_to_list(fields: list[MarcField]) -> None:
    """
    Add additional fields to the FIELDS list

    Args:
        fields (list[MarcField]): The list of fields to add additional fields to.

    Returns:
        None
    """
    if fields is None or len(fields) == 0:
        return
    for field in fields:
        add_field_to_list(field)


def get_field_tags() -> list[str]:
    """
    Get the list of field tags.

    Returns:
        set[str]: The set of field tags.
    """
    tags: list[str] = [mf.tag for mf in FIELDS]

    return tags


def get_field_by_tag(tag: str = '') -> MarcField:
    if tag in get_field_tags():
        for mf in FIELDS:
            if mf.tag == tag:
                return mf


def add_additional_subfield_to_field_in_list(tag: str, subfield: SubField) -> None:
    """
    Add an additional subfield to a field in the list.

    Args:
        tag (str): The tag of the field.
        subfield (SubField): The subfield to be added.

    Returns:
        None
    """
    if tag != "" and subfield:
        mf : MarcField = get_field_by_tag(tag)
        for sf in mf.subfields:
            if sf.tag == subfield.tag:
                return

        mf.subfields.append(subfield)


def get_dictionary(verbose: bool = False) -> str:
    """
    Returns a JSON string representation of a dictionary.
    
    Args:
        verbose (bool): Whether to include verbose information in the dictionary.
        
    Returns:
        str: JSON string representation of the dictionary.
    """
    data = []
    tags: list[str] = get_field_tags()

    tags.sort()

    for tag in tags:
        mf: MarcField = get_field_by_tag(tag)
        field_data = {
            'tag': mf.tag,
            'type': mf.type,
            'repeatable': mf.repeatable
        }
        if verbose:
            field_data['description'] = mf.description

        if mf.type == 'd':
            field_data['indicators'] = mf.indicators
            field_data['subfields'] = []
            for sf in mf.subfields:
                subfield_data = {
                    'tag': sf.tag,
                    'repeatable': sf.repeatable
                }
                if verbose:
                    subfield_data['description'] = sf.description
                field_data['subfields'].append(subfield_data)

        data.append(field_data)

    return json.dumps(data, indent=4)


def switch_type_of_field(tag: str):
    for f in FIELDS:
        if f.tag == tag:
            if f.type == 'c':
                f.type = 'd'
            else:
                f.type = 'c'


def switch_repeatability_of_field(tag: str):
    for f in FIELDS:
        if f.tag == tag:
            f.repeatable = not f.repeatable


@dataclass(init=False, eq=True, order=True)
class BaseField:
    tag: str
    description: str
    field_type: str
    record_separator: str
    field_separator: str

    def __init__(self, tag: str, description: str, field_type: str):
        self.tag = tag
        self.description = description
        self.field_type = field_type
        self.record_separator = '^^'
        self.field_separator = '^_'

    def __del__(self):
        del self.tag
        del self.description
        del self.field_type
        del self.record_separator
        del self.field_separator

    def set_separators(self, record_separator: str, field_separator: str):
        self.record_separator = record_separator
        self.field_separator = field_separator


# class for control fields (tag 000 - 009)
@dataclass(eq=True, order=True)
class CField(BaseField):
    data: str

    def __init__(self, tag: str, description: str, data: str):
        super().__init__(tag, description.strip(), 'c')
        if tag == '' or data == '':
            raise MarcException('Tag and data cannot be empty for CField')

        valid = False

        for mf in FIELDS:
            if mf.tag == tag and mf.type == 'c':
                valid = True
                break

        if not valid:
            raise MarcException('Tag %s is not defined as a CField' % tag)

        self.data = data
        self.field_type = 'c'

    def __del__(self):
        super().__del__()
        del self.data

    def __repr__(self, show_description: bool = False) -> str:
        msg: list[str] = []

        if show_description:
            msg.append('%s%s [%s]' % (self.record_separator, self.tag, self.description))
        else:
            msg.append('%s%s' % (self.record_separator, self.tag))

        msg.append(self.data)

        return self.field_separator.join(msg)


@dataclass(eq=True, order=True)
class DField(BaseField):
    indicators: str
    subfields: list[SubField]

    def __init__(self, tag: str, description: str, indicators: str, subfields: list[SubField]):
        super().__init__(tag, description.strip(), 'd')
        if tag == '':
            raise MarcException('Tag cannot be empty for DField')

        valid = False

        for mf in FIELDS:
            if mf.tag == tag and mf.type == 'd':
                valid = True
                break

        if not valid:
            raise MarcException('Tag %s is not defined as a DField' % tag)

        self.indicators = indicators
        self.subfields = subfields.copy()
        self.field_type = 'd'

    def __del__(self):
        super().__del__()
        del self.indicators
        for sf in self.subfields:
            del sf
        del self.subfields


    def __repr__(self, show_description: bool = False) -> str:
        msg: list[str] = []

        if show_description:
            msg.append('%s%s [%s]%s' % (self.record_separator, self.tag, self.description, self.indicators))
        else:
            msg.append('%s%s%s' % (self.record_separator, self.tag, self.indicators))

        for s in self.subfields:
            msg.append(s.__repr__(show_description))

        return self.field_separator.join(msg)


    def addSubField(self, tag: str, value: str):
        repeatable: bool = True
        new_sf: SubField = None

        for mf in FIELDS:
            if mf.tag == self.tag:
                for sf in mf.subfields:
                    if sf.tag == tag:
                        new_sf = sf.__copy__()
                        repeatable=sf.repeatable
                        new_sf.value = value
                        break

        if new_sf is not None:
            if not repeatable:
                found=[sf for sf in self.subfields if sf.tag == tag]

                if len(found) > 0:
                    raise MarcException('Non repeatable subfield \'$%s\' tried to be added more than once to field \'%s\'' % (tag, self.tag))

            self.subfields.append(new_sf)
        else:
            raise MarcException('Subfield \'%s\' is not defined for field \'%s\'' % (tag, self.tag))

        return self


@dataclass
class MarcDto:
    _cfields: list[CField] = field(default_factory=list)
    _dfields: list[DField] = field(default_factory=list)


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
        msg: list[str] = [f.__repr__(show_description) for f in self._cfields]+ [f.__repr__(show_description) for f in self._dfields]
        msg.sort()

        return '\n'.join(msg)

    def __len__(self) -> int:
        return len(self._cfields) + len(self._dfields)

    def as_list(self, show_description: bool = False) -> list[str]:
        msg: list[str] = [f.__repr__(show_description) for f in self._cfields] + [f.__repr__(show_description) for f in self._dfields]
        msg.sort()

        return msg

    def set_separators(self, record_separator: str, field_separator: str):
        for f in self._cfields:
            f.set_separators(record_separator, field_separator)

        for f in self._dfields:
            f.set_separators(record_separator, field_separator)

        return self


    def __find_definition_for_field(self, tag: str) -> MarcField | None:
        definitions = [field for field in FIELDS if field.tag == tag]

        if len(definitions) == 0: return None
        if len(definitions) > 1: return None

        return definitions[0].__copy__()

    def __create_cfield(self, tag: str, description: str, data: str) -> CField:
        return CField(tag=tag, description=description, data=data)

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

        return DField(tag=tag, description=definition.description, indicators=field_indicators, subfields=subs)

    def create_field(self, tag: str, indicators: str = '', data: str = '',
                     subfields=None) -> CField | DField:

        if subfields is None:
            subfields = []

        definition = self.__find_definition_for_field(tag)

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
