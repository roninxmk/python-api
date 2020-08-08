import markdown
import os
import io
import shelve
import werkzeug
from tinytag import TinyTag
from pprint import pprint

tempfile = os.path.join("myfile.wav")

# Analyze file
with io.open(tempfile, 'rb') as fh:
    parser = TinyTag.get_parser_class(tempfile, fh)

# pprint((parser))
# pprint(vars(parser))
# pprint(vars(vars(parser)['_parse_tag']))
# pprint(dir(vars(parser)['_parse_tag']))
# pprint(type(vars(parser)['_parse_tag']))
pprint(id(vars(parser)['_parse_tag']))
# pprint(id(vars(parser)['_parse_tag']))
# pprint(getattr(vars(parser)['_parse_tag'], "Wave"))

pprint((parser).__name__)
# pprint(getattr((parser), "tinytag.tinytag.Wave"))

# print("Parser: {}" .format(parser))
# print("Vars: {}" .format(vars(parser)))
# print("Type: {}" .format(type(parser)))
# print("Dir: {}" .format(dir(parser)))
# print("Vars(_parse_tag): {}" .format((vars(parser))['_parse_tag']))
# print("Vars(Vars(_parse_tag)): {}" .format(vars(vars(parser))['_parse_tag']))

if (parser.__name__ == "Wave"):
    print("Found WAV file")
    tag = TinyTag.get(tempfile)
