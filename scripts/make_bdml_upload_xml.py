from lxml.builder import ElementMaker
from lxml import etree
import os

from .helpers import bdml_namespace_dict


def make_bdml_upload_xml(BDMLMetadataPrepper):
    project_dir = BDMLMetadataPrepper.project_dir
    project_name = BDMLMetadataPrepper.project_name
    upload_xml_filename = "{}-fmpro-to-kmc.xml".format(project_name)
    upload_xml_filepath = os.path.join(project_dir, upload_xml_filename)
    items = BDMLMetadataPrepper.items
    bdml_config = BDMLMetadataPrepper.bdml_config
    project_config = BDMLMetadataPrepper.project_config
    project_category = project_config["category"]
    project_access_profile = project_config["access_profile"]
    CATEGORY = bdml_config["categories"][project_category]
    ACCESSCONTROLID = bdml_config["access_control"][project_access_profile]
    bdml_namespaces = bdml_namespace_dict()
    nsmap = bdml_namespaces["nsmap"]
    xsi_attrib = bdml_namespaces["xsi_attrib"]
    E = ElementMaker(nsmap=nsmap)
    kmc_xml = E.mrss(xsi_attrib)
    channel = E.channel()
    for item_identifier, item_metadata in items.items():
        item_media_type = item_metadata["media_type"]
        media_type_id = bdml_config["media_types"][item_media_type]
        urls = item_metadata["urls"]
        content_url = urls["content"]
        images = urls["images"]
        thumbnail = urls["thumbnail"]
        tags = E.tags(
            E.tag(item_metadata["item_number"]),
            E.tag(item_metadata["collection_title"].replace(",", ""))
        )

        if item_metadata.get("audio_genres"):
            for audio_genre in item_metadata["audio_genres"]:
                tags.append(E.tag(audio_genre.replace(",", "")))

        if item_metadata.get("item_subjects"):
            for item_subject in item_metadata["item_subjects"]:
                tags.append(E.tag(item_subject.replace(",", "")))

        if project_config.get("has_ead") in ["true", "y", "yes"]:
            if project_config.get("ead_id"):
                ead_id = project_config["ead_id"]
            else:
                ead_id = item_metadata["collection_id"]
            relation = '<a href="https://quod.lib.umich.edu/b/bhlead/umich-bhl-{}" target="new">{}</a>'.format(ead_id, item_metadata["collection_title"])
        else:
            relation = item_metadata["collection_title"] 

        if images:
            attachments = E.attachments()
            for image in sorted(images):
                attachment = E.attachment({"format": "2"},
                                E.urlContentResource(url=image),
                                E.filename(image.split("/")[-1]),
                                E.description("Images of original media and any accompanying notes")
                            )
                attachments.append(attachment)
        else:
            attachments = ""

        if thumbnail:
            thumbnails = E.thumbnails(
                            E.thumbnail({"isDefault": "true"},
                                E.urlContentResource({"url": thumbnail})
                            )
                        )
        else:
            if item_metadata["media_type"] == "audio":
                print("NO THUMBNAIL FOUND FOR {}".format(item_identifier))
            thumbnails = ""

        item = E.item(
            E.action(bdml_config["general"]["action"]),
            E.referenceId(item_identifier),
            E.type(bdml_config["general"]["type"]),
            E.userId(bdml_config["general"]["userid"]),
            E.name(item_metadata["item_title"]),
            E.description(item_metadata["description"]),
            tags,
            E.categories(
                E.category(CATEGORY)
                ),
            E.accessControlId(ACCESSCONTROLID),
            E.conversionProfileId(bdml_config["general"]["conversionprofileid"]),
            E.media(
                E.mediaType(media_type_id)
                ),
            E.contentAssets(
                E.content(
                    E.urlContentResource({"url": content_url})
                    )
                ),
            thumbnails,
            E.customDataItems(
                E.customData({"metadataProfileId": bdml_config["general"]["metadataprofileid"]},
                    E.xmlData(
                        E.metadata(
                            E.Relation(relation),
                            E.Stewardship('<a href="https://bentley.umich.edu" target="new">Bentley Historical Library</a>'),
                            E.Creator(item_metadata["collection_creator"]),
                            E.Coverage(item_metadata["coverage"]),
                            E.Language("English"),
                            E.Source(item_metadata["source"]),
                            E.Identifier(item_identifier),
                            E.Rights(bdml_config["default_statements"]["rights"]),
                            E.Disclaimer(bdml_config["default_statements"]["disclaimer"])
                            )
                        )
                    )
                ),
            attachments
            )

        channel.append(item)
    kmc_xml.append(channel)

    with open(upload_xml_filepath, "wb") as f:
        f.write(etree.tostring(kmc_xml, encoding="utf-8", xml_declaration=True, pretty_print=True))
