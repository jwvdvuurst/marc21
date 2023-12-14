from marc21 import *



def main():
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
    fld = dto.create_field(tag='240', indicators='10')
    fld.addSubField(tag='a', value='Nineteen eighty-four')
    dto.insert_field(fld)

    # and this can also be done on one line
    dto.insert_field(dto.create_field(tag='300').addSubField(tag='a', value='267 p. ;').addSubField(tag='c', value='21 cm'))

    # when the record is finished, it can be printed

    # print(dto.set_separators(subfield_separator=chr(30), subfield_separator=chr(31)))
    print(dto.__repr__(True))

    dto.set_separators(field_separator=chr(30), subfield_separator=chr(31))
    print(dto)

    # print(get_dictionary(True, '871'))

    #
    # mf = MarcField(tag='905', type='d', repeatable=False, description='Address')
    # sf = SubField(tag='a', repeatable=False, description='country')
    # mf.add_SubField(new_sf=sf)
    # sf = SubField(tag='b', repeatable=False, description='city')
    # mf.add_SubField(new_sf=sf)
    #
    # add_field_to_list(mf)
    #
    # add_field_to_list(MarcField(tag='908', type='d', repeatable=True, description='Fictional Character', subfields=[
    #     SubField(tag='a', repeatable=False, description='Name'),
    #     SubField(tag='b', repeatable=True, description='Characterization')
    # ]))
    #
    # add_additional_fields_to_list( [
    #     MarcField('400', 'd', True, 'alternative name', True, '  ', '', [
    #         SubField('a', False, 'full name'),
    #         SubField('3', False, 'name use'),
    #         SubField('2', False, 'source')
    #     ]),
    #     MarcField('671', 'd', True, 'title URLs', True, '  ', '', [
    #         SubField('g', False, 'type'),
    #         SubField('u', False, 'url'),
    #         SubField('2', False, 'source')
    #     ]),
    #     MarcField('902', 'd', True, 'ISSN', True, '  ', '', [
    #         SubField('a', False, 'ISSN'),
    #         SubField('2', False, 'source')
    #     ])
    # ])
    #
    # print(get_dictionary(True))


if __name__ == '__main__':
    main()
