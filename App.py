import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import re
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="VIDeMI Email Newsletter Manager",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better display
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .email-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    /* Ensure all text is visible */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #000000 !important;
    }
    /* Fix expander text color */
    div[data-testid="stExpander"] {
        color: #000000 !important;
    }
    div[data-testid="stExpander"] * {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

# Hardcoded Google Sheets configuration
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vzihyp5r1voFX6A7s2JPFAn1mMmSy75PRvLWQ0Y_6-s/edit?gid=2100751315#gid=2100751315"
SHEET_ID = "1vzihyp5r1voFX6A7s2JPFAn1mMmSy75PRvLWQ0Y_6-s"
SHEET_GID = "2100751315"

# Default images
DEFAULT_HEADER_IMAGE = "https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-20-39.jpg"
DEFAULT_FOOTER_IMAGE = "https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-31-56.jpg"

def log_activity(action, details=""):
    """Log user activities"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.activity_log.insert(0, {
        'timestamp': timestamp,
        'action': action,
        'details': details
    })
    st.session_state.activity_log = st.session_state.activity_log[:50]

def load_data_from_sheets(client, spreadsheet_id):
    """Load data from Google Sheets"""
    try:
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.get_worksheet(0)
        
        # Get all values (more reliable than get_all_records for large content)
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            st.error("❌ Sheet is empty or has no data rows")
            return None
        
        # First row is headers
        headers = all_values[0]
        data_rows = all_values[1:]
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        
        # Ensure required columns exist
        required_columns = ['Email_Number', 'Title', 'Subject_Line', 'Complete_HTML_Code']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Convert Email_Number to numeric
        df['Email_Number'] = pd.to_numeric(df['Email_Number'], errors='coerce')
        
        # Remove rows with invalid email numbers
        df = df[df['Email_Number'].notna()]
        
        # Sort by email number
        df = df.sort_values('Email_Number')
        
        return df[required_columns]
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        log_activity("Error", f"Failed to load data: {str(e)}")
        return None

# Sidebar
with st.sidebar:
    st.markdown("# 🎛️ Control Panel")
    st.markdown("---")
    
    # Authentication section
    st.markdown("### 🔐 Authentication")
    
    uploaded_file = st.file_uploader(
        "Upload Service Account JSON",
        type=['json'],
        help="Upload your Google Cloud service account JSON file",
        key="json_uploader"
    )
    
    if uploaded_file is not None:
        try:
            service_account_info = json.load(uploaded_file)
            
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_info(
                service_account_info,
                scopes=scopes
            )
            
            st.session_state.client = gspread.authorize(creds)
            st.session_state.authenticated = True
            
            st.success("✅ Authenticated!")
            service_email = service_account_info.get('client_email', 'N/A')
            st.caption(f"📧 {service_email[:30]}...")
            
            log_activity("Authentication", "Successfully authenticated")
            
        except Exception as e:
            st.error(f"❌ Auth failed: {str(e)}")
            st.session_state.authenticated = False
    
    st.markdown("---")
    
    # Connection status
    st.markdown("### 📊 Connection Status")
    
    if st.session_state.authenticated:
        st.success("🟢 Connected")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.session_state.df = None
                log_activity("Refresh", "Data refreshed")
                st.rerun()
        with col2:
            if st.button("🔌 Disconnect", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.client = None
                st.session_state.df = None
                log_activity("Disconnect", "Disconnected")
                st.rerun()
    else:
        st.warning("🔴 Not Connected")
        st.caption("Upload JSON to connect")
    
    st.markdown("---")
    
    # Quick stats
    if st.session_state.authenticated and st.session_state.df is not None:
        st.markdown("### 📈 Quick Stats")
        df = st.session_state.df
        
        total = len(df)
        completed = len(df[df['Complete_HTML_Code'].astype(str).str.strip() != ''])
        pending = total - completed
        progress = (completed / 52 * 100) if total > 0 else 0
        
        st.metric("Total Emails", total)
        st.metric("Completed", completed)
        st.metric("Pending", pending)
        st.progress(progress / 100)
        st.caption(f"Progress: {progress:.1f}%")
    
    st.markdown("---")
    
    # Activity log
    with st.expander("📜 Activity Log"):
        if st.session_state.activity_log:
            for activity in st.session_state.activity_log[:10]:
                st.markdown(f"""
                <div style="padding: 0.5rem; border-left: 3px solid #667eea; margin-bottom: 0.5rem; background: #f8f9fa;">
                    <small><strong>{activity['action']}</strong></small><br>
                    <small style="color: #666;">{activity['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No recent activity")

# Main content
st.markdown('<div class="main-header">📧 VIDeMI Email Newsletter Manager</div>', unsafe_allow_html=True)

# Load data if authenticated
if st.session_state.authenticated:
    if st.session_state.df is None:
        with st.spinner("🔄 Loading data from Google Sheets..."):
            st.session_state.df = load_data_from_sheets(st.session_state.client, SHEET_ID)
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(df)
        completed = len(df[df['Complete_HTML_Code'].astype(str).str.strip() != ''])
        pending = total - completed
        progress = (completed / 52 * 100) if total > 0 else 0
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 0.9rem;">📨 TOTAL</h3>
                <h2 style="margin: 0.5rem 0 0 0; font-size: 2rem;">{total}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <h3 style="margin: 0; font-size: 0.9rem;">✅ COMPLETED</h3>
                <h2 style="margin: 0.5rem 0 0 0; font-size: 2rem;">{completed}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <h3 style="margin: 0; font-size: 0.9rem;">⏳ PENDING</h3>
                <h2 style="margin: 0.5rem 0 0 0; font-size: 2rem;">{pending}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <h3 style="margin: 0; font-size: 0.9rem;">📈 PROGRESS</h3>
                <h2 style="margin: 0.5rem 0 0 0; font-size: 2rem;">{progress:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Main tabs
        tab1, tab2 = st.tabs(["📚 Newsletter Library", "👁️ Email Preview"])
        
        with tab1:
            st.markdown("## 📚 Email Newsletter Library")
            
            # Search and filter
            search_col1, search_col2 = st.columns([3, 1])
            
            with search_col1:
                search_term = st.text_input(
                    "🔍 Search newsletters",
                    placeholder="Search by number, title, or subject...",
                    key="search_input"
                )
            
            with search_col2:
                status_filter = st.selectbox("Status", ["All", "Completed", "Pending"])
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_term:
                mask = (
                    df['Email_Number'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['Title'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['Subject_Line'].astype(str).str.contains(search_term, case=False, na=False)
                )
                filtered_df = df[mask]
            
            if status_filter == "Completed":
                filtered_df = filtered_df[filtered_df['Complete_HTML_Code'].astype(str).str.strip() != '']
            elif status_filter == "Pending":
                filtered_df = filtered_df[filtered_df['Complete_HTML_Code'].astype(str).str.strip() == '']
            
            st.markdown(f"**Showing {len(filtered_df)} of {len(df)} newsletters**")
            st.markdown("---")
            
            # Display as cards
            for idx, email_data in filtered_df.iterrows():
                has_html = str(email_data['Complete_HTML_Code']).strip() != ''
                status = "✅ Completed" if has_html else "⏳ Pending"
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="email-card">
                        <h3 style="margin: 0 0 0.5rem 0; color: #000;">Week {int(email_data['Email_Number'])}</h3>
                        <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #000;"><strong>{email_data['Title']}</strong></p>
                        <p style="color: #666; margin: 0.5rem 0;">{email_data['Subject_Line']}</p>
                        <p style="margin: 0; color: #000;"><strong>Status:</strong> {status}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"👁️ Preview", key=f"preview_{idx}", use_container_width=True):
                        st.session_state.selected_email = int(email_data['Email_Number'])
                        log_activity("View", f"Viewed Week {int(email_data['Email_Number'])}")
        
        with tab2:
            st.markdown("## 👁️ Email Preview")
            
            # Email selector
            email_numbers = df['Email_Number'].tolist()
            
            if email_numbers:
                selected = st.selectbox(
                    "Select newsletter to preview:",
                    email_numbers,
                    format_func=lambda x: f"Week {int(x)} - {df[df['Email_Number']==x]['Title'].iloc[0]}",
                    index=0 if 'selected_email' not in st.session_state else 
                          (email_numbers.index(st.session_state.selected_email) if st.session_state.selected_email in email_numbers else 0),
                    key="preview_selector"
                )
                
                if selected:
                    email_data = df[df['Email_Number'] == selected].iloc[0]
                    html_code = str(email_data['Complete_HTML_Code'])
                    
                    # Email metadata
                    meta_col1, meta_col2, meta_col3 = st.columns(3)
                    with meta_col1:
                        st.metric("Week Number", int(email_data['Email_Number']))
                    with meta_col2:
                        st.metric("HTML Size", f"{len(html_code):,} chars")
                    with meta_col3:
                        status = "✅ Ready" if html_code.strip() else "⏳ Draft"
                        st.metric("Status", status)
                    
                    st.markdown(f"**📧 Subject:** {email_data['Subject_Line']}")
                    st.markdown("---")
                    
                    # Preview tabs
                    preview_tab1, preview_tab2 = st.tabs(["🎨 Rendered Email", "💻 HTML Source"])
                    
                    with preview_tab1:
                        st.markdown("### Live Email Preview")
                        st.caption("This is how your email will appear to recipients")
                        
                        if html_code.strip():
                            components.html(
                                html_code,
                                height=1400,
                                scrolling=True
                            )
                        else:
                            st.info("📝 No HTML content available for this newsletter yet.")
                    
                    with preview_tab2:
                        st.markdown("### HTML Source Code")
                        
                        if html_code.strip():
                            st.code(html_code, language='html', line_numbers=True)
                            
                            # Code stats
                            lines = html_code.count('\n') + 1
                            words = len(html_code.split())
                            st.caption(f"📊 Stats: {lines} lines, {words} words, {len(html_code):,} characters")
                            
                            # Download button
                            st.download_button(
                                label="📥 Download HTML",
                                data=html_code.encode('utf-8'),
                                file_name=f"newsletter_week_{int(selected)}.html",
                                mime="text/html"
                            )
                        else:
                            st.info("📝 No HTML content available.")
            else:
                st.info("No newsletters available.")
    
    else:
        st.error("❌ Failed to load data. Please check your connection and try again.")

else:
    # Not authenticated - Welcome screen
    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; border-left: 4px solid #667eea;">
        <h2 style="color: #000;">👋 Welcome to VIDeMI Email Newsletter Manager!</h2>
        <p style="color: #000;">Manage your 52-week email newsletter campaign with ease.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## ✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📚 Library Management
        - Browse all newsletters
        - Search & filter
        - View completion status
        """)
    
    with col2:
        st.markdown("""
        ### 👁️ Live Preview
        - Rendered HTML emails
        - View source code
        - Download HTML files
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Analytics
        - Track progress
        - Monitor completion
        - Activity logging
        """)
    
    st.markdown("---")
    
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        ### Setup Instructions
        
        1. **Create Google Cloud Project** at [console.cloud.google.com](https://console.cloud.google.com/)
        2. **Enable APIs**: Google Sheets API & Google Drive API
        3. **Create Service Account** and download JSON key
        4. **Share your spreadsheet** with the service account email
        5. **Upload JSON** in the sidebar to connect
        
        Your spreadsheet: [Open Sheet](""" + SHEET_URL + """)
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
    <h3 style="color: #000;">📧 VIDeMI Email Newsletter Manager</h3>
    <p style="color: #666;">Built with Streamlit | Powered by Google Sheets API</p>
    <p style="color: #666;">Version 3.0 | © 2025</p>
</div>
""", unsafe_allow_html=True)
