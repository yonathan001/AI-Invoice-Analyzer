from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model with the correct model name and generation config
generation_config = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_with_regex(text):
    """Fallback method to extract data using regex patterns."""
    import re
    import datetime
    
    result = {
        "vendor_name": None,
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "total_amount": None,
        "notes": "Using fallback regex parser - results may be less accurate"
    }
    
    # Try to find vendor name (look for common company name patterns)
    vendor_match = re.search(r'(?i)(?:from|bill from|vendor|supplier)[\s:]*([A-Z][A-Za-z0-9\s\.&,-]+(?:Inc\.?|LLC|Ltd\.?|Corp\.?|Company)?)', text)
    if vendor_match:
        result["vendor_name"] = vendor_match.group(1).strip()
    
    # Try to find invoice number
    inv_match = re.search(r'(?i)(?:invoice\s*#?|no\.?|number)[\s:]*([A-Z0-9-]+)', text)
    if inv_match:
        result["invoice_number"] = inv_match.group(1).strip()
    
    # Try to find dates (common date formats)
    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
    dates = re.findall(date_pattern, text)
    if len(dates) >= 1:
        result["invoice_date"] = dates[0]
    if len(dates) >= 2:
        result["due_date"] = dates[1]
    
    # Try to find total amount (supports ETB, Birr, or numbers with commas/decimals)
    total_match = re.search(r'(?i)(?:total\s*amount|amount\s*due|balance\s*due|total|ጠቅላላ|ብር)[\s:]*[ETB\$]?\s*([\d,]+(?:\.\d{2})?)', text)
    if total_match:
        # Format the number with ETB and proper thousand separators
        amount = total_match.group(1).replace(',', '')
        try:
            formatted_amount = "{:,.2f}".format(float(amount))
            result["total_amount"] = f"ETB {formatted_amount}"
        except ValueError:
            result["total_amount"] = f"ETB {amount}"
    
    return result

def extract_invoice_data(text):
    """Extract invoice data using Gemini AI with fallback to regex."""
    # First try with Gemini API
    try:
        # Truncate text if it's too long (Gemini has token limits)
        max_length = 30000
        truncated_text = text[:max_length] if len(text) > max_length else text
        
        prompt = """
        Extract these fields from the invoice in a valid JSON format with exact field names:
        {
            "vendor_name": "Name of the vendor or company",
            "invoice_number": "Invoice number or ID",
            "invoice_date": "Date of the invoice in YYYY-MM-DD format",
            "due_date": "Due date in YYYY-MM-DD format",
            "total_amount": "Total amount with currency"
        }
        
        If a field is not found, use null as the value.
        Return only the JSON object, nothing else.
        
        Invoice text:
        """ + truncated_text
        
        response = model.generate_content(prompt)
        
        # Clean up the response to extract just the JSON content
        response_text = response.text.strip()
        
        # Remove markdown code block markers if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
      
        try:
            result = json.loads(response_text)
           
            expected_fields = ["vendor_name", "invoice_number", "invoice_date", "due_date", "total_amount"]
            for field in expected_fields:
                if field not in result:
                    result[field] = None
            # Add metadata about the extraction method
            result["extraction_method"] = "AI (Google Gemini)"
            result["extraction_confidence"] = "high"
            return result
        except json.JSONDecodeError as e:
            # If JSON parsing fails, fall back to regex
            print(f"AI response parsing failed, falling back to regex: {str(e)}")
            result = extract_with_regex(truncated_text)
            result["extraction_method"] = "regex (fallback)"
            result["extraction_confidence"] = "medium"
            return result
            
    except Exception as e:
        # If any error occurs with the API, fall back to regex
        print(f"AI processing failed, falling back to regex: {str(e)}")
        result = extract_with_regex(text[:10000] if len(text) > 10000 else text)
        result["extraction_method"] = "regex (fallback)"
        result["extraction_confidence"] = "medium"
        return result

@app.route('/analyze', methods=['POST'])
def analyze_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        if not text.strip():
            return jsonify({"error": "Could not extract text from PDF"}), 400
        
        # Extract data using Gemini
        result = extract_invoice_data(text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
