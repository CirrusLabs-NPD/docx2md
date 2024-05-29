# DOCX to Markdown Converter

This project provides a utility to convert `.docx` files to Markdown format and a Streamlit application to facilitate the conversion process.

## Prerequisites

- Python 3.6 or later
- pip (Python package installer)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/docx-to-md-converter.git
cd docx-to-md-converter
```

### 2. Set Up Virtual Environment
Create a virtual environment to manage dependencies.

```bash 
python -m venv venv
```

### 3. Activate the virtual environment:
On Windows:
```bash
venv\Scripts\activate
```
On macOS and Linux:
```
source venv/bin/activate
```

### 4. Install Required Packages
Install the necessary Python packages using pip:

```bash
pip install python-docx markdown streamlit

```

### 5. Directory Structure
Ensure your directory structure looks like this:
```bash
docx-to-md-converter/
│
├── images/
│
├── app.py
│
└── utils.py

```
### 6. Run the Streamlit App
Start the Streamlit app:

```bash
 python -m streamlit run app.py

```

### 7. Using the App
- Open the provided URL in your browser (usually http://localhost:8501).

- Upload a .docx file using the file uploader.
View the converted Markdown content and download the Markdown file.
- View any extracted images from the .docx file.
### 8. Project Files:
- app.py: Contains the Streamlit app code.
- utils.py: Contains utility functions for converting .docx to Markdown and reading Markdown files.
