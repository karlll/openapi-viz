
import json
import yaml
from graphviz import Digraph

class OpenAPIGraphGenerator:
    def __init__(self, spec_path):
        self.spec_path = spec_path
        self.spec = self._load_spec()
        self.graph = Digraph('API_Graph', format='png')
        self.graph.attr(rankdir='LR', size='8,5', fontname='Helvetica')
        self.graph.attr('node', shape='box', style='filled', fillcolor='lightblue', fontname='Helvetica')
        self.processed_refs = set()  # Track processed references to avoid duplicates

    def _load_spec(self):
        """Load the OpenAPI specification from a file."""
        with open(self.spec_path, 'r') as f:
            if self.spec_path.endswith('.yaml') or self.spec_path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def generate_graph(self):
        """Generate the GraphViz representation of the API."""
        self._add_info_node()
        self._add_paths()
        self._add_schemas()
        self._add_relationships()
        return self.graph

    def _add_info_node(self):
        pass

    def _add_paths(self):
        pass

    def _add_schemas(self):
        """Add component schemas."""
        components = self.spec.get('components', {})
        schemas = components.get('schemas', {})

        if not schemas:
            return

        # Create schemas subgraph
        with self.graph.subgraph(name='cluster_schemas') as schemas_graph:
            schemas_graph.attr(label='Schemas', style='filled', fillcolor='lightcyan')

            for schema_name, schema in schemas.items():
                schema_id = f"schema_{schema_name}"

                # Process the schema type and create the node
                self._process_type(schema_name, schema, schema_id, schemas_graph)

    def _properties_as_html_table(self, schema_name, properties, parent_id, graph):
        """Convert properties to an HTML table format with links to referenced types."""
        if not properties:
            return "<TABLE><TR><TD>No properties</TD></TR></TABLE>"

        table = "<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>"
        table += f"<TR><TD COLSPAN='2'><B>{schema_name}</B></TD></TR>"
        table += "<TR><TD><B>Property</B></TD><TD><B>Type</B></TD></TR>"

        for prop_name, prop_details in properties.items():
            prop_type = self._get_property_type_label(prop_details)
            table += f"<TR><TD>{prop_name}</TD><TD>{prop_type}</TD></TR>"

            # Create edges for array and object properties
            if '$ref' in prop_details:
                ref_type = prop_details['$ref'].split('/')[-1]
                ref_id = f"schema_{ref_type}"
                graph.edge(parent_id, ref_id, label=prop_name)
            elif prop_details.get('type') == 'array' and 'items' in prop_details:
                if '$ref' in prop_details['items']:
                    ref_type = prop_details['items']['$ref'].split('/')[-1]
                    ref_id = f"schema_{ref_type}"
                    graph.edge(parent_id, ref_id, label=f"{prop_name} (array)")
                elif 'type' in prop_details['items'] and prop_details['items']['type'] == 'object':
                    # Handle inline object definitions in array items
                    if 'properties' in prop_details['items']:
                        nested_id = f"{parent_id}_{prop_name}_items"
                        nested_props = prop_details['items']['properties']
                        self._process_type(f"{prop_name} items",
                                           {'type': 'object', 'properties': nested_props},
                                           nested_id, graph)
                        graph.edge(parent_id, nested_id, label=f"{prop_name} (array)")
            elif prop_details.get('type') == 'object' and 'properties' in prop_details:
                # Handle inline object definitions
                nested_id = f"{parent_id}_{prop_name}"
                self._process_type(f"{prop_name}",
                                   {'type': 'object', 'properties': prop_details['properties']},
                                   nested_id, graph)
                graph.edge(parent_id, nested_id, label=prop_name)

        table += "</TABLE>"
        return table

    def _get_property_type_label(self, prop_details):
        """Get a human-readable label for a property type."""
        if '$ref' in prop_details:
            ref_type = prop_details['$ref'].split('/')[-1]
            return f"reference to {ref_type}"
        elif 'type' in prop_details:
            prop_type = prop_details['type']
            if prop_type == 'array':
                if 'items' in prop_details:
                    if '$ref' in prop_details['items']:
                        item_type = prop_details['items']['$ref'].split('/')[-1]
                        return f"array of {item_type}"
                    elif 'type' in prop_details['items']:
                        return f"array of {prop_details['items']['type']}"
                return "array"
            return prop_type
        return "unknown"

    def _process_type(self, schema_name, schema, schema_id, graph):
        """Process a schema type and create the appropriate node and edges."""
        # Skip if we've already processed this schema
        if schema_id in self.processed_refs:
            return

        # Mark as processed
        self.processed_refs.add(schema_id)

        # Handle reference type
        if '$ref' in schema:
            ref_type = schema['$ref'].split('/')[-1]
            ref_id = f"schema_{ref_type}"
            label = f"<{schema_name}<BR/><FONT POINT-SIZE='10'>type: reference</FONT>>"
            graph.node(schema_id, label=label)
            graph.edge(schema_id, ref_id, label="references")
            return

        # Handle different schema types
        schema_type = schema.get('type', 'object')  # Default to object if type not specified

        if schema_type == 'object':
            properties = schema.get('properties', {})
            prop_table = self._properties_as_html_table(schema_name, properties, schema_id, graph)
            label = f"<{prop_table}>"
            graph.node(schema_id, label=label)

            # Process additional properties if they are objects or references
            if 'additionalProperties' in schema and isinstance(schema['additionalProperties'], dict):
                add_props = schema['additionalProperties']
                if '$ref' in add_props:
                    ref_type = add_props['$ref'].split('/')[-1]
                    ref_id = f"schema_{ref_type}"
                    graph.edge(schema_id, ref_id, label="additionalProperties")
                elif add_props.get('type') == 'object' and 'properties' in add_props:
                    add_props_id = f"{schema_id}_additionalProps"
                    self._process_type("additionalProperties", add_props, add_props_id, graph)
                    graph.edge(schema_id, add_props_id, label="additionalProperties")

        elif schema_type == 'array':
            if 'items' in schema:
                items = schema['items']
                if '$ref' in items:
                    ref_type = items['$ref'].split('/')[-1]
                    ref_id = f"schema_{ref_type}"
                    label = f"<{schema_name}<BR/><FONT POINT-SIZE='10'>type: array of {ref_type}</FONT>>"
                    graph.node(schema_id, label=label)
                    graph.edge(schema_id, ref_id, label="items")
                elif 'type' in items:
                    item_type = items['type']
                    label = f"<{schema_name}<BR/><FONT POINT-SIZE='10'>type: array of {item_type}</FONT>>"
                    graph.node(schema_id, label=label)

                    # If array items are objects with properties, process them
                    if item_type == 'object' and 'properties' in items:
                        items_id = f"{schema_id}_items"
                        self._process_type(f"{schema_name} items",
                                           {'type': 'object', 'properties': items['properties']},
                                           items_id, graph)
                        graph.edge(schema_id, items_id, label="items")
                else:
                    label = f"<{schema_name}<BR/><FONT POINT-SIZE='10'>type: array</FONT>>"
                    graph.node(schema_id, label=label)
            else:
                label = f"<{schema_name}<BR/><FONT POINT-SIZE='10'>type: array</FONT>>"
                graph.node(schema_id, label=label)
        else:
            # Simple type
            label = f"<{schema_name}<BR/><FONT POINT-SIZE='10'>type: {schema_type}</FONT>>"
            graph.node(schema_id, label=label)

            # Handle enum values for simple types
            if 'enum' in schema:
                enum_values = schema['enum']
                if len(enum_values) <= 5:  # Only show if not too many values
                    enum_str = ", ".join(str(v) for v in enum_values[:5])
                    if len(enum_values) > 5:
                        enum_str += "..."
                    label = f"<{schema_name}<BR/><FONT POINT-SIZE='10'>type: {schema_type}<BR/>enum: {enum_str}</FONT>>"
                    graph.node(schema_id, label=label, _attributes={'tooltip': str(enum_values)})

    def _add_relationships(self):
        pass

    def save(self, output_path):
        """Save the graph to a file."""
        self.graph.render(output_path, format="svg", cleanup=True)


# Example usage
if __name__ == "__main__":
    generator = OpenAPIGraphGenerator('./bundled.yaml')
    graph = generator.generate_graph()
    generator.save('api_graph')
    print(f"Graph saved to api_graph.svg")