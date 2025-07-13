import './App.css';

import axios from 'axios';
import { useState } from 'react';

interface InvoiceData {
  vendor_name?: string;
  invoice_number?: string;
  invoice_date?: string;
  due_date?: string;
  total_amount?: string;
  error?: string;
  raw_response?: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<InvoiceData | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setResult(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'An error occurred while processing the invoice');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      

      <main className="app-content">
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-container">
            <input
              type="file"
              id="file-upload"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={isLoading}
            />
            <label htmlFor="file-upload" className="file-upload-label">
              {file ? file.name : 'Choose PDF file'}
            </label>
          </div>
          
          <button 
            type="submit" 
            className="analyze-button"
            disabled={!file || isLoading}
          >
            {isLoading ? 'Analyzing . . ' : 'Analyze Invoice'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {isLoading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing your invoice...</p>
          </div>
        )}

        {result && (
          <div className="result-container">
            <h2>Extracted Information</h2>
            {result.error ? (
              <div className="error-message">
                <p>Error: {result.error}</p>
                {result.raw_response && (
                  <details>
                    <summary>Raw Response</summary>
                    <pre>{result.raw_response}</pre>
                  </details>
                )}
              </div>
            ) : (
              <div className="result-details">
                {/* <div className="result-row">
                  <span className="result-label">Vendor Name:</span>
                  <span className="result-value">{result.vendor_name || 'Not found'}</span>
                </div> */}
                <div className="result-row">
                  <span className="result-label">Invoice Number:</span>
                  <span className="result-value">{result.invoice_number || 'Not found'}</span>
                </div>
                <div className="result-row">
                  <span className="result-label">Invoice Date:</span>
                  <span className="result-value">{result.invoice_date || 'Not found'}</span>
                </div>
                <div className="result-row">
                  <span className="result-label">Due Date:</span>
                  <span className="result-value">{result.due_date || 'Not found'}</span>
                </div>
                <div className="result-row total">
                  <span className="result-label">Total Amount:</span>
                  <span className="result-value">{result.total_amount || 'Not found'}</span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      
    </div>
  )
}

export default App
