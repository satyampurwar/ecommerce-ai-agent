import os
from datasets import load_dataset
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import VECTOR_DB_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME, FAQ_DATASET_NAME, FAQ_DATASET_SPLIT

class FAQVectorStore:
    """
    Handles setup, persistence, and semantic search for FAQ using Chroma and sentence-transformers.
    """

    def __init__(self, 
                 vector_db_dir=VECTOR_DB_DIR,
                 embedding_model_name=EMBEDDING_MODEL_NAME,
                 collection_name=COLLECTION_NAME,
                 dataset_name=FAQ_DATASET_NAME,
                 dataset_split=FAQ_DATASET_SPLIT):
        self.vector_db_dir = vector_db_dir
        self.embedding_model_name = embedding_model_name
        self.collection_name = collection_name
        self.dataset_name = dataset_name
        self.dataset_split = dataset_split

        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self.vector_db = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.vector_db_dir
        )
        self._ensure_faqs_loaded()

    def _ensure_faqs_loaded(self):
        """
        Checks if the FAQ vector DB is already populated. If not, loads and embeds the dataset.
        """
        ids = self.vector_db.get().get('ids', [])
        if not ids:
            print("Loading FAQ dataset and populating vector store...")
            faq_dataset = load_dataset(self.dataset_name)[self.dataset_split]
            faqs = [f"{row['question']} {row['answer']}" for row in faq_dataset]
            ids = [str(i) for i in range(len(faqs))]
            self.vector_db.add_texts(faqs, ids=ids)
            print(f"Persisted {len(faqs)} FAQs to vector store.")
        else:
            print("FAQ vector store already populated.")

    def semantic_search(self, query, k=2):
        """
        Perform a semantic search on the FAQs.
        Returns the k most relevant entries.
        """
        docs = self.vector_db.similarity_search(query, k=k)
        if not docs:
            return "No relevant FAQ found."
        return "\n\n".join([doc.page_content for doc in docs])

    def add_faq(self, question, answer):
        """
        Adds a new FAQ to the vector store.
        """
        text = f"{question} {answer}"
        new_id = str(max([int(i) for i in self.vector_db.get()['ids']] + [0]) + 1)
        self.vector_db.add_texts([text], ids=[new_id])
        print(f"Added FAQ #{new_id}")

# For quick usage:
faq_vectorstore = FAQVectorStore()

def semantic_faq_search(query, k=2):
    return faq_vectorstore.semantic_search(query, k=k)
