# marc21 module

marc21 is a Python library for writing marc21 bibliographic records.

marc is an acronym for **MA**chine **R**eadable **C**atalogue.

## Installation

Use the Python package manager [pip](https://pip.pypa.io/en/stable/) to install marc21.

```commandline
pip install marc21
```

## Usage

```python
import marc21

# view recognized marc21 fields and subfields in json format
# the information is taken from the website of the Library of Congress
# the option True denotes to include the description of the field/subfield
print(get_dictionary(True))

# create marc21 data transfer object
dto = MarcDto()

# add the control fields  (please note when outputting the record the fields gets sorted)
# control fields in marc21 have a data field and no subfields
fld = dto.create_field(tag='001', data='3303902')
dto.insert_field(fld)

# this can also be done in one line
dto.insert_field(dto.create_field(tag='003', data='LoC'))

# add fields with subfields
# with default indicators as double space '  '
fld = dto.create_field(tag='010')
fld.addSubField(tag='a', value='83165326')
dto.insert_field(fld)

# or with specific indicators
fld = dto.create_field(tag='100', indicators='1 ')
fld.addSubField(tag='a', value='Orwell, George')
fld.addSubField(tag='d', value='1903-1950')
dto.insert_field(fld)

# subfields can also be chained
fld = dto.create_field(tag='245', indicators='10')
fld.addSubField(tag='a', value='1984').addSubField(tag='b', value='a novel').addSubField(tag='c',
                                                                                         value='by George Orwell')
dto.insert_field(fld)

# fields do not need to be added in order
# indicators can also be set after creating the field
fld = dto.create_field(tag='240', indicators='10')
fld.addSubField(tag='a', value='Nineteen eighty-four')
dto.insert_field(fld)

# and this can also be done on one line
dto.insert_field(dto.create_field(tag='300').addSubField(tag='a', value='267 p. ;').addSubField(tag='c', value='21 cm'))

# when the record is finished, it can be printed

print(dto)
```

Which results in:
```marc21
^^001^_3303902
^^003^_LoC
^^010  ^_a83165326
^^1001 ^_aOrwell, George^_d1903-1950
^^24010^_aNineteen eighty-four
^^24510^_a1984^_ba novel^_cby George Orwell
^^300  ^_a267 p. ;^_c21 cm
```

In order to change the default record-separator (^^) and field-seperator (^_), one can
call set_separators before printing the MarcDto instance

```python
dto.set_separators(field_separator='  ', subfield_separator=' $')

print(dto)
```

### New in 0.6: Convenience helpers

Quickly read and modify values without manual field traversal:

```python
# read values
dto.get_value('001')                 # control field data
dto.get_value('245', 'a')            # first 245 $a
dto.list_values('650', 'a')          # all 650 $a

# set or add
dto.set_value('001', '3303902')      # set control field
dto.set_value('245', '1984', 'a')    # set first 245 $a (replaces if non-repeatable)
dto.add_subfield('245', 'b', 'a novel')

# remove
dto.remove('650', 'a')               # remove all 650 $a subfields
dto.remove('246')                    # remove all 246 fields
```

### extending the dictionary

The marc21 standard reserved the 9xx range of fields for custom-fields.

This library supports the addition of new fields and the alteration of existing fields.

```python
    # create a MarcField, separate SubFields, link them together adn add them to the dictionary

    mf = MarcField(tag='905', type='d', repeatable=False, description='Address')
    sf = SubField(tag='a', repeatable=False, description='country')
    mf.add_SubField(new_sf=sf)
    sf = SubField(tag='b', repeatable=False, description='city')
    mf.add_SubField(new_sf=sf)

    add_field_to_list(mf)

    # Or do it in one go, adding the subfields as a list 
    add_field_to_list(MarcField(tag='908', type='d', repeatable=True, description='Fictional Character', subfields=[
        SubField(tag='a', repeatable=False, description='Name'),
        SubField(tag='b', repeatable=True, description='Characterization')
    ]))

    # Or in bulk, add a list of MarcFields to the dictionary
    add_additional_fields_to_list( [
        MarcField('400', 'd', True, 'alternative name', True, '  ', '', [
            SubField('a', False, 'full name'),
            SubField('3', False, 'name use'),
            SubField('2', False, 'source')
        ]),
        MarcField('671', 'd', True, 'title URLs', True, '  ', '', [
            SubField('g', False, 'type'),
            SubField('u', False, 'url'),
            SubField('2', False, 'source')
        ]),
        MarcField('902', 'd', True, 'ISSN', True, '  ', '', [
            SubField('a', False, 'ISSN'),
            SubField('2', False, 'source')
        ])
    ])
```

### Exceptions

A **MarcException** is raised when: 

- You try to add a subfield without a tag
- You try to add a subfield without a value
- You try to add a field with a unknown type (other **c**-ontrol or **d**-ata)
- You supplied to few information to add a subfield to a field
- You try to add a non-repeatable subfield more than once
- You try to add a non-defined subfield to a field (not in dictionary)
- You try to add a non-repeatable field more than once
- You try to add a non-defined field (not in dictionary)

## API

### Overview classes
- MarcDto           : marc data transfer object, holds up to 1 record at a time
- CField            : internal definition of a control field
- DField            : internal definition of a data field
- BaseField         : internal base class for CField and DField
- MarcField         : external definition of a field in a marc record (can be a CField or DField)
- SubField          : external definition of a subfield for MarcField of type 'd' (DField)
- MarcDictionary    : internal dictionary containing the definition of the marc fields
- MarcException     : custom exception (see section Exceptions above)

#### MarcDto

- **MarcDto**()

  initializes a new record
  
- __repr__([show_description:bool = False])

  When show_description is supplied as True, the fields and subfields will contain the description of these fields

- __len__([count_characters:bool = False])

  if count_characters is omitted or supplied as False this method returns the number of fields in the record
  otherwise is returns the total number of characters in the fields

- __json__()

  returns json representation of the record
  
  ```text
  [
	{
		'tag': <tag>,
		'...': ''
	},
	{
		'tag': <tag>,
		'...': ''
	},
	...
  ]
  ```
	
- **set_separators**(field_separator: str, subfield_separator:str)

  if both the field_separator and subfield_separator are non-empty strings the supplied separators will be used within the representation of the record
  
  <field_separator><tag><data>		for control fields
  <field_separator><tag><indicators>[<subfield_separator><tag><value>]+
  
- **create_field**(tag: str, [indicators: str = ''], [data: str = ''], [subfields = None]) -> CField | DField

  prepares a new field for the current record (**but does not insert it yet**)
  if tag does not point to an existing field definition in the MarcDictionary, a MarcException is raised.
  depending on the field definition:
  - the field created is a control field (CField) or data field (DField).
  - if is checked whether a field if repeatable or not (and whether it is already present in the current record)
  
  Depending on the type of the created field:
  - control field (CField): the data argument is used
  - data field (DField): the indicators and subfields are used
  
  returns the prepared field
  
- **insert_field**(marc_field: CField | DField)

  inserts the field to the current record if the field is not an exact duplicate of a field already present in the record
  
- **is_tag_present**(tag:str)

  returns true if at least one field with the supplied tag is present in the current record
  
- **perform_filter**(tag_present: str, tag_remove: str)

  if at least one field with the supplied tag_present is present in the current record, fields with the supplied tag_remove will be removed from the current record
  

#### CField  (subclass of BaseField)

- **CField**(tag: str, description: str, data: str)

  Initializes a new control field (CField)
  
- __repr__([show_description: bool = False])

  returns the contents of the field. The format depends on the value of show_description:
	if show_description is False: <field_separator><tag><data>
	if show_description is True : <field_separator><tag> [<description>] <data>
  
- __json__()

  returns the json representation of the field as:
  ```text
  {
     'tag': <tag>,
	 'data': <data>
  }
  ```
  
#### DField  (subclass of BaseField)
    
- **DField**(tag:str, description: str, inidicators: str, subfields: list[SubField])

  Initializes a new data field (DField)
  
- __repr__([show_description: bool = False])

  returns the contents of the field. The format depends on the value of show_description:
	if show_description is False: <field_separator><tag><indicators>[<subfield_separator><tag><value>]+
	if show_description is True : <field_separator><tag> [<description>] <indicators>[<subfield_separator><tag><value>]+

- __json__()

  returns the json representation of the field as:
  
  ```text
  {
	  'tag': <tag>,
	  'indicators': <indicators>
	  'subfields': [
	     {
		    'tag': <tag>
			'value': <value>
		 },
	     {
		    'tag': <tag>
			'value': <value>
		 },
         ...
	  ]
  }
  ```
  
- **addSubField**(tag: str, value: str)

  if tag does not refer to a subfield defined for current DField tag a MarcException is raised
  if defined subfield is not repeatable and it is already in the subfield list for the DField a MarcException is raised
  
  a new SubField object is created and added to the list of subfields for the DField
  

#### MarcField

This class is primarily used in the MarcDictionary and used to instantiate CField and DField objects

- **MarcField**(tag: str, fieldtype: str, repeatable: bool = False, description: str = 'not supplied', has_indicators: bool = True, indicators: str = '  ', data: str = '  ', subfields: Optional[list[SubField]] = None)

  initializes a new MarcField object

  - fieldtype is 'c' for control field or 'd' for data field
  - repeatable denotes whether more than 1 instance of this field can exist in a record
  - has_indicators denotes whether the field uses indicators
  
  if fieldtype is not 'c' or 'd' a MarcException is raised
  if fieldtype is 'c' has_indicators is set to False
  
- __json__()

  returns a json representation of the MarcField
  
  depending on the fieldtype as
  - 'c':
  
  ```text
  {
	'tag': <tag>,
	'fieldtype': <fieldtype>,
	'description': <description>
  }
  ```
  - 'd':
  ```text
  {
	'tag': <tag>,
	'fieldtype': <fieldtype>,
	'description': <description>,
	'has_indicators': <has_indicators>,
	'indicators': <indicators>,
	'subfields': [
	   [ { <subfield> } ]+
	]
  ```
  
- **add_SubField**([new_sf: SubField = None], [tag: str = ''], [repeatable: bool = False], [description: str = ''])

  if both new_sf is None and tag is empty a MarcException is raised
  
  if new_sf is None, but tag is supplied a new SubField instance is created with the tag, repeatable and description
  
  if new_sf.repeatable is False, it is checked if no other instance of the subfield is already present in the list of subfields, otherwise a MarcException is raised.
  
  the new subfield is added to the list of subfields of the current MarcField.
  
- **is_subfield_present**(tag: str)

  returns True if a subfield with the given tag is present in the list of subfields of the current MarcField
  
- **get_subfields**()

  returns the list of subfields for t he current MarcField, if the fieldtype is 'd', otherwise an empty list.

#### SubField

- **SubField**([tag: str = ''], [repeatable: bool = True], [description: str = ''], [value: str = 'dummy'])

  initializes a new SubField

  if either tag or value is an empty string a MarcException is raised

- __repr__([show_description: bool = False])

  if show_description is False returns <tag><value>
  otherwise returns <tag> [<description>] <value>
  
- __json__()

  returns the json representation of the current subfield
  
  ```text
  {
	'tag': <tag>,
	'description': <description>,
	'value': <value>
  }
  ```
  
## ISO 2709 Support

You can serialize a `MarcDto` to ISO 2709 (binary MARC21 format) and back using the provided functions:

### 🔄 Convert to ISO 2709
```python
from marc21 import MarcDto, to_iso2709

record = MarcDto()
record.insert_field(record.create_field(tag="001", data="123456"))
...
binary = to_iso2709(record)
with open("record.iso2709", "wb") as f:
    f.write(binary)
```

### 🔁 Load from ISO 2709
```python
from marc21 import from_iso2709

with open("record.iso2709", "rb") as f:
    binary = f.read()
record = from_iso2709(binary)
print(record.to_string())
```

---

## MARCXML Support

The library can also generate and read MARCXML format.

### 🔄 Convert to MARCXML
```python
from marc21 import to_marcxml

xml_string = to_marcxml(record)
print(xml_string)
```

### 🔁 Load from MARCXML
```python
from marc21 import from_xml

record = from_xml(xml_string)
print(record.to_string())
```

---

Both formats support full round-trip conversion, and are verified via unit tests for integrity. These functions are especially useful for interoperability with systems like library catalogs, OAI-PMH services, and archival platforms.


  
## Contributing

Feel free to suggest improvements and/or open a pull request

## To Do

Add functionality to:
- read marc21 records
- supply marc21 fields as json
- remove fields from dictionary

## Contact

- Author: John van der Vuurst
- Email (@OCLC)   : vdvuursj@oclc.org
- Email (external): JWvdVuurst@gmail.com

## Appendix - the current default dictionary

```json
[
    {
        "tag": "001",
        "type": "c",
        "repeatable": false,
        "description": "Control Number"
    },
    {
        "tag": "003",
        "type": "c",
        "repeatable": false,
        "description": "Control Number Identifier"
    },
    {
        "tag": "005",
        "type": "c",
        "repeatable": false,
        "description": "Date and Time of Latest Transaction"
    },
    {
        "tag": "006",
        "type": "c",
        "repeatable": false,
        "description": "Fixed-Length Data Elements - Additional Material Characteristics"
    },
    {
        "tag": "007",
        "type": "c",
        "repeatable": false,
        "description": "Physical Description Fixed Field-General Information"
    },
    {
        "tag": "008",
        "type": "c",
        "repeatable": false,
        "description": "Fixed-Length Data Elements"
    },
    {
        "tag": "010",
        "type": "d",
        "repeatable": false,
        "description": "Library of Congress Control Number",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "LC control number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "NUCMC control number"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Cancelled/Invalid LC control number"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field Link and Sequence number"
            }
        ]
    },
    {
        "tag": "013",
        "type": "d",
        "repeatable": true,
        "description": "Patent Control Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Country"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Type of number"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Status"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Party of document"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "015",
        "type": "d",
        "repeatable": true,
        "description": "National Bibliography Number",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "National Bibliography number"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Qualifying information"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Cancelled/Invalid national bibliography number"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "017",
        "type": "d",
        "repeatable": true,
        "description": "Copyright or legal deposit number",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Copyright or legal deposit number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Assigning agency"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Display Text"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Cancelled/Invalid Copyright or legal deposit number"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "018",
        "type": "d",
        "repeatable": false,
        "description": "Copyright Article-Fee Code ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Copyright article-fee code"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            }
        ]
    },
    {
        "tag": "020",
        "type": "d",
        "repeatable": true,
        "description": "International Standard Book Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "International Standard Book Number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Terms of availability"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Qualifying information"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid ISBN"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "022",
        "type": "d",
        "repeatable": true,
        "description": "International Standard Serial Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "ISSN-L"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Canceled ISSN-L"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Incorrect ISSN"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled ISSN"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "024",
        "type": "d",
        "repeatable": true,
        "description": "Other Standard Identifier ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Standard number or code"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Terms of availability"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Additional codes following the standard number or code"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Qualifying information"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid standard number or code"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of number or code"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "025",
        "type": "d",
        "repeatable": true,
        "description": "Overseas Acquisition Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Overseas acquisition number"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "026",
        "type": "d",
        "repeatable": true,
        "description": "Fingerprint Identifier ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "First and second groups of characters"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Third and fourth groups of characters"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Date"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Number of volume or part"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Unparsed fingerprint"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "027",
        "type": "d",
        "repeatable": true,
        "description": "Standard Technical Report Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Standard technical report number"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Qualifying information"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid number"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "028",
        "type": "d",
        "repeatable": true,
        "description": "Publisher or Distributor Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Publisher or distributor number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Source"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Qualifying information"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "030",
        "type": "d",
        "repeatable": true,
        "description": "CODEN Designation ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "CODEN"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid CODEN"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "031",
        "type": "d",
        "repeatable": true,
        "description": "Musical Incipits Information ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Number of work"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Number of movement"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Number of excerpt"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Caption or heading"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Role"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Clef"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Voice/instrument"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Key signature"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Time signature"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Musical notation"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "General note"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Key or mode"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Coded validity note"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Text incipit"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Link text"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "System code"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "032",
        "type": "d",
        "repeatable": true,
        "description": "Postal Registration Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Postal registration number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Source agency assigning number"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "033",
        "type": "d",
        "repeatable": true,
        "description": "Date/Time and Place of an Event ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Formatted date/time"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Geographic classification area code"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Geographic classification subarea code"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Place of event"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "034",
        "type": "d",
        "repeatable": true,
        "description": "Coded Cartographic Mathematical Data ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Category of scale"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Constant ratio linear horizontal scale"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Constant ratio linear vertical scale"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Coordinates - westernmost longitude"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Coordinates - easternmost longitude"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Coordinates - northernmost latitude"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Coordinates - southernmost latitude"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Angular scale"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Declination - northern limit"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Declination - southern limit"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Right ascension - eastern limit"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Right ascension - western limit"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Equinox"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Distance from earth"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "G-ring latitude"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "G-ring longitude"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Beginning date"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Ending date"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Name of extraterrestrial body"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "035",
        "type": "d",
        "repeatable": true,
        "description": "System Control Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "System control number"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid control number"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "036",
        "type": "d",
        "repeatable": true,
        "description": "Original Study Number for Computer Data Files ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Original study number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Source agency assigning number"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "037",
        "type": "d",
        "repeatable": true,
        "description": "Source of Acquisition ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Stock number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Source of stock number/acquisition"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Terms of availability"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Form of issue"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Additional format characteristics"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "038",
        "type": "d",
        "repeatable": false,
        "description": "Record Content Licensor ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Record content licensor"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "040",
        "type": "d",
        "repeatable": false,
        "description": "Cataloging Source ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Original cataloging agency"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Language of cataloging"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Transcribing agency"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Modifying agency"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Description conventions"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "041",
        "type": "d",
        "repeatable": true,
        "description": "Language Code ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Language code of text/sound track or separate title"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Language code of summary or abstract"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Language code of sung or spoken text"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Language code of librettos"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Language code of table of contents"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Language code of accompanying material other than librettos and transcripts"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Language code of original"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Language code of intertitles"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Language code of subtitles"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Language code of intermediate translations"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Language code of original accompanying materials other than librettos"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Language code of original libretto"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Language code of captions"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Language code of accessible audio"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Language code of accessible visual language (non-textual)"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Language code of accompanying transcripts for audiovisual materials"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of code"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "042",
        "type": "d",
        "repeatable": false,
        "description": "Authentication Code ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Authentication code"
            }
        ]
    },
    {
        "tag": "043",
        "type": "d",
        "repeatable": true,
        "description": "Geographic Area Code ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Geographic area code"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Local GAC code"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "ISO code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of local code"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "044",
        "type": "d",
        "repeatable": false,
        "description": "Country of Publishing/Producing Entity Code ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "MARC country code"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Local subentity code"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "ISO country code"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of local subentity code"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "045",
        "type": "d",
        "repeatable": false,
        "description": "Time Period of Content ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Time period code"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Formatted 9999 B.C. through C.E. time period"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Formatted pre-9999 B.C. time period"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "046",
        "type": "d",
        "repeatable": true,
        "description": "Special Coded Dates ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Type of date code"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Date 1, B.C.E. date"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Date 1, C.E. date"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date 2, B.C.E. date"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Date 2, C.E. date"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Date resource modified"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Beginning or single date created"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Ending date created"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Beginning of date valid"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "End of date valid"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Single or starting date for aggregated content"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Ending date for aggregated content"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of date"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "047",
        "type": "d",
        "repeatable": true,
        "description": "Form of Musical Composition Code ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Form of musical composition code"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of code"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "048",
        "type": "d",
        "repeatable": true,
        "description": "Number of Musical Instruments or Voices Codes ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Performer or ensemble"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Soloist"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of code"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "050",
        "type": "d",
        "repeatable": true,
        "description": "Library of Congress Call Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "051",
        "type": "d",
        "repeatable": true,
        "description": "Library of Congress Copy, Issue, Offprint Statement ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Copy information"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "052",
        "type": "d",
        "repeatable": true,
        "description": "Geographic Classification ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Geographic classification area code"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Geographic classification subarea code"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Populated place name"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Code source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "055",
        "type": "d",
        "repeatable": true,
        "description": "Classification Numbers Assigned in Canada ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of call/class number"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "060",
        "type": "d",
        "repeatable": true,
        "description": "National Library of Medicine Call Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "061",
        "type": "d",
        "repeatable": true,
        "description": "National Library of Medicine Copy Statement ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Copy information"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "066",
        "type": "d",
        "repeatable": false,
        "description": "Character Sets Present ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Primary G0 character set"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Primary G1 character set"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Alternate G0 or G1 character set"
            }
        ]
    },
    {
        "tag": "070",
        "type": "d",
        "repeatable": true,
        "description": "National Agricultural Library Call Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "071",
        "type": "d",
        "repeatable": true,
        "description": "National Agricultural Library Copy Statement ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Copy information"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "072",
        "type": "d",
        "repeatable": true,
        "description": "Subject Category Code ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Subject category code"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Subject category code subdivision"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "074",
        "type": "d",
        "repeatable": true,
        "description": "GPO Item Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "GPO item number"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid GPO item number"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "080",
        "type": "d",
        "repeatable": true,
        "description": "Universal Decimal Classification Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Universal Decimal Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Common auxiliary subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Edition identifier"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "082",
        "type": "d",
        "repeatable": true,
        "description": "Dewey Decimal Classification Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Standard or optional designation"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Assigning agency"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Edition information"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "083",
        "type": "d",
        "repeatable": true,
        "description": "Additional Dewey Decimal Classification Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Classification number--Ending number of span"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Standard or optional designation"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Assigning agency"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Table sequence number for internal subarrangement or add table"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Table identification"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Edition information"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "084",
        "type": "d",
        "repeatable": true,
        "description": "Other Classification Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Item number"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Assigning agency"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Number source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "085",
        "type": "d",
        "repeatable": true,
        "description": "Synthesized Classification Number Components ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Number where instructions are found-single number or beginning number of span"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Base number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Classification number-ending number of span"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Facet designator"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Root number"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Digits added from classification number in schedule or external table"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Digits added from internal subarrangement or add table"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Number being analyzed"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Number in internal subarrangement or add table where instructions are found"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Table identification-Internal subarrangement or add table"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Table sequence number for internal subarrangement or add table"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Table identification"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "086",
        "type": "d",
        "repeatable": true,
        "description": "Government Document Classification Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Classification number"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid classification number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Number source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "088",
        "type": "d",
        "repeatable": true,
        "description": "Report Number ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Report number"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Canceled/invalid report number"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "090",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "091",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "092",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "093",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "094",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "095",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "096",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "097",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "098",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "099",
        "type": "d",
        "repeatable": true,
        "description": "Local Call Numbers",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "100",
        "type": "d",
        "repeatable": false,
        "description": "Main Entry - Personal Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Personal name"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Numeration"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Titles and words associated with a name"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Dates associated with a name"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Attribution qualifier"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Fuller form of name"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Affiliation"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "110",
        "type": "d",
        "repeatable": false,
        "description": "Main Entry - Corporate Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Corporate name or jurisdiction name as entry element"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Affiliation"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "111",
        "type": "d",
        "repeatable": false,
        "description": "Main Entry - Meeting Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Meeting name or jurisdiction name as entry element"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Name of meeting following jurisdiction name entry element"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Affiliation"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "130",
        "type": "d",
        "repeatable": false,
        "description": "Main Entry - Uniform Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of treaty signing"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title of a work"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "210",
        "type": "d",
        "repeatable": true,
        "description": "Abbreviated Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Abbreviated title"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Qualifying information"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "222",
        "type": "d",
        "repeatable": true,
        "description": "Key Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Key title"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Qualifying information"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "240",
        "type": "d",
        "repeatable": false,
        "description": "Uniform Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of treaty signing"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "242",
        "type": "d",
        "repeatable": true,
        "description": "Translation of Title by Cataloging Agency ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Remainder of title"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Statement of responsibility, etc."
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Language code of translated title"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "243",
        "type": "d",
        "repeatable": false,
        "description": "Collective Uniform Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of treaty signing"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "245",
        "type": "d",
        "repeatable": false,
        "description": "Title Statement ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Remainder of title"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Statement of responsibility, etc."
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Inclusive dates"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Bulk dates"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "246",
        "type": "d",
        "repeatable": true,
        "description": "Varying Form of Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Title proper/short title"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Remainder of title"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date or sequential designation"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Display text"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "247",
        "type": "d",
        "repeatable": true,
        "description": "Former Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Remainder of title"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date or sequential designation"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "250",
        "type": "d",
        "repeatable": true,
        "description": "Edition Statement ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Edition statement"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Remainder of edition statement"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "251",
        "type": "d",
        "repeatable": true,
        "description": "Version Information ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Version"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "254",
        "type": "d",
        "repeatable": false,
        "description": "Musical Presentation Statement ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Musical presentation statement"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "255",
        "type": "d",
        "repeatable": true,
        "description": "Cartographic Mathematical Data ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Statement of scale"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Statement of projection"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Statement of coordinates"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Statement of zone"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Statement of equinox"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Outer G-ring coordinate pairs"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Exclusion G-ring coordinate pairs"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "256",
        "type": "d",
        "repeatable": false,
        "description": "Computer File Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Computer file characteristics"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "257",
        "type": "d",
        "repeatable": true,
        "description": "Country of Producing Entity ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Country of producing entity"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "258",
        "type": "d",
        "repeatable": true,
        "description": "Philatelic Issue Data ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Issuing jurisdiction"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Denomination"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "260",
        "type": "d",
        "repeatable": true,
        "description": "Publication, Distribution, etc. ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Place of publication, distribution, etc."
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Name of publisher, distributor, etc."
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Date of publication, distribution, etc."
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Place of manufacture"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Manufacturer"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Date of manufacture"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number (Imprint)"
            }
        ]
    },
    {
        "tag": "263",
        "type": "d",
        "repeatable": false,
        "description": "Projected Publication Date ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Projected publication date"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "264",
        "type": "d",
        "repeatable": true,
        "description": "Production, Publication, Distribution, Manufacture, and Copyright Notice ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Place of production, publication, distribution, manufacture"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Name of producer, publisher, distributor, manufacturer"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Date of production, publication, distribution, manufacture, or copyright notice"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "270",
        "type": "d",
        "repeatable": true,
        "description": "Address ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Address"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "City"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "State or province"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Country"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Postal code"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Terms preceding attention name"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Attention name"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Attention position"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Type of address"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Specialized telephone number"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Telephone number"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Fax number"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Electronic mail address"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "TDD or TTY number"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Contact person"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Title of contact person"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Hours"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "300",
        "type": "d",
        "repeatable": false,
        "description": "Physical Description ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Extent"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Other physical details"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Dimensions"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Accompanying material"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Type of unit"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Size of unit"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "306",
        "type": "d",
        "repeatable": true,
        "description": "Playing Time ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Playing time"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "307",
        "type": "d",
        "repeatable": true,
        "description": "Hours, etc. ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Playing time"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "310",
        "type": "d",
        "repeatable": true,
        "description": "Current Publication Frequency ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Current publication frequency"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Date of current publication frequency"
            },
            {
                "tag": "0",
                "repeatable": false,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "321",
        "type": "d",
        "repeatable": true,
        "description": "Former Publication Frequency ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Former publication frequency"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Dates of former publication frequency"
            },
            {
                "tag": "0",
                "repeatable": false,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "334",
        "type": "d",
        "repeatable": true,
        "description": "Mode of Issuance ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Mode of issuance term"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Mode of issuance code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "335",
        "type": "d",
        "repeatable": true,
        "description": "Extension Plan ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Extension plan term"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Extension plan code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "336",
        "type": "d",
        "repeatable": true,
        "description": "Content Type ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Content type term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Content type code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "337",
        "type": "d",
        "repeatable": true,
        "description": "Media Type ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Media type term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Media type code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "338",
        "type": "d",
        "repeatable": true,
        "description": "Carrier Type ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Carrier type term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Carrier type code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "340",
        "type": "d",
        "repeatable": true,
        "description": "Physical Medium ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Material base and configuration"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Dimensions"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Materials applied to surface"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Information recording technique"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Support"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Reduction ratio value"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Color content"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Location within medium"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Technical specifications of medium"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Generation"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Layout"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Binding"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Book format"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Font size"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Polarity"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Illustrative content"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Reduction ratio designator"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "341",
        "type": "d",
        "repeatable": true,
        "description": "Accessibility Content ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Content access mode"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Textual assistive features"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Visual assistive features"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Auditory assistive features"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Tactile assistive features"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "342",
        "type": "d",
        "repeatable": true,
        "description": "Geospatial Reference Data ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Name"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Coordinate units or distance units"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Latitude resolution"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Longitude resolution"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Standard parallel or oblique line latitude"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Oblique line longitude"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Longitude of central meridian or projection center"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Latitude of projection center or projection origin"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "False easting"
            },
            {
                "tag": "j",
                "repeatable": false,
                "description": "False northing"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "Scale factor"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Height of perspective point above surface"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Azimuthal angle"
            },
            {
                "tag": "n",
                "repeatable": false,
                "description": "Azimuth measure point longitude or straight vertical longitude from pole"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Landsat number and path number"
            },
            {
                "tag": "p",
                "repeatable": false,
                "description": "Zone identifier"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Ellipsoid name"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Semi-major axis"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Denominator of flattening ratio"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Vertical resolution"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Vertical encoding method"
            },
            {
                "tag": "v",
                "repeatable": false,
                "description": "Local planar, local, or other projection or grid description"
            },
            {
                "tag": "w",
                "repeatable": false,
                "description": "Local planar or local georeference information"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Reference method used"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "343",
        "type": "d",
        "repeatable": true,
        "description": "Planar Coordinate Data ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Planar coordinate encoding method"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Planar distance units"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Abscissa resolution"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Ordinate resolution"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Distance resolution"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Bearing resolution"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Bearing units"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Bearing reference direction"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Bearing reference meridian"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "344",
        "type": "d",
        "repeatable": true,
        "description": "Sound Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Type of recording"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Recording medium"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Playing speed"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Groove characteristic"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Track configuration"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Tape configuration"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Configuration of playback channels"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Special playback characteristics"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Sound content"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Original capture and storage technique"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "345",
        "type": "d",
        "repeatable": true,
        "description": "Moving Image Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Presentation format"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Projection speed"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Aspect ratio value"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Aspect ratio designator"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "346",
        "type": "d",
        "repeatable": true,
        "description": "Video Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Video format"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Broadcast standard"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "347",
        "type": "d",
        "repeatable": true,
        "description": "Digital File Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "File type"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Encoding format"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "File size"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Resolution"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Regional encoding"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Encoded bitrate"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "348",
        "type": "d",
        "repeatable": true,
        "description": "Notated Music Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Format of notated music term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Format of notated music code"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Form of musical notation term"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Form of musical notation code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "351",
        "type": "d",
        "repeatable": true,
        "description": "Organization and Arrangement of Materials ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Organization"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Arrangement"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Hierarchical level"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "352",
        "type": "d",
        "repeatable": true,
        "description": "Digital Graphic Representation ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Direct reference method"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Object type"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Object count"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Row count"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Column count"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Vertical count"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "VPF topology level"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Indirect reference description"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Format of the digital image"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "353",
        "type": "d",
        "repeatable": true,
        "description": "Supplementary Content Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Supplementary content term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Supplementary content code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "355",
        "type": "d",
        "repeatable": true,
        "description": "Security Classification Control ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Security classification"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Handling instructions"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "External dissemination information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Downgrading or declassification event"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Classification system"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Country of origin code"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Downgrading date"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Declassification date"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Authorization"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "357",
        "type": "d",
        "repeatable": true,
        "description": "Originator Dissemination Control ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Originator control term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Originating agency"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Authorized recipients of material"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Other restrictions"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "361",
        "type": "d",
        "repeatable": true,
        "description": "Structured Ownership and Custodial History ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Name"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Ownership and custodial history evidence term"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "Formatted date"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Date"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Type of ownership and custodial history information"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Shelf mark of copy described"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "Identifier of the copy described"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "362",
        "type": "d",
        "repeatable": true,
        "description": "Dates of Publication and/or Sequential Designation ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Dates of publication and/or sequential designation"
            },
            {
                "tag": "z",
                "repeatable": false,
                "description": "Source of information"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "363",
        "type": "d",
        "repeatable": true,
        "description": "Normalized Date and Sequential Designation ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "First level of enumeration"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Second level of enumeration"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Third level of enumeration"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Fourth level of enumeration"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Fifth level of enumeration"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Sixth level of enumeration"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Alternative numbering scheme, first level of enumeration"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Alternative numbering scheme, second level of enumeration"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "First level of chronology"
            },
            {
                "tag": "j",
                "repeatable": false,
                "description": "Second level of chronology"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "Third level of chronology"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Fourth level of chronology"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Alternative numbering scheme, chronology"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "First level textual designation"
            },
            {
                "tag": "v",
                "repeatable": false,
                "description": "First level of chronology, issuance"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": false,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "365",
        "type": "d",
        "repeatable": true,
        "description": "Trade Price ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Price type code"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Price amount"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Currency code"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Unit of pricing"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Price note"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Price effective from"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Price effective until"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Tax rate 1"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Tax rate 2"
            },
            {
                "tag": "j",
                "repeatable": false,
                "description": "ISO country code"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "MARC country code"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Identification of pricing entity"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of price type code"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "366",
        "type": "d",
        "repeatable": true,
        "description": "Trade Availability Information ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Publishers' compressed title identification"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Detailed date of publication"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Availability status code"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Expected next availability date"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Note"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Publisher's discount category"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Date made out of print"
            },
            {
                "tag": "j",
                "repeatable": false,
                "description": "ISO country code"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "MARC country code"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Identification of agency"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of availability status code"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "370",
        "type": "d",
        "repeatable": true,
        "description": "Associated Place ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "c",
                "repeatable": true,
                "description": "Associated country"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Other associated place"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Place of origin of work or expression"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Start period"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "End period"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Source of information"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "377",
        "type": "d",
        "repeatable": true,
        "description": "Associated Language ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Language code"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language term"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "380",
        "type": "d",
        "repeatable": true,
        "description": "Form of Work ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Form of work"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "381",
        "type": "d",
        "repeatable": true,
        "description": "Other Distinguishing Characteristics of Work or Expression ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Other distinguishing characteristic"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Source of information"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "382",
        "type": "d",
        "repeatable": true,
        "description": "Medium of Performance ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Medium of performance"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Soloist"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Doubling instrument"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Number of ensembles of the same type"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of performers of the same medium"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Alternative medium of performance"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Total number of individuals performing alongside ensembles"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Total number of performers"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Total number of ensembles"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "383",
        "type": "d",
        "repeatable": true,
        "description": "Numeric Designation of Musical Work ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Serial number"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Opus number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Thematic index number"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Thematic index code"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Publisher associated with opus number"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "384",
        "type": "d",
        "repeatable": true,
        "description": "Key ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Key"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "385",
        "type": "d",
        "repeatable": true,
        "description": "Audience Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Audience term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Audience code"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Demographic group term"
            },
            {
                "tag": "n",
                "repeatable": false,
                "description": "Demographic group code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "386",
        "type": "d",
        "repeatable": true,
        "description": "Creator/Contributor Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Creator/contributor term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Creator/contributor code"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Demographic group term"
            },
            {
                "tag": "n",
                "repeatable": false,
                "description": "Demographic group code"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "387",
        "type": "d",
        "repeatable": true,
        "description": "Representative Expression Characteristics ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Aspect ratio of representative expression"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Color content of representative expression"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Content type of representative expression"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of capture of representative expression"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Date of representative expression"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Duration of representative expression"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Intended audience of representative expression"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Language of representative expression"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Place of capture of representative expression"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Projection of cartographic content of representative expression"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Scale of representative expression"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Script of representative expression"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Sound content of representative expression"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "388",
        "type": "d",
        "repeatable": true,
        "description": "Time Period of Creation ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Time period of creation term"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "500",
        "type": "d",
        "repeatable": true,
        "description": "General Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "General note"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "501",
        "type": "d",
        "repeatable": true,
        "description": "With Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "With note"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "502",
        "type": "d",
        "repeatable": true,
        "description": "Dissertation Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Dissertation note"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Degree type"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Name of granting institution"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Year degree granted"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Dissertation identifier"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "504",
        "type": "d",
        "repeatable": true,
        "description": "Bibliography, etc. Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Bibliography, etc. note"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Number of references"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "505",
        "type": "d",
        "repeatable": true,
        "description": "Formatted Contents Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Formatted contents note"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Statement of responsibility"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "506",
        "type": "d",
        "repeatable": true,
        "description": "Restrictions on Access Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Formatted contents note"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Statement of responsibility"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "507",
        "type": "d",
        "repeatable": true,
        "description": "Scale Note for Visual Materials ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Representative fraction of scale note"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Remainder of scale note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "508",
        "type": "d",
        "repeatable": true,
        "description": "Creation/Production Credits Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Creation/production credits note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "510",
        "type": "d",
        "repeatable": true,
        "description": "Citation/References Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Name of source"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Coverage of source"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Location within source"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "511",
        "type": "d",
        "repeatable": true,
        "description": "Participant or Performer Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Participant or performer note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "513",
        "type": "d",
        "repeatable": true,
        "description": "Type of Report and Period Covered Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Type of report"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Period covered"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "514",
        "type": "d",
        "repeatable": true,
        "description": "Data Quality Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Attribute accuracy report"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Attribute accuracy value"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Attribute accuracy explanation"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Logical consistency report"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Completeness report"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Horizontal position accuracy report"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Horizontal position accuracy value"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Horizontal position accuracy explanation"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Vertical positional accuracy report"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Vertical positional accuracy value"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Vertical positional accuracy explanation"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Cloud cover"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Display note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "515",
        "type": "d",
        "repeatable": true,
        "description": "Numbering Peculiarities Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Numbering peculiarities note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "516",
        "type": "d",
        "repeatable": true,
        "description": "Type of Computer File or Data Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Type of computer file or data note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "518",
        "type": "d",
        "repeatable": true,
        "description": "Date/Time and Place of an Event Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Date/time and place of an event note"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of event"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other event information"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Place of event"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "520",
        "type": "d",
        "repeatable": true,
        "description": "Summary, etc. ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Summary, etc."
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Expansion of summary note"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Assigning source"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "521",
        "type": "d",
        "repeatable": true,
        "description": "Target Audience Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Target audience note"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "522",
        "type": "d",
        "repeatable": true,
        "description": "Geographic Coverage Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Geographic coverage note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "524",
        "type": "d",
        "repeatable": true,
        "description": "Preferred Citation of Described Materials Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Preferred citation of described materials note"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of schema used"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "525",
        "type": "d",
        "repeatable": true,
        "description": "Supplement Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Supplement note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "526",
        "type": "d",
        "repeatable": true,
        "description": "Study Program Information Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Program name"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Interest level"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Reading level"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Title point value"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Display text"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "530",
        "type": "d",
        "repeatable": true,
        "description": "Additional Physical Form available Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Additional physical form available note"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Availability source"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Availability conditions"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Order number"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "532",
        "type": "d",
        "repeatable": true,
        "description": "Accessibility Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Summary of accessibility"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "533",
        "type": "d",
        "repeatable": true,
        "description": "Reproduction Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Type of reproduction"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Place of reproduction"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Agency responsible for reproduction"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Date of reproduction"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Physical description of reproduction"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Series statement of reproduction"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Dates and/or sequential designation of issues reproduced"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note about reproduction"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Fixed-length data elements of reproduction"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "534",
        "type": "d",
        "repeatable": true,
        "description": "Original Version Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry of original"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition statement of original"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Publication, distribution, etc. of original"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Physical description, etc. of original"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Series statement of original"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Key title of original"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Location of original"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note about original"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other resource identifier"
            },
            {
                "tag": "p",
                "repeatable": false,
                "description": "Introductory phrase"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title statement of original"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "International Standard Book Number"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "535",
        "type": "d",
        "repeatable": true,
        "description": "Location of Originals/Duplicates Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Custodian"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Postal address"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Country"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Telecommunications address"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Repository location code"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "536",
        "type": "d",
        "repeatable": true,
        "description": "Funding Information Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Text of note"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Contract number"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Grant number"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Undifferentiated number"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Program element number"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Project number"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Task number"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Work unit number"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "538",
        "type": "d",
        "repeatable": true,
        "description": "System Details Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "System details note"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Display text"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "540",
        "type": "d",
        "repeatable": true,
        "description": "Terms Governing Use and Reproduction Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Terms governing use and reproduction"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Jurisdiction"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Authorization"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Authorized users"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Use and reproduction rights"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Availability date"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Supplying agency"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "541",
        "type": "d",
        "repeatable": true,
        "description": "Immediate Source of Acquisition Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Source of acquisition"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Address"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Method of acquisition"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Date of acquisition"
            },
            {
                "tag": "e",
                "repeatable": false,
                "description": "Accession number"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Owner"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Purchase price"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Extent"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Type of unit"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "542",
        "type": "d",
        "repeatable": true,
        "description": "Information Relating to Copyright Status ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Personal creator"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Personal creator death date"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Corporate creator"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Copyright holder"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Copyright holder contact information"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Copyright statement"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Copyright date"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Copyright renewal date"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Publication date"
            },
            {
                "tag": "j",
                "repeatable": false,
                "description": "Creation date"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Publisher"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Copyright status"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Publication status"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Research date"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Country of publication or creation"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Supplying agency"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Jurisdiction of copyright assessment"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Source of information"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "544",
        "type": "d",
        "repeatable": true,
        "description": "Location of Other Archival Materials Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Custodian"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Address"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Country"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Title"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Provenance"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "545",
        "type": "d",
        "repeatable": true,
        "description": "Biographical or Historical Data ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Biographical or historical data"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Expansion"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "546",
        "type": "d",
        "repeatable": true,
        "description": "Language Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Language note"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Information code or alphabet"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "547",
        "type": "d",
        "repeatable": true,
        "description": "Former Title Complexity Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Former title complexity note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "550",
        "type": "d",
        "repeatable": true,
        "description": "Issuing Body Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Issuing body note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "552",
        "type": "d",
        "repeatable": true,
        "description": "Entity and Attribute Information Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Entity type label"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Entity type definition and source"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Attribute label"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Attribute definition and source"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Enumerated domain value"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Enumerated domain value definition and source"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Range domain minimum and maximum"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Codeset name and source"
            },
            {
                "tag": "i",
                "repeatable": false,
                "description": "Unrepresentable domain"
            },
            {
                "tag": "j",
                "repeatable": false,
                "description": "Attribute units of measurement and resolution"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "Beginning and ending date of attribute values"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Attribute value accuracy"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Attribute value accuracy explanation"
            },
            {
                "tag": "n",
                "repeatable": false,
                "description": "Attribute measurement frequency"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Entity and attribute overview"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Entity and attribute detail citation"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Display note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "555",
        "type": "d",
        "repeatable": true,
        "description": "Cumulative Index/Finding Aids Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Cumulative index/finding aids note"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Availability source"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Degree of control"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Bibliographic reference"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "556",
        "type": "d",
        "repeatable": true,
        "description": "Information About Documentation Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Information about documentation note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "International Standard Book Number"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "561",
        "type": "d",
        "repeatable": true,
        "description": "Ownership and Custodial History ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "History"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "562",
        "type": "d",
        "repeatable": true,
        "description": "Copy and Version Identification Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Identifying markings"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Copy identification"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Version identification"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Presentation format"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Number of copies"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "563",
        "type": "d",
        "repeatable": true,
        "description": "Binding Information ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Binding note"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "565",
        "type": "d",
        "repeatable": true,
        "description": "Case File Characteristics Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Number of cases/variables"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Name of variable"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Unit of analysis"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Universe of data"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Filing scheme or code"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "567",
        "type": "d",
        "repeatable": true,
        "description": "Methodology Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Methodology note"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Controlled term"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "580",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Complexity Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Linking entry complexity note"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "581",
        "type": "d",
        "repeatable": true,
        "description": "Publications About Described Materials Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Publications about described materials note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "International Standard Book Number"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "583",
        "type": "d",
        "repeatable": true,
        "description": "Action Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Action"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Action identification"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Time/date of action"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Action interval"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Contingency for action"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Authorization"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Jurisdiction"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Method of action"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Site of action"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Action agent"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Status"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Extent"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Type of unit"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "584",
        "type": "d",
        "repeatable": true,
        "description": "Accumulation and Frequency of Use Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Accumulation"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Frequency of use"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "585",
        "type": "d",
        "repeatable": true,
        "description": "Exhibitions Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Exhibitions note"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "586",
        "type": "d",
        "repeatable": true,
        "description": "Awards Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Awards note"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "588",
        "type": "d",
        "repeatable": true,
        "description": "Source of Description, Etc. Note ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Source of description note"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "590",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "591",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "592",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "593",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "594",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "595",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "596",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "597",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "598",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "599",
        "type": "d",
        "repeatable": true,
        "description": "Local Notes",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "600",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Personal Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Personal name"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Numeration"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Titles and other words associated with a name"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Dates associated with a name"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Attribution qualifier"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Fuller form of name"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Affiliation"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "610",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Corporate Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Corporate name or jurisdiction name as entry element"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Affiliation"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "611",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Meeting Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Meeting name or jurisdiction name as entry element"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Name of meeting following jurisdiction name entry element"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Affiliation"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "630",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Uniform Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "647",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Named Event ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Named event"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of named event"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Date of named event"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "648",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Chronological Term ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Chronological term"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "650",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Topical Term ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Topical term or geographic name entry element"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Topical term following geographic name entry element"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Location of event"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Active dates"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "651",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Geographic Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Geographic name"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "653",
        "type": "d",
        "repeatable": true,
        "description": "Index Term - Uncontrolled ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Uncontrolled term"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "654",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Faceted Topical Terms ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Focus term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Non-focus term"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Facet/hierarchy designation"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "655",
        "type": "d",
        "repeatable": true,
        "description": "Index Term - Genre/Form ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Genre/form data or focus term"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Non-focus term"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Facet/hierarchy designation"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "656",
        "type": "d",
        "repeatable": true,
        "description": "Index Term - Occupation ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Occupation"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "Form"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "657",
        "type": "d",
        "repeatable": true,
        "description": "Index Term - Function ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Function"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Form subdivision"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "General subdivision"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Chronological subdivision"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Geographic subdivision"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "658",
        "type": "d",
        "repeatable": true,
        "description": "Index Term - Curriculum Objective ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main curriculum objective"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Subordinate curriculum objective"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Curriculum code"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Correlation factor"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term or code"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "662",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Hierarchical Place Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Country or larger entity"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "First-order political jurisdiction"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Intermediate political jurisdiction"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "City"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "City subsection"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Other nonjurisdictional geographic region and feature"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Extraterrestrial area"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "688",
        "type": "d",
        "repeatable": true,
        "description": "Subject Added Entry - Type of Entity Unspecified ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Name, title, or term"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of name, title, or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "690",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "691",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "692",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "693",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "694",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "695",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "696",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "697",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "698",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "699",
        "type": "d",
        "repeatable": true,
        "description": "Local Subject Access Fields ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "700",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Personal Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Personal name"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Numeration"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Titles and other words associated with a name"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Dates associated with a name"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Attribution qualifier"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Fuller form of name"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Affiliation"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "710",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Corporate Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Corporate name or jurisdiction name as entry element"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Medium"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Affiliation"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": true,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": true,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "711",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Meeting Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Meeting name or jurisdiction name as entry element"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Name of meeting following jurisdiction name entry element"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Affiliation"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": true,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "720",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Uncontrolled Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Name"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "730",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Uniform Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of treaty signing"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "740",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Uncontrolled Related/Analytical Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Uncontrolled related/analytical title"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "751",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Geographic Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Geographic name"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "752",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Hierarchical Place Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Country or larger entity"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "First-order political jurisdiction"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Intermediate political jurisdiction"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "City"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "City subsection"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Other nonjurisdictional geographic region and feature"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Extraterrestrial area"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "753",
        "type": "d",
        "repeatable": true,
        "description": "System Details Access to Computer Files ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Make and model of machine"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Programming language"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Operating system"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of term"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "754",
        "type": "d",
        "repeatable": true,
        "description": "Added Entry - Taxonomic Identification ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Taxonomic name"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Taxonomic category"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Common or alternative name"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Non-public note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of taxonomic identification"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "758",
        "type": "d",
        "repeatable": true,
        "description": "Resource Identifier ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Label"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "760",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "761",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "762",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "763",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "764",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "765",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "766",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "767",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "768",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "769",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "770",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "771",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "772",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "773",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "774",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "775",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "776",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "777",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "778",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "779",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "780",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "781",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "782",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "783",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "784",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "785",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "786",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "787",
        "type": "d",
        "repeatable": true,
        "description": "Linking Entry Fields - General Information",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "788",
        "type": "d",
        "repeatable": true,
        "description": "Parallel Description in Another Language of Cataloging ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Main entry heading"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Edition"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Qualifying information"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Place, publisher, and date of publication"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Related parts"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Physical description"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Relationship information"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "m",
                "repeatable": false,
                "description": "Material-specific details"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Note"
            },
            {
                "tag": "o",
                "repeatable": true,
                "description": "Other item identifier"
            },
            {
                "tag": "s",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": false,
                "description": "CODEN designation"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "800",
        "type": "d",
        "repeatable": true,
        "description": "Series Added Entry - Personal Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Personal name"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Numeration"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Titles and other words associated with a name"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Dates associated with a name"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Attribution qualifier"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Fuller form of name"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Affiliation"
            },
            {
                "tag": "v",
                "repeatable": false,
                "description": "Volume/sequential designation"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Bibliographic record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "810",
        "type": "d",
        "repeatable": true,
        "description": "Series Added Entry - Corporate Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Corporate name or jurisdiction name as entry element"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Affiliation"
            },
            {
                "tag": "v",
                "repeatable": false,
                "description": "Volume/sequential designation"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Bibliographic record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "811",
        "type": "d",
        "repeatable": true,
        "description": "Series Added Entry - Meeting Name ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Meeting name or jurisdiction name as entry element"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Location of meeting"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of meeting or treaty signing"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Subordinate unit"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Relator term"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section/meeting"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Name of meeting following jurisdiction name entry element"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Affiliation"
            },
            {
                "tag": "v",
                "repeatable": false,
                "description": "Volume/sequential designation"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Bibliographic record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "4",
                "repeatable": true,
                "description": "Relationship"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "830",
        "type": "d",
        "repeatable": true,
        "description": "Series Added Entry - Uniform Title ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Uniform title"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Date of treaty signing"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Date of a work"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Miscellaneous information"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Medium"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Form subheading"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Language of a work"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Medium of performance for music"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Number of part/section of a work"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Arranged statement for music"
            },
            {
                "tag": "p",
                "repeatable": true,
                "description": "Name of part/section of a work"
            },
            {
                "tag": "r",
                "repeatable": false,
                "description": "Key for music"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Version"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Title of a work"
            },
            {
                "tag": "v",
                "repeatable": false,
                "description": "Volume/sequential designation"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Bibliographic record control number"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "International Standard Serial Number"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of heading or term"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": true,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Control subfield"
            }
        ]
    },
    {
        "tag": "841",
        "type": "d",
        "repeatable": true,
        "description": "Holdings Coded Data Values ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "842",
        "type": "d",
        "repeatable": true,
        "description": "Textual Physical Form Designator ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "843",
        "type": "d",
        "repeatable": true,
        "description": "Reproduction Note ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "844",
        "type": "d",
        "repeatable": true,
        "description": "Name of Unit ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "845",
        "type": "d",
        "repeatable": true,
        "description": "Terms Governing Use and Reproduction ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "850",
        "type": "d",
        "repeatable": true,
        "description": "Holding Institution ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Holding institution"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "852",
        "type": "d",
        "repeatable": true,
        "description": "Location ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Location"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Sublocation or collection"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Shelving location"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Former shelving location"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Address"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Coded location qualifier"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Non-coded location qualifier"
            },
            {
                "tag": "h",
                "repeatable": false,
                "description": "Classification part"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Item part"
            },
            {
                "tag": "j",
                "repeatable": false,
                "description": "Shelving control number"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Call number prefix"
            },
            {
                "tag": "l",
                "repeatable": false,
                "description": "Shelving form of title"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Call number suffix"
            },
            {
                "tag": "n",
                "repeatable": false,
                "description": "Country code"
            },
            {
                "tag": "p",
                "repeatable": false,
                "description": "Piece designation"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Piece physical condition"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "Copyright article-fee code"
            },
            {
                "tag": "t",
                "repeatable": false,
                "description": "Copy number"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of classification or shelving scheme"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": false,
                "description": "Sequence number"
            }
        ]
    },
    {
        "tag": "853",
        "type": "d",
        "repeatable": true,
        "description": "Captions and Pattern - Basic Bibliographic Unit ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "854",
        "type": "d",
        "repeatable": true,
        "description": "Captions and Pattern - Supplementary Material ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "855",
        "type": "d",
        "repeatable": true,
        "description": "Captions and Pattern - Indexes ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "856",
        "type": "d",
        "repeatable": true,
        "description": "Electronic Location and Access ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Host name"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Compression information"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Path"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Electronic name"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Persistent identifier"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Non-functioning Uniform Resource Identifier"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Standardized information governing access"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Contact for access assistance"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Terms governing access"
            },
            {
                "tag": "o",
                "repeatable": false,
                "description": "Operating system"
            },
            {
                "tag": "p",
                "repeatable": false,
                "description": "Port"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Electronic format type"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Standardized information governing use and reproduction"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "File size"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Terms governing use and reproduction"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "v",
                "repeatable": true,
                "description": "Hours access method available"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Link text"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Access method"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Access status"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "857",
        "type": "d",
        "repeatable": true,
        "description": "Electronic Archive Location and Access ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "b",
                "repeatable": false,
                "description": "Name of archiving agency"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Name of Web archive or digital archive repository"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Date range of archived material"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Data provenance"
            },
            {
                "tag": "f",
                "repeatable": false,
                "description": "Archive completeness"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Persistent identifier"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Non-functioning Uniform Resource Identifier"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Standardized information governing access"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Contact for access assistance"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Terms governing access"
            },
            {
                "tag": "q",
                "repeatable": true,
                "description": "Electronic format type"
            },
            {
                "tag": "r",
                "repeatable": true,
                "description": "Standardized information governing use and reproduction"
            },
            {
                "tag": "s",
                "repeatable": true,
                "description": "File size"
            },
            {
                "tag": "t",
                "repeatable": true,
                "description": "Terms governing use and reproduction"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "y",
                "repeatable": true,
                "description": "Link text"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Access method"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "7",
                "repeatable": false,
                "description": "Access status"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "863",
        "type": "d",
        "repeatable": true,
        "description": "Enumeration and Chronology - Basic Bibliographic Unit ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "864",
        "type": "d",
        "repeatable": true,
        "description": "Enumeration and Chronology - Supplementary Material ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "865",
        "type": "d",
        "repeatable": true,
        "description": "Enumeration and Chronology - Indexes ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "866",
        "type": "d",
        "repeatable": true,
        "description": "Textual Holdings - Basic Bibliographic Unit ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "867",
        "type": "d",
        "repeatable": true,
        "description": "Textual Holdings - Supplementary Material ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "868",
        "type": "d",
        "repeatable": true,
        "description": "Textual Holdings - Indexes ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "876",
        "type": "d",
        "repeatable": true,
        "description": "Item Information - Basic Bibliographic Unit ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "877",
        "type": "d",
        "repeatable": true,
        "description": "Item Information - Supplementary Material ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "878",
        "type": "d",
        "repeatable": true,
        "description": "Item Information - Indexes ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "880",
        "type": "d",
        "repeatable": true,
        "description": "Alternate Graphic Representation ",
        "indicators": "  ",
        "subfields": []
    },
    {
        "tag": "881",
        "type": "d",
        "repeatable": true,
        "description": "Manifestation Statements ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Manifestation statement, high-level/general"
            },
            {
                "tag": "b",
                "repeatable": true,
                "description": "Manifestation identifier statement"
            },
            {
                "tag": "c",
                "repeatable": true,
                "description": "Manifestation title and responsibility statement"
            },
            {
                "tag": "d",
                "repeatable": true,
                "description": "Manifestation edition statement"
            },
            {
                "tag": "e",
                "repeatable": true,
                "description": "Manifestation production statement"
            },
            {
                "tag": "f",
                "repeatable": true,
                "description": "Manifestation publication statement"
            },
            {
                "tag": "g",
                "repeatable": true,
                "description": "Manifestation distribution statement"
            },
            {
                "tag": "h",
                "repeatable": true,
                "description": "Manifestation manufacture statement"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Manifestation copyright statement"
            },
            {
                "tag": "j",
                "repeatable": true,
                "description": "Manifestation frequency statement"
            },
            {
                "tag": "k",
                "repeatable": true,
                "description": "Manifestation designation of sequence statement"
            },
            {
                "tag": "l",
                "repeatable": true,
                "description": "Manifestation series statement"
            },
            {
                "tag": "m",
                "repeatable": true,
                "description": "Manifestation dissertation statement"
            },
            {
                "tag": "n",
                "repeatable": true,
                "description": "Manifestation regional encoding statement"
            },
            {
                "tag": "3",
                "repeatable": false,
                "description": "Materials specified"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "882",
        "type": "d",
        "repeatable": true,
        "description": "Replacement Record Information ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": true,
                "description": "Replacement title"
            },
            {
                "tag": "i",
                "repeatable": true,
                "description": "Explanatory text"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Replacement bibliographic record control number"
            },
            {
                "tag": "6",
                "repeatable": false,
                "description": "Linkage"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "883",
        "type": "d",
        "repeatable": true,
        "description": "Metadata Provenance ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Creation process"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Confidence value"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Creation date"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Assigning or generating agency"
            },
            {
                "tag": "x",
                "repeatable": false,
                "description": "Validity end date"
            },
            {
                "tag": "u",
                "repeatable": false,
                "description": "Uniform Resource Identifier"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Bibliographic record control number"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "8",
                "repeatable": true,
                "description": "Field link and sequence number"
            }
        ]
    },
    {
        "tag": "884",
        "type": "d",
        "repeatable": true,
        "description": "Description Conversion Information ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Conversion process"
            },
            {
                "tag": "g",
                "repeatable": false,
                "description": "Conversion date"
            },
            {
                "tag": "k",
                "repeatable": false,
                "description": "Identifier of source metadata"
            },
            {
                "tag": "q",
                "repeatable": false,
                "description": "Conversion agency"
            },
            {
                "tag": "u",
                "repeatable": true,
                "description": "Uniform Resource Identifier"
            }
        ]
    },
    {
        "tag": "885",
        "type": "d",
        "repeatable": true,
        "description": "Matching Information ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Matching information"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Status of matching and its checking"
            },
            {
                "tag": "c",
                "repeatable": false,
                "description": "Confidence value"
            },
            {
                "tag": "d",
                "repeatable": false,
                "description": "Generation date"
            },
            {
                "tag": "w",
                "repeatable": true,
                "description": "Record control number"
            },
            {
                "tag": "x",
                "repeatable": true,
                "description": "Nonpublic note"
            },
            {
                "tag": "z",
                "repeatable": true,
                "description": "Public note"
            },
            {
                "tag": "0",
                "repeatable": true,
                "description": "Authority record control number or standard number"
            },
            {
                "tag": "1",
                "repeatable": true,
                "description": "Real World Object URI"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source"
            },
            {
                "tag": "5",
                "repeatable": false,
                "description": "Institution to which field applies"
            }
        ]
    },
    {
        "tag": "886",
        "type": "d",
        "repeatable": true,
        "description": "Foreign MARC Information Field ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Tag of the foreign MARC field"
            },
            {
                "tag": "b",
                "repeatable": false,
                "description": "Content of the foreign MARC field"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of data"
            }
        ]
    },
    {
        "tag": "887",
        "type": "d",
        "repeatable": true,
        "description": "Non-MARC Information Field ",
        "indicators": "  ",
        "subfields": [
            {
                "tag": "a",
                "repeatable": false,
                "description": "Content of non-MARC field"
            },
            {
                "tag": "2",
                "repeatable": false,
                "description": "Source of data"
            }
        ]
    }
]
```
