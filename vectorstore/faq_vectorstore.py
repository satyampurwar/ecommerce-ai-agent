"""Utility for building and querying the FAQ vector store."""

from datasets import load_dataset
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import (
    VECTOR_DB_DIR,
    EMBEDDING_MODEL_NAME,
    COLLECTION_NAME,
    FAQ_DATASET_NAME,
    FAQ_DATASET_SPLIT,
)

class FAQVectorStore:
    """Wrapper around a Chroma vector store for FAQs."""

    def __init__(
        self,
        vector_db_dir: str = VECTOR_DB_DIR,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        collection_name: str = COLLECTION_NAME,
        dataset_name: str = FAQ_DATASET_NAME,
        dataset_split: str = FAQ_DATASET_SPLIT,
    ) -> None:
        """Create or load the FAQ vector store.

        Parameters
        ----------
        vector_db_dir : str, optional
            Directory for Chroma persistence.
        embedding_model_name : str, optional
            HuggingFace model used for embeddings.
        collection_name : str, optional
            Name of the Chroma collection.
        dataset_name : str, optional
            HuggingFace dataset containing FAQs.
        dataset_split : str, optional
            Which split of the dataset to load.
        """
        self.vector_db_dir = vector_db_dir
        self.embedding_model_name = embedding_model_name
        self.collection_name = collection_name
        self.dataset_name = dataset_name
        self.dataset_split = dataset_split

        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        # Persist embeddings using Chroma so we don't recompute on each run
        self.vector_db = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.vector_db_dir
        )
        self._ensure_faqs_loaded()

    def _ensure_faqs_loaded(self):
        """Load FAQ data into the vector store if it is empty."""
        ids = self.vector_db.get().get('ids', [])
        if not ids:
            print("Loading FAQ dataset and populating vector store...")
            faq_dataset = load_dataset(self.dataset_name)[self.dataset_split]
            faqs = [f"{row['question']} {row['answer']}" for row in faq_dataset]
            ids = [str(i) for i in range(len(faqs))]
            self.vector_db.add_texts(faqs, ids=ids)
            print(f"Persisted {len(faqs)} FAQs to vector store.")
        else:
            # Already populated, nothing to do
            pass

    def semantic_search(self, query: str, k: int = 2) -> str:
        """Search the FAQ vector store for relevant entries.

        Parameters
        ----------
        query : str
            Natural language question.
        k : int, optional
            Number of results to return.

        Returns
        -------
        str
            ``\n\n`` joined string of the retrieved FAQ chunks.
        """
        docs = self.vector_db.similarity_search(query, k=k)
        if not docs:
            return "No relevant FAQ found."
        return "\n\n".join([doc.page_content for doc in docs])

    def add_faq(self, question: str, answer: str) -> None:
        """Add a new FAQ entry to the vector store."""
        text = f"{question} {answer}"
        # Generate a numeric ID for the new entry
        new_id = str(max([int(i) for i in self.vector_db.get()['ids']] + [0]) + 1)
        self.vector_db.add_texts([text], ids=[new_id])
        print(f"Added FAQ #{new_id}")

faq_vectorstore = None

def get_faq_vectorstore() -> FAQVectorStore:
    """Return a singleton instance of :class:`FAQVectorStore`."""
    global faq_vectorstore
    if faq_vectorstore is None:
        faq_vectorstore = FAQVectorStore()
    return faq_vectorstore

def semantic_faq_search(query, k=2):
    """Convenience wrapper for performing a FAQ semantic search.

    Parameters
    ----------
    query : str
        User question to search for.
    k : int, optional
        Number of FAQ entries to return.

    Returns
    -------
    str
        Combined text from the most similar FAQs.
    """
    store = get_faq_vectorstore()
    return store.semantic_search(query, k=k)


def main():
    """Command line entry-point for building the FAQ vector store."""
    get_faq_vectorstore()
    print("FAQ vector store is ready.")


if __name__ == "__main__":
    main()
