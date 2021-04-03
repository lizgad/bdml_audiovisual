def beal_element_mappings():
    element_mappings = [
        {"name": "identifier", "type": "xpath", "xpath": "./fmpro:DigFile_Calc"},
        {"name": "item_number", "type": "xpath", "xpath": "./fmpro:CollItemNo"},
        {"name": "collection_title", "type": "xpath", "xpath": "./fmpro:CollectionTitle/fmpro:DATA"},
        {"name": "collection_creator", "type": "xpath", "xpath": "./fmpro:CollectionCreator/fmpro:DATA"},
        {"name": "collection_id", "type": "xpath", "xpath": "./fmpro:CollectionID/fmpro:DATA"},
        {"name": "description", "type": "xpath", "xpath": "./fmpro:NoteContent"},
        {"name": "item_title", "type": "xpath", "xpath": "./fmpro:ItemTitle"},
        {"name": "item_part_title", "type": "xpath", "xpath": "./fmpro:ItemPartTitle"},
        {"name": "item_part_segment", "type": "xpath", "xpath": "./fmpro:ItemPart_Segment"},
        {"name": "coverage", "type": "xpath", "xpath": "./fmpro:ItemDate"},
        {"name": "audio_genres", "type": "xpath_multiple", "xpath": "./fmpro:Audio_Genre/fmpro:DATA"},
        {"name": "item_subjects", "type": "xpath_multiple", "xpath": "./fmpro:Audio_Subject/fmpro:DATA"},
        {"name": "av_type", "type": "xpath", "xpath": "./fmpro:AVType"},
        {"name": "reel_size", "type": "xpath", "xpath": "./fmpro:ReelSize/fmpro:DATA"},
        {"name": "tape_speed", "type": "xpath", "xpath": "./fmpro:TapeSpeed/fmpro:DATA"},
        {"name": "item_color", "type": "xpath", "xpath": "./fmpro:ItemColor"},
        {"name": "item_time", "type": "xpath", "xpath": "./fmpro:ItemTime"},
        {"name": "item_sound", "type": "xpath", "xpath": "./fmpro:ItemSound"},
        {"name": "fidelity", "type": "xpath", "xpath": "./fmpro:Fidleity/fmpro:DATA"},
    ]
    return element_mappings


def clean_beal_audio(metadata):
    items = {}
    for item_identifier, item_metadata in metadata.items():
        if item_metadata["item_part_title"]:
            item_metadata["item_title"] += " " + item_metadata["item_part_title"]
        del item_metadata["item_part_title"]
        item_metadata["item_number"] = item_metadata["item_number"].replace("\n", "").replace("\r", "").replace(" ", "").strip()
        if "-sr-" in item_metadata["item_number"].lower():
            item_metadata["media_type"] = "audio"
        else:
            item_metadata["media_type"] = "video"

        source_parenthical_bits = [item_metadata["reel_size"], item_metadata["tape_speed"]]
        source_parenthical_bits = [bit for bit in source_parenthical_bits if bit]
        if source_parenthical_bits:
            item_metadata["source"] = "{} ({})".format(item_metadata["av_type"], ", ".join(source_parenthical_bits))
        else:
            item_metadata["source"] = item_metadata["av_type"]
        source_additional_bits = [item_metadata["item_color"], item_metadata["item_sound"], item_metadata["fidelity"], item_metadata["item_time"]]
        source_additional_bits = [bit for bit in source_additional_bits if bit]
        if source_additional_bits:
            item_metadata["source"] = item_metadata["source"] + ", {}".format(", ".join(source_additional_bits))

        del item_metadata["av_type"]
        del item_metadata["reel_size"]
        del item_metadata["tape_speed"]
        del item_metadata["item_color"]
        del item_metadata["item_time"]
        del item_metadata["item_sound"]
        del item_metadata["fidelity"]
        items[item_identifier] = item_metadata
    return items
