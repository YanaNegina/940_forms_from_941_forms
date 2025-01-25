import PyPDF2
import os

# Paths to the F940 template and directory containing Q3 forms
f940_pdf_path = 'f940.pdf'
q3_forms_directory = 'path/to/q3_forms/'  # Directory containing Q3 forms (e.g., '941 Q3 2024 (1).pdf')
output_directory = 'path/to/output_forms/'

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

def load_q3_form_data(q3_pdf_path):
    """Extracts and maps fields from a Q3 form to match F940 structure."""
    with open(q3_pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        fields = reader.get_form_text_fields()

    # Mapping Q3 fields to F940 fields, with shifts for f2_x fields
    mapped_data = {}
    for field_name, value in fields.items():
        if field_name.startswith('f2_'):
            # Shift f2_x fields by +1 to match F940
            new_field_name = f'f2_{int(field_name[3:-3]) + 1}[0]'
        else:
            new_field_name = field_name  # Keep other field names the same

        mapped_data[new_field_name] = value

    return mapped_data

def fill_f940_form(f940_pdf_path, output_pdf_path, form_data):
    """Fills an F940 form with the given data and saves to the specified output path."""
    with open(f940_pdf_path, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        writer = PyPDF2.PdfWriter()

        # Loop through each page and apply the field data
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            writer.add_page(page)
            writer.update_page_form_field_values(writer.pages[page_number], form_data)

        # Write filled form to output path
        with open(output_pdf_path, 'wb') as outfile:
            writer.write(outfile)

# Process each Q3 form in the directory
for q3_filename in os.listdir(q3_forms_directory):
    if q3_filename.endswith('.pdf'):
        q3_pdf_path = os.path.join(q3_forms_directory, q3_filename)

        # Load and map data from the Q3 form
        form_data = load_q3_form_data(q3_pdf_path)

        # Get the company name for output filename, or default if missing
        company_name = form_data.get('f1_3[0]', 'filled_f940')
        output_pdf_path = os.path.join(output_directory, f"{company_name}_f940_filled.pdf")

        # Fill the F940 form and save it
        fill_f940_form(f940_pdf_path, output_pdf_path, form_data)
        print(f"Filled F940 form saved as '{output_pdf_path}'")