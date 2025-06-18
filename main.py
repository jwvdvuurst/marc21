from marc21 import load_marc21_from_text, MarcDto, get_dictionary

def main():
    print("Dictionary: \n%s" % get_dictionary(True))

    # create marc21 data transfer object
    print("\nCreate new MARC record\n")
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
    print("\nPrint MARC record without descriptions: \n%s\n" % dto.__repr__(False))
    print("\nPrint MARC record with descriptions: \n%s\n" % dto.__repr__(True))

    print("\nChange the separators\n")
    dto.set_separators(field_separator=chr(30), subfield_separator=chr(31))
    print("\nPrint MARC record with the separators: \n%s\n" % dto.__repr__(False))

    print("\nSave MARC record to string\n")
    message=repr(dto)

    print("\nLoad new MARC record from the string\n")
    dto = load_marc21_from_text(message, field_separator=chr(30), subfield_separator=chr(31))

    print("\nLoaded MARC record: \n%s\n" % dto.__repr__(False))

    print("\nChange the separators\n")
    dto.set_separators(field_separator='^^', subfield_separator='^_')

    print("\nPrint MARC record with the separators: \n%s\n" % dto.__repr__(False))

    print("\nPrint MARC record as json: \n%s\n" % dto.__json__())

    print("\nPrint MARC record as xml: \n%s\n" % dto.__xml__())


if __name__ == '__main__':
    main()
