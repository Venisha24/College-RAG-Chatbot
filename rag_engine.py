import os
import re
import math
import warnings
import requests
from collections import Counter
import pypdf

warnings.filterwarnings('ignore')

# Import SDKs
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class SimpleVectorizer:
    """Lightweight BM25 / TF-IDF Vectorizer for instant, zero-dependency exact RAG retrieval."""
    def __init__(self):
        self.doc_freqs = Counter()
        self.num_docs = 0
        self.doc_tokens = []
        self.doc_len = []
        self.avg_doc_len = 0.0

    @staticmethod
    def tokenize(text):
        return re.findall(r'\w+', text.lower())

    def fit(self, corpus):
        self.num_docs = len(corpus)
        self.doc_tokens = []
        self.doc_len = []
        self.doc_freqs = Counter()

        for doc in corpus:
            tokens = self.tokenize(doc)
            self.doc_tokens.append(tokens)
            self.doc_len.append(len(tokens))
            unique_tokens = set(tokens)
            for t in unique_tokens:
                self.doc_freqs[t] += 1

        self.avg_doc_len = sum(self.doc_len) / max(1, self.num_docs)

    def search(self, query, top_k=5, k1=1.5, b=0.75):
        query_tokens = self.tokenize(query)
        scores = []

        for idx, tokens in enumerate(self.doc_tokens):
            score = 0.0
            doc_len = self.doc_len[idx]
            token_counts = Counter(tokens)

            for qt in query_tokens:
                if qt in self.doc_freqs:
                    df = self.doc_freqs[qt]
                    idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)
                    tf = token_counts[qt]
                    numerator = tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * (doc_len / max(1, self.avg_doc_len)))
                    score += idf * (numerator / denominator)

                    if qt.isdigit() or len(qt) > 4:
                        if qt in tokens:
                            score += 1.5

            scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class CollegeRAGEngine:
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.chunks = []
        self.vectorizer = SimpleVectorizer()
        self.is_indexed = False
        self.load_and_index_documents()

    def load_and_index_documents(self):
        self.chunks = []
        if not os.path.exists(self.data_folder):
            print(f"[RAG ENGINE] Warning: Folder {self.data_folder} does not exist.")
            return

        pdf_files = [f for f in os.listdir(self.data_folder) if f.lower().endswith('.pdf')]
        print(f"[RAG ENGINE] Found {len(pdf_files)} PDF database files for extraction.")

        for filename in pdf_files:
            file_path = os.path.join(self.data_folder, filename)
            try:
                reader = pypdf.PdfReader(file_path)
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    clean_text = self._clean_text(page_text)

                    if not clean_text:
                        continue

                    paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip()]
                    for p_idx, para in enumerate(paragraphs):
                        if len(para) < 20:
                            continue
                        self.chunks.append({
                            'id': len(self.chunks),
                            'source': filename,
                            'page': page_idx + 1,
                            'text': para
                        })
            except Exception as e:
                print(f"[RAG ENGINE] Error extracting {filename}: {e}")

        corpus = [c['text'] for c in self.chunks]
        if corpus:
            self.vectorizer.fit(corpus)
            self.is_indexed = True
            print(f"[RAG ENGINE] Successfully indexed {len(self.chunks)} knowledge chunks from GLS University PDFs!")

    def _clean_text(self, text):
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def retrieve_relevant_chunks(self, query, top_k=4):
        if not self.is_indexed or not self.chunks:
            return []

        top_results = self.vectorizer.search(query, top_k=top_k)
        retrieved = []
        for idx, score in top_results:
            if score > 0.05:
                item = self.chunks[idx].copy()
                item['score'] = round(score, 3)
                retrieved.append(item)

        if not retrieved and top_results:
            for idx, score in top_results[:2]:
                item = self.chunks[idx].copy()
                item['score'] = round(score, 3)
                retrieved.append(item)

        return retrieved

    def get_openrouter_free_models(self):
        """Dynamically fetch currently active free model IDs from OpenRouter API."""
        try:
            res = requests.get('https://openrouter.ai/api/v1/models', timeout=5)
            if res.status_code == 200:
                data = res.json().get('data', [])
                free_models = [m['id'] for m in data if m['id'].endswith(':free')]
                if free_models:
                    # Put google/gemma & liquid models first if present
                    priority = [m for m in free_models if 'gemma' in m or 'liquid' in m or 'nemotron' in m]
                    others = [m for m in free_models if m not in priority]
                    return priority + others
        except Exception:
            pass
        return ["google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free", "liquid/lfm-2.5-2.6b:free", "nvidia/nemotron-3.5-lightning:free"]

    def generate_response(self, user_query, api_key, provider="OpenRouter API (100% Free - Active)", top_k=4):
        if not api_key or not api_key.strip():
            return {
                'error': 'API_KEY_MISSING',
                'answer': f'⚠️ **{provider} API Key Required!**\nPlease enter your API key in the sidebar text box.',
                'sources': [],
                'context_used': ''
            }

        retrieved_chunks = self.retrieve_relevant_chunks(user_query, top_k=top_k)

        if not retrieved_chunks:
            return {
                'answer': "I'm sorry, I couldn't find specific information matching your question in the official GLS University documents.",
                'sources': [],
                'context_used': ''
            }

        context_blocks = []
        sources_summary = []
        for idx, chunk in enumerate(retrieved_chunks):
            citation_str = f"[{chunk['source']} - Page {chunk['page']}]"
            context_blocks.append(f"--- Context Snippet {idx+1} {citation_str} ---\n{chunk['text']}")
            sources_summary.append({
                'source': chunk['source'],
                'page': chunk['page'],
                'text': chunk['text'],
                'score': chunk.get('score', 0)
            })

        combined_context = "\n\n".join(context_blocks)

        prompt = f"""You are the official AI Academic Assistant for GLS University (Ahmedabad).
Your goal is to answer student and applicant questions with 100% accuracy, specificity, and exact context based ONLY on the provided official university document snippets below.

CRITICAL INSTRUCTIONS:
1. Rely STRICTLY on the facts contained in the provided Context Snippets. Do NOT invent, assume, or extrapolate information.
2. If the context contains exact numbers, fees, percentages, dates, codes, or contact details, quote them accurately.
3. Be clear, polite, and student-friendly. Use bullet points or bold text where appropriate for readability.
4. Always cite the relevant document name (e.g., college_handbook.pdf, admissions_guide.pdf) in your answer when referencing specific policies or fees.
5. If the answer cannot be found in the provided context, state clearly: "Based on the available GLS University documents, this specific detail is not mentioned."

Official Context Snippets:
{combined_context}

Student Question: {user_query}

Detailed, Accurate Answer:"""

        answer_text = ""
        last_exception = None

        # ------------------------------------------------------------------
        # PROVIDER: OPENROUTER API (Dynamic Free Models)
        # ------------------------------------------------------------------
        if "OpenRouter" in provider:
            try:
                headers = {
                    "Authorization": f"Bearer {api_key.strip()}",
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "GLS University RAG Chatbot",
                    "Content-Type": "application/json"
                }
                free_models = self.get_openrouter_free_models()
                print(f"[RAG ENGINE] OpenRouter dynamically retrieved {len(free_models)} active free models.")

                for or_model in free_models:
                    try:
                        payload = {
                            "model": or_model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.1,
                            "max_tokens": 800
                        }
                        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=20)
                        if res.status_code == 200:
                            data = res.json()
                            choices = data.get('choices', [])
                            if choices and choices[0].get('message'):
                                answer_text = choices[0]['message'].get('content', '')
                                if answer_text:
                                    print(f"[RAG ENGINE] Successfully generated response using model: {or_model}")
                                    break
                        elif res.status_code == 401:
                            return {
                                'error': 'INVALID_API_KEY',
                                'answer': "❌ **Invalid OpenRouter API Key**: Please check your key starting with `sk-or-v1-...` from [https://openrouter.ai/keys](https://openrouter.ai/keys).",
                                'sources': sources_summary,
                                'context_used': combined_context
                            }
                        else:
                            last_exception = Exception(f"Model {or_model} Status {res.status_code}: {res.text}")
                    except Exception as ore:
                        last_exception = ore
                        continue
            except Exception as e:
                last_exception = e

        # ------------------------------------------------------------------
        # PROVIDER: GROQ API
        # ------------------------------------------------------------------
        elif "Groq" in provider:
            if not HAS_GROQ:
                return {
                    'error': 'GROQ_SDK_MISSING',
                    'answer': '⚠️ `groq` Python library is not installed. Please run `pip install groq`',
                    'sources': sources_summary,
                    'context_used': combined_context
                }
            try:
                client = Groq(api_key=api_key.strip())
                for groq_model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-70b-8192"]:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model=groq_model,
                            temperature=0.1,
                            max_tokens=800,
                        )
                        answer_text = chat_completion.choices[0].message.content
                        if answer_text:
                            break
                    except Exception as ge:
                        last_exception = ge
                        continue
            except Exception as e:
                last_exception = e

        # ------------------------------------------------------------------
        # PROVIDER: GOOGLE GEMINI API
        # ------------------------------------------------------------------
        else:
            if HAS_GENAI:
                try:
                    client = genai.Client(api_key=api_key.strip())
                    for g_model in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                        try:
                            res = client.models.generate_content(
                                model=g_model,
                                contents=prompt
                            )
                            if res and res.text:
                                answer_text = res.text
                                break
                        except Exception as ge:
                            last_exception = ge
                            continue
                except Exception as e:
                    last_exception = e

        if answer_text:
            return {
                'answer': answer_text,
                'sources': sources_summary,
                'context_used': combined_context
            }

        err_msg = str(last_exception) if last_exception else f"Could not generate response using {provider}"
        return {
            'error': 'API_CALL_FAILED',
            'answer': f"⚠️ **{provider} Request Error**: {err_msg}\n\nPlease verify your API key is active and correctly formatted.",
            'sources': sources_summary,
            'context_used': combined_context
        }
