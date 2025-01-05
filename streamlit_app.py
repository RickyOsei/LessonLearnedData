import streamlit as st
from top2vec import Top2Vec
from pyvis.network import Network
import os
from tempfile import TemporaryDirectory


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

# Page navigation in session state
if "page" not in st.session_state:
    st.session_state["page"] = "Search Lessons"
if "lessons" not in st.session_state:
    st.session_state["lessons"] = []
if "selected_doc_id" not in st.session_state:
    st.session_state["selected_doc_id"] = None


# Navigation function
def go_to_page(page_name):
    st.session_state["page"] = page_name


# Graph Generation Function
def generate_graph(query_doc_id, num_docs=10):
    documents, document_scores, document_ids = model.search_documents_by_documents(
        doc_ids=[query_doc_id], num_docs=num_docs
    )
    net = Network(height="600px", width="100%", directed=False, cdn_resources="in_line")
    net.add_node(str(query_doc_id), label=f"{query_doc_id}", color="red")
    for doc_id, score, doc_text in zip(document_ids, document_scores, documents):
        net.add_node(str(doc_id), label=f"{doc_id}")
        net.add_edge(str(query_doc_id), str(doc_id), value=score)
    with TemporaryDirectory() as tmpdir:
        graph_path = os.path.join(tmpdir, "network.html")
        net.save_graph(graph_path)
        return open(graph_path, "r").read()


# Page 1: Search Lessons
if st.session_state["page"] == "Search Lessons":
    st.title("Search Lessons Learned")
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
            if st.session_state["lessons"]:
                st.session_state["selected_doc_id"] = st.session_state["lessons"][0]["id"]

    # Left Sidebar: Selected Lesson and Generate Graph
    with st.sidebar:
        st.markdown("### Selected Lesson")
        if st.session_state["selected_doc_id"]:
            selected_doc_id = st.session_state["selected_doc_id"]
            selected_doc = next(
                (lesson for lesson in st.session_state["lessons"] if lesson["id"] == selected_doc_id), None
            )
            if selected_doc:
                st.write(f"**Lesson ID:** {selected_doc_id}")
                st.write(f"**Description:** {selected_doc['description']}")
                st.write(f"**Date Captured:** {dummy_data['date_captured']}")
                st.write(f"**Project Name:** {dummy_data['project_name']}")
                st.write(f"**Creator:** {dummy_data['creator']}")
                st.write(f"**Last Updated:** {dummy_data['last_updated']}")
                st.write(f"**Project Manager:** {dummy_data['project_manager']}")
                st.write(f"**Area:** {dummy_data['area']}")

                # Generate Graph Button
                if st.button("Generate Network Graph"):
                    go_to_page("Network Graph")

    # Main Panel: List of Lessons as Styled Cards
    if st.session_state["lessons"]:
        st.markdown("### Relevant Lessons")
        card_styles = """
            <style>
            .card {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease-in-out;
                background-color: #ffffff;
                cursor: pointer;
            }
            .card:hover {
                transform: translateY(-3px);
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
            }
            .card h4 {
                color: #0078D7;
                font-size: 16px;
                margin-bottom: 5px;
            }
            .card p {
                color: #555;
                font-size: 14px;
                margin: 0;
            }
            </style>
        """
        st.markdown(card_styles, unsafe_allow_html=True)

        for lesson in st.session_state["lessons"]:
            card_html = f"""
            <div class="card">
                <h4>Lesson ID {lesson['id']}</h4>
                <p>{lesson['description'][:80]}...</p>
            </div>
            """
            # Proper rendering of HTML
            if st.button(f"Select Lesson {lesson['id']}", key=f"lesson_{lesson['id']}"):
                st.session_state["selected_doc_id"] = lesson["id"]

# Page 2: Network Graph
elif st.session_state["page"] == "Network Graph":
    st.title("Lessons Network Graph")

    if st.session_state["selected_doc_id"]:
        query_doc_id = st.session_state["selected_doc_id"]
        graph_html = generate_graph(query_doc_id)

        # Three-column layout
        col1, col2, col3 = st.columns([2, 6, 2])

        # Left Sidebar: Similar Lessons
        with col1:
            st.markdown("### Similar Lessons")
            for lesson in st.session_state["lessons"]:
                if st.button(f"Lesson ID {lesson['id']}", key=f"graph_lesson_{lesson['id']}"):
                    st.session_state["selected_doc_id"] = lesson["id"]

        # Center: Network Graph
        with col2:
            st.markdown("### Interactive Graph")
            st.components.v1.html(graph_html, height=600)

        # Right Sidebar: Details of Selected Node
        with col3:
            selected_doc_id = st.session_state["selected_doc_id"]
            selected_doc = next(
                (lesson for lesson in st.session_state["lessons"] if lesson["id"] == selected_doc_id), None
            )
            if selected_doc:
                st.markdown(f"### Details of Lesson ID {selected_doc_id}")
                st.write(f"**Description:** {selected_doc['description']}")
                st.write(f"**Date Captured:** {dummy_data['date_captured']}")
                st.write(f"**Project Name:** {dummy_data['project_name']}")
                st.write(f"**Creator:** {dummy_data['creator']}")
                st.write(f"**Last Updated:** {dummy_data['last_updated']}")
                st.write(f"**Project Manager:** {dummy_data['project_manager']}")
                st.write(f"**Area:** {dummy_data['area']}")

    # Navigation Button
    if st.button("Back to Search"):
        go_to_page("Search Lessons")
