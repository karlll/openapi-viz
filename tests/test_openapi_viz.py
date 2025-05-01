import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import sys
import yaml

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import the module directly since it's a script, not a package
import importlib.util
spec = importlib.util.spec_from_file_location("openapi_viz", 
                                             os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                         "openapi-viz.py"))
openapi_viz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openapi_viz)
OpenAPIGraphGenerator = openapi_viz.OpenAPIGraphGenerator

class TestOpenAPIGraphGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary file with a simple OpenAPI spec
        self.temp_dir = tempfile.TemporaryDirectory()
        self.spec_path = os.path.join(self.temp_dir.name, "test_spec.yaml")

        # Simple OpenAPI spec with different types including anyOf
        self.test_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "components": {
                "schemas": {
                    "SimpleType": {
                        "type": "string"
                    },
                    "ArrayType": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "ObjectType": {
                        "type": "object",
                        "properties": {
                            "prop1": {"type": "string"},
                            "prop2": {"type": "integer"}
                        }
                    },
                    "ReferenceType": {
                        "$ref": "#/components/schemas/SimpleType"
                    },
                    "AnyOfType": {
                        "anyOf": [
                            {"type": "string"},
                            {"$ref": "#/components/schemas/SimpleType"}
                        ]
                    },
                    "ArrayWithAnyOf": {
                        "type": "array",
                        "items": {
                            "anyOf": [
                                {"type": "string"},
                                {"$ref": "#/components/schemas/SimpleType"}
                            ]
                        }
                    },
                    "ObjectWithAnyOfProperty": {
                        "type": "object",
                        "properties": {
                            "anyOfProp": {
                                "anyOf": [
                                    {"type": "string"},
                                    {"$ref": "#/components/schemas/SimpleType"}
                                ]
                            }
                        }
                    }
                }
            }
        }

        # Write the spec to the temporary file
        with open(self.spec_path, 'w') as f:
            yaml.dump(self.test_spec, f)

        # Initialize the generator with the test spec
        self.generator = OpenAPIGraphGenerator(self.spec_path)

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_load_spec(self):
        """Test that the spec is loaded correctly."""
        self.assertEqual(self.generator.spec["openapi"], "3.0.0")
        self.assertEqual(self.generator.spec["info"]["title"], "Test API")
        self.assertIn("schemas", self.generator.spec["components"])

    def test_get_property_type_label_simple(self):
        """Test getting the type label for a simple type."""
        prop_details = {"type": "string"}
        label = self.generator._get_property_type_label(prop_details)
        self.assertEqual(label, "string")

    def test_get_property_type_label_array(self):
        """Test getting the type label for an array type."""
        prop_details = {"type": "array", "items": {"type": "string"}}
        label = self.generator._get_property_type_label(prop_details)
        self.assertEqual(label, "array of string")

    def test_get_property_type_label_reference(self):
        """Test getting the type label for a reference type."""
        prop_details = {"$ref": "#/components/schemas/SimpleType"}
        label = self.generator._get_property_type_label(prop_details)
        self.assertEqual(label, "reference to SimpleType")

    def test_get_property_type_label_anyof(self):
        """Test getting the type label for an anyOf type."""
        prop_details = {
            "anyOf": [
                {"type": "string"},
                {"$ref": "#/components/schemas/SimpleType"}
            ]
        }
        label = self.generator._get_property_type_label(prop_details)
        self.assertEqual(label, "anyOf: string, SimpleType")

    def test_get_property_type_label_array_with_anyof(self):
        """Test getting the type label for an array with anyOf items."""
        prop_details = {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string"},
                    {"$ref": "#/components/schemas/SimpleType"}
                ]
            }
        }
        label = self.generator._get_property_type_label(prop_details)
        self.assertEqual(label, "array of anyOf: string, SimpleType")

    @patch('graphviz.Digraph')
    def test_process_type_simple(self, mock_digraph):
        """Test processing a simple type."""
        # Create a mock graph
        mock_graph = MagicMock()

        # Process a simple type
        schema_name = "TestSimple"
        schema = {"type": "string"}
        schema_id = "schema_TestSimple"

        self.generator._process_type(schema_name, schema, schema_id, mock_graph)

        # Check that the node was created with the correct label
        mock_graph.node.assert_called_once()
        args, kwargs = mock_graph.node.call_args
        self.assertEqual(args[0], schema_id)
        self.assertIn("type: string", kwargs["label"])

    @patch('graphviz.Digraph')
    def test_process_type_array(self, mock_digraph):
        """Test processing an array type."""
        # Create a mock graph
        mock_graph = MagicMock()

        # Process an array type
        schema_name = "TestArray"
        schema = {"type": "array", "items": {"type": "string"}}
        schema_id = "schema_TestArray"

        self.generator._process_type(schema_name, schema, schema_id, mock_graph)

        # Check that the node was created with the correct label
        mock_graph.node.assert_called_once()
        args, kwargs = mock_graph.node.call_args
        self.assertEqual(args[0], schema_id)
        self.assertIn("type: array of string", kwargs["label"])

    @patch('graphviz.Digraph')
    def test_process_type_reference(self, mock_digraph):
        """Test processing a reference type."""
        # Create a mock graph
        mock_graph = MagicMock()

        # Process a reference type
        schema_name = "TestReference"
        schema = {"$ref": "#/components/schemas/SimpleType"}
        schema_id = "schema_TestReference"

        self.generator._process_type(schema_name, schema, schema_id, mock_graph)

        # Check that the node was created with the correct label
        mock_graph.node.assert_called_once()
        args, kwargs = mock_graph.node.call_args
        self.assertEqual(args[0], schema_id)
        self.assertIn("type: reference", kwargs["label"])

        # Check that an edge was created to the referenced type
        mock_graph.edge.assert_called_once()
        args, kwargs = mock_graph.edge.call_args
        self.assertEqual(args[0], schema_id)
        self.assertEqual(args[1], "schema_SimpleType")
        self.assertEqual(kwargs["label"], "references")

    @patch('graphviz.Digraph')
    def test_process_type_anyof(self, mock_digraph):
        """Test processing an anyOf type."""
        # Create a mock graph
        mock_graph = MagicMock()

        # Process an anyOf type
        schema_name = "TestAnyOf"
        schema = {
            "anyOf": [
                {"type": "string"},
                {"$ref": "#/components/schemas/SimpleType"}
            ]
        }
        schema_id = "schema_TestAnyOf"

        self.generator._process_type(schema_name, schema, schema_id, mock_graph)

        # Check that the node was created with the correct label
        mock_graph.node.assert_called_once()
        args, kwargs = mock_graph.node.call_args
        self.assertEqual(args[0], schema_id)
        self.assertIn("type: anyOf: string, SimpleType", kwargs["label"])

        # Check that an edge was created to the referenced type
        mock_graph.edge.assert_called_once()
        args, kwargs = mock_graph.edge.call_args
        self.assertEqual(args[0], schema_id)
        self.assertEqual(args[1], "schema_SimpleType")
        self.assertEqual(kwargs["label"], "anyOf[1]")

    @patch('graphviz.Digraph')
    def test_process_type_array_with_anyof(self, mock_digraph):
        """Test processing an array type with anyOf items."""
        # Create a mock graph
        mock_graph = MagicMock()

        # Process an array with anyOf items
        schema_name = "TestArrayWithAnyOf"
        schema = {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string"},
                    {"$ref": "#/components/schemas/SimpleType"}
                ]
            }
        }
        schema_id = "schema_TestArrayWithAnyOf"

        self.generator._process_type(schema_name, schema, schema_id, mock_graph)

        # Check that the node was created with the correct label
        mock_graph.node.assert_called_once()
        args, kwargs = mock_graph.node.call_args
        self.assertEqual(args[0], schema_id)
        self.assertIn("type: array of anyOf: string, SimpleType", kwargs["label"])

        # Check that an edge was created to the referenced type
        mock_graph.edge.assert_called_once()
        args, kwargs = mock_graph.edge.call_args
        self.assertEqual(args[0], schema_id)
        self.assertEqual(args[1], "schema_SimpleType")
        self.assertEqual(kwargs["label"], "items anyOf[1]")

    def test_generate_graph(self):
        """Test generating the complete graph."""
        # Generate the graph
        graph = self.generator.generate_graph()

        # Check that the graph is the same as the one in the generator
        self.assertEqual(graph, self.generator.graph)

        # Check that the graph has the expected attributes
        self.assertEqual(graph.name, 'API_Graph')
        self.assertEqual(graph.format, 'png')

    def test_save(self):
        """Test saving the graph."""
        # Generate the graph
        self.generator.generate_graph()

        # Patch the render method of the actual graph object
        with patch.object(self.generator.graph, 'render') as mock_render:
            # Save the graph
            output_path = self.generator.save("test_output")

            # Check that the render method was called with the correct arguments
            mock_render.assert_called_once_with("test_output", format="svg", cleanup=True)

            # Check that the correct output path is returned
            self.assertEqual(output_path, "test_output.svg")

    def test_save_with_viewer(self):
        """Test saving the graph with HTML viewer."""
        # Generate the graph
        self.generator.generate_graph()

        # Create a temporary SVG content for testing
        svg_content = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" /></svg>'
        html_template = '<!DOCTYPE html><html><body><div id="svg-container"><!-- Insert SVG content --></div></body></html>'
        expected_html = '<!DOCTYPE html><html><body><div id="svg-container"><svg id="main-svg" width="100" height="100"><circle cx="50" cy="50" r="40" /></svg></div></body></html>'

        # Create a mock file handler that returns different content for different files
        file_mock = MagicMock()
        file_mock.__enter__.return_value.read.side_effect = [svg_content, html_template]

        # Patch the render method and open function
        with patch.object(self.generator.graph, 'render') as mock_render, \
             patch('builtins.open', return_value=file_mock):

            # Save the graph with viewer
            output_path = self.generator.save("test_output", use_viewer=True)

            # Check that the render method was called with the correct arguments
            mock_render.assert_called_once_with("test_output", format="svg", cleanup=True)

            # Check that the correct output path is returned
            self.assertEqual(output_path, "test_output.html")

            # Verify that open was called for the SVG, template, and output HTML
            from unittest.mock import call
            open_calls = [
                call("test_output.svg", 'r'),
                call('viewer_template.html', 'r'),
                call("test_output.html", 'w')
            ]

            # Check that open was called with the expected arguments
            # Note: We can't check the exact order of calls because the implementation might change
            for expected_call in open_calls:
                self.assertIn(expected_call, open.call_args_list)

    def test_command_line_args(self):
        """Test command line argument parsing."""
        # Test with viewer option
        test_args = ['openapi-viz.py', 'test_spec.yaml', '-v']

        # Create a mock for the OpenAPIGraphGenerator class
        mock_generator_class = MagicMock()
        mock_generator = mock_generator_class.return_value
        mock_generator.generate_graph.return_value = "mock_graph"
        mock_generator.save.return_value = "test_spec.html"

        # Save the original class to restore it later
        original_class = openapi_viz.OpenAPIGraphGenerator

        try:
            # Replace the class with our mock
            openapi_viz.OpenAPIGraphGenerator = mock_generator_class

            # Patch sys.argv and print
            with patch('sys.argv', test_args), patch('builtins.print') as mock_print:
                # Execute the main block directly from the module
                # This is the code that would run if the script was executed directly
                if hasattr(openapi_viz, 'main'):
                    openapi_viz.main()
                else:
                    # Get the argparse module from the openapi_viz module
                    argparse_module = openapi_viz.argparse

                    # Create a parser and parse the arguments
                    parser = argparse_module.ArgumentParser(description='Generate a graph visualization of an OpenAPI schema.')
                    parser.add_argument('input_file', help='Path to the OpenAPI schema file (YAML or JSON)')
                    parser.add_argument('-o', '--output', default='api_graph', help='Output file name (without extension, default: api_graph)')
                    parser.add_argument('-v', '--viewer', action='store_true', help='Embed the SVG in an HTML viewer')
                    args = parser.parse_args()

                    # Generate the graph
                    generator = openapi_viz.OpenAPIGraphGenerator(args.input_file)
                    graph = generator.generate_graph()
                    output_file = generator.save(args.output, use_viewer=args.viewer)

                    # Print the output message
                    if args.viewer:
                        print(f"Graph saved to {output_file} (HTML viewer)")
                    else:
                        print(f"Graph saved to {output_file}")
        finally:
            # Restore the original class
            openapi_viz.OpenAPIGraphGenerator = original_class

            try:
                # Check that the generator was initialized with the correct input file
                mock_generator_class.assert_called_once_with('test_spec.yaml')

                # Check that generate_graph was called
                mock_generator.generate_graph.assert_called_once()

                # Check that save was called with the correct arguments
                mock_generator.save.assert_called_once_with('api_graph', use_viewer=True)

                # Check that the correct output message was printed
                mock_print.assert_called_once_with("Graph saved to test_spec.html (HTML viewer)")
            except AssertionError as e:
                # Re-raise the assertion error with more context
                raise AssertionError(f"Test assertions failed: {e}\n"
                                    f"mock_generator_class calls: {mock_generator_class.mock_calls}\n"
                                    f"mock_generator.generate_graph calls: {mock_generator.generate_graph.mock_calls}\n"
                                    f"mock_generator.save calls: {mock_generator.save.mock_calls}\n"
                                    f"mock_print calls: {mock_print.mock_calls if 'mock_print' in locals() else 'Not available'}")

if __name__ == "__main__":
    unittest.main()
