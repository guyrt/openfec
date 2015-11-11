from json import loads


class FecFileParser(object):
	"""
	Given a file from the FEC, apply correct definitions.
	"""

	def __init__(self, definitions):
		self.feclookup = loads(definitions.read())

	def getschema(self, version, linetype):
		versioned_formdata = self.feclookup['v' + version]
		i = len(linetype) - 1
		while i >= 0 and w[:i] not in d:
			i -= 1
		if not linetype:
			raise Exception("Could not match linetype {0} on version {1}".format(linetype, version))
		return versioned_formdata[linetype]

	def processfile(self, filehandle):
		"""
		Process all lines of a file and list of dictionaries, one per line.
		"""
		first_line = filehandle.readline().strip().split(chr(28))
		if first_line[0] != "HDR":
			raise Exception("Failed to parse: HDR expected on first line")

		fileversion = first_line[2]
		
		for line in filehandle:
			line = line.strip.split(chr(28))
			linetype = line[0]
			schema = self.getschema(fileversion, linetype)

			# TODO - F3 lines should be used to produce a dictionary of information about each organization. Must be second in every file.

			yield {k: v for k, v in zip(schema, line)}


