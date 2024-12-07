from fpdf import FPDF
import os

def xml2pdf_complex(content):
  # Create instance of FPDF class
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", size=12)

  # Parse XML (simple approach for demonstration)
  import xml.etree.ElementTree as ET
  root = ET.fromstring(content)

  # Add content to the PDF
  for topic in root.findall('topic'):
      name = topic.find('name').text  # Extract name (contains bold HTML tags)
      summary = topic.find('summary').text.strip()  # Extract summary
      print("topic name:",name)
      print(summary)    
      # Add bold topic name
      pdf.set_font("Arial", style='B', size=14)
      pdf.cell(0, 10, name.replace('<![CDATA[', '').replace(']]>', '').replace('<b>', '').replace('</b>', ''), ln=True)
      
      # Add summary text
      pdf.set_font("Arial", size=12)
      pdf.multi_cell(0, 10, summary)
      pdf.ln(5)  # Add some spacing

  # Save the PDF
  output_path = "/tmp/cheatsheet.pdf"
  pdf.output(output_path)
  print(f"PDF saved at {output_path}")
