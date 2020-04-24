import os
import shutil
import subprocess


def permutate_file_identifier(file_identifier):
    permutations = [file_identifier, file_identifier.lower()]
    identifier_parts = file_identifier.split("-")
    identifier_with_pm = "{}-pm".format(file_identifier)
    identifier_with_am = "{}-am".format(file_identifier)
    identifier_no_dashes = "".join(identifier_parts)
    identifier_with_dashes = "-".join(identifier_parts)
    if len(identifier_parts) == 3:
        identifier_no_second_dash = "{}-{}{}".format(identifier_parts[0], identifier_parts[1], identifier_parts[2])
        permutations.append(identifier_no_second_dash)
    if len(identifier_parts) == 4:
        identifier_no_second_dash = "{}-{}{}-{}".format(identifier_parts[0], identifier_parts[1], identifier_parts[2], identifier_parts[3])
        permutations.append(identifier_no_second_dash)
    identifier_appended = "{}-1".format(identifier_with_dashes)
    identifier_appended_with_pm = "{}-pm".format(identifier_appended)
    identifier_appended_with_am = "{}-am".format(identifier_appended)
    identifier_periods_to_underscores = file_identifier.replace(".", "_")
    for permutation in [identifier_with_pm, identifier_appended_with_pm, identifier_appended,
                        identifier_no_dashes, identifier_with_dashes, identifier_with_am, identifier_appended_with_am, identifier_periods_to_underscores]:
        if permutation not in permutations:
            permutations.append(permutation)
        if permutation.lower() not in permutations:
            permutations.append(permutation.lower())
    return permutations


def locate_src_filepath(item_directory, item_number, file_identifier, preferred_extension, default_extension):
    src_filepath = ""
    possible_filenames = permutate_file_identifier(file_identifier)
    possible_filenames.append(item_number)
    files_in_directory = os.listdir(item_directory)
    if preferred_extension:
        file_extension = preferred_extension
    else:
        file_extension = default_extension
    for possible_filename in possible_filenames:
        filename_with_extension = "{}.{}".format(possible_filename, file_extension)
        if filename_with_extension in files_in_directory:
            src_filepath = os.path.join(item_directory, filename_with_extension)
            break
    return src_filepath


def locate_dst_filepath(src_filepath, bdml_upload_dir, media_type, collection_id, item_number, file_identifier):
    bdml_media_dir = os.path.join(bdml_upload_dir, media_type)
    src_filename = os.path.split(src_filepath)[-1]
    bdml_collection_dir = os.path.join(bdml_media_dir, collection_id)
    if not os.path.exists(bdml_collection_dir):
        os.makedirs(bdml_collection_dir)
    bdml_item_dir = os.path.join(bdml_collection_dir, item_number)
    if not os.path.exists(bdml_item_dir):
        os.makedirs(bdml_item_dir)
    dst_filepath = os.path.join(bdml_item_dir, src_filename)
    return src_filename, bdml_item_dir, dst_filepath


def find_item_directory(r_drive_location, collection_id, item_number):
    collection_dir = os.path.join(r_drive_location, collection_id)
    base_item_dir = os.path.join(r_drive_location, item_number)
    if os.path.exists(collection_dir):
        item_dir = os.path.join(collection_dir, item_number)
        item_appended_dir = os.path.join(collection_dir, "{}-1".format(item_number))
        if os.path.exists(item_dir):
            return item_dir
        elif os.path.exists(item_appended_dir):
            return item_appended_dir
        else:
            return collection_dir
    elif os.path.exists(base_item_dir):
        return base_item_dir
    else:
        return r_drive_location


def make_bdml_url(media_base_url, media_type, collection_id, item_number, filename):
    return "{}/{}/{}/{}/{}".format(media_base_url, media_type, collection_id, item_number, filename)


def copy_files(BDMLMetadataPrepper, metadata):
    project_config = BDMLMetadataPrepper.project_config
    bdml_config = BDMLMetadataPrepper.bdml_config
    r_drive_location = project_config["r_drive_location"]
    media_base_url = bdml_config["base_paths"]["media"]
    bdml_upload_dir = bdml_config["base_paths"]["filesystem"]
    files_not_found = []
    for file_identifier, file_metadata in metadata.items():
        print(file_identifier)
        collection_id = file_metadata["collection_id"]
        item_number = file_metadata["item_number"]
        media_type = file_metadata["media_type"]
        preferred_extension = project_config.get("preferred_{}_extension".format(media_type))
        default_extension = bdml_config["default_extensions"][media_type]
        item_directory = find_item_directory(r_drive_location, collection_id, item_number)
        src_filepath = locate_src_filepath(item_directory, item_number, file_identifier, preferred_extension, default_extension)
        if src_filepath:
            src_filename, dst_dirpath, dst_filepath = locate_dst_filepath(src_filepath, bdml_upload_dir, media_type, collection_id, item_number, file_identifier)
            if (not os.path.exists(dst_filepath) or BDMLMetadataPrepper.force_copy) and not BDMLMetadataPrepper.skip_copy:
                print("Copying {} to {}".format(src_filepath, dst_filepath))
                cmd = ["robocopy", item_directory, dst_dirpath, src_filename]
                subprocess.call(cmd)
            image_filenames = copy_item_images(BDMLMetadataPrepper, item_directory, bdml_upload_dir, media_type, collection_id, item_number)
            item_urls = {"images": [], "content": "", "thumbnail": ""}
            item_urls["content"] = make_bdml_url(media_base_url, media_type, collection_id, item_number, src_filename)
            for image_filename in image_filenames:
                item_urls["images"].append(make_bdml_url(media_base_url, media_type, collection_id, item_number, image_filename))
            if media_type == "audio" and image_filenames:
                thumbnail_filenames = [filename for filename in image_filenames if filename.split("-")[-1].startswith("001")]
                if thumbnail_filenames:
                    item_urls["thumbnail"] = make_bdml_url(media_base_url, media_type, collection_id, item_number, thumbnail_filenames[0])
            file_metadata["urls"] = item_urls
        else:
            files_not_found.append(file_identifier)
    for file_not_found in files_not_found:
        del metadata[file_not_found]
    BDMLMetadataPrepper.items = metadata
    return files_not_found


def copy_item_images(BDMLMetadataPrepper, item_directory, bdml_upload_dir, media_type, collection_id, item_number):
    image_extensions = ["jpg", "JPG"]
    image_files = [filename for filename in os.listdir(item_directory) if filename.split(".")[-1] in image_extensions]
    dst_directory = os.path.join(bdml_upload_dir, media_type, collection_id, item_number)
    for image_file in image_files:
        image_src = os.path.join(item_directory, image_file)
        image_dst = os.path.join(dst_directory, image_file)
        if (not os.path.exists(image_dst) or BDMLMetadataPrepper.force_copy) and not BDMLMetadataPrepper.skip_copy:
            print("Copying {} to {}".format(image_src, image_dst))
            shutil.copy(image_src, image_dst)
    return image_files
