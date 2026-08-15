# ==================================================
# PDF / XML COMPARATOR
# Comparaison locale des données PDF et XML → Local PDF and XML data comparison
# ==================================================

import tkinter as tk
from tkinter import filedialog, scrolledtext
from pathlib import Path
import xml.etree.ElementTree as ET
import re

from pypdf import PdfReader


# ==================================================
# EXTRACTION PDF → PDF EXTRACTION
# ==================================================

def extract_pdf_text(file_path):
    reader = PdfReader(file_path)

    text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


# ==================================================
# EXTRACTION XML → XML EXTRACTION
# ==================================================

def extract_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    values = []

    for element in root.iter():

        if element.text and element.text.strip():
            values.append(
                f"{element.tag} = {element.text.strip()}"
            )

    return "\n".join(values)


# ==================================================
# NORMALISATION TEXTE → TEXT NORMALIZATION
# ==================================================

def normalize_text(value):
    """
    Normalisation légère pour les recherches textuelles
    Light normalization for textual searches
    """

    if value is None:
        return ""

    value = str(value).strip().lower()
    value = value.replace("\u00a0", " ")
    value = " ".join(value.split())

    return value


# ==================================================
# NORMALISATION COMPACTE → COMPACT NORMALIZATION
# ==================================================

def normalize_compact(value):
    """
    Normalise les séparateurs visuels sans interpréter
    la signification métier de la donnée.

    Normalize visual separators without interpreting
    the business meaning of the data.
    """

    value = normalize_text(value)

    for char in [
        " ",
        "\n",
        "\t",
        "\u00a0",
        "€",
    ]:
        value = value.replace(char, "")

    return value


# ==================================================
# NORMALISATION NOMBRE → NUMBER NORMALIZATION
# ==================================================

def normalize_number(value):
    """
    Normalise uniquement une valeur reconnue comme numérique.
    Normalize only a value recognized as numeric.
    """

    value = str(value).strip()

    value = (
        value
        .replace("\u00a0", "")
        .replace(" ", "")
        .replace("€", "")
        .replace("EUR", "")
        .replace("eur", "")
        .replace("%", "")
    )

    # Format français → French format
    if "," in value and "." not in value:
        value = value.replace(",", ".")

    try:
        number = float(value)
        return f"{number:.2f}"

    except ValueError:
        return None


# ==================================================
# EXTRACTION DES VALEURS XML → XML VALUE EXTRACTION
# ==================================================

def extract_xml_values(file_path):
    """
    Extrait toutes les valeurs XML sans dépendre
    d'un schéma ou d'une norme particulière.

    Extract all XML values without depending
    on a specific schema or standard.
    """

    tree = ET.parse(file_path)
    root = tree.getroot()

    values = []

    for element in root.iter():

        if not element.text:
            continue

        raw_value = element.text.strip()

        if not raw_value:
            continue

        tag_name = element.tag.split("}")[-1]

        values.append({
            "tag": tag_name,
            "raw": raw_value
        })

    return values


# ==================================================
# VARIANTES DE RECHERCHE → SEARCH VARIANTS
# ==================================================

def build_search_variants(value):
    """
    Génère plusieurs formes possibles d'une même donnée
    sans interpréter sa signification métier.

    Generates several possible forms of the same data
    without interpreting its business meaning.
    """

    raw = str(value).strip()

    variants = {
        normalize_text(raw),
        normalize_compact(raw)
    }

    # ==================================================
    # NOMBRE → NUMBER
    # ==================================================

    number_candidate = (
        raw.replace("\u00a0", "")
        .replace(" ", "")
        .replace("€", "")
        .replace(",", ".")
    )

    try:
        number = float(number_candidate)

        variants.add(str(number))
        variants.add(f"{number:.2f}")
        variants.add(f"{number:.2f}".replace(".", ","))

    except ValueError:
        pass

    # ==================================================
    # DATE YYYYMMDD → COMMON DATE FORMATS
    # ==================================================

    if len(raw) == 8 and raw.isdigit():

        year = raw[0:4]
        month = raw[4:6]
        day = raw[6:8]

        variants.add(f"{day}/{month}/{year}")
        variants.add(f"{day}-{month}-{year}")
        variants.add(f"{year}-{month}-{day}")

    # ==================================================
    # DATE DD/MM/YYYY → XML DATE FORMAT
    # ==================================================

    date_match = re.fullmatch(
        r'(\d{2})[/-](\d{2})[/-](\d{4})',
        raw
    )

    if date_match:

        day, month, year = date_match.groups()

        variants.add(f"{year}{month}{day}")
        variants.add(f"{year}-{month}-{day}")

    return {
        variant
        for variant in variants
        if variant
    }


# ==================================================
# EXTRACTION DES VALEURS PDF → PDF VALUE EXTRACTION
# ==================================================

def extract_pdf_values(pdf_text):
    """
    Extrait des valeurs candidates depuis le texte du PDF
    sans interpréter leur signification métier.

    Extract candidate values from PDF text
    without interpreting their business meaning.
    """

    values = set()

    # ==================================================
    # EMAILS → EMAILS
    # ==================================================

    emails = re.findall(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        pdf_text
    )

    values.update(emails)

    # ==================================================
    # DATES → DATES
    # ==================================================

    dates = re.findall(
        r'\b(?:\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b',
        pdf_text
    )

    values.update(dates)

    # ==================================================
    # RÉFÉRENCES → REFERENCES
    # ==================================================

    references = re.findall(
        r'\b(?=[A-Za-z0-9-]*[A-Za-z])'
        r'(?=[A-Za-z0-9-]*\d)'
        r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b',
        pdf_text
    )

    values.update(references)

    # ==================================================
    # NOMBRES / MONTANTS → NUMBERS / AMOUNTS
    # ==================================================

    numbers = re.findall(
        r'(?<![A-Za-z0-9])'
        r'\d{1,3}(?:[ \u00a0]\d{3})*(?:[.,]\d+)?'
        r'(?![A-Za-z0-9])',
        pdf_text
    )

    values.update(
        value.strip()
        for value in numbers
        if value.strip()
    )

    # ==================================================
    # SUPPRESSION DES FRAGMENTS → REMOVE FRAGMENTS
    # ==================================================

    cleaned_values = set()

    for value in values:

        # Évite de conserver un simple fragment numérique
        # déjà contenu dans une référence complète.
        #
        # Avoid keeping a numeric fragment already
        # contained in a complete reference.

        if value.isdigit():

            contained_in_reference = any(
                value in reference
                for reference in references
            )

            if contained_in_reference:
                continue

        cleaned_values.add(value)

    return sorted(cleaned_values)


# ==================================================
# EXTRACTION TEXTE XML → XML TEXT EXTRACTION
# ==================================================

def extract_xml_search_text(file_path):
    """
    Construit une représentation textuelle globale du XML.
    Build a global searchable text representation of the XML.
    """

    tree = ET.parse(file_path)
    root = tree.getroot()

    values = []

    for element in root.iter():

        if element.text and element.text.strip():
            values.append(element.text.strip())

    return "\n".join(values)


# ==================================================
# RECHERCHE DANS LE XML → SEARCH IN XML
# ==================================================

def value_exists_in_xml(value, xml_text):
    """
    Recherche une valeur PDF dans le XML sans interprétation métier.
    Search for a PDF value in XML without business interpretation.
    """

    normal_xml = normalize_text(xml_text)
    compact_xml = normalize_compact(xml_text)

    # Recherche textuelle → Text search
    normal_value = normalize_text(value)
    compact_value = normalize_compact(value)

    if normal_value in normal_xml:
        return True

    if compact_value in compact_xml:
        return True

    # Recherche numérique → Numeric search
    normalized_number = normalize_number(value)

    if normalized_number is not None:

        xml_values = xml_text.splitlines()

        for xml_value in xml_values:

            xml_number = normalize_number(xml_value)

            if (
                xml_number is not None
                and xml_number == normalized_number
            ):
                return True

    # Variantes, notamment les dates → Variants, including dates
    variants = build_search_variants(value)

    for variant in variants:

        if normalize_text(variant) in normal_xml:
            return True

        if normalize_compact(variant) in compact_xml:
            return True

    return False


# ==================================================
# RECHERCHE DANS LE PDF → SEARCH IN PDF
# ==================================================

def value_exists_in_pdf(value, pdf_text):
    """
    Recherche une valeur XML dans le PDF sous plusieurs formes.
    Search for an XML value in the PDF using several representations.
    """

    normal_pdf = normalize_text(pdf_text)
    compact_pdf = normalize_compact(pdf_text)

    # Recherche directe → Direct search
    normal_value = normalize_text(value)
    compact_value = normalize_compact(value)

    if normal_value in normal_pdf:
        return True

    if compact_value in compact_pdf:
        return True

    # Recherche numérique → Numeric search
    normalized_number = normalize_number(value)

    if normalized_number is not None:

        pdf_values = extract_pdf_values(pdf_text)

        for pdf_value in pdf_values:

            pdf_number = normalize_number(pdf_value)

            if (
                pdf_number is not None
                and pdf_number == normalized_number
            ):
                return True

    # Variantes, notamment les dates → Variants, including dates
    variants = build_search_variants(value)

    for variant in variants:

        if normalize_text(variant) in normal_pdf:
            return True

        if normalize_compact(variant) in compact_pdf:
            return True

    return False


# ==================================================
# COMPARAISON PDF → XML → PDF TO XML COMPARISON
# ==================================================

def compare_pdf_xml():

    if not pdf_path.get() or not xml_path.get():

        result_output.delete("1.0", tk.END)

        result_output.insert(
            tk.END,
            "Veuillez sélectionner un PDF et un XML.\n"
            "Please select both a PDF and an XML file."
        )

        return

    pdf_text = extract_pdf_text(pdf_path.get())
    xml_text = extract_xml_search_text(xml_path.get())

    pdf_values = extract_pdf_values(pdf_text)
    xml_values = extract_xml_values(xml_path.get())

    pdf_review_values = []
    xml_review_values = []

    # ==================================================
    # PDF → XML
    # ==================================================

    for value in pdf_values:

        if not value_exists_in_xml(
            value,
            xml_text
        ):
            pdf_review_values.append(value)

    # ==================================================
    # XML → PDF
    # Détection + déduplication → Detection + deduplication
    # ==================================================

    seen_xml_reviews = set()

    for item in xml_values:

        if not value_exists_in_pdf(
            item["raw"],
            pdf_text
        ):

            key = (
                item["tag"],
                normalize_text(item["raw"])
            )

            if key not in seen_xml_reviews:

                seen_xml_reviews.add(key)
                xml_review_values.append(item)

    # ==================================================
    # RAPPORT → REPORT
    # ==================================================

    report = []

    report.append(
        "========================================\n"
        "PDF / XML DATA COMPARISON\n"
        "========================================\n\n"
        "Les valeurs ci-dessous n'ont pas été retrouvées dans l'autre représentation.\n"
        "Certaines peuvent correspondre à des données techniques ou à des différences normales.\n"
        "Ce rapport ne constitue pas une validation de conformité.\n"
        "Une vérification humaine est nécessaire.\n\n"
        "The values below were not found in the other representation.\n"
        "Some may correspond to technical data or expected differences.\n"
        "This report does not constitute a compliance validation.\n"
        "Human review is required.\n"
    )

    # ==================================================
    # PDF → XML
    # ==================================================

    report.append(
        "\n"
        "========================================\n"
        "VALEURS PDF NON RETROUVÉES DANS LE XML\n"
        "PDF VALUES NOT FOUND IN XML\n"
        "========================================\n"
    )

    if not pdf_review_values:

        report.append(
            "✓ Toutes les valeurs PDF détectées ont été retrouvées.\n"
            "✓ All detected PDF values were found.\n"
        )

    else:

        report.append(
            f"⚠ {len(pdf_review_values)} valeur(s) à vérifier / "
            f"value(s) to review\n"
        )

        for value in pdf_review_values:

            report.append(
                f"\nPDF : {value}\n"
            )

    # ==================================================
    # XML → PDF
    # ==================================================

    report.append(
        "\n"
        "========================================\n"
        "VALEURS XML NON RETROUVÉES DANS LE PDF\n"
        "XML VALUES NOT FOUND IN PDF\n"
        "========================================\n"
    )

    if not xml_review_values:

        report.append(
            "✓ Toutes les valeurs XML détectées ont été retrouvées.\n"
            "✓ All detected XML values were found.\n"
        )

    else:

        report.append(
            f"⚠ {len(xml_review_values)} valeur(s) à vérifier / "
            f"value(s) to review\n"
        )

        for item in xml_review_values:

            report.append(
                f"\nBalise / Tag : {item['tag']}\n"
                f"XML          : {item['raw']}\n"
            )

    # ==================================================
    # AFFICHAGE → DISPLAY
    # ==================================================

    result_output.delete("1.0", tk.END)

    result_output.insert(
        tk.END,
        "\n".join(report)
    )


# ==================================================
# OUVERTURE PDF → OPEN PDF
# ==================================================

def select_pdf():
    file_path = filedialog.askopenfilename(
        title="Select PDF",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not file_path:
        return

    pdf_path.set(file_path)

    text = extract_pdf_text(file_path)

    pdf_output.delete("1.0", tk.END)
    pdf_output.insert(tk.END, text)


# ==================================================
# OUVERTURE XML → OPEN XML
# ==================================================

def select_xml():
    file_path = filedialog.askopenfilename(
        title="Select XML",
        filetypes=[("XML files", "*.xml")]
    )

    if not file_path:
        return

    xml_path.set(file_path)

    text = extract_xml(file_path)

    xml_output.delete("1.0", tk.END)
    xml_output.insert(tk.END, text)


# ==================================================
# INTERFACE → INTERFACE
# ==================================================

root = tk.Tk()

root.title("PDF / XML Comparator")
root.geometry("1000x700")


pdf_path = tk.StringVar()
xml_path = tk.StringVar()


# ==================================================
# PDF
# ==================================================

tk.Button(
    root,
    text="Select PDF",
    command=select_pdf
).pack(pady=10)

tk.Label(
    root,
    textvariable=pdf_path
).pack()

pdf_output = scrolledtext.ScrolledText(
    root,
    height=12
)

pdf_output.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


# ==================================================
# XML
# ==================================================

tk.Button(
    root,
    text="Select XML",
    command=select_xml
).pack(pady=10)

tk.Label(
    root,
    textvariable=xml_path
).pack()

xml_output = scrolledtext.ScrolledText(
    root,
    height=12
)

xml_output.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


# ==================================================
# COMPARAISON → COMPARISON
# ==================================================

tk.Button(
    root,
    text="COMPARE PDF / XML",
    command=compare_pdf_xml
).pack(pady=15)


result_output = scrolledtext.ScrolledText(
    root,
    height=14
)

result_output.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


# ==================================================
# DÉMARRAGE → START
# ==================================================

root.mainloop()
