import firebase_admin
from firebase_admin import firestore

if not firebase_admin._apps:
    raise ValueError("Firebase app is not initialized")

db = firestore.client()


def add_document(collection_name, document_data):
    """
    Add a new document to the specified collection
    Args:
        collection_name: (str) The name of the collection to add the document to
        document_data: (dict) The data to be added to the document

    Returns:
        The ID of the newly created document
    """
    doc_ref = db.collection(collection_name).document()
    doc_ref.set(document_data)
    return doc_ref.id


def get_document_by_id(collection_name, doc_id):
    """
    Get a document from the specified collection by its ID
    Args:
        collection_name: (str) The name of the collection to get the document from
        doc_id: (str) The ID of the document to get

    Returns:
          The document data if the document exists, otherwise None
    """
    doc_ref = db.collection(collection_name).document(doc_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None


# TODO: Implement pagination on "get_all" queries down the road.
def get_all_documents(collection_name):
    """
    Get all documents from the specified collection
    Args:
        collection_name: (str) The name of the collection to get the documents from

    Returns:
        A list of all documents in the collection
    """
    docs = db.collection(collection_name).stream()
    return [doc.to_dict() for doc in docs]


def update_document(collection_name, doc_id, update_data, transaction=None):
    """
    Update a document in the specified collection
    Args:
        collection_name: (str) The name of the collection to update the document in
        doc_id: (str) The ID of the document to update
        update_data: (dict) The data to update the document with
        transaction: (firestore.Transaction) An optional transaction to perform the update in

    Returns:
        The updated document data
    """
    doc_ref = db.collection(collection_name).document(doc_id)
    if transaction is not None:
        transaction.update(doc_ref, update_data)
    else:
        doc_ref.update(update_data)
    return doc_ref.get().to_dict()


def delete_document(collection_name, doc_id, transaction=None):
    """
    Delete a document from the specified collection
    Args:
        collection_name: (str) The name of the collection to delete the document from
        doc_id: (str) The ID of the document to delete
        transaction: (firestore.Transaction) An optional transaction to perform the delete in

    Returns:
        None
    """
    doc_ref = db.collection(collection_name).document(doc_id)
    if transaction is not None:
        transaction.delete(doc_ref)
    else:
        doc_ref.delete()
