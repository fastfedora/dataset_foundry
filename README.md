# Dataset Foundry

A toolkit for building validated datasets.

Dataset Foundry uses the concept of data pipelines to load, generate or validate datasets. A
pipeline is a sequence of actions executed either against the dataset itself or the individual items
in the dataset.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the package:
   ```bash
   pip install -e .
   ```
4. Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Default Settings

- Default Model: gpt-4o-mini
- Default Temperature: 0.7
- Default Number of Samples: 10
- Dataset Directory: ./datasets
- Logs Directory: ./logs

## Project Structure

```
dataset-foundry/
├── src/
│   └── dataset_foundry/
│       ├── actions/       # Actions for processing datasets and items within those datasets
│       ├── cli/           # Command-line interface tools
│       ├── core/          # Core functionality
│       └── utils/         # Utility functions
├── datasets/              # Generated datasets
├── examples/              # Example pipelines
│   └── refactorable_code/ # Example pipelines to build a dataset of code requiring refactoring
└── logs/                  # Operation logs
```

## Running Pipelines

Pipelines can be run from the command line using the `dataset-foundry` command.

```bash
dataset-foundry <pipeline_module> <dataset_name>
```

For example, to run the `generate_spec` pipeline to create specs for a dataset saved to
`datasets/dataset1`, you would use:

```bash
dataset-foundry examples/refactorable_code/generate_spec/pipeline.py dataset1
```

Use `dataset-foundry --help` to see available arguments.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.