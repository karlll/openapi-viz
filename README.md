# OpenAPI Visualization Tool

A tool for visualizing OpenAPI schemas as interactive graphs.

## Features

- Visualizes OpenAPI schemas as interactive graphs
- Supports different types of schema components:
  - Simple types (string, integer, boolean, etc.)
  - Array types
  - Object types with properties
  - Reference types
  - AnyOf types (multiple possible types)
- Generates SVG output for easy embedding in documentation

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/openapi-viz.git
   cd openapi-viz
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. For development, install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

```bash
python openapi-viz.py
```

By default, the tool will look for a file named `bundled.yaml` in the current directory and generate an SVG file named `api_graph.svg`.

You can modify the input and output paths in the script:

```python
if __name__ == "__main__":
    generator = OpenAPIGraphGenerator('./path/to/your/openapi.yaml')
    graph = generator.generate_graph()
    generator.save('output_filename')
    print(f"Graph saved to output_filename.svg")
```

## Testing

Run the tests with pytest:

```bash
pytest
```

For test coverage report:

```bash
pytest --cov=.
```

## How It Works

The tool processes the OpenAPI schema and creates a graph representation:

1. Each schema component becomes a node in the graph
2. References between components become edges in the graph
3. Different types of components are visualized differently:
   - Simple types: Show the type name and type
   - Array types: Show the type name and array item type, with an edge to the item type
   - Object types: Show the type name and properties as a table, with edges to referenced types
   - Reference types: Show the type name and a reference edge to the target type
   - AnyOf types: Show the type name and all possible types, with edges to each type

## License

[MIT](LICENSE)