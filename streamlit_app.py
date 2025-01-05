import streamlit as st
from top2vec import Top2Vec

# Dummy data for additional details
dummy_data = {
    "date_captured": "2023-12-31",
    "project_name": "Project Alpha",
    "creator": "John Doe",
    "last_updated": "2024-01-05",
    "project_manager": "Jane Smith",
    "area": "Operations",
}

# Load the Top2Vec model
@st.cache_resource
def load_model():
    return Top2Vec.load("topic_modelling/data/topic_model")

model = load_model()

st.title("Query-Based Document Search")

# Session state to track selected document
if "selected_doc_id" not in st.session_state:
    st.session_state["selected_doc_id"] = None

# Query Text Search
st.header("Search Lessons by Query Text")
query = st.text_input("Enter your search query:")
num_docs = st.slider("Number of Lessons to display:", 1, 20, 10)

if st.button("Search Lessons"):
    if not query.strip():
        st.warning("Please enter a valid query.")
    else:
        documents, doc_scores, doc_ids = model.query_documents(query, num_docs)
        st.session_state["lessons"] = [
            {"id": doc_id, "description": doc_text}
            for doc_id, doc_text in zip(doc_ids, documents)
        ]

# Display lessons as interactive Streamlit cards
if "lessons" in st.session_state:
    st.markdown("### Relevant Lessons")
    card_styles = """
        <style>
        .card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            background-color: #fff;
            cursor: pointer;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            background-color: #f6f6f6;
        }
        .card h4 {
            color: #0078D7;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .card p {
            color: #555;
            font-size: 14px;
            line-height: 1.5;
        }
        </style>
    """
    st.markdown(card_styles, unsafe_allow_html=True)

    for lesson in st.session_state["lessons"]:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"{lesson['description'][:100]}...", key=f"lesson_{lesson['id']}"):
                st.session_state["selected_doc_id"] = lesson["id"]

# Sidebar for selected lesson details
if st.session_state["selected_doc_id"] is not None:
    selected_doc_id = st.session_state["selected_doc_id"]
    selected_doc = next(
        (lesson for lesson in st.session_state["lessons"] if lesson["id"] == selected_doc_id), None
    )
    if selected_doc:
        st.sidebar.header(f"Details of Lesson ID {selected_doc_id}")
        st.sidebar.write(f"**Project Description:** {selected_doc['description']}")
        st.sidebar.write(f"**Date Captured:** {dummy_data['date_captured']}")
        st.sidebar.write(f"**Project Name:** {dummy_data['project_name']}")
        st.sidebar.write(f"**Creator:** {dummy_data['creator']}")
        st.sidebar.write(f"**Last Updated:** {dummy_data['last_updated']}")
        st.sidebar.write(f"**Project Manager:** {dummy_data['project_manager']}")
        st.sidebar.write(f"**Area:** {dummy_data['area']}")
