# 🎓 GLS University AI Student Assistant — RAG Chatbot (NLP Project)

An interactive, high-accuracy Retrieval-Augmented Generation (RAG) chatbot created for **GLS University, Ahmedabad**. This application uses a single API key (**Google Gemini API Key**) and parses official university `.pdf` documents to deliver exact, factual answers with source citations.

---

## 📁 Project Folder Structure

```
gls_university_rag_chatbot/
│
├── data/                             # Demo Database PDF Dataset (GLS University)
│   ├── college_handbook.pdf          # Academic policies, 75% attendance rule, CGPA scale, contact info
│   ├── programs_overview.pdf         # Course catalogs (Integrated M.Sc IT, BCA, MCA, BBA, MBA, B.Des)
│   ├── admissions_guide.pdf          # Deadlines, eligibility criteria, annual fee structures, scholarships
│   └── student_faq.pdf               # Structured FAQs (Academics, Hostel, Placements, IT support)
│
├── generate_pdfs.py                  # Script used to generate the 4 PDF dataset files
├── rag_engine.py                     # RAG Backend: PyPDF Extractor, BM25 Indexer, Gemini LLM caller
├── app.py                            # Streamlit Web Application (Interactive Student UI)
├── api_server.py                     # FastAPI REST API Backend (Optional Server mode)
├── .env                              # Environment configuration (Paste GEMINI_API_KEY here)
├── .env.example                      # Environment template
└── README.md                         # Project documentation
```

---

## 🔑 Where to Paste your Google Gemini API Key

You can configure your **Google Gemini API Key** in either of two places:

### Option 1: Directly in the Web UI (Recommended for Demo)
1. Launch the web app (`streamlit run app.py`).
2. On the left **Sidebar**, locate the **`🔑 API Key Configuration`** input field.
3. Paste your Gemini API key (starts with `AIzaSy...`) into the text box and press Enter.

### Option 2: In the `.env` File
Open the `.env` file in your code editor and paste your key:
```env
GEMINI_API_KEY=AIzaSyYourActualGeminiKeyHere
```

> **Note:** Get a free API Key from [Google AI Studio](https://aistudio.google.com/).

---

## 🚀 How to Run the Project

### 1. Launch Interactive Web App (Frontend + RAG Engine)
Run the following command in your terminal:

```bash
streamlit run C:\Users\LENOVO\.gemini\antigravity\scratch\gls_university_rag_chatbot\app.py
```

This will automatically open the browser at `http://localhost:8501`.

### 2. Launch FastAPI REST Backend (Optional)
If you need a standalone REST API endpoint:

```bash
python C:\Users\LENOVO\.gemini\antigravity\scratch\gls_university_rag_chatbot\api_server.py
```
API Documentation will be available at `http://127.0.0.1:8000/docs`.

---

## 🎯 Benchmark Questions for 100% Accuracy Testing

Try asking these questions in the chatbot to test context extraction:

1. **Attendance Policy:** *"What is the mandatory attendance percentage required at GLS University?"*
   - *Expected Fact:* **75% minimum attendance** in each course; below 60% leads to detention.
2. **Tuition Fees:** *"What is the annual tuition fee for Integrated M.Sc. (IT) and BCA?"*
   - *Expected Fact:* **INR 55,000/year** for Integrated M.Sc. IT; **INR 48,000/year** for BCA.
3. **Contact Info & Location:** *"Where is GLS University located and how to contact the Registrar?"*
   - *Expected Fact:* **Opposite Law Garden, Ellisbridge, Ahmedabad - 380006**. Registrar email: `registrar@glsuniversity.ac.in`.
4. **Incubation Funding:** *"What is GLS i-Hub and what startup funding does it offer?"*
   - *Expected Fact:* Startup Incubation Center providing seed funding up to **INR 5,00,000**.
5. **Grading Scale:** *"What is the grading scale used at GLS University?"*
   - *Expected Fact:* 10-point CGPA scale ranging from O (Outstanding - 10 points) down to P (4 points) and F (0 points).
