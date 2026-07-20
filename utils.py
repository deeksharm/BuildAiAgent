"""
utils.py

Utility functions for reading and chunking documents.
"""

import os


# -----------------------------
# Read Local Documents (Optional)
# -----------------------------

def read_documents(folder_path):

    documents = []

    for filename in os.listdir(folder_path):

        if filename.endswith(".txt"):

            with open(
                os.path.join(folder_path, filename),
                "r",
                encoding="utf-8"
            ) as file:

                documents.append(
                    {
                        "filename": filename,
                        "content": file.read()
                    }
                )

    return documents


# -----------------------------
# Chunk Text
# -----------------------------

def chunk_text(text, chunk_size=500):

    chunks = []

    for i in range(0, len(text), chunk_size):

        chunks.append(text[i:i + chunk_size])

    return chunks


# -----------------------------
# Prepare Chunks
# -----------------------------

def prepare_chunks(documents):

    prepared_chunks = []

    for document in documents:

        chunks = chunk_text(document["content"])

        for chunk in chunks:

            prepared_chunks.append(
                {
                    "filename": document["filename"],
                    "content": chunk
                }
            )

    return prepared_chunks
