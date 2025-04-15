import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

# Config
st.set_page_config(
    page_title="SHL Assessment Recommender Pro",
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="expanded"
)

# Custom CSS for basic styling
st.markdown("""
<style>
    .assessment-card {
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background: #2d3a3a;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    .relevance-badge {
        background: #1e3a1e;
        color: #8bc34a;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
    }
    .ai-insights {
        background: #2a3535;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
        border-left: 3px solid #607d8b;
    }
    .detail-container {
        display: flex;
        margin: 0.5rem 0;
    }
    .detail-label {
        font-weight: 600;
        color: #a8c7cb;
        min-width: 120px;
    }
    .detail-value {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🎯 SHL Assessment Recommender")
st.caption("Intelligent matching for talent acquisition professionals")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    use_ai = st.toggle("Enable AI Insights", value=True)
    
    with st.expander("🔧 Advanced Settings"):
        api_url = st.text_input(
            "API Endpoint",
            value="https://shl-assessment-recommendor.onrender.com/recommend",
        )
    
    st.markdown("---")
    st.markdown("""
    **📊 Interpretation Guide**
    - **Relevance Score**: Lower is better (0.0 = perfect match)
    - **Support Icons**: 
      - 🟢 = Supported 
      - 🔴 = Not Supported 
      - ❓ = Unknown
    """)

# Main Content
query = st.text_input(
    "🔍 Describe the role or paste job URL:",
    placeholder="e.g. 'Mid-level account manager with client experience'"
)

if st.button("Find Assessments", type="primary") and query:
    with st.spinner("🔍 Finding optimal assessments..."):
        try:
            response = requests.post(
                api_url,
                json={"text": query, "use_ai": use_ai},
                timeout=120
            ).json()

            if not response:
                st.warning("No assessments found. Try different keywords.")
            else:
                st.success(f"🎉 Found {len(response)} matching assessments")
                
                for item in sorted(response, key=lambda x: x['score']):
                    # Safely handle all fields with defaults
                    name = item.get('name', 'Unknown Assessment')
                    url = item.get('url', '#')
                    score = item.get('score', 1.0)
                    duration = item.get('duration', 'Not specified')
                    languages = ''.join(item.get('languages', [])) or 'Not specified'
                    job_level = item.get('job_level', 'Not specified')
                    remote_testing = item.get('remote_testing', '❓')
                    adaptive_support = item.get('adaptive_support', item.get('adaptive/irt_support', '❓'))
                    test_type = item.get('test_type', 'Not specified')
                    description = item.get('description', 'No description available')
                    ai_insights = item.get('ai_insights', '') if use_ai else ''
                    
                    # Create assessment card using Streamlit components
                    with st.container():
                        st.markdown('<div class="assessment-card">', unsafe_allow_html=True)
                        
                        # Header row
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.subheader(name)
                        with col2:
                            st.markdown(f'<span class="relevance-badge">Relevance: {score:.3f}</span>', 
                                      unsafe_allow_html=True)
                        
                        # Details using columns for layout
                        def detail_row(label, value):
                            cols = st.columns([1, 3])
                            with cols[0]:
                                st.markdown(f'<div class="detail-label">{label}</div>', unsafe_allow_html=True)
                            with cols[1]:
                                st.markdown(f'<div class="detail-value">{value}</div>', unsafe_allow_html=True)
                        
                        detail_row("🔗 URL:", f'<a href="{url}" target="_blank">View Assessment</a>')
                        detail_row("⏱ Duration:", duration)
                        detail_row("🗣 Languages:", languages)
                        detail_row("📊 Job Level:", job_level)
                        detail_row("🏠 Remote Testing:", f'<span class="support-icon">{remote_testing}</span>')
                        detail_row("🔄 Adaptive/IRT:", f'<span class="support-icon">{adaptive_support}</span>')
                        detail_row("🧪 Test Type:", test_type)
                        
                        # Description
                        st.markdown("---")
                        st.markdown("**Description:**")
                        st.markdown(description)
                        
                        # AI Insights
                        if ai_insights:
                            st.markdown('<div class="ai-insights">', unsafe_allow_html=True)
                            st.markdown("**🤖 AI Analysis:**")
                            for line in ai_insights.split('\n'):
                                if line.strip():
                                    st.markdown(f"• {line.strip()}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            st.info("Please ensure the API is running at the specified endpoint")

# Footer
st.markdown("---")
st.caption("SHL Assessment Recommender | Professional Edition")