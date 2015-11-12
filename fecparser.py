from json import loads


class FecFileParser(object):
    """
    Given a file from the FEC, apply correct definitions.
    """

    def __init__(self, definitions, upload_date):
        self.feclookup = loads(definitions.read())
        definitions.seek(0)
        self.upload_date = upload_date
        self.organization_information = dict()
        self.header = dict()

    def getschema(self, version, linetype):
        versioned_formdata = self.feclookup['v' + version]
        i = len(linetype) - 1
        while i >= 0 and linetype[:i] not in versioned_formdata:
            i -= 1
        if not linetype:
            raise Exception("Could not match linetype {0} on version {1}".format(linetype, version))
        import pdb; pdb.set_trace()
        return linetype[:i], versioned_formdata[linetype[:i]]

    def processfile(self, filehandle):
        """
        Process all lines of a file and list of dictionaries, one per line.
        """
        first_line = filehandle.readline().strip().split(chr(28))
        if first_line[0] != "HDR":
            raise Exception("Failed to parse: HDR expected on first line")

        fileversion = first_line[2]

        for line in filehandle:
            line = line.strip().split(chr(28))
            linetype = line[0]
            clean_linetype, schema = self.getschema(fileversion, linetype)

            # TODO - F3 lines should be used to produce a dictionary of information about each organization. Must be second in every file.

            line_dict = {k: v for k, v in zip(schema, line)}
            line_dict["clean_linetype"] = clean_linetype
            line_dict['upload_date'] = upload_date

            if clean_linetype == "F3":
                self.organization_information = line_dict
            elif clean_linetype == "HEAD":
                self.header = line_dict

            yield line_dict
