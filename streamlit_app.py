# import streamlit as st
# import requests
# import time
# from streamlit_lottie import st_lottie
# import json

# # Minimalist Professional Config
# st.set_page_config(
#     page_title="SHL Assessment Recommender Pro",
#     layout="wide",
#     page_icon="🎯",
#     initial_sidebar_state="expanded"
# )

# # ---- Clean CSS ----
# st.markdown("""
# <style>
#     /* Modern minimalist style */
#     [data-testid="stAppViewContainer"] {
#         background: #343939FF;
#     }
#     .assessment-card {
#         border-radius: 8px;
#         padding: 1.5rem;
#         margin-bottom: 1rem;
#         background: #3c5947;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.05);
#         border-left: 4px solid #4CAF50;
#         transition: transform 0.2s;
#     }
#     .assessment-card:hover {
#         transform: translateX(4px);
#         box-shadow: 0 4px 12px rgba(0,0,0,0.1);
#     }
#     .relevance-badge {
#         font-size: 0.9rem;
#         padding: 0.25rem 0.75rem;
#         border-radius: 12px;
#         background: #202C20FF;
#         color: #b3c5b3;
#         display: inline-block;
#     }
#     .ai-insights {
#         background: #333A34FF;
#         padding: 1rem;
#         border-radius: 6px;
#         margin-top: 1rem;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ---- Header ----
# st.title("🎯 SHL Assessment Recommender")
# st.caption("Precision matching for talent acquisition team")

# # ---- Sidebar ----
# with st.sidebar:
#     st.header("Settings")
#     use_ai = st.toggle("Enable AI Insights", value=True)
    
#     with st.expander("Advanced"):
#         api_url = st.text_input(
#             "API URL",
#             value="https://shl-assessment-recommendor.onrender.com/recommend"
#         )
    
#     st.markdown("---")
#     st.markdown("""
#     **About Relevance Scores**  
#     Lower scores indicate better matches:  
#     - 🔥 < 0.3: Excellent match  
#     - ✅ 0.3-0.6: Good match  
#     - ⚠️ > 0.6: Weak match  
#     """)

# # ---- Search ----
# query = st.text_input(
#     "Describe the role or paste job URL:",
#     placeholder="e.g. 'Java developer with Spring experience'"
# )

# if st.button("Find Assessments", type="primary") and query:
#     with st.spinner("Finding optimal assessments..."):
#         try:
#             response = requests.post(
#                 api_url,
#                 json={"text": query, "use_ai": use_ai},
#                 timeout=100
#             ).json()

#             if not response:
#                 st.warning("No assessments found. Try different keywords.")
#             else:
#                 st.success(f"Found {len(response)} assessments")
                
#                 for item in sorted(response, key=lambda x: x['score']):  # Sort by relevance
#                     with st.container():
#                         st.markdown(f"""
#                         <div class="assessment-card">
#                             <h3>{item['name']}</h3>
#                             <div style="display:flex; justify-content:space-between; align-items:center">
#                                 <a href="{item['url']}" target="_blank">🔗 View Assessment</a>
#                                 <span class="relevance-badge">Relevance: {item['score']:.2f}</span>
#                             </div>
#                         """, unsafe_allow_html=True)
                        
#                         if use_ai and item["ai_insights"]:
#                             st.markdown("""
#                             <div class="ai-insights">
#                                 <strong>🧠 AI Analysis:</strong><br>
#                                 {insights}
#                             </div>
#                             """.format(insights="<br>• ".join(item["ai_insights"].split("\n"))), 
#                             unsafe_allow_html=True)
                        
#                         st.markdown("</div>", unsafe_allow_html=True)
                        
#         except Exception as e:
#             st.error(f"System error: {str(e)}")
#             st.info("Ensure the API is running at: " + api_url)

# # ---- Footer ----
# st.markdown("---")
# st.caption("SHL Assessment Recommender | Made with ❤️ by Manoj (For SHL's Talent Acquisition Team)")


import streamlit as st
import chromadb
from bs4 import BeautifulSoup
import requests
import cohere
from dotenv import load_dotenv
import os
import json
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Load environment variables
load_dotenv()

os.environ["STREAMLIT_SERVER_FILEWATCHER_TYPE"] = "none"


# Minimalist Professional Config
st.set_page_config(
    page_title="SHL Assessment Recommender",
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="expanded"
)

# ---- Initialize ChromaDB with Data Loading ----
@st.cache_resource
def initialize_vector_db():
    """Initialize ChromaDB with data loading"""
    client = chromadb.PersistentClient(path="app/chroma_db")
    embedding_function = SentenceTransformerEmbeddingFunction()
    
    try:
        # Try to get existing collection
        collection = client.get_collection(
            name="shl_assessments",
            embedding_function=embedding_function
        )
        st.success("✅ Loaded existing vector DB")
        return collection
    except ValueError:
        # Create new collection if doesn't exist
        st.warning("Initializing vector database...")
        
        try:
            # 1. Load assessment data
            with open("app/data/shl_assessments_complete.json") as f:
                assessments = json.load(f)
            
            # 2. Prepare documents and metadata
            documents = []
            metadatas = []
            for item in assessments:
                documents.append(f"{item['name']}: {item['description']}")
                metadatas.append({
                    "name": item["name"],
                    "url": item["url"],
                    "description": item["description"]
                })
            
            # 3. Create collection
            collection = client.create_collection(
                name="shl_assessments",
                embedding_function=embedding_function
            )
            
            # 4. Add data in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_end = min(i + batch_size, len(documents))
                collection.add(
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    ids=[str(j) for j in range(i, batch_end)]
                )
            
            st.success("🚀 Created new vector DB with assessments!")
            return collection
            
        except Exception as e:
            st.error(f"Failed to initialize database: {str(e)}")
            return None

# ---- Initialize Cohere ----
@st.cache_resource
def get_cohere_client():
    """Initialize Cohere client with caching"""
    try:
        return cohere.Client(os.getenv("COHERE_API_KEY"))
    except:
        st.warning("Cohere API key not found. AI insights disabled.")
        return None

# ---- Core Functions ----
def scrape_job_description(url: str) -> str:
    """Scrape job description from URL"""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=50)
        soup = BeautifulSoup(response.text, "html.parser")
        job_desc_div = soup.select_one("div.job-description, section.description")
        return job_desc_div.get_text(" ", strip=True) if job_desc_div else ""
    except Exception as e:
        st.warning(f"Scraping error: {str(e)}")
        return ""

def normalize_score(score: float) -> float:
    """Ensure scores are between 0-1"""
    try:
        return max(0.0, min(1.0, abs(float(score))))
    except:
        return 0.5

def generate_cohere_insights(name: str, description: str) -> str:
    """Generate AI insights"""
    co = get_cohere_client()
    if not co:
        return "AI insights unavailable"
    
    try:
        prompt = f"""As an HR expert, analyze this SHL assessment:
        
        Assessment: {name}
        Description: {description[:300]}
        
        Respond in exactly 3 lines:
        1. Key skills: [4-5 words]
        2. Job level: [2-3 words]  
        3. Best use: [4-5 words]"""
        
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=50,
            temperature=0.5
        )
        return response.generations[0].text
    except Exception as e:
        return "AI insights unavailable (limit reached)"

def get_recommendations(query_text: str, use_ai: bool = True):
    """Main recommendation logic"""
    collection = initialize_vector_db()
    if not collection:
        return []
    
    # Handle URL input
    if query_text.startswith(("http://", "https://")):
        query_text = scrape_job_description(query_text)
    
    # Semantic search
    results = collection.query(
        query_texts=[query_text],
        n_results=10
    )
    
    # Process results
    recommendations = []
    for i in range(len(results["ids"][0])):
        item = {
            "name": results["metadatas"][0][i]["name"],
            "url": results["metadatas"][0][i]["url"],
            "score": normalize_score(results["distances"][0][i]),
            "ai_insights": ""
        }
        
        if use_ai:
            item["ai_insights"] = generate_cohere_insights(
                item["name"],
                results["metadatas"][0][i]["description"]
            )
        
        recommendations.append(item)
    
    return sorted(recommendations, key=lambda x: x['score'])

# ---- UI Components ----
def assessment_card(item):
    """Render a single assessment card"""
    st.markdown(f"""
    <div class="assessment-card">
        <h3>{item['name']}</h3>
        <div style="display:flex; justify-content:space-between; align-items:center">
            <a href="{item['url']}" target="_blank">🔗 View Assessment</a>
            <span class="relevance-badge">Relevance: {item['score']:.2f}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if item["ai_insights"]:
        st.markdown(f"""
        <div class="ai-insights">
            <strong>🧠 AI Analysis:</strong><br>
            {item["ai_insights"].replace("\n", "<br>• ")}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---- CSS ----
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: #343939FF;
    }
    .assessment-card {
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: #3c5947;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #4CAF50;
        transition: transform 0.2s;
    }
    .assessment-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .relevance-badge {
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        background: #202C20FF;
        color: #b3c5b3;
        display: inline-block;
    }
    .ai-insights {
        background: #333A34FF;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---- Main UI ----
st.title("🎯 SHL Assessment Recommender")
st.caption("Precision matching for talent acquisition team")

# Sidebar
with st.sidebar:
    st.header("Settings")
    use_ai = st.toggle("Enable AI Insights", value=True)
    
    st.markdown("---")
    st.markdown("""
    **About Relevance Scores**  
    Lower scores indicate better matches:  
    - 🔥 < 1.0: Excellent match  
    - ✅ 1.0: Decent match 
    """)

# Search
query = st.text_input(
    "Describe the role or paste job URL:",
    placeholder="e.g. 'Java developer with Spring experience'"
)

if st.button("Find Assessments", type="primary") and query:
    with st.spinner("Finding optimal assessments..."):
        recommendations = get_recommendations(query, use_ai)
        
        if not recommendations:
            st.warning("No assessments found. Try different keywords.")
        else:
            st.success(f"Found {len(recommendations)} assessments")
            for item in recommendations:
                assessment_card(item)

# Footer
st.markdown("---")
st.caption("SHL Assessment Recommender | Made with ❤️ by Manoj (For SHL's Talent Acquisition Team)")