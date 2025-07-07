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

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

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

def extract_invoice_data(text):
    """Extract invoice data using Gemini AI."""
    try:
        prompt = f"""
        Extract these fields from the invoice in JSON format with exact field names:
        - vendor_name
        - invoice_number
        - invoice_date
        - due_date
        - total_amount

        If any field is not found, use null as the value.
        
        Invoice text:
        """{text}"""
        """
        
        response = model.generate_content(prompt)
        
        # Try to extract JSON from the response
        json_str = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        if json_str:
            return json.loads(json_str.group(1))
        
        # If no code block found, try to parse the entire response as JSON
        try:
            return json.loads(response.text)
        except:
            # If all else fails, return the raw text
            return {"error": "Failed to parse AI response", "raw_response": response.text}
            
    except Exception as e:
        return {"error": f"Error processing with Gemini: {str(e)}"}

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
