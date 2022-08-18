from xml.dom import minidom
from xml.etree.ElementTree import tostring


def prettify(elem):
    rough_string = tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
