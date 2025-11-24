import pdfplumber
from fastapi import UploadFile

async def extract_text_from_pdf(file: UploadFile, page_number: int = 1) -> str:
    """
    Extracts text from the specified page of an uploaded PDF file.
    page_number is 1-indexed.
    """
    try:
        # Read the file into memory
        content = await file.read()
        
        # Save temporarily to process with pdfplumber (or use BytesIO)
        # pdfplumber can open file-like objects
        from io import BytesIO
        with pdfplumber.open(BytesIO(content)) as pdf:
            if not pdf.pages:
                return ""
            
            # Validate page number
            if page_number < 1 or page_number > len(pdf.pages):
                return f"Error: Page {page_number} out of range. Document has {len(pdf.pages)} pages."
            
            # Extract text from the specific page (0-indexed in list)
            page = pdf.pages[page_number - 1]
            text = page.extract_text()
            return text or ""
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""
