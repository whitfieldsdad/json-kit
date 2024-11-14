import os


object_types = [
    'attack-pattern',
    'campaign',
    'course-of-action',
    'identity',
    'intrusion-set',
    'malware',
    'marking-definition',
    'relationship',
    'tool',
    'x-mitre-data-component',
    'x-mitre-data-source',
    'x-mitre-matrix',
    'x-mitre-tactic',
]
for object_type in object_types:
    input_dir = f'~/src/cti/enterprise-attack/{object_type}'
    dot_file = f'examples/mitre-attack-enterprise/{object_type}.dot'
    png_file = f'examples/mitre-attack-enterprise/{object_type}.png'

    os.system(f'poetry run tool draw {input_dir} -o {dot_file}')
    os.system(f'dot -Tpng -Gdpi=300 {dot_file} -o {png_file}')
