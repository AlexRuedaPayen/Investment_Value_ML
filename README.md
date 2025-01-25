# Investment Value ML

This project aims at uncovering reliable financial metrics that decompose a financial product between different degree of value, from Fundamental Investment Value to Speculative Value.

## Description

<TBD>

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Installation

Follow these steps to set up the project on your local machine:

1. Clone the repository:

    ```bash
    git clone https://github.com/AlexRuedaPayen/Investment_Value_ML.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Investment_Value_ML
    ```

3. Create and activate a virtual environment:

    ```bash
    python3.10 -m venv venv
    venv/Scripts/pip install -r requirements.txt #Linus/MacOS
    venv\Scripts\pip install -r requirements.txt
    ```

## Usage

Here are some examples of how to use the project once it's installed:

### Example 1: Running the main script

To start the project:

    ```bash
    venv/Scripts/python main.py
    ```

### Example 2: Using the Google Drive Handler in Python

    ```bash
    from google_drive_handler import GoogleDriveHandler

    handler = GoogleDriveHandler()
    handler.authenticate()
    handler.upload_file("path/to/your/file")
    ```

### Tests
To run tests for the project, use pytest:

    ```bash
    pytest
    ```

You can also specify a particular test file or test case to run:
    
    ```bash
    pytest tests/test_google_drive_handler.py
    ```

## Contributing

We welcome contributions! Please follow these steps to contribute:
Fork the repository.
Create a new branch for your feature or fix:

    ```bash
    git checkout -b feature/your-feature
    ```

Make your changes and commit them:

    ```bash
    git commit -m "Add new feature"
    ```

Push to your fork:

    ```bash
    git push origin feature/your-feature
    ```

Create a pull request to merge your changes into the main branch.
Ensure that all tests pass before submitting the PR.
Please follow any code style guidelines and ensure your changes are well-documented.

## License

This project is not licensed yet, but some special R&D libraries developped will be kept secret until the intellectual property issue solved - see the LICENSE file for details.

## Acknowledgments

Thanks to all people that took time developping open-source libraries that I used here.


### Notes:
- **Project Title**: <TBD>
- **Description**: <TBD>
- **Installation Steps**: <TBD>
- **License**: <TBD>
- **Acknowledgments**: <TBD>