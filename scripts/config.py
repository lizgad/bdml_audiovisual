import configparser
import os
import shutil
import sys


def load_config(config_file):
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config
    else:
        print("Config file {} not found".format(config_file))
        sys.exit()


def load_bdml_config(bdml_config_file):
    bdml_config = load_config(bdml_config_file)
    sections = bdml_config.sections()
    bdml_config_dict = {}
    for section in sections:
        bdml_config_dict[section] = {key: value for (key, value) in bdml_config.items(section)}
    return bdml_config_dict


def create_config(BDMLMetadataPrepper):
    bdml_config = BDMLMetadataPrepper.bdml_config
    default_audio_dir = bdml_config["base_paths"]["default_audio_dir"]
    default_video_dir = bdml_config["base_paths"]["default_video_dir"]
    default_audio_extension = bdml_config["default_extensions"]["audio"]
    default_video_extension = bdml_config["default_extensions"]["video"]
    default_access_control = bdml_config["access_control"]["default"]
    default_category = bdml_config["categories"]["default"]

    access_profile_choices = ["reading_room", "public"]
    category_choices = ["reading_room", "public", "staging"]

    access_profile = ""
    while access_profile not in access_profile_choices:
        print("\n\nCONFIGURE ACCESS PROFILE (default: {})".format(default_access_control))
        for access_profile_choice in access_profile_choices:
            print("* - {}".format(access_profile_choice))
        access_profile_input = input("Enter a profile or leave blank for default: ")
        if access_profile_input == "":
            access_profile = default_access_control
        else:
            access_profile = access_profile_input

    category = ""
    while category not in category_choices:
        print("\n\nCONFIGURE CATEGORY (default: {})".format(default_category))
        for category_choice in category_choices:
            print("* - {}".format(category_choice))
        category_input = input("Enter a category or leave blank for default: ")
        if category_input == "":
            category = default_category
        else:
            category = category_input

    print("\n\nCONFIGURE LOCATION OF CONTENT")
    print("default audio directory: {}".format(default_audio_dir))
    print("default video directory: {}".format(default_video_dir))
    print("Enter the base directory for the content, or enter audio or video to use the defaults")
    content_location = input(": ")
    if content_location == "audio":
        r_drive_location = default_audio_dir
    elif content_location == "video":
        r_drive_location = default_video_dir
    else:
        r_drive_location = content_location

    print("\n\nCONFIGURE PREFERRED CONTENT EXTENSIONS")
    print("default audio extension: {}".format(default_audio_extension))
    print("default video extension: {}".format(default_video_extension))
    default_extensions = input("Would you like to use the default extensions for audio and video ? (y/n) ")
    if default_extensions.lower().strip() in ["y", "yes"]:
        preferred_audio_extension = default_audio_extension
        preferred_video_extension = default_video_extension
    else:
        preferred_audio_extension = input("Enter the preferred extension for audio files (or leave blank): ")
        preferred_video_extension = input("Enter the preferred extension for video files (or leave blank): ")
    print("\n\nConfigure EAD")
    has_ead_input = input("Does this collection have an EAD? (y/n) ")
    if has_ead_input.lower().strip() in ["y", "yes"]:
        has_ead = "true"
        ead_id = input("Enter the numerical portion of the EAD ID (or leave blank if same as collection ID): ")
    else:
        has_ead = "false"
        ead_id = ""
    config = configparser.RawConfigParser()
    config.add_section("main")
    config.set("main", "access_profile", access_profile)
    config.set("main", "category", category)
    config.set("main", "r_drive_location", r_drive_location)
    config.set("main", "preferred_audio_extension", preferred_audio_extension)
    config.set("main", "preferred_video_extension", preferred_video_extension)
    config.set("main", "has_ead", has_ead)
    config.set("main", "ead_id", ead_id)
    return config


def load_project_config(BDMLMetadataPrepper, default_config_file):
    project_dir = BDMLMetadataPrepper.project_dir
    project_config_file = ""
    project_config_cfg = os.path.join(project_dir, "config.cfg")
    project_default_config_cfg = os.path.join(project_dir, "default_config.cfg")
    if os.path.exists(project_config_cfg):
        project_config_file = project_config_cfg
    elif os.path.exists(project_default_config_cfg):
        project_config_file = project_default_config_cfg
    else:
        default_config = load_config(default_config_file)
        print("Config file not found for {}".format(BDMLMetadataPrepper.project_name))
        print("*** CONFIG DEFAULTS ***")
        for key, value in default_config.items("main"):
            print("{} = {}".format(key, value))
        use_defaults = input("Would you like to use the default configuration? (y/n) ")
        if use_defaults.lower().strip() in ["y", "yes"]:
            shutil.copy(default_config_file, project_config_file)
        else:
            create_config_input = input("Create config file now? (y/n) ")
            if create_config_input.lower().strip() in ["y", "yes"]:
                config = create_config(BDMLMetadataPrepper)
                with open(project_config_file, "w") as f:
                    config.write(f)
            else:
                print("goodbye!")
                sys.exit()
    project_config = load_config(project_config_file)
    return {key: value for (key, value) in project_config.items("main")}
