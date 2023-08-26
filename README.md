# Reverse Engineer Machine Readible Curricula for Rheinland Pfalz

# Requirements
- Python3

# Installation
```
pip3 install rdflib
```
# Execution

## Running the Application
```
python3 rheinland_pfalz.py
```
## Outputs
The application creates a rdf file ```rheinland_pfalz.rdf``` and ```rheinland_pfalz.txt``` in the application directory. This rdf file contains the reverse engineered triples derived from rheinland_pfalz.json and the txt file is a tree-like representation of the output.

```rheinland_pfalz.rdf``` and  ```curriculum.rdf``` (which is already in the application directory), can now be loaded into an ontology editor such as Protege for inspection.
