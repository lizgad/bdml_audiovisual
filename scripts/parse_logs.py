import csv
import os
from collections import Counter
from lxml import etree
import sys


def parse_logs(BDMLMetadataPrepper):
    project_dir = BDMLMetadataPrepper.project_dir
    project_name = BDMLMetadataPrepper.project_name
    project_upload_xml = os.path.join(project_dir, "{}-fmpro-to-kmc.xml".format(project_name))
    project_logs = os.path.join(project_dir, "logs.xml")
    errors_csv = os.path.join(project_dir, "errors.csv")
    beal_to_mivideo_ids_csv = os.path.join(project_dir, "beal_to_mivideo_ids.csv")
    if not os.path.exists(project_logs):
        print("Logs not found at {}".format(project_logs))
        sys.exit()
    uploaded_tree = etree.parse(project_upload_xml)
    logs_tree = etree.parse(project_logs)
    submitted_identifiers = [item.xpath('./referenceId')[0].text for item in uploaded_tree.xpath("//item")]
    beal_to_mivideo_ids = {}
    error_messages = {}
    logs_identifiers = []
    for item in logs_tree.xpath("//item"):
        beal_id = item.xpath("./referenceID")[0].text
        mivideo_id = item.xpath("./entryId")[0].text
        logs_identifiers.append(beal_id)

        if beal_id not in beal_to_mivideo_ids:
            beal_to_mivideo_ids[beal_id] = []
        beal_to_mivideo_ids[beal_id].append(mivideo_id)
        error_message = item.xpath("./result/errorDescription")[0].text
        if error_message:
            error_message[beal_id] = error_message
    error_data = []
    not_uploaded = [identifier for identifier in submitted_identifiers if identifier not in logs_identifiers]
    duplicates = [identifier for identifier in logs_identifiers if Counter(logs_identifiers)[identifier] > 1]
    error_data.extend([[identifier, "", "Not Uploaded"] for identifier in not_uploaded])
    error_data.extend([[identifier, beal_to_mivideo_ids[identifier], "Duplicate"] for identifier in duplicates])
    error_data.extend([[identifier, beal_to_mivideo_ids[identifier], error_message] for identifier, error_message in error_messages.items()])
    beal_to_mivideo_data = [[identifier, beal_to_mivideo_ids[identifier][0]] for identifier in beal_to_mivideo_ids if len(beal_to_mivideo_ids[identifier]) == 1 and identifier not in duplicates]

    if error_data:
        print("Errors detected!")
        with open(errors_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["beal_id", "mivideo_ids", "description"])
            writer.writerows(error_data)

    with open(beal_to_mivideo_ids_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["digfilecalc", "mivideo_id"])
        writer.writerows(beal_to_mivideo_data)
