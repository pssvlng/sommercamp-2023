import json

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
    output_file.write('  ' * level + node['title'] + '\n')    
    for child in node.get('children', []):
        print_tree_to_file(child, level + 1, output_file)

def write_tree_to_rdf(node, level=0):
    pass

def main():
    json_filename = 'rf.json'
    output_file = 'rf.txt'
    data = read_json_file(json_filename)

    if isinstance(data, list):        
        tree = build_tree(data)
        with open(output_file, 'w') as file:
            for root_node in tree.values():
                if root_node.get('parent_id') is None:
                    print_tree_to_file(root_node, 0, file)
                    #write_tree_to_rdf(root_node, 0)
    else:
        print("Invalid data format:", data)

if __name__ == "__main__":
    main()