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

    def getschema(self, version, linetype):
        versioned_formdata = self.feclookup['v' + version]
        i = len(linetype)
        while i >= 0 and linetype[:i] not in versioned_formdata:
            i -= 1
        if not linetype:
            raise Exception("Could not match linetype {0} on version {1}".format(linetype, version))
        final_key = linetype[:i]
        return final_key, versioned_formdata.get(final_key, dict())

    def processfile(self, filehandle, filename):
        """
        Process all lines of a file and list of dictionaries, one per line.
        """
        first_line = filehandle.readline().replace('"', '').strip().split(chr(28))
        if first_line[0] != "HDR":
            raise Exception("Failed to parse: HDR expected on first line")

        fileversion = first_line[2].strip()

        in_comment = False

        for line in filehandle:
            line = line.strip()
            line = line.replace('"', '')

            if not line:
                continue
            
            if line == '[BEGINTEXT]':
                in_comment = True
                continue
            elif in_comment:
                if line == '[ENDTEXT]':
                    in_comment = False
                continue

            line = line.split(chr(28))
            linetype = line[0]
            clean_linetype, schema = self.getschema(fileversion, linetype)
            if schema:
                line_dict = {k: v for k, v in zip(schema, line)}
            else:
                line_dict = {'contents': ','.join(line), 'clean_linetype': clean_linetype, 'FORM': linetype, "Error": "NoSchema"}
                line_dict['filename'] = filename
                line_dict["clean_linetype"] = clean_linetype
                line_dict['upload_date'] = self.upload_date

            if clean_linetype[0] == "F" and schema:
                self.organization_information = line_dict
                
            
            yield line_dict
