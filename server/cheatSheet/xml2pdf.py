from fpdf import FPDF
import os
def xml2pdf():
    # Define the content from the XML structure in text form
    content = """
    Pompeii, an ancient Roman city located near the modern-day city of Naples in Italy, is one of the world's most extraordinary archaeological sites. Destroyed and buried under volcanic ash during the catastrophic eruption of Mount Vesuvius in 79 AD, the city was remarkably preserved, offering a detailed glimpse into Roman life. Excavations have revealed well-preserved homes, intricate mosaics, and even the poignant remains of its inhabitants, frozen in time by the volcanic disaster. Today, Pompeii serves as a powerful reminder of nature's destructive power and a window into history, attracting millions of visitors annually to explore its storied streets and ancient ruins.
    """

    # Create a PDF instance
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add content to the PDF
    pdf.multi_cell(0, 10, content)

    # Save the PDF
    #run os.mkdir("tmp/results") once in the beginning!
    #os.mkdir("tmp/results")

    output_path = "/tmp/cheatsheet.pdf"
    pdf.output(output_path)

    print("filed saved to:", output_path)
    