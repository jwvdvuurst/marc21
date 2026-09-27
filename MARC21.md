# MARC21 Dictionary

A glossary of business, domain, and bibliographic terms, abbreviations, and acronyms used in the MARC21 Python module.

## Core MARC21 Terms

### MARC / MARC21
- **MARC**: Machine-Readable Cataloging
- **MARC21**: The current standard for MARC bibliographic records, maintained by the Library of Congress

### Record Structure
- **Bibliographic Record**: A structured description of a bibliographic item (book, journal, etc.)
- **Control Field (CField)**: A field type (tags 000-009) containing fixed-length data without indicators or subfields
- **Data Field (DField)**: A field type (tags 010+) containing variable data with indicators and subfields
- **Tag**: A three-character numeric code identifying a field (e.g., '001', '245', '650')
- **Indicator**: Two characters at the start of a data field that provide additional information about the field
- **Subfield**: A component of a data field, identified by a single character code (e.g., 'a', 'b', 'z')
- **Subfield Code**: The single character identifier for a subfield (e.g., '$a', '$b')
- **Repeatable**: A property indicating whether a field or subfield can appear multiple times in a record
- **Leader**: The first 24 characters of a MARC record containing fixed-length control information
- **Directory**: A structure in ISO 2709 format listing field tags, lengths, and starting positions

### Data Transfer Objects
- **DTO (Data Transfer Object)**: A container object that carries data between processes
- **MarcDto**: The main data transfer object class that holds a single MARC21 bibliographic record

### File Formats
- **ISO 2709**: The international standard binary format for MARC records
- **MARCXML**: An XML representation of MARC21 records using the Library of Congress MARCXML schema

### Format Constants
- **FIELD_TERMINATOR** (0x1E): Byte value marking the end of a field in ISO 2709
- **RECORD_TERMINATOR** (0x1D): Byte value marking the end of a record in ISO 2709
- **SUBFIELD_DELIMITER** (0x1F): Byte value marking the start of a subfield in ISO 2709
- **LEADER_LENGTH**: Fixed length of 24 characters for the MARC leader
- **DIRECTORY_ENTRY_LENGTH**: Fixed length of 12 characters per directory entry

## Bibliographic Identifiers

### Standard Numbers
- **ISBN**: International Standard Book Number - unique identifier for books
- **ISSN**: International Standard Serial Number - unique identifier for serial publications
- **ISSN-L**: Linking ISSN - connects different media versions of the same serial
- **CODEN**: A six-character code used to identify scientific and technical periodicals
- **LC Control Number**: Library of Congress Control Number - unique identifier assigned by LC
- **National Bibliography Number**: Identifier assigned by national bibliographic agencies
- **Standard Technical Report Number (STRN)**: Identifier for technical reports
- **Overseas Acquisition Number**: Identifier for materials acquired from overseas sources

### Other Identifiers
- **Patent Control Number**: Identifier for patent documents
- **Copyright or Legal Deposit Number**: Identifier for copyrighted or legally deposited materials
- **Postal Registration Number**: Identifier used in postal systems
- **Fingerprint Identifier**: Historical identifier based on book characteristics
- **Publisher or Distributor Number**: Commercial identifier assigned by publishers/distributors

## Organizations and Agencies

- **LC / LoC**: Library of Congress - the national library of the United States and maintainer of MARC21
- **NUCMC**: National Union Catalog of Manuscript Collections - a program for cataloging manuscript collections
- **OCLC**: Online Computer Library Center - a global library cooperative

## Bibliographic Concepts

### Cataloging Terms
- **Authority Record**: A record that establishes the authorized form of a name, subject, or title
- **Bibliographic Description**: The structured description of a bibliographic item
- **Cataloging Source**: The agency or system that created the cataloging record
- **Description Conventions**: The cataloging rules used (e.g., AACR2, RDA)
- **Transcribing Agency**: The agency that transcribed the record
- **Modifying Agency**: The agency that modified an existing record

### Subject and Classification
- **Subject Heading**: A controlled vocabulary term describing the subject of a work
- **Classification Number**: A code from a classification system (e.g., Dewey Decimal, Library of Congress Classification)
- **Geographic Classification**: Classification by geographic area
- **Genre/Form Term**: A term describing the genre or form of a work

### Physical Description
- **Physical Description Fixed Field**: Coded information about the physical characteristics of an item
- **Material Characteristics**: Attributes describing the physical or digital nature of materials
- **Cartographic Data**: Information about maps and geographic materials
- **Mathematical Data**: Coordinate and scale information for cartographic materials

### Access and Location
- **Electronic Location and Access**: Information for accessing digital resources
- **Uniform Resource Identifier (URI)**: A string of characters that unambiguously identifies a resource
- **URL**: Uniform Resource Locator - a type of URI specifying the location of a web resource
- **Access Status**: Information about the availability or accessibility of a resource
- **Terms of Availability**: Conditions under which an item is available
- **Terms Governing Use**: Restrictions on how an item may be used

## Technical Terms

### Data Structures
- **Dictionary**: In this context, the MarcDictionary containing field and subfield definitions
- **Field Definition**: The metadata describing a MARC field (tag, type, repeatability, subfields)
- **Field Map**: A fast lookup structure mapping tags to field definitions (O(1) access)
- **Base Field**: The base class for both control fields and data fields

### Validation and Constraints
- **Repeatability Check**: Validation to ensure non-repeatable fields/subfields appear only once
- **Field Type Validation**: Verification that a field is created with the correct type ('c' or 'd')
- **Subfield Validation**: Verification that subfields are defined in the dictionary for their field

### Serialization
- **Serialization**: The process of converting a data structure into a format for storage or transmission
- **Deserialization**: The process of reconstructing a data structure from a serialized format
- **Roundtrip**: The ability to serialize and deserialize data without loss of information

## Field-Specific Terms

### Common Subfield Codes
- **$a**: Primary data element (often the main content)
- **$b**: Secondary data element or qualifier
- **$c**: Additional data or qualifier
- **$d**: Date information
- **$e**: Relationship term or qualifier
- **$f**: Date of a work
- **$g**: Miscellaneous information
- **$h**: Medium or physical carrier
- **$i**: Display text or relationship information
- **$j**: Geographic area code
- **$k**: Form subheading
- **$l**: Language of a work
- **$m**: Medium of performance for music
- **$n**: Number of part/section
- **$o**: Arranged statement for music
- **$p**: Name of part/section
- **$q**: Qualifying information
- **$r**: Key for music
- **$s**: Version, edition, etc.
- **$t**: Title of a work
- **$u**: URI or URL
- **$v**: Volume designation
- **$w**: Record control number
- **$x**: General subdivision
- **$y**: Chronological subdivision
- **$z**: Geographic subdivision
- **$0**: Authority record control number
- **$1**: Real World Object URI
- **$2**: Source of term or code
- **$3**: Materials specified
- **$5**: Institution to which field applies
- **$6**: Linkage
- **$7**: Access status or control subfield
- **$8**: Field link and sequence number

### Field Ranges
- **000-009**: Control fields (fixed-length data)
- **010-099**: Numbers and codes
- **100-199**: Main entry - personal names
- **200-299**: Titles and title-related information
- **300-399**: Physical description
- **400-499**: Series statements
- **500-599**: Notes
- **600-699**: Subject access fields
- **700-799**: Added entries
- **800-899**: Series added entries
- **900-999**: Local fields (reserved for local use)

## Musical Terms

- **Musical Incipits**: The opening notes or measures of a musical work
- **Clef**: A musical symbol indicating pitch
- **Key Signature**: The sharps or flats at the beginning of a musical staff
- **Time Signature**: Notation indicating the meter of a piece
- **Voice/Instrument**: The performing medium for a musical work

## Geographic and Cartographic Terms

- **Coordinates**: Geographic location expressed as latitude/longitude
- **Longitude**: Angular distance east or west from the prime meridian
- **Latitude**: Angular distance north or south from the equator
- **Scale**: The ratio between a distance on a map and the corresponding distance on the ground
- **G-ring**: A closed polygon used to define geographic boundaries
- **Equinox**: The time when the sun crosses the celestial equator
- **Declination**: Angular distance north or south of the celestial equator
- **Right Ascension**: Angular distance measured eastward along the celestial equator

## Digital and Electronic Terms

- **Electronic Format Type**: The digital format of an electronic resource (e.g., PDF, HTML)
- **File Size**: The size of a digital file
- **Operating System**: The software system required to access a resource
- **Port**: A network port number for accessing a resource
- **Compression Information**: Details about file compression
- **Data Provenance**: Information about the origin and history of data
- **Persistent Identifier**: A long-lasting identifier for a digital resource
- **Web Archive**: A repository for archived web content
- **Digital Archive Repository**: An institution maintaining digital archives

## Legal and Rights Terms

- **Copyright**: Legal protection for original works
- **Legal Deposit**: Requirement to deposit copies of publications with designated institutions
- **Jurisdiction**: The legal authority or geographic area of legal control
- **Security Classification**: Level of security classification for materials
- **Terms Governing Access**: Conditions for accessing restricted materials
- **Terms Governing Use and Reproduction**: Restrictions on using or copying materials

## Notes and Annotations

- **General Note**: A note providing additional information
- **Public Note**: A note intended for public display
- **Nonpublic Note**: A note for internal use only
- **Materials Specified**: Specific parts of a work to which a note applies
- **Location Note**: Information about where an item is located
- **Reproduction Note**: Information about reproductions of an item

## Linkage and Relationships

- **Linkage**: Connection between related fields or records
- **Field Link and Sequence Number**: Mechanism for linking related fields
- **Relationship Information**: Data describing relationships between entities
- **Related Work**: A work connected to the described item

## Local and Custom Fields

- **Local Field**: A field in the 9xx range reserved for local use
- **Custom Field**: A field defined by an institution for local needs
- **Local Call Number**: A call number assigned locally by an institution

## See Also

- [Library of Congress MARC21 Documentation](https://www.loc.gov/marc/bibliographic/)
- [MARC21 Format for Bibliographic Data](https://www.loc.gov/marc/bibliographic/)
- [ISO 2709 Standard](https://www.iso.org/standard/7795.html)

