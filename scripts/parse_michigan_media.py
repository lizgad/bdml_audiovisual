def michigan_media_element_mappings():
    element_mappings = [
        {"name": "identifier", "type": "xpath", "xpath": "./fmpro:coll_itemno"},
        {"name": "media_type", "type": "string", "string": "video"},
        {"name": "collection_title", "type": "string", "string": "Media Resources Center (University of Michigan) records"},
        {"name": "collection_creator", "type": "string", "string": "University of Michigan. Media Resources Center."},
        {"name": "collection_id", "type": "string", "string": "851831"},
        {"name": "description", "type": "xpath", "xpath": "./fmpro:SubjectAndTalent"},
        {"name": "program_title", "type": "xpath", "xpath": "./fmpro:title"},
        {"name": "program_part_number", "type": "xpath", "xpath": "./fmpro:program"},
        {"name": "program_part_title", "type": "xpath", "xpath": "./fmpro:progname"},
        {"name": "coverage", "type": "xpath", "xpath": "./fmpro:date"},
        {"name": "item_subjects", "type": "xpath_multiple", "xpath": "./fmpro:subject/fmpro:DATA"},
        {"name": "av_type", "type": "xpath", "xpath": "./fmpro:avtype"},
        {"name": "sound", "type": "xpath", "xpath": "./fmpro:sound"},
        {"name": "item_color", "type": "xpath", "xpath": "./fmpro:color"}
    ]
    return element_mappings


def clean_michigan_media(metadata):
    items = {}
    for item_identifier, item_metadata in metadata.items():
        item_metadata["item_number"] = item_metadata["identifier"]
        if item_metadata["program_part_number"]:
            item_metadata["item_title"] = item_metadata["program_title"] + " [Part {}]: ".format(item_metadata["program_part_number"]) + item_metadata["program_part_title"]
        else:
            item_metadata["item_title"] = item_metadata["program_title"]
        del item_metadata["program_title"]
        del item_metadata["program_part_number"]
        del item_metadata["program_part_title"]

        parenthetical_bits = [item_metadata["item_color"], item_metadata["sound"]]
        parenthetical_bits = [bit for bit in parenthetical_bits if bit]
        if parenthetical_bits:
            item_metadata["source"] = "{} ({})".format(item_metadata["av_type"], ", ".join(parenthetical_bits))
        else:
            item_metadata["source"] = item_metadata["av_type"]

        del item_metadata["item_color"]
        del item_metadata["sound"]
        del item_metadata["av_type"]

        items[item_metadata["identifier"]] = item_metadata
    return items
