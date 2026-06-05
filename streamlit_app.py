"""
Streamlit UI for TaskMeister Intent Agent Testing
"""
import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="TaskMeister - Intent Extractor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .result-box {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d1e7dd;
        border-left: 4px solid #198754;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")
api_url = st.sidebar.text_input(
    "API Base URL",
    value="http://localhost:8000",
    help="URL of the TaskMeister API server"
)

st.sidebar.markdown("---")
st.sidebar.title("📋 About")
st.sidebar.info(
    """
    **TaskMeister Intent Extractor**
    
    Test the intent extraction agent with various user queries.
    The agent will extract structured procurement intent from natural language input.
    """
)

# Main content
st.title("🎯 TaskMeister - Intent Extractor")
st.markdown("Extract structured procurement intent from user queries")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Extract Intent", "Test Examples", "API Info"])

with tab1:
    st.subheader("Enter Your Query")
    
    # Query input
    query = st.text_area(
        "What service do you need?",
        placeholder="e.g., I need a plumber in Berlin to fix a leaky faucet. Budget is €150-300, needed by this Saturday.",
        height=100,
        help="Describe your service needs in natural language"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("🔍 Extract Intent", type="primary", use_container_width=True)
    with col2:
        st.empty()
    
    # Display results
    if submit_button:
        if not query.strip():
            st.error("❌ Please enter a query")
        else:
            with st.spinner("Extracting intent..."):
                try:
                    response = requests.post(
                        f"{api_url}/intent/extract",
                        json={"query": query},
                        timeout=30
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # Status
                    status = result.get("status", "unknown")
                    
                    if status == "complete":
                        st.markdown('<div class="result-box success-box">', unsafe_allow_html=True)
                        st.success("✅ Intent extracted successfully!")
                        
                        if result.get("intent"):
                            intent = result["intent"]
                            
                            # Create columns for organized display
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Service Details**")
                                st.write(f"🔧 **Service Category:** {intent.get('service_category', 'N/A')}")
                                st.write(f"📍 **Location:** {intent.get('location', 'Not specified')}")
                                st.write(f"⏱️ **Timeline:** {intent.get('timeline', 'Not specified')}")
                                st.write(f"🚨 **Urgency:** {intent.get('urgency', 'medium').upper()}")
                            
                            with col2:
                                st.markdown("**Budget & Other**")
                                if intent.get('budget_min') or intent.get('budget_max'):
                                    budget_str = f"{intent.get('budget_min', 'N/A')} - {intent.get('budget_max', 'N/A')} {intent.get('currency', 'EUR')}"
                                    st.write(f"💰 **Budget:** {budget_str}")
                                else:
                                    st.write(f"💰 **Budget:** Not specified")
                                st.write(f"🌐 **Language:** {intent.get('detected_language', 'en').upper()}")
                                st.write(f"📊 **Confidence:** {intent.get('confidence', 0):.1%}")
                            
                            # Special requirements
                            if intent.get('special_requirements'):
                                st.info(f"📝 **Special Requirements:** {intent['special_requirements']}")
                            
                            # Missing fields
                            if intent.get('missing_fields'):
                                st.warning(f"⚠️ **Missing Fields:** {', '.join(intent['missing_fields'])}")
                            
                            # Show raw JSON
                            with st.expander("📦 Raw JSON"):
                                st.json(intent)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    elif status == "needs_clarification":
                        st.markdown('<div class="result-box warning-box">', unsafe_allow_html=True)
                        st.warning("❓ Clarification Needed")
                        st.write("The intent extraction was partially successful but needs clarification on the following points:")
                        
                        for i, question in enumerate(result.get("clarification_questions", []), 1):
                            st.write(f"{i}. {question}")
                        
                        if result.get("intent"):
                            with st.expander("📦 Partial Intent Extracted"):
                                st.json(result["intent"])
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    elif status == "error":
                        st.markdown('<div class="result-box error-box">', unsafe_allow_html=True)
                        st.error("❌ Error")
                        st.write(f"**Error Details:** {result.get('error', 'Unknown error')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                except requests.exceptions.ConnectionError:
                    st.error(f"❌ Could not connect to API at {api_url}")
                    st.info("Make sure the FastAPI server is running: `uvicorn app.main:app --reload`")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timeout. The API took too long to respond.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab2:
    st.subheader("Test with Examples")
    st.write("Click on an example to load it into the query field above:")
    
    examples = [
        {
            "title": "Simple plumbing job",
            "query": "I need a plumber to fix a leaky faucet in my kitchen"
        },
        {
            "title": "Detailed with budget",
            "query": "Looking for an electrician in Munich to install new lights in the living room. Budget: €200-500. Needed ASAP!"
        },
        {
            "title": "Multilingual query",
            "query": "Ich brauche einen Maler in Berlin für mein Wohnzimmer. Budget ist €500-1000. Nächste Woche möglich."
        },
        {
            "title": "Complex request",
            "query": "Need a professional house cleaner for a 3-bedroom apartment in London. Weekly cleaning, starting next month. Budget around £80-120 per session. Must have experience with hardwood floors and carpets."
        },
        {
            "title": "Vague query",
            "query": "I need help with something"
        },
    ]
    
    for example in examples:
        if st.button(example["title"], key=example["title"], use_container_width=True):
            st.session_state.example_query = example["query"]
            st.info(f"✅ Example loaded: {example['query']}")

with tab3:
    st.subheader("API Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Endpoint Details**")
        st.code("POST /intent/extract", language="http")
        
        st.markdown("**Request Schema**")
        st.json({
            "query": "string (required) - User's service request"
        })
    
    with col2:
        st.markdown("**Response Schema**")
        st.json({
            "status": "complete | needs_clarification | error",
            "intent": {
                "service_category": "string",
                "location": "string or null",
                "budget_min": "number or null",
                "budget_max": "number or null",
                "currency": "string",
                "timeline": "string or null",
                "urgency": "low | medium | high",
                "detected_language": "en | de",
                "confidence": "number (0.0 - 1.0)",
                "missing_fields": ["list of strings"],
                "special_requirements": "string or null"
            },
            "clarification_questions": ["list of strings"],
            "error": "string or null"
        })
    
    st.markdown("---")
    st.markdown("**Server Status**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔗 Check Connection", key="health_check"):
            try:
                response = requests.get(f"{api_url}/", timeout=5)
                if response.status_code == 200:
                    st.success(f"✅ Server is running: {response.json()}")
                else:
                    st.error(f"❌ Server returned status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Cannot connect to {api_url}: {str(e)}")
