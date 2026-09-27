from marc21 import BIBFRAME_NAMESPACE, MarcDto, bibframe_types_for


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