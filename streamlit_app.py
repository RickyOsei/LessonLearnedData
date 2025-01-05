import streamlit as st
from top2vec import Top2Vec
import pandas
import networkx as nx
from pyvis.network import Network


# Load the Top2Vec model
@st.cache_resource
def load_model():
    return Top2Vec.load("data/top2vec_model")

model = load_model()

st.title("Query-Based Document Search and Network Graph")