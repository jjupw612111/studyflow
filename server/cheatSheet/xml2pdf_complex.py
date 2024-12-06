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


# test case
# content='''<?xml version="1.0" encoding="UTF-8"?>
# <document>
# <topic>
# <name><![CDATA[<b>General Summary</b>]]></name>
# <summary>The content primarily concerns the second project of the CS 310: Scalable Software Architectures course. The project involves the development of a Multi-tier PhotoApp using AWS EC2, S3, and RDS. Submissions are made via Gradescope, with unlimited submissions permitted. The policy accepts only individual work, but late submissions are allowed up to 3 days after the deadline, which is on Monday, May 01 at 11:59 pm CST. Lectures 05, 06, and 07 given on April 13, 18, and 20 are prerequisites for undertaking this assignment.
# </summary>
# </topic>
# <topic>
# <name><![CDATA[<b>Intuitive Explanation</b>]]></name>
# <summary>The second project of the CS 310 course progresses a two-tier PhotoApp that directly interacts with AWS, particularly the RDS and S3 services, through client-side Python code. The goal for this project is to inject a web service tier between the Python-based client and the AWS services. This web service is to be scripted in JavaScript using Node.js integrated with the Express js framework. The client remains Python-based despite this enhancement.
# </summary>
# </topic>
# </document>'''
#xml2pdf_complex(content)