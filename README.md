# OpenAPI Visualization Tool

A tool for visualizing OpenAPI schemas as graphs.

## Example
![Example based on the OpenAPI Pet store schema](https://raw.githubusercontent.com/karlll/openapi-viz/main/sample.png)

Based on [Swagger Petstore example](https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml)
## Features

- Visualizes OpenAPI schemas as graphs
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
   git clone https://github.com/karlll/openapi-viz.git
   cd openapi-viz
   ```

2. Install dependencies:
   ```bash
   uv install -e .
   ```

3. For development, install development dependencies:
   ```bash
   uv install -e ".[dev]"
   ```

## Usage

Basic usage:

```bash
python openapi-viz.py /path/to/your/openapi.yaml
```

This will generate a graph visualization of the OpenAPI schema and save it as `api_graph.svg`.

Specify a custom output filename:

```bash
python openapi-viz.py /path/to/your/openapi.yaml -o custom_output
```

This will save the graph as `custom_output.svg`.

### Command Line Options

```
usage: openapi-viz.py [-h] [-o OUTPUT] input_file

Generate a graph visualization of an OpenAPI schema.

positional arguments:
  input_file            Path to the OpenAPI schema file (YAML or JSON)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file name (without extension, default: api_graph)
```

### Programmatic Usage

You can also use the `OpenAPIGraphGenerator` class directly in your Python code:

```python
# If you have the script in your project
from openapi_viz import OpenAPIGraphGenerator

# Or import it from a file path
import importlib.util
spec = importlib.util.spec_from_file_location("openapi_viz", "/path/to/openapi-viz.py")
openapi_viz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openapi_viz)
OpenAPIGraphGenerator = openapi_viz.OpenAPIGraphGenerator

# Then use it
generator = OpenAPIGraphGenerator('/path/to/your/openapi.yaml')
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
## License

[MIT](LICENSE)
