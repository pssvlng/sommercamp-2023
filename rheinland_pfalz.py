import json
from rdflib import XSD, Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, SKOS, RDFS
import uuid

RESOURCE_NS = Namespace("https://edu.yovisto.com/resource/lp/rp/")
GRAPH_NS = Namespace("https://edu.yovisto.com/graph/lp/rp/")
ONTOLOGY_NS = Namespace("https://w3id.org/lehrplan/ontology/")

def read_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def build_tree(data):    
    tree = {}
    for inner_list in data:
        for item in inner_list:
            item_id = item['id']
            parent_id = item.get('parent_id', None)
            
            if item_id not in tree:
                tree[item_id] = item
                tree[item_id]['children'] = []
                
            if parent_id is not None:
                parent = tree.get(parent_id, {})
                parent.setdefault('children', []).append(tree[item_id])
                tree[parent_id] = parent

    return tree

def print_tree_to_file(node, level=0, output_file=None):
    output_file.write('  ' * level + remove_special_chars(node['title']) + '\n')    
    for child in node.get('children', []):
        print_tree_to_file(child, level + 1, output_file)

def remove_special_chars(input: str):
    chars = [('⭐', ''), ('...', ''), ('&gt;', '>'), ('*', ''), ('', ' ')]
    for char, replace in chars:
        input = input.replace(char, replace)

    return input.strip()    

def write_tree_to_rdf(graph, level, parent_node, node, graph_uri=None, index=0):    
    if (level == 0):        
        guid = uuid.uuid1()
        curri = URIRef(RESOURCE_NS[f'{guid}'])
        local_graph_uri = URIRef(GRAPH_NS[f'{guid}'])        
        graph.add((curri, RDFS.isDefinedBy, local_graph_uri))        
        graph.add((curri, RDF.type, ONTOLOGY_NS.LP_00000433))        
        graph.add((curri, RDFS.label, Literal(remove_special_chars(node['title']))))
        graph.add((curri, RDFS.comment, Literal(f"Rahmenlehrplan Rheinland Pfalz: {remove_special_chars(node['title'])}")))        
        graph.add((curri, ONTOLOGY_NS.LP_00000029, parent_node))            
        for local_index, child in enumerate(node.get('children', [])):
            write_tree_to_rdf(graph, level + 1, curri, child, graph_uri=local_graph_uri, index=local_index)
    if (level == 1): 
        for local_index, child in enumerate(node.get('children', [])):
            write_tree_to_rdf(graph, level + 1, parent_node, child, graph_uri=graph_uri, index=local_index)
    if (level == 2):        
        competence_area = URIRef(RESOURCE_NS[f'{uuid.uuid1()}'])             
        graph.add((competence_area, RDF.type, ONTOLOGY_NS.LP_00000431))        
        graph.add((competence_area, RDFS.label, Literal(remove_special_chars(node['title']))))               
        graph.add((competence_area, RDFS.isDefinedBy, graph_uri))                           
        graph.add((parent_node, ONTOLOGY_NS.LP_00000008, competence_area))        
        graph.add((competence_area, ONTOLOGY_NS.LP_00000460, Literal(index + 1, datatype=XSD.int)))                        
        for local_index, child in enumerate(node.get('children', [])):
            write_tree_to_rdf(graph, level + 1, competence_area, child, graph_uri=graph_uri, index=local_index)
    if (level == 3):        
        competence = URIRef(RESOURCE_NS[f'{uuid.uuid1()}'])
        graph.add((competence, RDF.type, ONTOLOGY_NS.LP_00000432))        
        graph.add((competence, RDFS.label, Literal(remove_special_chars(node['title']))))       
        graph.add((competence, RDFS.isDefinedBy, graph_uri))                           
        graph.add((parent_node, ONTOLOGY_NS.LP_00000008, competence))               
        graph.add((competence, ONTOLOGY_NS.LP_00000460, Literal(index + 1, datatype=XSD.int)))                                

def main():
    json_filename = 'rheinland_pfalz.json'
    output_file = 'rheinland_pfalz.txt'
    data = read_json_file(json_filename)

    if isinstance(data, list):        
        tree = build_tree(data)
        graph = Graph()
        
        rp = ONTOLOGY_NS.LP_30000046
        with open(output_file, 'w') as file:
            for root_node in tree.values():
                if root_node.get('parent_id') is None:
                    print_tree_to_file(root_node, 0, file)
                    write_tree_to_rdf(graph, 0, rp, root_node)
        
        output_file = "rheinland_pfalz.ttl"
        graph.serialize(destination=output_file, format="ttl")
        print(f"Triples added and saved to {output_file}")
    else:
        print("Invalid data format:", data)
    
if __name__ == "__main__":
    global curriculum_cntr, competence_area_cntr, compentence_cntr
    curriculum_cntr = 0
    competence_area_cntr = 0
    compentence_cntr = 0
    main()