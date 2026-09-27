"""Conservative MARC 21 to BIBFRAME 2 resource-type mappings.

The table identifies BIBFRAME resources commonly represented by a MARC field.
It is not a lossless MARC-to-RDF conversion: indicators, subfield semantics,
and cataloging rules are required to create BIBFRAME statements.
"""

from collections.abc import Iterable
from typing import TypeGuard


BIBFRAME_NAMESPACE = 'http://id.loc.gov/ontologies/bibframe/'

MARC_TO_BIBFRAME_TYPES: dict[str, tuple[str, ...]] = {
    '001': ('AdminMetadata',),
    '003': ('AdminMetadata',),
    '005': ('AdminMetadata',),
    '008': ('AdminMetadata', 'Work', 'Instance'),
    '010': ('Identifier',),
    '020': ('Isbn',),
    '022': ('Issn',),
    '024': ('Identifier',),
    '035': ('Identifier',),
    '040': ('AdminMetadata',),
    '100': ('Agent', 'Work'),
    '110': ('Agent', 'Work'),
    '111': ('Meeting', 'Work'),
    '130': ('Work', 'Title'),
    '240': ('Work', 'Title'),
    '245': ('Work', 'Instance', 'Title'),
    '246': ('Title',),
    '250': ('ProvisionActivity',),
    '264': ('ProvisionActivity',),
    '300': ('Instance', 'Extent'),
    '336': ('Content',),
    '337': ('Media',),
    '338': ('Carrier',),
    '490': ('Series',),
    '5XX': ('Note',),
    '600': ('Topic', 'Agent'),
    '610': ('Topic', 'Agent'),
    '611': ('Topic', 'Meeting'),
    '630': ('Topic', 'Work'),
    '648': ('Topic', 'Temporal'),
    '650': ('Topic',),
    '651': ('Topic', 'Place'),
    '655': ('GenreForm',),
    '700': ('Agent', 'Work'),
    '710': ('Agent', 'Work'),
    '711': ('Meeting', 'Work'),
    '730': ('Work', 'Title'),
    '740': ('Work', 'Title'),
    '76X': ('Work', 'Instance'),
    '77X': ('Work', 'Instance'),
    '78X': ('Work', 'Instance'),
    '80X': ('Series',),
    '81X': ('Series',),
    '830': ('Series', 'Work', 'Title'),
    '856': ('Electronic',),
}


def bibframe_types_for(*fields: str | object | Iterable[str | object]) -> set[str]:
    """Return absolute BIBFRAME type IRIs for MARC tags or field objects.

    Each item may be a three-character tag, an object with a ``tag`` attribute,
    or an iterable of either. Unmapped tags return no types.
    """
    types: set[str] = set()
    for field in fields:
        values = field if _is_tag_iterable(field) else (field,)
        for value in values:
            tag = value if isinstance(value, str) else getattr(value, 'tag', '')
            for bibframe_type in _types_for_tag(tag):
                types.add(BIBFRAME_NAMESPACE + bibframe_type)
    return types


def _is_tag_iterable(value: object) -> TypeGuard[Iterable[str | object]]:
    return not isinstance(value, (str, bytes)) and isinstance(value, Iterable)


def _types_for_tag(tag: str) -> tuple[str, ...]:
    if tag in MARC_TO_BIBFRAME_TYPES:
        return MARC_TO_BIBFRAME_TYPES[tag]
    if len(tag) == 3 and tag.startswith('5'):
        return MARC_TO_BIBFRAME_TYPES['5XX']
    if len(tag) == 3 and tag.startswith('76'):
        return MARC_TO_BIBFRAME_TYPES['76X']
    if len(tag) == 3 and tag.startswith('77'):
        return MARC_TO_BIBFRAME_TYPES['77X']
    if len(tag) == 3 and tag.startswith('78'):
        return MARC_TO_BIBFRAME_TYPES['78X']
    if len(tag) == 3 and tag.startswith('80'):
        return MARC_TO_BIBFRAME_TYPES['80X']
    if len(tag) == 3 and tag.startswith('81'):
        return MARC_TO_BIBFRAME_TYPES['81X']
    return ()