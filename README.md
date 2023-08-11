# json-kit

A Python3 module for translating JSON and JSONL documents into JSON Schemas, DOT files, and images.

![Pivot points](docs/pivot-points.png)

> 👷 🚧: this project is experimental, doesn't have a stable API, and is under active development.

## Requirements

- [Python](https://www.python.org/) 3.10+ (see [pyproject.toml](pyproject.toml))
- [Poetry](https://python-poetry.org/)

## Installation

To install this project and its dependencies, run:

```bash
make install
```

## Usage

The following examples use a STIX 2.0 representation of the MITRE ATT&CK framework as a sample dataset when generating JSON Schemas, DOT files, and images.

You can download the latest version of the MITRE ATT&CK framework as follows:

```bash
mkdir -p demo/generated
git clone https://github.com/mitre/cti --depth=1 demo/cti
```

### JSON to JSON Schema

As an example, let's generate a JSON Schema for all `campaign` objects from the MITRE ATT&CK framework and print it to the console:

```bash
poetry run json2schema demo/cti/enterprise-attack/campaign/*.json | jq
```

Yielding:

```json
{
  "$schema": "http://json-schema.org/schema#",
  "type": "object",
  "properties": {
    "type": {
      "type": "string"
    },
    "id": {
      "type": "string"
    },
    "spec_version": {
      "type": "string"
    },
    "objects": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "modified": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "aliases": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "first_seen": {
            "type": "string"
          },
          "last_seen": {
            "type": "string"
          },
          "x_mitre_first_seen_citation": {
            "type": "string"
          },
          "x_mitre_last_seen_citation": {
            "type": "string"
          },
          "x_mitre_deprecated": {
            "type": "boolean"
          },
          "x_mitre_version": {
            "type": "string"
          },
          "type": {
            "type": "string"
          },
          "id": {
            "type": "string"
          },
          "created": {
            "type": "string"
          },
          "created_by_ref": {
            "type": "string"
          },
          "revoked": {
            "type": "boolean"
          },
          "external_references": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "source_name": {
                  "type": "string"
                },
                "url": {
                  "type": "string"
                },
                "external_id": {
                  "type": "string"
                },
                "description": {
                  "type": "string"
                }
              },
              "required": [
                "source_name"
              ]
            }
          },
          "object_marking_refs": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "x_mitre_attack_spec_version": {
            "type": "string"
          },
          "x_mitre_modified_by_ref": {
            "type": "string"
          },
          "x_mitre_domains": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "x_mitre_contributors": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "required": [
          "aliases",
          "created",
          "created_by_ref",
          "description",
          "external_references",
          "first_seen",
          "id",
          "last_seen",
          "modified",
          "name",
          "object_marking_refs",
          "revoked",
          "type",
          "x_mitre_attack_spec_version",
          "x_mitre_deprecated",
          "x_mitre_domains",
          "x_mitre_first_seen_citation",
          "x_mitre_last_seen_citation",
          "x_mitre_modified_by_ref",
          "x_mitre_version"
        ]
      }
    }
  },
  "required": [
    "id",
    "objects",
    "spec_version",
    "type"
  ]
}
```

You can save the output to a file using shell redirection or the `--output-file/-o` option:

```bash
# Option #1: shell redirection
poetry run json2schema demo/cti/enterprise-attack/campaign/*.json | jq '.' > demo/generated/campaign.schema.json

# Option #2: use the --output-file/-o flag
poetry run json2schema demo/cti/enterprise-attack/campaign/*.json -o demo/generated/campaign.schema.json
```

You can also generate one JSON Schema per input file by passing a directory to the `--output-file/-o` option:

```bash
poetry run json2schema cti/enterprise-attack/campaign/*.json -o demo/generated
```
