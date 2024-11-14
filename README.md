# json-kit

`json_kit` is a Python3 library that contains a variety of helper functions for working with JSON documents.

The primary focus of the library is to make it easier to understand the abstract structure of one or more JSON documents.

## Features

- Recursively list the keys in one or more JSON documents
- Generate a JSON schema from one or more JSON documents
- Draw JSON schemas as [directed acyclic graphs (DAGs)](https://en.wikipedia.org/wiki/Directed_acyclic_graph) using [GraphViz](https://graphviz.org/)<sub>1</sub>

<sub>1. To render [DOT markup](https://graphviz.org/doc/info/lang.html), this library uses [`dot`](https://graphviz.org/doc/info/command.html), and `dot` must be installed to render DOT markup.</sub>

## Usage

## Recursively listing the keys in JSON files

```bash
poetry run tool keys '~/src/cti/enterprise-attack/attack-pattern/*.json'
```

```json
[
    "id",
    "objects[]",
    "objects[].created",
    "objects[].created_by_ref",
    "objects[].description",
    "objects[].external_references[]",
    "objects[].external_references[].description",
    "objects[].external_references[].external_id",
    "objects[].external_references[].source_name",
    "objects[].external_references[].url",
    "objects[].id",
    "objects[].kill_chain_phases[]",
    "objects[].kill_chain_phases[].kill_chain_name",
    "objects[].kill_chain_phases[].phase_name",
    "objects[].modified",
    "objects[].name",
    "objects[].object_marking_refs[]",
    "objects[].revoked",
    "objects[].type",
    "objects[].x_mitre_attack_spec_version",
    "objects[].x_mitre_contributors[]",
    "objects[].x_mitre_data_sources[]",
    "objects[].x_mitre_defense_bypassed[]",
    "objects[].x_mitre_deprecated",
    "objects[].x_mitre_detection",
    "objects[].x_mitre_domains[]",
    "objects[].x_mitre_effective_permissions[]",
    "objects[].x_mitre_impact_type[]",
    "objects[].x_mitre_is_subtechnique",
    "objects[].x_mitre_modified_by_ref",
    "objects[].x_mitre_network_requirements",
    "objects[].x_mitre_permissions_required[]",
    "objects[].x_mitre_platforms[]",
    "objects[].x_mitre_remote_support",
    "objects[].x_mitre_system_requirements[]",
    "objects[].x_mitre_version",
    "spec_version",
    "type"
]
```

## Generating JSON Schema

```bash
poetry run tool json-schema '~/src/cti/enterprise-attack/attack-pattern/*.json'
```

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
                    "x_mitre_platforms": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "x_mitre_domains": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "object_marking_refs": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "id": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string"
                    },
                    "created": {
                        "type": "string"
                    },
                    "created_by_ref": {
                        "type": "string"
                    },
                    "external_references": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_name": {
                                    "type": "string"
                                },
                                "external_id": {
                                    "type": "string"
                                },
                                "url": {
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
                    "modified": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "kill_chain_phases": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "kill_chain_name": {
                                    "type": "string"
                                },
                                "phase_name": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "kill_chain_name",
                                "phase_name"
                            ]
                        }
                    },
                    "x_mitre_detection": {
                        "type": "string"
                    },
                    "x_mitre_is_subtechnique": {
                        "type": "boolean"
                    },
                    "x_mitre_version": {
                        "type": "string"
                    },
                    "x_mitre_modified_by_ref": {
                        "type": "string"
                    },
                    "x_mitre_data_sources": {
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
                    },
                    "x_mitre_deprecated": {
                        "type": "boolean"
                    },
                    "x_mitre_defense_bypassed": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "revoked": {
                        "type": "boolean"
                    },
                    "x_mitre_attack_spec_version": {
                        "type": "string"
                    },
                    "x_mitre_permissions_required": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "x_mitre_system_requirements": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "x_mitre_remote_support": {
                        "type": "boolean"
                    },
                    "x_mitre_effective_permissions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "x_mitre_impact_type": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "x_mitre_network_requirements": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "created",
                    "created_by_ref",
                    "description",
                    "external_references",
                    "id",
                    "kill_chain_phases",
                    "modified",
                    "name",
                    "object_marking_refs",
                    "type",
                    "x_mitre_domains",
                    "x_mitre_is_subtechnique",
                    "x_mitre_modified_by_ref",
                    "x_mitre_platforms",
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

## Visualizing JSON files as DAGs

```bash
poetry run tool draw '~/src/cti/enterprise-attack/attack-pattern/*.json' -o examples/mitre-attack-enterprise/attack-pattern.dot
```

```
digraph G {
    node [shape=box, style=rounded]
    layout=dot
    rankdir=LR
    splines=true
    ranksep=0.5
    nodesep=0.1

    "id"
    "."
    "objects[]"
    "objects[].created" [label="created"]
    "objects[].created_by_ref" [label="created_by_ref"]
    "objects[].description" [label="description"]
    "objects[].external_references[]" [label="external_references[]"]
    "objects[].external_references[].description" [label="description"]
    "objects[].external_references[].external_id" [label="external_id"]
    "objects[].external_references[].source_name" [label="source_name"]
    "objects[].external_references[].url" [label="url"]
    "objects[].id" [label="id"]
    "objects[].kill_chain_phases[]" [label="kill_chain_phases[]"]
    "objects[].kill_chain_phases[].kill_chain_name" [label="kill_chain_name"]
    "objects[].kill_chain_phases[].phase_name" [label="phase_name"]
    "objects[].modified" [label="modified"]
    "objects[].name" [label="name"]
    "objects[].object_marking_refs[]" [label="object_marking_refs[]"]
    "objects[].revoked" [label="revoked"]
    "objects[].type" [label="type"]
    "objects[].x_mitre_attack_spec_version" [label="x_mitre_attack_spec_version"]
    "objects[].x_mitre_contributors[]" [label="x_mitre_contributors[]"]
    "objects[].x_mitre_data_sources[]" [label="x_mitre_data_sources[]"]
    "objects[].x_mitre_defense_bypassed[]" [label="x_mitre_defense_bypassed[]"]
    "objects[].x_mitre_deprecated" [label="x_mitre_deprecated"]
    "objects[].x_mitre_detection" [label="x_mitre_detection"]
    "objects[].x_mitre_domains[]" [label="x_mitre_domains[]"]
    "objects[].x_mitre_effective_permissions[]" [label="x_mitre_effective_permissions[]"]
    "objects[].x_mitre_impact_type[]" [label="x_mitre_impact_type[]"]
    "objects[].x_mitre_is_subtechnique" [label="x_mitre_is_subtechnique"]
    "objects[].x_mitre_modified_by_ref" [label="x_mitre_modified_by_ref"]
    "objects[].x_mitre_network_requirements" [label="x_mitre_network_requirements"]
    "objects[].x_mitre_permissions_required[]" [label="x_mitre_permissions_required[]"]
    "objects[].x_mitre_platforms[]" [label="x_mitre_platforms[]"]
    "objects[].x_mitre_remote_support" [label="x_mitre_remote_support"]
    "objects[].x_mitre_system_requirements[]" [label="x_mitre_system_requirements[]"]
    "objects[].x_mitre_version" [label="x_mitre_version"]
    "spec_version"
    "type"

    "." -> "id"
    "." -> "objects[]"
    "." -> "spec_version"
    "." -> "type"
    "objects[]" -> "objects[].created"
    "objects[]" -> "objects[].created_by_ref"
    "objects[]" -> "objects[].description"
    "objects[]" -> "objects[].external_references[]"
    "objects[]" -> "objects[].id"
    "objects[]" -> "objects[].kill_chain_phases[]"
    "objects[]" -> "objects[].modified"
    "objects[]" -> "objects[].name"
    "objects[]" -> "objects[].object_marking_refs[]"
    "objects[]" -> "objects[].revoked"
    "objects[]" -> "objects[].type"
    "objects[]" -> "objects[].x_mitre_attack_spec_version"
    "objects[]" -> "objects[].x_mitre_contributors[]"
    "objects[]" -> "objects[].x_mitre_data_sources[]"
    "objects[]" -> "objects[].x_mitre_defense_bypassed[]"
    "objects[]" -> "objects[].x_mitre_deprecated"
    "objects[]" -> "objects[].x_mitre_detection"
    "objects[]" -> "objects[].x_mitre_domains[]"
    "objects[]" -> "objects[].x_mitre_effective_permissions[]"
    "objects[]" -> "objects[].x_mitre_impact_type[]"
    "objects[]" -> "objects[].x_mitre_is_subtechnique"
    "objects[]" -> "objects[].x_mitre_modified_by_ref"
    "objects[]" -> "objects[].x_mitre_network_requirements"
    "objects[]" -> "objects[].x_mitre_permissions_required[]"
    "objects[]" -> "objects[].x_mitre_platforms[]"
    "objects[]" -> "objects[].x_mitre_remote_support"
    "objects[]" -> "objects[].x_mitre_system_requirements[]"
    "objects[]" -> "objects[].x_mitre_version"
    "objects[].external_references[]" -> "objects[].external_references[].description"
    "objects[].external_references[]" -> "objects[].external_references[].external_id"
    "objects[].external_references[]" -> "objects[].external_references[].source_name"
    "objects[].external_references[]" -> "objects[].external_references[].url"
    "objects[].kill_chain_phases[]" -> "objects[].kill_chain_phases[].kill_chain_name"
    "objects[].kill_chain_phases[]" -> "objects[].kill_chain_phases[].phase_name"
}
```

![`attack-pattern`](examples/mitre-attack-enterprise/attack-pattern.png)
