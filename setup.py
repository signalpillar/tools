
from setuptools import setup


def get_content(path):
    """Read content of the file

    str -> str
    """
    with open(path) as file_:
        return file_.read()


setup(
    name="vw-tools-py",
    description="Tools for interacting with VirtualWisdom.",
    version="0.0.1",
    entry_points={
        'console_scripts': [
            'vw_import_entities       = vw.EntityImport:main',
            'vw_export_entities       = vw.ExportEntities:main',
            'vw_csv_nickname_to_json  = vw.CSVNicknameToJSON:main',
            'vw_csv_relations_to_json = vw.CSVRelationsToJSON:main',
            'vw_show_topology         = vw.ShowTopology:main',
            'vw_expand_app_to_initiator_target = vw.ExpandApplicationToInitiatorTarget:main',
            'vw_export_data           = vw.export_data:main',
        ],
    },
    install_requires=[
        "requests>=2.7.0",
        # parse naturally described dates
        "parsedatetime==1.4",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    long_description=get_content("README.md"),
)
