import streamlit as st
import requests
import time
from streamlit_lottie import st_lottie
import json

# Minimalist Professional Config
st.set_page_config(
    page_title="SHL Assessment Recommender Pro",
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="expanded"
)

# ---- Clean CSS ----
st.markdown("""
<style>
    /* Modern minimalist style */
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

# ---- Header ----
st.title("🎯 SHL Assessment Recommender")
st.caption("Precision matching for talent acquisition team")

# ---- Sidebar ----
with st.sidebar:
    st.header("Settings")
    use_ai = st.toggle("Enable AI Insights", value=True)
    
    with st.expander("Advanced"):
        api_url = st.text_input(
            "API URL",
            value="https://shl-assessment-recommendor.onrender.com/recommend"
        )
    
    st.markdown("---")
    st.markdown("""
    **About Relevance Scores**  
    Lower scores indicate better matches:  
    - 🔥 < 1.0: Excellent match  
    - ✅ 1.0: Good match  
    """)

# ---- Search ----
query = st.text_input(
    "Describe the role or paste job URL:",
    placeholder="e.g. 'Java developer with Spring experience'"
)

if st.button("Find Assessments", type="primary") and query:
    with st.spinner("Finding optimal assessments..."):
        try:
            response = requests.post(
                api_url,
                json={"text": query, "use_ai": use_ai},
                timeout=100
            ).json()

            if not response:
                st.warning("No assessments found. Try different keywords.")
            else:
                st.success(f"Found {len(response)} assessments")
                
                for item in sorted(response, key=lambda x: x['score']):  # Sort by relevance
                    with st.container():
                        st.markdown(f"""
                        <div class="assessment-card">
                            <h3>{item['name']}</h3>
                            <div style="display:flex; justify-content:space-between; align-items:center">
                                <a href="{item['url']}" target="_blank">🔗 View Assessment</a>
                                <span class="relevance-badge">Relevance: {item['score']:.2f}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if use_ai and item["ai_insights"]:
                            st.markdown("""
                            <div class="ai-insights">
                                <strong>🧠 AI Analysis:</strong><br>
                                {insights}
                            </div>
                            """.format(insights="<br>• ".join(item["ai_insights"].split("\n"))), 
                            unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"System error: {str(e)}")
            st.info("Ensure the API is running at: " + api_url)

# ---- Footer ----
st.markdown("---")
st.caption("SHL Assessment Recommender | Made with ❤️ by Manoj (For SHL's Talent Acquisition Team)")
