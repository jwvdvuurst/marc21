"""Conservative MARC 21 to BIBFRAME 2 resource-type mappings.

The table identifies BIBFRAME resources commonly represented by a MARC field.
It is not a lossless MARC-to-RDF conversion: indicators, subfield semantics,
and cataloging rules are required to create BIBFRAME statements.
"""

from collections.abc import Iterable
from typing import TypeGuard
from urllib.parse import quote
import xml.etree.ElementTree as ET


BIBFRAME_NAMESPACE = 'http://id.loc.gov/ontologies/bibframe/'
RDF_NAMESPACE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

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


def to_bibframe_rdfxml(record: object, base_uri: str = 'urn:marc21:') -> str:
    """Serialize supported MARC bibliographic fields as a BIBFRAME RDF/XML graph.

    The output models a Work linked to an Instance. It currently supports the
    identifiers, title, responsibility, contribution, edition, publication,
    extent, RDA 33X, subject, note, and electronic-location fields represented
    in :data:`MARC_TO_BIBFRAME_TYPES`. Fields without an implemented statement
    mapping are intentionally omitted.
    """
    control_fields = getattr(record, '_cfields', ())
    data_fields = getattr(record, '_dfields', ())
    record_id = _control_value(control_fields, '001') or 'record'
    resource_uri = f"{base_uri.rstrip('/')}/{quote(record_id, safe='')}"
    work_uri = f'{resource_uri}#Work'
    instance_uri = f'{resource_uri}#Instance'

    ET.register_namespace('bf', BIBFRAME_NAMESPACE)
    ET.register_namespace('rdf', RDF_NAMESPACE)
    root = ET.Element(_rdf('RDF'))
    work = ET.SubElement(root, _bf('Work'), {_rdf('about'): work_uri})
    instance = ET.SubElement(root, _bf('Instance'), {_rdf('about'): instance_uri})
    ET.SubElement(work, _bf('hasInstance'), {_rdf('resource'): instance_uri})
    ET.SubElement(instance, _bf('instanceOf'), {_rdf('resource'): work_uri})

    for marc_field in data_fields:
        tag = getattr(marc_field, 'tag', '')
        if tag == '010':
            _append_identifiers(instance, marc_field, 'Lccn')
        elif tag == '020':
            _append_identifiers(instance, marc_field, 'Isbn')
        elif tag == '022':
            _append_identifiers(instance, marc_field, 'Issn')
        elif tag in ('100', '110', '111'):
            _append_contribution(work, marc_field, 'primaryContribution')
        elif tag in ('700', '710', '711'):
            _append_contribution(work, marc_field, 'contribution')
        elif tag == '245':
            _append_title(work, marc_field)
            _append_title(instance, marc_field)
            _append_literal(instance, 'responsibilityStatement', _subfield_value(marc_field, 'c'))
        elif tag == '250':
            _append_literal(instance, 'editionStatement', _subfield_value(marc_field, 'a'))
        elif tag in ('260', '264'):
            _append_provision_activity(instance, marc_field)
        elif tag == '300':
            _append_literal(instance, 'extent', _subfield_value(marc_field, 'a'))
        elif tag in ('336', '337', '338'):
            _append_rda_term(instance, marc_field, {'336': 'content', '337': 'media', '338': 'carrier'}[tag])
        elif tag in ('650', '651', '655'):
            _append_subject(work, marc_field, {'650': 'Topic', '651': 'Place', '655': 'GenreForm'}[tag])
        elif tag.startswith('5'):
            _append_note(instance, marc_field)
        elif tag == '856':
            _append_literal(instance, 'electronicLocator', _subfield_value(marc_field, 'u'))

    return ET.tostring(root, encoding='unicode', xml_declaration=True)


def _append_identifiers(parent: ET.Element, marc_field: object, identifier_type: str) -> None:
    for value in _subfield_values(marc_field, 'a'):
        identifier = ET.SubElement(parent, _bf('identifiedBy'))
        typed_identifier = ET.SubElement(identifier, _bf(identifier_type))
        ET.SubElement(typed_identifier, _rdf('value')).text = value


def _append_contribution(parent: ET.Element, marc_field: object, property_name: str) -> None:
    name = _subfield_value(marc_field, 'a')
    if not name:
        return
    contribution = ET.SubElement(parent, _bf(property_name))
    contribution_node = ET.SubElement(contribution, _bf('Contribution'))
    agent = ET.SubElement(contribution_node, _bf('agent'))
    agent_node = ET.SubElement(agent, _bf('Agent'))
    ET.SubElement(agent_node, _bf('label')).text = name


def _append_title(parent: ET.Element, marc_field: object) -> None:
    main_title = _subfield_value(marc_field, 'a')
    subtitle = _subfield_value(marc_field, 'b')
    if not main_title and not subtitle:
        return
    title = ET.SubElement(parent, _bf('title'))
    title_node = ET.SubElement(title, _bf('Title'))
    _append_literal(title_node, 'mainTitle', main_title)
    _append_literal(title_node, 'subtitle', subtitle)


def _append_provision_activity(parent: ET.Element, marc_field: object) -> None:
    place = _subfield_value(marc_field, 'a')
    agent = _subfield_value(marc_field, 'b')
    date = _subfield_value(marc_field, 'c')
    if not any((place, agent, date)):
        return
    provision = ET.SubElement(parent, _bf('provisionActivity'))
    activity = ET.SubElement(provision, _bf('ProvisionActivity'))
    _append_literal(activity, 'place', place)
    _append_literal(activity, 'agent', agent)
    _append_literal(activity, 'date', date)


def _append_rda_term(parent: ET.Element, marc_field: object, property_name: str) -> None:
    value = _subfield_value(marc_field, 'a')
    if not value:
        return
    term = ET.SubElement(parent, _bf(property_name))
    ET.SubElement(term, _bf(property_name.title())).text = value


def _append_subject(parent: ET.Element, marc_field: object, subject_type: str) -> None:
    value = _subfield_value(marc_field, 'a')
    if not value:
        return
    subject = ET.SubElement(parent, _bf('subject'))
    subject_node = ET.SubElement(subject, _bf(subject_type))
    ET.SubElement(subject_node, _bf('label')).text = value


def _append_note(parent: ET.Element, marc_field: object) -> None:
    value = _subfield_value(marc_field, 'a')
    if not value:
        return
    note = ET.SubElement(parent, _bf('note'))
    note_node = ET.SubElement(note, _bf('Note'))
    ET.SubElement(note_node, _bf('noteType')).text = getattr(marc_field, 'tag', '')
    ET.SubElement(note_node, _bf('label')).text = value


def _append_literal(parent: ET.Element, property_name: str, value: str | None) -> None:
    if value:
        ET.SubElement(parent, _bf(property_name)).text = value


def _control_value(fields: Iterable[object], tag: str) -> str | None:
    for field in fields:
        if getattr(field, 'tag', '') == tag:
            return getattr(field, 'data', '') or None
    return None


def _subfield_value(marc_field: object, tag: str) -> str | None:
    return next(iter(_subfield_values(marc_field, tag)), None)


def _subfield_values(marc_field: object, tag: str) -> list[str]:
    return [
        subfield.value
        for subfield in getattr(marc_field, 'subfields', ())
        if getattr(subfield, 'tag', '') == tag and getattr(subfield, 'value', '')
    ]


def _bf(local_name: str) -> str:
    return f'{{{BIBFRAME_NAMESPACE}}}{local_name}'


def _rdf(local_name: str) -> str:
    return f'{{{RDF_NAMESPACE}}}{local_name}'


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