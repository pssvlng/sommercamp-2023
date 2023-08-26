import json
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, SKOS 

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

def write_tree_to_rdf(graph, level, parent_node, node):
    global curriculum_cntr, competence_area_cntr, compentence_cntr

    if (level == 0):
        curriculum_cntr += 1
        curri = URIRef(f"https://edu.yovisto.com/resource/rf/curriculum/{curriculum_cntr}")
        graph.add((curri, RDF.type, SKOS.ConceptScheme))
        graph.add((curri, RDF.type, URIRef("https://w3id.org/dini/dini-ns/Curriculum")))
        graph.add((curri, SKOS.prefLabel, Literal(remove_special_chars(node['title']))))
        graph.add((curri, SKOS.definition, Literal(f"Rahmenlehrplan Rheinland Pfalz: {remove_special_chars(node['title'])}")))
        has_curriculum = URIRef("https://w3id.org/curriculum/hasCurriculum")
        graph.add((parent_node, has_curriculum, curri))    
        graph.add((parent_node, SKOS.narrower, curri))    
        graph.add((curri, SKOS.broader, curri))    
        for child in node.get('children', []):
            write_tree_to_rdf(graph, level + 1, curri, child)
    if (level == 1): 
        for child in node.get('children', []):
            write_tree_to_rdf(graph, level + 1, parent_node, child)
    if (level == 2):
        competence_area_cntr += 1
        competence_area = URIRef(f"https://edu.yovisto.com/resource/rf/competencearea/{competence_area_cntr}")
        graph.add((competence_area, RDF.type, SKOS.Concept))
        graph.add((competence_area, RDF.type, URIRef("https://w3id.org/curriculum/CompetenceArea")))
        graph.add((competence_area, RDF.type, URIRef("https://w3id.org/curriculum/CompetenceItem")))
        graph.add((competence_area, RDF.type, URIRef("https://w3id.org/dini/dini-ns/CurriculumItem")))
        graph.add((competence_area, SKOS.prefLabel, Literal(remove_special_chars(node['title']))))       
        has_competence_area = URIRef("https://w3id.org/curriculum/hasCompetenceArea")
        graph.add((parent_node, has_competence_area, competence_area))
        graph.add((parent_node, SKOS.narrower, competence_area))    
        graph.add((competence_area, SKOS.broader, parent_node))    
        for child in node.get('children', []):
            write_tree_to_rdf(graph, level + 1, competence_area, child)
    if (level == 3):
        compentence_cntr += 1
        competence = URIRef(f"https://edu.yovisto.com/resource/rf/competence/{compentence_cntr}")
        graph.add((competence, RDF.type, SKOS.Concept))
        graph.add((competence, RDF.type, URIRef("https://w3id.org/curriculum/Competence")))
        graph.add((competence, RDF.type, URIRef("https://w3id.org/curriculum/CompetenceItem")))
        graph.add((competence, RDF.type, URIRef("https://w3id.org/dini/dini-ns/CurriculumItem")))
        graph.add((competence, SKOS.prefLabel, Literal(remove_special_chars(node['title']))))       
        has_competence = URIRef("https://w3id.org/curriculum/hasCompetence")
        graph.add((parent_node, has_competence, competence))       
        graph.add((parent_node, SKOS.narrower, competence))    
        graph.add((competence, SKOS.broader, parent_node))     

def main():
    json_filename = 'rheinland_pfalz.json'
    output_file = 'rheinland_pfalz.txt'
    data = read_json_file(json_filename)

    if isinstance(data, list):        
        tree = build_tree(data)
        graph = Graph()
        rf = URIRef("https://edu.yovisto.com/resource/rf/curriculum/RF")
        federal_state = URIRef("https://w3id.org/curriculum/FederalState")
        graph.add((rf, RDF.type, federal_state))
        graph.add((rf, SKOS.prefLabel, Literal('Rheinland Pfalz')))  
        with open(output_file, 'w') as file:
            for root_node in tree.values():
                if root_node.get('parent_id') is None:
                    print_tree_to_file(root_node, 0, file)
                    write_tree_to_rdf(graph, 0, rf, root_node)
        
        output_file = "rheinland_pfalz.rdf"
        graph.serialize(destination=output_file, format="xml")
        print(f"RDF triples added and saved to {output_file}")
    else:
        print("Invalid data format:", data)
    
if __name__ == "__main__":
    global curriculum_cntr, competence_area_cntr, compentence_cntr
    curriculum_cntr = 0
    competence_area_cntr = 0
    compentence_cntr = 0
    main()