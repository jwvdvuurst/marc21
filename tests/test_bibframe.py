import xml.etree.ElementTree as ET

from marc21 import BIBFRAME_NAMESPACE, DField, MarcDto, bibframe_types_for, to_bibframe_rdfxml


def test_bibframe_types_for_tags_and_fields():
    dto = MarcDto()
    title = dto.create_field('245', indicators='10')

    types = bibframe_types_for('020', title, ['650', '856'])

    assert BIBFRAME_NAMESPACE + 'Isbn' in types
    assert BIBFRAME_NAMESPACE + 'Title' in types
    assert BIBFRAME_NAMESPACE + 'Topic' in types
    assert BIBFRAME_NAMESPACE + 'Electronic' in types


def test_bibframe_types_for_unmapped_tag_is_empty():
    assert bibframe_types_for('999') == set()


def test_to_bibframe_rdfxml_converts_core_work_and_instance_mappings():
    dto = MarcDto()
    dto.insert_field(dto.create_field('001', data='record-1'))
    isbn = dto.create_field('020', subfields=[])
    contributor = dto.create_field('100', indicators='1 ')
    title = dto.create_field('245', indicators='10')
    extent = dto.create_field('300', subfields=[])
    assert isinstance(isbn, DField)
    assert isinstance(contributor, DField)
    assert isinstance(title, DField)
    assert isinstance(extent, DField)
    dto.insert_field(isbn.addSubField('a', '9781234567890'))
    dto.insert_field(contributor.addSubField('a', 'Morrison, Toni'))
    dto.insert_field(title.addSubField('a', 'Beloved').addSubField('b', 'a novel').addSubField('c', 'Toni Morrison'))
    dto.insert_field(extent.addSubField('a', '324 pages'))

    root = ET.fromstring(to_bibframe_rdfxml(dto, base_uri='https://example.test/resources/'))
    namespaces = {'bf': BIBFRAME_NAMESPACE, 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}

    work = root.find("bf:Work[@rdf:about='https://example.test/resources/record-1#Work']", namespaces)
    instance = root.find("bf:Instance[@rdf:about='https://example.test/resources/record-1#Instance']", namespaces)

    assert work is not None
    assert instance is not None
    main_title = work.find('bf:title/bf:Title/bf:mainTitle', namespaces)
    contribution_label = work.find('bf:primaryContribution/bf:Contribution/bf:agent/bf:Agent/bf:label', namespaces)
    subtitle = instance.find('bf:title/bf:Title/bf:subtitle', namespaces)
    responsibility_statement = instance.find('bf:responsibilityStatement', namespaces)
    extent_value = instance.find('bf:extent', namespaces)
    isbn_value = instance.find('bf:identifiedBy/bf:Isbn/rdf:value', namespaces)

    assert main_title is not None and main_title.text == 'Beloved'
    assert contribution_label is not None and contribution_label.text == 'Morrison, Toni'
    assert subtitle is not None and subtitle.text == 'a novel'
    assert responsibility_statement is not None and responsibility_statement.text == 'Toni Morrison'
    assert extent_value is not None and extent_value.text == '324 pages'
    assert isbn_value is not None and isbn_value.text == '9781234567890'