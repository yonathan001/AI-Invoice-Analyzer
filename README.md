# AI Invoice Analyzer

A full-stack application that uses AI to extract key information from PDF invoices.

## Features

- Upload PDF invoices for analysis
- Extract key information using Google's Gemini AI:
  - Vendor Name
  - Invoice Number
  - Invoice Date
  - Due Date
  - Total Amount
- Clean, responsive UI with loading states
- Error handling and validation

## Tech Stack

- **Frontend**: React with TypeScript
- **Backend**: Python with Flask
- **AI**: Google Gemini Pro
- **PDF Processing**: pdfplumber
- **Styling**: CSS with modern features (CSS Variables, Flexbox, etc.)

## Prerequisites

- Node.js (v14 or higher)
- Python (3.7 or higher)
- Google Gemini API key

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Start the Flask server:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

### Frontend Setup

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required packages:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   The frontend will open in your default browser at `http://localhost:3000`

## Usage

1. Click "Choose PDF file" to select an invoice PDF
2. Click "Analyze Invoice" to process the file
3. View the extracted information in a clean, organized format

## Project Structure

```
AI-Invoice-Analyzer/
├── backend/
│   ├── app.py              # Flask application
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/             # Static files
│   └── src/
│       ├── components/     # React components
│       ├── App.tsx         # Main App component
│       ├── App.css         # Main styles
│       └── index.tsx       # Entry point
└── README.md              # This file
```

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- [Google Gemini](https://ai.google.dev/) for the AI capabilities
- [React](https://reactjs.org/) for the frontend framework
- [Flask](https://flask.palletsprojects.com/) for the backend server
- [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF text extraction
