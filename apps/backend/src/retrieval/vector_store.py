"""ChromaDB vector store for legal document chunks."""

from typing import List, Dict
import sys

from ..ingestion.models import LegalChunk

# Check Python version and import accordingly
if sys.version_info >= (3, 14):
    # Python 3.14+ compatibility: Use fallback implementation
    import json
    import os
    try:
        import numpy as np
    except ImportError:
        # Fallback: use math for basic operations
        import math
        class np:
            """Minimal numpy replacement for vector operations"""
            @staticmethod
            def array(x):
                return x

            @staticmethod
            def dot(a, b):
                return sum(x * y for x, y in zip(a, b))

            @staticmethod
            def linalg_norm(x):
                return math.sqrt(sum(v * v for v in x))

            @staticmethod
            def argsort(x):
                return sorted(range(len(x)), key=lambda i: x[i])

        # Add linalg module
        class _linalg:
            @staticmethod
            def norm(x):
                return math.sqrt(sum(v * v for v in x))

        np.linalg = _linalg()

    class _MockCollection:
        """Mock collection for Python 3.14+ compatibility"""
        def __init__(self, name: str, metadata: Dict, persist_dir: str):
            self.name = name
            self.metadata = metadata
            self.persist_dir = persist_dir
            self._data = {"ids": [], "embeddings": [], "documents": [], "metadatas": []}
            self._load()

        def _load(self):
            """Load data from disk if exists"""
            file_path = os.path.join(self.persist_dir, f"{self.name}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        self._data = json.load(f)
                except:
                    pass

        def _save(self):
            """Save data to disk"""
            os.makedirs(self.persist_dir, exist_ok=True)
            file_path = os.path.join(self.persist_dir, f"{self.name}.json")
            # Convert numpy arrays to lists for JSON serialization
            save_data = {
                "ids": self._data["ids"],
                "embeddings": [[float(v) for v in emb] if isinstance(emb, np.ndarray) else emb
                               for emb in self._data["embeddings"]],
                "documents": self._data["documents"],
                "metadatas": self._data["metadatas"]
            }
            with open(file_path, 'w') as f:
                json.dump(save_data, f)

        def add(self, ids, embeddings, documents, metadatas):
            """Add items to collection"""
            for i, id_val in enumerate(ids):
                if id_val in self._data["ids"]:
                    # Update existing
                    idx = self._data["ids"].index(id_val)
                    self._data["embeddings"][idx] = embeddings[i]
                    self._data["documents"][idx] = documents[i]
                    self._data["metadatas"][idx] = metadatas[i]
                else:
                    # Add new
                    self._data["ids"].append(id_val)
                    self._data["embeddings"].append(embeddings[i])
                    self._data["documents"].append(documents[i])
                    self._data["metadatas"].append(metadatas[i])
            self._save()

        def query(self, query_embeddings, n_results):
            """Query collection by embedding similarity"""
            if not self._data["ids"]:
                return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

            query_emb = np.array(query_embeddings[0])
            distances = []

            for emb in self._data["embeddings"]:
                emb_array = np.array(emb)
                # Cosine distance = 1 - cosine similarity
                cos_sim = np.dot(query_emb, emb_array) / (np.linalg.norm(query_emb) * np.linalg.norm(emb_array))
                distances.append(1 - cos_sim)

            # Sort by distance (lower is better)
            sorted_indices = np.argsort(distances)[:n_results]

            return {
                "ids": [[self._data["ids"][i] for i in sorted_indices]],
                "documents": [[self._data["documents"][i] for i in sorted_indices]],
                "metadatas": [[self._data["metadatas"][i] for i in sorted_indices]],
                "distances": [[distances[i] for i in sorted_indices]]
            }

        def delete(self, where):
            """Delete items matching filter"""
            if "source_id" in where:
                indices_to_remove = []
                for i, metadata in enumerate(self._data["metadatas"]):
                    if metadata.get("source_id") == where["source_id"]:
                        indices_to_remove.append(i)

                # Remove in reverse order to maintain indices
                for i in sorted(indices_to_remove, reverse=True):
                    del self._data["ids"][i]
                    del self._data["embeddings"][i]
                    del self._data["documents"][i]
                    del self._data["metadatas"][i]
                self._save()

        def get(self):
            """Get all items"""
            return self._data

        def count(self):
            """Count items in collection"""
            return len(self._data["ids"])

    class _MockClient:
        """Mock client for Python 3.14+ compatibility"""
        def __init__(self, persist_dir: str):
            self.persist_dir = persist_dir
            self._collections = {}

        def get_or_create_collection(self, name: str, metadata: Dict):
            if name not in self._collections:
                self._collections[name] = _MockCollection(name, metadata, self.persist_dir)
            return self._collections[name]

    def PersistentClient(path: str):
        return _MockClient(path)

else:
    # Python < 3.14: Try to use real ChromaDB, fallback to mock if not available
    try:
        import chromadb
        PersistentClient = chromadb.PersistentClient
    except (ImportError, ModuleNotFoundError):
        # ChromaDB not available, use mock implementation
        import json
        import os
        import math
        try:
            import numpy as np
        except ImportError:
            # Fallback: use math for basic operations
            class np:
                """Minimal numpy replacement for vector operations"""
                @staticmethod
                def array(x):
                    return x

                @staticmethod
                def dot(a, b):
                    return sum(x * y for x, y in zip(a, b))

                @staticmethod
                def linalg_norm(x):
                    return math.sqrt(sum(v * v for v in x))

                @staticmethod
                def argsort(x):
                    return sorted(range(len(x)), key=lambda i: x[i])

                @staticmethod
                def ndarray(x):
                    return list

            # Add linalg module
            class _linalg:
                @staticmethod
                def norm(x):
                    return math.sqrt(sum(v * v for v in x))

            np.linalg = _linalg()
            np.ndarray = list

        class _MockCollection:
            """Mock collection for when ChromaDB is not available"""
            def __init__(self, name: str, metadata: Dict, persist_dir: str):
                self.name = name
                self.metadata = metadata
                self.persist_dir = persist_dir
                self._data = {"ids": [], "embeddings": [], "documents": [], "metadatas": []}
                self._load()

            def _load(self):
                """Load data from disk if exists"""
                file_path = os.path.join(self.persist_dir, f"{self.name}.json")
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            self._data = json.load(f)
                    except:
                        pass

            def _save(self):
                """Save data to disk"""
                os.makedirs(self.persist_dir, exist_ok=True)
                file_path = os.path.join(self.persist_dir, f"{self.name}.json")
                # Convert numpy arrays to lists for JSON serialization
                save_data = {
                    "ids": self._data["ids"],
                    "embeddings": [[float(v) for v in emb] if isinstance(emb, np.ndarray) else emb
                                   for emb in self._data["embeddings"]],
                    "documents": self._data["documents"],
                    "metadatas": self._data["metadatas"]
                }
                with open(file_path, 'w') as f:
                    json.dump(save_data, f)

            def add(self, ids, embeddings, documents, metadatas):
                """Add items to collection"""
                for i, id_val in enumerate(ids):
                    if id_val in self._data["ids"]:
                        # Update existing
                        idx = self._data["ids"].index(id_val)
                        self._data["embeddings"][idx] = embeddings[i]
                        self._data["documents"][idx] = documents[i]
                        self._data["metadatas"][idx] = metadatas[i]
                    else:
                        # Add new
                        self._data["ids"].append(id_val)
                        self._data["embeddings"].append(embeddings[i])
                        self._data["documents"].append(documents[i])
                        self._data["metadatas"].append(metadatas[i])
                self._save()

            def query(self, query_embeddings, n_results):
                """Query collection by embedding similarity"""
                if not self._data["ids"]:
                    return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

                query_emb = np.array(query_embeddings[0])
                distances = []

                for emb in self._data["embeddings"]:
                    emb_array = np.array(emb)
                    # Cosine distance = 1 - cosine similarity
                    cos_sim = np.dot(query_emb, emb_array) / (np.linalg.norm(query_emb) * np.linalg.norm(emb_array))
                    distances.append(1 - cos_sim)

                # Sort by distance (lower is better)
                sorted_indices = np.argsort(distances)[:n_results]

                return {
                    "ids": [[self._data["ids"][i] for i in sorted_indices]],
                    "documents": [[self._data["documents"][i] for i in sorted_indices]],
                    "metadatas": [[self._data["metadatas"][i] for i in sorted_indices]],
                    "distances": [[distances[i] for i in sorted_indices]]
                }

            def delete(self, where):
                """Delete items matching filter"""
                if "source_id" in where:
                    indices_to_remove = []
                    for i, metadata in enumerate(self._data["metadatas"]):
                        if metadata.get("source_id") == where["source_id"]:
                            indices_to_remove.append(i)

                    # Remove in reverse order to maintain indices
                    for i in sorted(indices_to_remove, reverse=True):
                        del self._data["ids"][i]
                        del self._data["embeddings"][i]
                        del self._data["documents"][i]
                        del self._data["metadatas"][i]
                    self._save()

            def get(self):
                """Get all items"""
                return self._data

            def count(self):
                """Count items in collection"""
                return len(self._data["ids"])

        class _MockClient:
            """Mock client for when ChromaDB is not available"""
            def __init__(self, persist_dir: str):
                self.persist_dir = persist_dir
                self._collections = {}

            def get_or_create_collection(self, name: str, metadata: Dict):
                if name not in self._collections:
                    self._collections[name] = _MockCollection(name, metadata, self.persist_dir)
                return self._collections[name]

        def PersistentClient(path: str):
            return _MockClient(path)


class VectorStore:
    """Vector store using ChromaDB for legal document chunks."""

    def __init__(self, persist_dir: str = "./chroma_db"):
        """Initialize vector store.

        Args:
            persist_dir: Directory for persistent storage
        """
        # Use PersistentClient for ChromaDB 1.4.1+
        self.client = PersistentClient(path=persist_dir)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="legal_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self,
        chunks: List[LegalChunk],
        embeddings: List[List[float]]
    ) -> None:
        """Add chunks with embeddings to store.

        Args:
            chunks: List of LegalChunk objects
            embeddings: List of embedding vectors (one per chunk)
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        # Generate unique IDs
        ids = [
            f"{c.source_id}_{c.artigo}_{c.paragrafo or 'caput'}_{i}"
            for i, c in enumerate(chunks)
        ]

        # Prepare metadata
        metadatas = [
            {
                "source_id": c.source_id,
                "artigo": c.artigo,
                "paragrafo": c.paragrafo or "",
                "chunk_type": c.chunk_type.value,
                "url": c.metadata.get("url", "")
            }
            for c in chunks
        ]

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Dict]:
        """Search for similar chunks.

        Args:
            query_embedding: Query vector (768 dims)
            top_k: Number of results to return

        Returns:
            List of dictionaries with:
                - text: Chunk text
                - metadata: Chunk metadata
                - distance: Similarity distance
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return formatted

    def delete_by_source(self, source_id: str) -> None:
        """Delete all chunks from a specific source.

        Args:
            source_id: Source identifier (e.g., "LC_214_2024")
        """
        self.collection.delete(
            where={"source_id": source_id}
        )

    def list_all_sources(self) -> List[Dict]:
        """List all unique source documents in the store.

        Returns:
            List of dictionaries with source metadata
        """
        # Get all metadatas
        all_data = self.collection.get()

        # Extract unique sources
        sources = {}
        for metadata in all_data["metadatas"]:
            source_id = metadata["source_id"]
            if source_id not in sources:
                sources[source_id] = {
                    "source_id": source_id,
                    "url": metadata.get("url", "")
                }

        return list(sources.values())
