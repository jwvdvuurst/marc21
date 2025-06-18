# -*- coding: utf-8 -*-
"""
    Tests for the MarcDto class.
    This module contains unit tests for the MarcDto class, which is responsible for managing MARC records.
"""
import pytest

from marc21 import MarcDto, MarcException, CField, DField, SubField, MarcField, add_field_to_list, get_dictionary, add_additional_fields_to_list, MarcDictionary, load_marc21_from_text
from marc21.lib.marcException import MarcSubfieldException, MarcInvalidTagException, MarcFieldTypeException
from marc21.lib.marcFields import MarcField

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

    def test_field_filtering(self):
        dto = MarcDto()
        md = MarcDictionary()

        tags=md.get_field_tags()
        even_tags = [tag for tag in tags if int(tag) % 2 == 0]
        odd_tags = [tag for tag in tags if int(tag) % 2 != 0]

        for tag in tags:
            field = dto.create_field(tag=tag, data=tag)

            if field.field_type == 'd':
                try:
                    field.addSubField('a', 'subfield for %s' % tag)
                except MarcException as m:
                    print(m)

            dto.insert_field(field)

        assert len(dto) > 0
        dto_len = len(dto)

        for tag in even_tags:
            if len(odd_tags) > 0:
                dto.perform_filter(tag, odd_tags.pop(0))
            else:
                dto.perform_filter(tag, tag)

        for tag in odd_tags:
            if len(even_tags) > 0:
                dto.perform_filter(tag, even_tags.pop(0))
            else:
                dto.perform_filter(tag, tag)

        dto.perform_filter(even_tags[0], '')
        dto.perform_filter('', even_tags[0])

        assert len(dto) < dto_len

    def test_dto_as_list(self):
        dto = MarcDto()
        md = MarcDictionary()

        tags=md.get_field_tags()

        for tag in tags:
            field = dto.create_field(tag=tag, data=tag)

            if field.field_type == 'd':
                subfields = md.get_valid_subfields_for_field(tag=tag)

                for sf in subfields:
                    field.addSubField(sf.tag, 'subfield %s for field %s' % (sf.tag, tag))

            dto.insert_field(field)

        dto_list = dto.as_list()
        dto_json = dto.__json__()

        assert len(dto_list) > 0
        assert len(dto_json) > 0

    def test_set_separators(self):
        dto = MarcDto()
        md = MarcDictionary()

        tags = md.get_field_tags()

        tags = [tag for tag in tags if int(tag) % 5 == 0]

        for tag in tags:
            field = dto.create_field(tag=tag, data=tag)

            if field.field_type == 'd':
                subfields = md.get_valid_subfields_for_field(tag=tag)

                for sf in subfields:
                    field.addSubField(sf.tag, 'subfield %s for field %s' % (sf.tag, tag))

            dto.insert_field(field)

        json1 = repr(dto)

        dto.set_separators('^_', '^^')

        json2 = repr(dto)

        dto.set_separators('field: ', 'subfield: ')

        json3 = repr(dto)

        dto.set_separators( '', '')

        json4 = repr(dto)

        assert len(json1) > 0
        assert len(json2) > 0

        assert json1 != json2

        assert len(json3) > 0

        assert json3 != json2

        assert len(json4) > 0

        assert json3 == json4

    def test_dto_representation(self):
        dto = MarcDto()
        md = MarcDictionary()

        tags = md.get_field_tags()
        tags = [tag for tag in tags if int(tag) % 7 == 0]

        for tag in tags:
            field = dto.create_field(tag=tag, data=tag)

            if field.field_type == 'd':
                subfields = md.get_valid_subfields_for_field(tag=tag)

                for sf in subfields:
                    field.addSubField(sf.tag, 'subfield %s for field %s' % (sf.tag, tag))

            dto.insert_field(field)

        json1 = dto.__repr__()
        json2 = dto.__repr__(True)

        assert len(json1) > 0
        assert len(json2) > 0
        assert json1 != json2

    def test_direct_DField_creation(self):
        tag = '027'
        df = DField(tag=tag, description='test', indicators='><', subfields=[])
        df.addSubField(tag='q', value='?')

        assert df.field_type == 'd'
        assert df.tag == tag

    def test_direct_invalid_DField_creation(self):
        with pytest.raises(MarcException):
            df = DField(tag='', description='test', indicators='><', subfields=[])
            df.addSubField(tag='q', value='?')

    def test_direct_DField_creation_with_CField_tag(self):
        tag = '003'

        with pytest.raises(MarcException):
            df = DField(tag=tag, description='test', indicators='<>', subfields=[])


    def test_direct_CField_creation(self):
        tag='003'

        cf = CField(tag=tag, description='test', data='?')

        assert cf.field_type == 'c'
        assert cf.tag == tag

    def test_direct_CField_creation_with_DField_tag(self):
        tag='027'

        with pytest.raises(MarcException):
            cf = CField(tag=tag, description='test', data='?')

    def test_direct_invalid_CField_creation(self):
        with pytest.raises(MarcException):
            cf = CField(tag='', description='test', data='?')


    def test_character_length_of_subfields(self):
        dto = MarcDto()
        md = MarcDictionary()

        tags = md.get_field_tags()
        tags = [tag for tag in tags if int(tag) % 7 == 0]

        for tag in tags:
            field = dto.create_field(tag=tag, data=tag)

            if field.field_type == 'd':
                subfields = md.get_valid_subfields_for_field(tag=tag)

                for sf in subfields:
                    field.addSubField(sf.tag, 'subfield %s for field %s' % (sf.tag, tag))

            dto.insert_field(field)

        assert dto.__len__(True) > 0

    def test_create_valid_record_from_text(self):
        message = "^^0016043368\n" + \
                "^^00520230117182517.0\n" + \
                "^^008770218s1818    enk           000 1 eng\n" + \
                "^^010  $a   53051218\n" + \
                "^^035  $a(OCoLC)2748084\n" + \
                "^^040  $aDLC$beng$cGEU$dOCoLC$dDLC\n" + \
                "^^042  $apremarc\n" + \
                "^^05000$aPR5397$b.F7 1818\n" + \
                "^^1001$aShelley, Mary Wollstonecraft,$d1797-1851.\n" + \
                "^^24510$aFrankenstein; or, The modern Prometheus.\n" + \
                "^^24630$aFrankenstein\n" + \
                "^^24630$aModern Prometheus\n" + \
                "^^260  $aLondon,$bPrinted for Lackington, Hughes, Harding, Mavor, &amp; Jones,$c1818.\n" + \
                "^^300  $a3 v.$c19 cm.\n" + \
                "^^561  $aYale Univ. exchange, 11-28-52, Rec. 4-23-53.$5DLC\n" + \
                ("^^85641$3Page view volume 1$drbc0001$f2018gen51218v1"
                 "$uhttps://hdl.loc.gov/loc.rbc/General.51218v1.1\n") + \
                ("^^85641$3Page view volume 2$drbc0001$f2018gen51218v2"
                 "$uhttps://hdl.loc.gov/loc.rbc/General.51218v2.1\n") + \
                ("^^85641$3Page view volume 3$drbc0001$f2018gen51218v3"
                 "$uhttps://hdl.loc.gov/loc.rbc/General.51218v3.1\n")

        try:
            dto = load_marc21_from_text(text=message, field_separator='^^', subfield_separator="$")
            assert dto is not None
            assert dto.__len__() == 18
            print(dto.__len__())
        except MarcException as e:
            print('error in test_create_valid_record_from_text %s' % e.__repr__())
            print(message)




