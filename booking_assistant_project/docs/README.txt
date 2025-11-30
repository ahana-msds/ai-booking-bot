This folder contains sample PDFs used for the RAG (Retrieval-Augmented Generation) pipeline.

You can place any policy documents, FAQs, service information, price lists, appointment rules, or instructions here.
These PDFs are processed by the application to:

1. Extract text
2. Chunk content
3. Build a vector store (TF-IDF)
4. Provide context-aware answers during the chat

When the app is running on Streamlit:
- Go to the left sidebar → "Upload PDFs"
- Upload any documents from this folder
- Click "Index PDFs" to make them searchable

Note:
- Only PDFs are supported.
- This folder is for reference; PDFs must be uploaded manually in the UI each time the application starts.
