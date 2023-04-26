from json_kit.constants import JSON_INDENT, MARKDOWN_INDENT
import json_kit.json_schema as json_schema
import json_kit.digraphs as digraphs
import glob
import json
import os

DIR = "resources/example-data/json/stix2/"

STIX2_TYPES = [
    "attack-pattern",
    "campaign",
    "course-of-action",
    "identity",
    "intrusion-set",
    "malware",
    "marking-definition",
    "relationship",
    "tool",
    "x-mitre-data-component",
    "x-mitre-data-source",
    "x-mitre-matrix",
    "x-mitre-tactic",
]

# JSON to JSON Schema.
for (
    input_directory,
    json_schema_output_directory,
    dot_output_directory,
    png_output_directory,
) in [
    [
        os.path.join(DIR, "mitre-attack", "json"),
        os.path.join(DIR, "mitre-attack", "json-schema"),
        os.path.join(DIR, "mitre-attack", "dot"),
        os.path.join(DIR, "mitre-attack", "png"),
    ],
    [
        os.path.join(DIR, "mitre-capec", "json"),
        os.path.join(DIR, "mitre-capec", "json-schema"),
        os.path.join(DIR, "mitre-capec", "dot"),
        os.path.join(DIR, "mitre-capec", "png"),
    ],
]:
    for stix2_type in STIX2_TYPES:
        pattern = os.path.join(input_directory, stix2_type + "*.json")
        input_files = glob.glob(pattern)
        if input_files:
            # Generate JSON Schema files.
            output_path = os.path.join(
                json_schema_output_directory, stix2_type + ".json"
            )
            if not os.path.exists(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

            schema = json_schema.generate_schema_from_files(input_files)
            with open(output_path, "w") as file:
                json.dump(schema, file, indent=JSON_INDENT)

            # Generate DOT files.
            output_path = os.path.join(dot_output_directory, stix2_type + ".dot")
            if not os.path.exists(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

            g = digraphs.schema_to_attribute_digraph(schema)
            dot = digraphs.digraph_to_dot(g, indent=MARKDOWN_INDENT)
            with open(output_path, "w") as file:
                file.write(dot)

            # Generate PNG files.
            output_path = os.path.join(png_output_directory, stix2_type + ".png")
            if not os.path.exists(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            digraphs.g_to_png(g, output_path)
