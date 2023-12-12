
import pytest

from marc21 import MarcDto, MarcException, CField, DField, SubField, MarcField, add_field_to_list, get_dictionary, add_additional_fields_to_list


class TestMarcDto:

    #  Creating a new instance of MarcDto should initialize empty lists for _cfields and _dfields.
    def test_new_instance_initializes_empty_lists(self):
        # Given
        marc_dto = MarcDto()

        # When

        # Then
        assert marc_dto._cfields == []
        assert marc_dto._dfields == []

    #  Adding a new CField to MarcDto using create_field() should create a new CField object and add it to _cfields.
    def test_add_new_cfield_creates_cfield_object_and_adds_to_cfields(self):
        # Given
        marc_dto = MarcDto()

        # When
        cfield = marc_dto.create_field('001', data='12345')
        marc_dto.insert_field(cfield)

        # Then
        assert isinstance(cfield, CField)
        assert cfield in marc_dto._cfields

    #  Adding a new DField to MarcDto using create_field() should create a new DField object and add it to _dfields.
    def test_add_new_dfield_creates_dfield_object_and_adds_to_dfields(self):
        # Given
        marc_dto = MarcDto()

        # When
        subfield = SubField(tag='a', value='Title')
        dfield = marc_dto.create_field('245', indicators='00', subfields=[subfield])
        marc_dto.insert_field(dfield)

        # Then
        assert isinstance(dfield, DField)
        assert dfield in marc_dto._dfields

    #  Adding a new non-repeatable DField to MarcDto using create_field() should raise a MarcException if a field with the same tag already exists.
    def test_add_non_repeatable_dfield_raises_exception_if_field_with_same_tag_exists(self):
        # Given
        marc_dto = MarcDto()
        dfield1 = marc_dto.create_field('245', indicators='00', subfields=[SubField(tag='a', value='Title')])
        marc_dto.insert_field(dfield1)

        # When
        with pytest.raises(MarcException):
            dfield2 = marc_dto.create_field('245', indicators='01', subfields=[SubField(tag='b', value='Subtitle')])
            marc_dto.insert_field(dfield2)

        # Then

    #  Adding a new repeatable DField to MarcDto using create_field() should add the new field even if a field with the same tag already exists.
    def test_add_repeatable_dfield_adds_new_field_if_field_with_same_tag_exists(self):
        # Given
        marc_dto = MarcDto()
        dfield1 = marc_dto.create_field('246', indicators='00', subfields=[SubField(tag='a', value='Title')])
        marc_dto.insert_field(dfield1)

        # When
        dfield2 = marc_dto.create_field('246', indicators='01', subfields=[SubField(tag='b', value='Subtitle')])
        marc_dto.insert_field(dfield2)

        # Then
        assert dfield1 in marc_dto._dfields
        assert dfield2 in marc_dto._dfields

    #  Calling is_tag_present() with an existing tag should return True.
    def test_is_tag_present_returns_true_for_existing_tag(self):
        # Given
        marc_dto = MarcDto()
        cfield = marc_dto.create_field('001', data='12345')
        marc_dto.insert_field(cfield)

        # When
        result = marc_dto.is_tag_present('001')

        # Then
        assert result is True

    #  Creating a new CField with an empty tag or data should raise a MarcException.
    def test_create_cfield_with_empty_tag_or_data_raises_exception(self):
        # Given
        marc_dto = MarcDto()

        # When/Then
        with pytest.raises(MarcException):
            marc_dto.create_field('', data='12345')

        with pytest.raises(MarcException):
            marc_dto.create_field('001', data='')



    #  Calling is_tag_present() with a non-existing tag should return False.
    def test_is_tag_present_with_non_existing_tag(self):
        # Given
        marc_dto = MarcDto()

        # When
        result = marc_dto.is_tag_present('non_existing_tag')

        # Then
        assert result  is False

    #  Calling perform_filter() with a tag_present and tag_remove that both exist in _dfields should remove the field with tag_remove from _dfields.
    def test_perform_filter_with_existing_tags_in_dfields(self):
        # Given
        marc_dto = MarcDto()
        tag_present = '100'
        tag_remove = '110'
        dfield_present = DField(tag=tag_present, description='Description', indicators='12', subfields=[])
        dfield_remove = DField(tag=tag_remove, description='Description', indicators='12', subfields=[])
        marc_dto._dfields.append(dfield_present)
        marc_dto._dfields.append(dfield_remove)

        # When
        marc_dto.perform_filter(tag_present, tag_remove)

        # Then
        assert len(marc_dto._dfields) == 1
        assert marc_dto._dfields[0].tag == tag_present

    #  Calling perform_filter() with a tag_present and tag_remove that both exist in _cfields should not modify _cfields.
    def test_perform_filter_with_existing_tags_in_cfields(self):
        # Given
        marc_dto = MarcDto()
        tag_present = '001'
        tag_remove = '003'
        cfield_present = CField(tag=tag_present, description='Description', data='Data')
        cfield_remove = CField(tag=tag_remove, description='Description', data='Data')
        marc_dto._cfields.append(cfield_present)
        marc_dto._cfields.append(cfield_remove)

        # When
        marc_dto.perform_filter(tag_present, tag_remove)

        # Then
        assert len(marc_dto._cfields) == 2
        assert marc_dto._cfields[0].tag == tag_present
        assert marc_dto._cfields[1].tag == tag_remove

    def test_add_field_to_dictionary(self):
        tag='900'

        fielddef = get_dictionary(tag=tag)

        assert fielddef == '[]'

        mf = MarcField(tag=tag, fieldtype='d', description='Description', indicators='12', subfields=[])

        add_field_to_list(mf)

        fielddef = get_dictionary(tag=tag)

        assert fielddef != '[]'

    def test_add_multiple_fields_to_dictionary(self):
        tags=['901', '902']

        for tag in tags:
            fielddef = get_dictionary(tag=tag)

            assert fielddef == '[]'

        fields = []

        for tag in tags:
            mf = MarcField(tag=tag, fieldtype='d', description='Description', indicators='12', subfields=[])
            fields.append(mf)

        add_additional_fields_to_list(fields)

        for tag in tags:
            fielddef = get_dictionary(tag=tag)

            assert fielddef != '[]'





