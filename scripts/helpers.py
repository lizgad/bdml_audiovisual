import os
import sys
from lxml import etree

from .parse_beal_audio import beal_element_mappings, clean_beal_audio
from .parse_michigan_media import michigan_media_element_mappings, clean_michigan_media


def filemaker_namespace():
    return {"fmpro": "http://www.filemaker.com/fmpdsoresult"}


def bdml_namespace_dict():
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    nsmap = {
        "xsi": xsi,
        "xsd": "http://www.w3.org/2001/XMLSchema",
        "file": "http://expath.org/ns/file"
    }
    xsi_attrib = {"{"+xsi+"}noNamespaceSchemaLocation": "bulkUploadXml.bulkUploadXML.xsd"}
    return {"xsi_attrib": xsi_attrib, "nsmap": nsmap}


def characterize_export(tree, BDMLMetadataPrepper):
    # determine if an export from filemaker is michigan media or beal audio
    database = tree.xpath(".//fmpro:DATABASE", namespaces=BDMLMetadataPrepper.fmpro_nsmap)[0].text.strip().lower()
    if database.startswith("mi media"):
        return "michigan_media"
    elif database.startswith("beal"):
        return "beal"
    else:
        print("Could not characterize database {}".format(database))
        sys.exit()


def extract_text_from_element(element):
    if element.text is not None:
        return element.text.strip().replace('“', '"').replace('”', '"')
    else:
        return ""


def extract_metadata_from_export(BDMLMetadataPrepper):
    project_name = BDMLMetadataPrepper.project_name
    project_dir = BDMLMetadataPrepper.project_dir
    project_export = os.path.join(project_dir, "{}-fmpro.xml".format(project_name))
    if not os.path.exists(project_export):
        print("Metadata export not found for {}".format(project_name))
        sys.exit()
    tree = etree.parse(project_export)
    michigan_media_or_beal = characterize_export(tree, BDMLMetadataPrepper)
    if michigan_media_or_beal == "michigan_media":
        element_mappings = michigan_media_element_mappings()
        metadata = generic_parser(tree, element_mappings, BDMLMetadataPrepper)
        metadata = clean_michigan_media(metadata)
    elif michigan_media_or_beal == "beal":
        element_mappings = beal_element_mappings()
        metadata = generic_parser(tree, element_mappings, BDMLMetadataPrepper)
        metadata = clean_beal_audio(metadata)
    return metadata


def generic_parser(tree, element_mappings, BDMLMetadataPrepper):
    items = {}
    fmpro_nsmap = BDMLMetadataPrepper.fmpro_nsmap
    rows = tree.xpath("//fmpro:ROW", namespaces=fmpro_nsmap)
    for row in rows:
        item_metadata = {}
        for element_mapping in element_mappings:
            element_name = element_mapping["name"]
            if element_mapping["type"] == "string":
                item_metadata[element_name] = element_mapping["string"]
            elif element_mapping["type"] == "xpath":
                xpath = element_mapping["xpath"]
                elements = row.xpath(xpath, namespaces=fmpro_nsmap)
                if elements:
                    element = elements[0]
                    item_metadata[element_name] = extract_text_from_element(element)
                else:
                    item_metadata[element_name] = ""
            elif element_mapping["type"] == "xpath_multiple":
                xpath = element_mapping["xpath"]
                item_metadata[element_name] = []
                elements = row.xpath(xpath, namespaces=fmpro_nsmap)
                for element in elements:
                    item_metadata[element_name].append(extract_text_from_element(element))

        if not item_metadata["coverage"]:
            item_metadata["coverage"] = "Undated"
        items[item_metadata["identifier"]] = item_metadata

    return items


def extract_part_from_filepath(filepath):
    filename = os.path.split(filepath)[-1]
    filename_no_extension = filename.split(".")[0]
    part = filename_no_extension.split("-")[-1]
    return int(part)


def make_title_addendum(part_index, total_parts):
    part_index_string = str(part_index)
    total_parts_string = str(total_parts)
    while len(part_index_string) < len(total_parts_string):
        part_index_string = "0" + part_index_string

    return "({} of {})".format(part_index_string, total_parts_string)
