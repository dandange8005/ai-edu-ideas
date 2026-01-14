# PDF to Text Conversion Tools for macOS

This document lists tools and methods available on this system for converting PDF files to text, ranging from built-in utilities to specialized command-line tools.

## 1. pdftotext (Recommended)
This tool is part of the Poppler suite and is already installed via Homebrew. It is generally the faster and most reliable for text-based PDFs.

*   **Location**: `/opt/homebrew/bin/pdftotext`
*   **To convert to a file**:
    ```zsh
    pdftotext input.pdf output.txt
    ```
*   **To output to terminal (stdout)**:
    ```zsh
    pdftotext input.pdf -
    ```

## 2. Apple Shortcuts (Built-in with OCR)
macOS includes the **Shortcuts** app, which has a native "Extract Text from PDF" action. This uses Apple's "Live Text" engine and is capable of performing **OCR on scanned images**.

*   **How to use**: Create a shortcut that accepts "Files" as input and uses the "Extract Text from PDF" action.
*   **Usage via CLI**:
    ```zsh
    shortcuts run --shortcut "YourShortcutName" --input-path input.pdf
    ```

## 3. Pandoc
Pandoc is installed and can be used for basic PDF-to-text conversion.

*   **Location**: `/opt/homebrew/bin/pandoc`
*   **Usage**:
    ```zsh
    pandoc input.pdf -t plain -o output.txt
    ```

## 4. Automator (Built-in)
You can create a "Quick Action" or "Application" in Automator using the **Extract PDF Text** action. This adds a right-click option in Finder to convert PDFs to text files instantly.

## 5. OCRmyPDF (For Scanned PDFs)
If a PDF is just a collection of images (no selectable text), `ocrmypdf` is the best tool for the job. It uses Tesseract OCR to add a text layer.

*   **Installation**: `brew install ocrmypdf`
*   **Usage**:
    ```zsh
    ocrmypdf input.pdf --sidecar output.txt output_with_ocr.pdf
    ```

## 6. Marker (State-of-the-Art Markdown Conversion)
Marker is currently considered the best open-source tool for converting PDFs to high-quality Markdown. It preserves headers, tables, and multi-column layouts using AI models.

*   **Repository**: [datalab-to/marker](https://github.com/datalab-to/marker)
*   **Key Advantage**: Best-in-class structural accuracy for complex documents.

## 7. PyMuPDF / pymupdf4llm
An extremely fast library for extracting text. The `pymupdf4llm` extension is specifically tuned for LLM-ready Markdown output.

*   **Usage**: `pip install pymupdf4llm`
*   **Key Advantage**: Lightning fast performance with clean Markdown output.

## 8. Unstructured
A library built specifically for RAG (Retrieval-Augmented Generation) and AI search workflows.

*   **Repository**: [Unstructured.io](https://github.com/Unstructured-IO/unstructured)
*   **Key Advantage**: Breaks documents into semantic "elements" (Title, Table, List, etc.) which is ideal for database insertion.

## 9. Docling
A powerful document parsing tool that converts PDFs to Markdown while preserving structure (tables, headers, etc.). Useful for complex documents.

*   **Note**: As noted in the project log, Docling output can be quite large and may include more metadata than necessary for simple text extraction.

---
*Last updated: 2026-01-14*
