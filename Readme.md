# 📚 Chat with PDF using Gemini

A powerful PDF chatbot application that allows you to upload PDF documents and ask questions about their content using Google's Gemini AI model and advanced natural language processing.

## 🌟 Features

- **PDF Upload**: Support for multiple PDF file uploads
- **Intelligent Text Extraction**: Extracts and processes text from PDF documents
- **Semantic Search**: Uses vector embeddings for finding relevant information
- **AI-Powered Responses**: Leverages Google Gemini AI for accurate answers
- **Interactive UI**: Clean and user-friendly Streamlit interface
- **Context-Aware**: Maintains context from uploaded documents for better responses

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.8+**: Programming language
- **Streamlit**: Web application framework for the UI
- **Google Gemini AI**: Large language model for generating responses

### AI/ML Libraries
- **LangChain**: Framework for developing LLM-powered applications
  - `langchain-text-splitters`: Text chunking and splitting
  - `langchain-google-genai`: Google Generative AI integration
  - `langchain-community`: Community-contributed integrations
  - `langchain-core`: Core LangChain functionality
  - `langchain-huggingface`: HuggingFace model integrations

### Vector Database & Embeddings
- **FAISS** (Facebook AI Similarity Search): Vector store for efficient similarity search
- **HuggingFace Embeddings**: Text embedding model (`all-MiniLM-L6-v2`)

### PDF Processing
- **PyPDF2**: PDF reading and text extraction

### Environment Management
- **python-dotenv**: Environment variable management

## 📋 Dependencies

### Required Python Packages

```txt
streamlit==1.29.0
PyPDF2==3.0.1
langchain==0.1.0
langchain-text-splitters==0.0.1
langchain-google-genai==0.0.5
langchain-community==0.0.13
langchain-core==0.1.10
langchain-huggingface==0.0.1
faiss-cpu==1.7.4
sentence-transformers==2.2.2
python-dotenv==1.0.0
google-generativeai==0.3.2
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google API Key (for Gemini AI)

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd pdf_chatbot
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv myenv
myenv\Scripts\activate

# Linux/Mac
python3 -m venv myenv
source myenv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the project root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

**To get your Google API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### Step 5: Run the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload PDFs
- Click on "Browse files" in the sidebar
- Select one or more PDF files
- Click "Submit & Process"
- Wait for the processing to complete

### 2. Ask Questions
- Type your question in the text input field
- Press Enter
- The AI will analyze the PDFs and provide an answer based on the content

### 3. Example Questions
- "What is the main topic of this document?"
- "Summarize the key points from chapter 3"
- "What are the conclusions mentioned in the report?"
- "Explain the methodology used in this research"

## 🏗️ Project Structure

```
pdf_chatbot/
│
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
│
├── myenv/                 # Virtual environment (created during setup)
│
└── faiss_index/           # Vector store (created when processing PDFs)
    ├── index.faiss
    └── index.pkl
```

## 🔧 Configuration

### Chunk Size & Overlap
Modify in `get_text_chunks()` function:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=5000,      # Adjust based on your needs
    chunk_overlap=500     # Overlap between chunks
)
```

### Embedding Model
Change in `get_vector_store()` and `user_input()`:
```python
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Other options: "sentence-transformers/all-mpnet-base-v2"
```

### Gemini Model
Modify in `get_conversational_chain()`:
```python
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # or "gemini-pro"
    temperature=0.3                 # 0.0 to 1.0
)
```

## ⚠️ Common Issues & Solutions

### Issue 1: Module Import Error
**Error:** `ModuleNotFoundError: No module named 'langchain.chains'`

**Solution:** 
```bash
pip uninstall langchain langchain-core langchain-community
pip install langchain==0.1.0 langchain-core langchain-community
```

### Issue 2: FAISS Installation Error
**Error:** FAISS installation fails

**Solution:**
```bash
# For CPU version
pip install faiss-cpu

# For GPU version (requires CUDA)
pip install faiss-gpu
```

### Issue 3: Google API Key Error
**Error:** `GOOGLE_API_KEY not found`

**Solution:**
- Ensure `.env` file exists in project root
- Check API key is correctly formatted
- Verify no extra spaces in `.env` file

### Issue 4: PDF Text Extraction Issues
**Problem:** No text extracted from PDF

**Solution:**
- Ensure PDF contains selectable text (not scanned images)
- For scanned PDFs, consider using OCR tools like `pytesseract`

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Add `.env` to `.gitignore`**:
   ```
   .env
   myenv/
   faiss_index/
   __pycache__/
   *.pyc
   ```
3. **Rotate API keys** regularly
4. **Use environment variables** for sensitive data

## 📊 Performance Optimization

### For Large PDFs
- Reduce `chunk_size` to 3000-4000
- Increase `chunk_overlap` to 600-800
- Process PDFs in batches

### For Faster Responses
- Use `gemini-2.0-flash-exp` (faster, less accurate)
- Reduce similarity search results (`k=2` instead of `k=4`)

### Memory Optimization
```python
# In similarity_search
docs = new_db.similarity_search(user_question, k=3)  # Reduce k value
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for the powerful language model
- **LangChain** for the excellent framework
- **Streamlit** for the intuitive UI framework
- **HuggingFace** for embedding models
- **Facebook AI** for FAISS vector search

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## 🔮 Future Enhancements

- [ ] Support for more document formats (DOCX, TXT, etc.)
- [ ] Conversation history/memory
- [ ] Export chat transcripts
- [ ] Multi-language support
- [ ] OCR for scanned PDFs
- [ ] Cloud deployment options
- [ ] User authentication
- [ ] Document summarization feature

## 📈 Version History

- **v1.0.0** (2024-01-30)
  - Initial release
  - PDF upload and processing
  - Question-answering with Gemini AI
  - Vector-based similarity search

---
