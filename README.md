<p align="center">
  <img src="docs/images/pdf_xml_comparator.png"
       alt="PDF / XML Comparator — local comparison highlighting data differences between PDF and XML files"
       width="600">
</p>

> 🇬🇧 English | [🇫🇷 Français](./README_FR.md)

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgreen.svg)
![Offline First](https://img.shields.io/badge/Mode-Offline%20First-0095b1?style=flat)
[![YouTube](https://img.shields.io/badge/YouTube-@Palks__Studio-FF0000?style=flat&logo=youtube&logoColor=white)](https://www.youtube.com/@Palks_Studio)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-@Palks__Studio-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/palks-studio/)

<p align="center">
  <a href="https://palks-studio.com">
    <img src="https://img.shields.io/badge/Palks%20Studio-Website-0095b1?style=for-the-badge" />
  </a>
</p>

# PDF / XML Comparator

A local, open-source tool for comparing data contained in a PDF file and an XML file.

The goal is simple: quickly identify values that are present in one representation but cannot be found in the other, making human review easier.

The program runs entirely locally, with no API, no external service, and no artificial intelligence.

---

## Project structure

```
pdf_xml_comparator/
│
├── main.py                        → Main application
├── requirements.txt               → Python project dependencies
├── LICENSE.md                     → MIT License
│
├── README.md                      → English documentation
├── README_FR.md                   → French documentation
│
└── docs/
    └── images/
        ├── Palks_Studio.png       → Palks Studio logo
        └── pdf_xml_comparator.png → Comparator presentation image
```

---

## Why this tool?

A PDF and an XML file can represent the same document while containing different information.

A reference may be different, an amount may have been changed, a value may exist only in the XML, or information visible in the PDF may not be found in the XML.

Manually checking both files can quickly become time-consuming.

PDF / XML Comparator automates a first comparison step by identifying potential differences between the two representations.

---

## How it works

The program compares the files in both directions:

### PDF to XML

Values detected in the PDF are searched for in the XML.

If a value from the PDF cannot be found in the XML, it is flagged for review.

### XML to PDF

Values contained in the XML are searched for in the PDF text.

If an XML value cannot be found in the PDF, it is also flagged for review.

This bidirectional comparison can notably identify situations where a correct value exists somewhere in both files, while another different value appears only in one of the representations.

---

## Normalization

Some formatting differences are automatically taken into account to reduce false differences.

For example:

- `1000.00` and `1 000,00`  
- `20260724` and `24/07/2026`  
- spaces and non-breaking spaces  
- some equivalent numeric representations

Normalization is intentionally kept lightweight and does not attempt to interpret the business meaning of the data.

---

## Report

After the comparison, the program displays two sections:

```text
PDF VALUES NOT FOUND IN XML
```

et :

```text
XML VALUES NOT FOUND IN PDF
```

Identical values reported multiple times on the XML side are deduplicated to make the report easier to read.

The interface also keeps a view of the content extracted from both files: the text detected in the PDF, the data extracted from the XML, and the report of the identified differences.

These three sections allow an initial comparison to be performed directly within the application, without constantly switching between the two files.

For a more detailed review, the original PDF and XML files remain the reference and can of course be opened and examined directly.

---

## Important

A flagged value is not necessarily an error.

The XML may contain technical codes, identifiers, or other information that is not intended to appear textually in the PDF.

Likewise, some information visible in the PDF may be represented differently in the XML.

The program therefore does not determine whether a difference is correct or incorrect.

It simply highlights elements that require human review.

---

## What this tool does not do

PDF / XML Comparator is not a compliance validator.

It does not check:

- compliance with an invoicing standard  
- XSD schemas  
- Schematron rules  
- PDF/A compliance  
- the legal or accounting validity of a document  
- the business consistency of a specific field

It does not replace a specialized validation tool.

Its sole purpose is to make data comparison between a PDF and an XML file easier.

---

## Generic approach

The comparator is intentionally not built around a predefined list of business fields.

It does not assume that a particular XML tag represents an amount, an invoice number, a quantity, or any other specific type of data.

This approach keeps the tool simple and generic, without tying the comparison engine to a specific XML structure.

---

## Usage

### 1. Install Python

Python 3 is required to run the program.

### 2. Install the dependency

```
pip install pypdf
```

### 3. Run the program

```
python main.py
```

### 4. Select the files

In the interface:

1. select the PDF file  
2. select the XML file  
3. click `COMPARE PDF / XML`  
4. review the flagged values

No data is sent to any external service.

---

## Dependencies

The project mainly uses:

- Python  
- Tkinter  
- pypdf  
- xml.etree.ElementTree  
- re

`Tkinter`, `xml.etree.ElementTree`, and `re` are part of the Python standard library.

The only external Python dependency currently required by the project is:

```
pypdf
```

## Limitations

The PDF comparison relies on text that can be extracted from the document.

A scanned PDF containing only images, a document with non-extractable text, or certain complex PDF structures may therefore produce incomplete results.

The program searches for the presence of values and equivalent representations, but does not establish business-level mappings between a specific area of the PDF and a specific XML tag.

This limitation is intentional: the tool prefers to flag a value for review rather than infer a correspondence that could be incorrect.

---

## Privacy

Processing is performed locally on the user's machine.

No external API is used, and no file is sent to any third-party service.

---

## License

This project is distributed under the MIT License.

© Palks Studio — see LICENSE.md  
- https://palks-studio.com
