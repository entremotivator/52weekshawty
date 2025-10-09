import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import html
import re
from io import BytesIO
import base64

# Page config
st.set_page_config(
    page_title="52 Week Email Newsletter Manager Pro",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    .metric-card h2 {
        margin: 0.5rem 0 0 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .html-preview {
        border: 3px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        background: #ffffff;
        max-height: 700px;
        overflow-y: auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        color: #000000;
    }
    .html-preview * {
        color: inherit;
    }
    .email-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        color: #000000;
    }
    .email-card:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        transform: translateX(5px);
    }
    .email-card h3, .email-card p {
        color: #000000;
    }
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-completed {
        background: #d4edda;
        color: #155724;
    }
    .status-pending {
        background: #fff3cd;
        color: #856404;
    }
    .status-draft {
        background: #d1ecf1;
        color: #0c5460;
    }
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .code-editor {
        font-family: 'Courier New', monospace;
        background: #282c34;
        color: #abb2bf;
        padding: 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
    }
    .stats-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        color: #000000;
    }
    .stats-container * {
        color: #000000;
    }
    .preview-toolbar {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #dee2e6;
    }
    .activity-item {
        padding: 0.75rem;
        border-left: 3px solid #667eea;
        margin-bottom: 0.5rem;
        background: #f8f9fa;
        border-radius: 4px;
    }
    .search-box {
        border: 2px solid #667eea;
        border-radius: 25px;
        padding: 0.5rem 1rem;
    }
    .tab-content {
        padding: 2rem 0;
        color: #000000;
    }
    .tab-content h1, .tab-content h2, .tab-content h3, 
    .tab-content h4, .tab-content h5, .tab-content h6,
    .tab-content p, .tab-content span, .tab-content div,
    .tab-content li, .tab-content label {
        color: #000000;
    }
    div[data-testid="stExpander"] {
        background: white;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        color: #000000;
    }
    div[data-testid="stExpander"] * {
        color: #000000;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        background: #f8f9fa;
        border-radius: 10px;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'client' not in st.session_state:
    st.session_state.client = None
if 'worksheet' not in st.session_state:
    st.session_state.worksheet = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'live'
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []
if 'preview_device' not in st.session_state:
    st.session_state.preview_device = 'desktop'
if 'sort_by' not in st.session_state:
    st.session_state.sort_by = 'Email_Number'
if 'sort_order' not in st.session_state:
    st.session_state.sort_order = 'asc'

# Hardcoded Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vzihyp5r1voFX6A7s2JPFAn1mMmSy75PRvLWQ0Y_6-s/edit?usp=sharing"
SHEET_ID = "1vzihyp5r1voFX6A7s2JPFAn1mMmSy75PRvLWQ0Y_6-s"

# Helper functions
def log_activity(action, details=""):
    """Log user activities"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.activity_log.insert(0, {
        'timestamp': timestamp,
        'action': action,
        'details': details
    })
    # Keep only last 50 activities
    st.session_state.activity_log = st.session_state.activity_log[:50]

def get_email_stats(df):
    """Calculate comprehensive email statistics"""
    if df is None or len(df) == 0:
        return {
            'total': 0,
            'completed': 0,
            'pending': 0,
            'draft': 0,
            'progress': 0,
            'avg_html_length': 0,
            'completion_rate': 0
        }
    
    completed = len(df[df['Complete_HTML_Code'].astype(str).str.strip() != ''])
    total = len(df)
    pending = total - completed
    
    # Calculate average HTML length
    html_lengths = df[df['Complete_HTML_Code'].astype(str).str.strip() != '']['Complete_HTML_Code'].astype(str).str.len()
    avg_length = html_lengths.mean() if len(html_lengths) > 0 else 0
    
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'draft': 0,  # Can be enhanced later
        'progress': (completed / 52 * 100) if total > 0 else 0,
        'avg_html_length': int(avg_length),
        'completion_rate': (completed / total * 100) if total > 0 else 0
    }

def validate_html(html_code):
    """Basic HTML validation"""
    issues = []
    
    if not html_code or html_code.strip() == "":
        return ["HTML code is empty"]
    
    # Check for basic structure
    if '<html' not in html_code.lower():
        issues.append("Missing <html> tag")
    if '<body' not in html_code.lower():
        issues.append("Missing <body> tag")
    if '</html>' not in html_code.lower():
        issues.append("Missing closing </html> tag")
    if '</body>' not in html_code.lower():
        issues.append("Missing closing </body> tag")
    
    # Check for balanced tags (basic check)
    open_tags = len(re.findall(r'<(?!/)(\w+)', html_code))
    close_tags = len(re.findall(r'</(\w+)>', html_code))
    
    if open_tags != close_tags:
        issues.append(f"Possible unbalanced tags (Open: {open_tags}, Close: {close_tags})")
    
    return issues if issues else ["✓ No major issues detected"]

def export_email_html(email_data):
    """Export email HTML for download"""
    html_content = str(email_data['Complete_HTML_Code'])
    return html_content.encode('utf-8')

def search_emails(df, search_term):
    """Advanced search across multiple fields"""
    if not search_term:
        return df
    
    mask = (
        df['Email_Number'].astype(str).str.contains(search_term, case=False, na=False) |
        df['Title'].astype(str).str.contains(search_term, case=False, na=False) |
        df['Subject_Line'].astype(str).str.contains(search_term, case=False, na=False) |
        df['Complete_HTML_Code'].astype(str).str.contains(search_term, case=False, na=False)
    )
    return df[mask]

# Sidebar
with st.sidebar:
    st.markdown("# 🎛️ Control Panel")
    st.markdown("---")
    
    # Authentication section
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🔐 Authentication")
        
        uploaded_file = st.file_uploader(
            "Upload Service Account JSON",
            type=['json'],
            help="Upload your Google Cloud service account JSON file for secure access",
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
                
                log_activity("Authentication", "Successfully authenticated with Google Sheets")
                
            except Exception as e:
                st.error(f"❌ Auth failed: {str(e)}")
                st.session_state.authenticated = False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Connection status
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📊 Connection Status")
        
        if st.session_state.authenticated:
            st.success("🟢 Connected")
            st.caption("Google Sheets API Active")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.session_state.df = None
                    log_activity("Refresh", "Data refreshed from Google Sheets")
                    st.rerun()
            with col2:
                if st.button("🔌 Disconnect", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.client = None
                    st.session_state.df = None
                    log_activity("Disconnect", "Disconnected from Google Sheets")
                    st.rerun()
        else:
            st.warning("🔴 Not Connected")
            st.caption("Upload JSON to connect")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # View mode section
    if st.session_state.authenticated:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 👁️ Display Settings")
            
            st.session_state.view_mode = st.radio(
                "View Mode:",
                options=['live', 'edit', 'split'],
                format_func=lambda x: {
                    'live': '🎨 Live Preview',
                    'edit': '✏️ Code Editor',
                    'split': '📱 Split View'
                }[x],
                index=['live', 'edit', 'split'].index(st.session_state.view_mode)
            )
            
            st.session_state.preview_device = st.selectbox(
                "Preview Device:",
                options=['desktop', 'tablet', 'mobile'],
                format_func=lambda x: {
                    'desktop': '🖥️ Desktop',
                    'tablet': '📱 Tablet',
                    'mobile': '📱 Mobile'
                }[x]
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick stats
        if st.session_state.df is not None:
            with st.container():
                st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                st.markdown("### 📈 Quick Stats")
                
                stats = get_email_stats(st.session_state.df)
                
                st.metric("Total Emails", stats['total'], delta=f"{stats['total']}/52")
                st.metric("Completed", stats['completed'], delta=f"{stats['completion_rate']:.1f}%")
                st.metric("Pending", stats['pending'])
                
                st.progress(stats['progress'] / 100)
                st.caption(f"Campaign Progress: {stats['progress']:.1f}%")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Activity log
        with st.expander("📜 Activity Log", expanded=False):
            if st.session_state.activity_log:
                for activity in st.session_state.activity_log[:10]:
                    st.markdown(f"""
                    <div class="activity-item">
                        <small><strong>{activity['action']}</strong></small><br>
                        <small style="color: #666;">{activity['timestamp']}</small><br>
                        <small>{activity['details']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No recent activity")
    
    st.markdown("---")
    
    # Sheet info
    with st.expander("ℹ️ Sheet Info"):
        st.markdown(f"""
        **Spreadsheet ID:**  
        `{SHEET_ID[:20]}...`
        
        **Full URL:**  
        [Open Sheet]({SHEET_URL})
        """)

# Main content
st.markdown('<div class="main-header">📧 52 Week Email Newsletter Manager Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Comprehensive Email Campaign Management System</div>', unsafe_allow_html=True)

# Load data function
def load_data():
    try:
        sheet = st.session_state.client.open_by_key(SHEET_ID)
        worksheet = sheet.get_worksheet(0)
        st.session_state.worksheet = worksheet
        
        data = worksheet.get_all_values()
        
        if len(data) > 0:
            df = pd.DataFrame(data[1:], columns=data[0])
            
            required_columns = ['Email_Number', 'Title', 'Subject_Line', 'Complete_HTML_Code']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Convert Email_Number to numeric for proper sorting
            df['Email_Number'] = pd.to_numeric(df['Email_Number'], errors='coerce')
            
            return df[required_columns]
        else:
            return pd.DataFrame(columns=['Email_Number', 'Title', 'Subject_Line', 'Complete_HTML_Code'])
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        log_activity("Error", f"Failed to load data: {str(e)}")
        return None

# Only proceed if authenticated
if st.session_state.authenticated:
    
    # Load data if not already loaded
    if st.session_state.df is None:
        with st.spinner("🔄 Loading newsletter data from Google Sheets..."):
            st.session_state.df = load_data()
    
    if st.session_state.df is not None:
        df = st.session_state.df
        stats = get_email_stats(df)
        
        # Enhanced metrics row
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h3>📨 TOTAL EMAILS</h3>
                <h2>{stats['total']}</h2>
                <small>out of 52 weeks</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <h3>✅ COMPLETED</h3>
                <h2>{stats['completed']}</h2>
                <small>{stats['completion_rate']:.1f}% done</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <h3>⏳ PENDING</h3>
                <h2>{stats['pending']}</h2>
                <small>{52 - stats['total']} not created</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <h3>📈 PROGRESS</h3>
                <h2>{stats['progress']:.1f}%</h2>
                <small>of campaign</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <h3>📏 AVG LENGTH</h3>
                <h2>{stats['avg_html_length']}</h2>
                <small>characters</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Progress bar
        st.markdown("### 🎯 Campaign Progress")
        progress_col1, progress_col2 = st.columns([3, 1])
        with progress_col1:
            st.progress(stats['progress'] / 100)
        with progress_col2:
            st.metric("Weeks Remaining", 52 - stats['completed'])
        
        st.markdown("---")
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Newsletter Library",
            "➕ Create New Email",
            "✏️ Edit Email",
            "📊 Analytics & Reports",
            "⚙️ Bulk Operations"
        ])
        
        # Tab 1: Newsletter Library
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown("## 📚 Email Newsletter Library")
            st.caption("Browse, search, and preview all your email newsletters")
            
            # Advanced search and filters
            search_col1, search_col2, search_col3, search_col4 = st.columns([3, 1, 1, 1])
            
            with search_col1:
                search_term = st.text_input(
                    "🔍 Search newsletters",
                    placeholder="Search by number, title, subject, or content...",
                    key="search_input"
                )
            
            with search_col2:
                status_filter = st.selectbox(
                    "Status Filter",
                    ["All", "Completed", "Pending"]
                )
            
            with search_col3:
                sort_by = st.selectbox(
                    "Sort By",
                    ["Email_Number", "Title"]
                )
            
            with search_col4:
                sort_order = st.selectbox(
                    "Order",
                    ["Ascending", "Descending"]
                )
            
            # Apply filters and sorting
            filtered_df = df.copy()
            
            if search_term:
                filtered_df = search_emails(filtered_df, search_term)
            
            if status_filter == "Completed":
                filtered_df = filtered_df[filtered_df['Complete_HTML_Code'].astype(str).str.strip() != '']
            elif status_filter == "Pending":
                filtered_df = filtered_df[filtered_df['Complete_HTML_Code'].astype(str).str.strip() == '']
            
            # Sort
            ascending = sort_order == "Ascending"
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
            
            # Display results count
            st.markdown(f"**Showing {len(filtered_df)} of {len(df)} newsletters**")
            
            # Card view or table view toggle
            view_type = st.radio(
                "Display Mode:",
                ["Card View", "Table View", "Detailed List"],
                horizontal=True
            )
            
            st.markdown("---")
            
            if view_type == "Card View":
                # Card grid layout
                cols_per_row = 3
                rows = (len(filtered_df) + cols_per_row - 1) // cols_per_row
                
                for row_idx in range(rows):
                    cols = st.columns(cols_per_row)
                    for col_idx in range(cols_per_row):
                        idx = row_idx * cols_per_row + col_idx
                        if idx < len(filtered_df):
                            email_data = filtered_df.iloc[idx]
                            has_html = str(email_data['Complete_HTML_Code']).strip() != ''
                            status = "Completed" if has_html else "Pending"
                            status_class = "status-completed" if has_html else "status-pending"
                            
                            with cols[col_idx]:
                                st.markdown(f"""
                                <div class="email-card">
                                    <h3>Week {email_data['Email_Number']}</h3>
                                    <p style="font-size: 1.1rem; margin: 0.5rem 0;"><strong>{email_data['Title']}</strong></p>
                                    <p style="color: #666; font-size: 0.9rem;">{email_data['Subject_Line'][:50]}...</p>
                                    <span class="status-badge {status_class}">{status}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button(f"View Week {email_data['Email_Number']}", key=f"view_{idx}"):
                                    st.session_state.selected_email = email_data['Email_Number']
                                    log_activity("View Email", f"Viewed Week {email_data['Email_Number']}")
            
            elif view_type == "Table View":
                # Enhanced table with status
                display_df = filtered_df.copy()
                display_df['Status'] = display_df['Complete_HTML_Code'].apply(
                    lambda x: '✅ Completed' if str(x).strip() != '' else '⏳ Pending'
                )
                display_df['HTML_Length'] = display_df['Complete_HTML_Code'].astype(str).str.len()
                
                st.dataframe(
                    display_df[['Email_Number', 'Title', 'Subject_Line', 'Status', 'HTML_Length']],
                    use_container_width=True,
                    height=500
                )
            
            else:  # Detailed List
                for idx, email_data in filtered_df.iterrows():
                    has_html = str(email_data['Complete_HTML_Code']).strip() != ''
                    status = "Completed" if has_html else "Pending"
                    status_class = "status-completed" if has_html else "status-pending"
                    
                    with st.expander(f"📧 Week {email_data['Email_Number']}: {email_data['Title']}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Subject Line:** {email_data['Subject_Line']}")
                            st.markdown(f"**Status:** <span class='status-badge {status_class}'>{status}</span>", unsafe_allow_html=True)
                            st.markdown(f"**HTML Length:** {len(str(email_data['Complete_HTML_Code']))} characters")
                        with col2:
                            if st.button("👁️ Preview", key=f"prev_{idx}"):
                                st.session_state.selected_email = email_data['Email_Number']
                            if st.button("✏️ Edit", key=f"edit_{idx}"):
                                st.session_state.selected_email = email_data['Email_Number']
                                st.info(f"Switch to 'Edit Email' tab to modify Week {email_data['Email_Number']}")
            
            # Email preview section
            st.markdown("---")
            st.markdown("## 👁️ Email Preview")
            
            email_numbers = filtered_df['Email_Number'].tolist()
            if email_numbers:
                preview_col1, preview_col2 = st.columns([3, 1])
                
                with preview_col1:
                    selected = st.selectbox(
                        "Select newsletter to preview:",
                        email_numbers,
                        format_func=lambda x: f"Week {x} - {filtered_df[filtered_df['Email_Number']==x]['Title'].iloc[0]}",
                        key="preview_selector"
                    )
                
                with preview_col2:
                    st.markdown("**Preview Actions:**")
                    export_button = st.button("📥 Export HTML", use_container_width=True)
                    validate_button = st.button("✓ Validate HTML", use_container_width=True)
                
                if selected:
                    email_data = filtered_df[filtered_df['Email_Number'] == selected].iloc[0]
                    html_code = str(email_data['Complete_HTML_Code'])
                    
                    # Email metadata
                    meta_col1, meta_col2, meta_col3 = st.columns(3)
                    with meta_col1:
                        st.metric("Week Number", email_data['Email_Number'])
                    with meta_col2:
                        st.metric("HTML Size", f"{len(html_code)} chars")
                    with meta_col3:
                        status = "✅ Ready" if html_code.strip() else "⏳ Draft"
                        st.metric("Status", status)
                    
                    st.markdown(f"**📧 Subject:** {email_data['Subject_Line']}")
                    
                    # Export functionality
                    if export_button:
                        html_bytes = export_email_html(email_data)
                        st.download_button(
                            label="💾 Download HTML File",
                            data=html_bytes,
                            file_name=f"newsletter_week_{selected}.html",
                            mime="text/html"
                        )
                        log_activity("Export", f"Exported Week {selected}")
                    
                    # Validation functionality
                    if validate_button:
                        issues = validate_html(html_code)
                        if issues[0].startswith("✓"):
                            st.success("✅ HTML validation passed!")
                        else:
                            st.warning("⚠️ Validation issues found:")
                            for issue in issues:
                                st.markdown(f"- {issue}")
                    
                    st.markdown("---")
                    
                    # Preview with device simulation
                    device_widths = {
                        'desktop': '100%',
                        'tablet': '768px',
                        'mobile': '375px'
                    }
                    
                    preview_width = device_widths[st.session_state.preview_device]
                    
                    if html_code.strip():
                        if st.session_state.view_mode == 'live':
                            st.markdown(f"""
                            <div class="preview-toolbar">
                                <strong>🎨 Live Preview</strong> - {st.session_state.preview_device.capitalize()} View
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.session_state.preview_device != 'desktop':
                                st.markdown(f'<div style="max-width: {preview_width}; margin: 0 auto; border: 2px solid #ddd; border-radius: 8px;">', unsafe_allow_html=True)
                            
                            st.components.v1.html(html_code, height=700, scrolling=True)
                            
                            if st.session_state.preview_device != 'desktop':
                                st.markdown('</div>', unsafe_allow_html=True)
                        
                        elif st.session_state.view_mode == 'edit':
                            st.markdown("### 📝 HTML Source Code")
                            st.code(html_code, language='html', line_numbers=True)
                            
                            # Code stats
                            lines = html_code.count('\n') + 1
                            words = len(html_code.split())
                            st.caption(f"📊 Stats: {lines} lines, {words} words, {len(html_code)} characters")
                        
                        elif st.session_state.view_mode == 'split':
                            split_col1, split_col2 = st.columns(2)
                            
                            with split_col1:
                                st.markdown("#### 🎨 Live Preview")
                                st.components.v1.html(html_code, height=600, scrolling=True)
                            
                            with split_col2:
                                st.markdown("#### 📝 Source Code")
                                st.code(html_code, language='html', line_numbers=True)
                    else:
                        st.info("📝 No HTML content available for this newsletter yet.")
            else:
                st.info("No newsletters match your search criteria.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 2: Create New Email
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown("## ➕ Create New Newsletter")
            st.caption("Add a new email to your 52-week campaign")
            
            # Template selector
            st.markdown("### 📋 Quick Start")
            template_option = st.selectbox(
                "Choose a starting point:",
                ["Blank Email", "Basic Template", "Rich Template", "Clone Existing"]
            )
            
            if template_option == "Basic Template":
                default_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newsletter</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 8px; }
        .content { padding: 20px 0; }
        .footer { text-align: center; color: #666; padding: 20px 0; border-top: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Your Newsletter Title</h1>
    </div>
    <div class="content">
        <h2>Welcome!</h2>
        <p>Your content goes here...</p>
    </div>
    <div class="footer">
        <p>&copy; 2025 Your Company. All rights reserved.</p>
    </div>
</body>
</html>"""
            elif template_option == "Rich Template":
                default_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newsletter</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }
        .content { padding: 40px 20px; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { background: #333; color: white; padding: 30px 20px; text-align: center; }
        h1 { margin: 0; font-size: 32px; }
        h2 { color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Your Awesome Newsletter</h1>
            <p>Week X - [Date]</p>
        </div>
        <div class="content">
            <h2>This Week's Highlights</h2>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit...</p>
            <a href="#" class="button">Learn More</a>
            <h2>Featured Content</h2>
            <p>Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...</p>
        </div>
        <div class="footer">
            <p>You're receiving this email because you subscribed to our newsletter.</p>
            <p><a href="#" style="color: #667eea;">Unsubscribe</a> | <a href="#" style="color: #667eea;">Manage Preferences</a></p>
        </div>
    </div>
</body>
</html>"""
            else:
                default_html = ""
            
            st.markdown("---")
            
            # Create form
            with st.form("add_email_form", clear_on_submit=False):
                st.markdown("### 📝 Newsletter Details")
                
                form_col1, form_col2 = st.columns(2)
                
                with form_col1:
                    new_email_number = st.number_input(
                        "📊 Email Number (1-52)",
                        min_value=1,
                        max_value=52,
                        value=len(df)+1 if len(df) < 52 else 1,
                        help="Select the week number for this newsletter"
                    )
                
                with form_col2:
                    # Check if number already exists
                    if new_email_number in df['Email_Number'].values:
                        st.warning(f"⚠️ Week {new_email_number} already exists!")
                    else:
                        st.success(f"✅ Week {new_email_number} is available")
                
                new_title = st.text_input(
                    "📧 Title (with emoji)",
                    placeholder="e.g., 🎉 Welcome to Our Newsletter!",
                    help="This will be used as the email title"
                )
                
                new_subject = st.text_input(
                    "📨 Subject Line",
                    value=new_title,
                    placeholder="e.g., Week 1: Getting Started",
                    help="The subject line that appears in the inbox"
                )
                
                st.markdown("### 🎨 HTML Content")
                
                # Code editor with tabs
                code_tab1, code_tab2 = st.tabs(["✏️ Edit", "👁️ Preview"])
                
                with code_tab1:
                    new_html = st.text_area(
                        "Complete HTML Code",
                        value=default_html,
                        height=400,
                        help="Paste or write your complete HTML email code here"
                    )
                    
                    st.caption(f"📊 {len(new_html)} characters, {new_html.count('<')} HTML tags")
                
                with code_tab2:
                    if new_html.strip():
                        st.components.v1.html(new_html, height=500, scrolling=True)
                    else:
                        st.info("Enter HTML code to see preview")
                
                st.markdown("---")
                
                # Action buttons
                button_col1, button_col2, button_col3 = st.columns(3)
                
                with button_col1:
                    submitted = st.form_submit_button("💾 Save Newsletter", type="primary", use_container_width=True)
                
                with button_col2:
                    validate_new = st.form_submit_button("✓ Validate HTML", use_container_width=True)
                
                with button_col3:
                    clear_form = st.form_submit_button("🗑️ Clear Form", use_container_width=True)
                
                if submitted:
                    if not new_title.strip():
                        st.error("❌ Please enter a title!")
                    elif not new_subject.strip():
                        st.error("❌ Please enter a subject line!")
                    else:
                        try:
                            # Check for duplicates
                            if new_email_number in df['Email_Number'].values:
                                st.error(f"❌ Week {new_email_number} already exists! Please choose a different number or edit the existing one.")
                            else:
                                row = [int(new_email_number), new_title, new_subject, new_html]
                                st.session_state.worksheet.append_row(row)
                                
                                st.success(f"✅ Newsletter Week {new_email_number} created successfully!")
                                log_activity("Create", f"Created Week {new_email_number}: {new_title}")
                                st.balloons()
                                st.session_state.df = None
                                
                                # Auto-navigate suggestion
                                st.info("💡 Tip: Switch to the 'Newsletter Library' tab to view your new email!")
                                
                        except Exception as e:
                            st.error(f"❌ Error creating newsletter: {str(e)}")
                            log_activity("Error", f"Failed to create newsletter: {str(e)}")
                
                if validate_new:
                    if new_html.strip():
                        issues = validate_html(new_html)
                        if issues[0].startswith("✓"):
                            st.success("✅ HTML validation passed! Your code looks good.")
                        else:
                            st.warning("⚠️ Validation issues detected:")
                            for issue in issues:
                                st.markdown(f"- {issue}")
                    else:
                        st.warning("⚠️ No HTML content to validate")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 3: Edit Email
        with tab3:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown("## ✏️ Edit Newsletter")
            st.caption("Modify or delete existing newsletters")
            
            email_numbers = df['Email_Number'].tolist()
            if email_numbers:
                # Newsletter selector
                select_col1, select_col2 = st.columns([3, 1])
                
                with select_col1:
                    edit_selected = st.selectbox(
                        "📧 Select newsletter to edit:",
                        email_numbers,
                        format_func=lambda x: f"Week {x} - {df[df['Email_Number']==x]['Title'].iloc[0]}"
                    )
                
                with select_col2:
                    st.markdown("**Quick Actions:**")
                    duplicate_btn = st.button("📋 Duplicate", use_container_width=True)
                
                if edit_selected:
                    email_data = df[df['Email_Number'] == edit_selected].iloc[0]
                    row_index = df[df['Email_Number'] == edit_selected].index[0] + 2
                    
                    # Display current info
                    st.markdown("### 📊 Current Newsletter Info")
                    info_col1, info_col2, info_col3 = st.columns(3)
                    
                    with info_col1:
                        st.metric("Week Number", email_data['Email_Number'])
                    with info_col2:
                        st.metric("HTML Size", f"{len(str(email_data['Complete_HTML_Code']))} chars")
                    with info_col3:
                        last_modified = "Unknown"
                        st.metric("Status", "✅ Complete" if str(email_data['Complete_HTML_Code']).strip() else "📝 Draft")
                    
                    st.markdown("---")
                    
                    # Edit form
                    with st.form("edit_email_form"):
                        st.markdown("### ✏️ Edit Details")
                        
                        edit_email_number = st.number_input(
                            "Email Number (1-52)",
                            min_value=1,
                            max_value=52,
                            value=int(email_data['Email_Number']),
                            help="Change the week number if needed"
                        )
                        
                        edit_title = st.text_input(
                            "Title (with emoji)",
                            value=email_data['Title']
                        )
                        
                        edit_subject = st.text_input(
                            "Subject Line",
                            value=email_data['Subject_Line']
                        )
                        
                        st.markdown("### 🎨 HTML Content Editor")
                        
                        edit_tabs = st.tabs(["✏️ Edit Code", "👁️ Live Preview", "📱 Split View"])
                        
                        with edit_tabs[0]:
                            edit_html = st.text_area(
                                "Complete HTML Code",
                                value=str(email_data['Complete_HTML_Code']),
                                height=450
                            )
                            
                            # Code statistics
                            lines = edit_html.count('\n') + 1
                            words = len(edit_html.split())
                            chars = len(edit_html)
                            
                            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                            stat_col1.metric("Lines", lines)
                            stat_col2.metric("Words", words)
                            stat_col3.metric("Characters", chars)
                            stat_col4.metric("HTML Tags", edit_html.count('<'))
                        
                        with edit_tabs[1]:
                            if edit_html.strip():
                                st.components.v1.html(edit_html, height=600, scrolling=True)
                            else:
                                st.info("No HTML content to preview")
                        
                        with edit_tabs[2]:
                            split_col1, split_col2 = st.columns(2)
                            with split_col1:
                                st.markdown("**Code:**")
                                st.code(edit_html[:1000] + ("..." if len(edit_html) > 1000 else ""), language='html')
                            with split_col2:
                                st.markdown("**Preview:**")
                                if edit_html.strip():
                                    st.components.v1.html(edit_html, height=400, scrolling=True)
                        
                        st.markdown("---")
                        
                        # Action buttons
                        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                        
                        with btn_col1:
                            update_submitted = st.form_submit_button("💾 Update", type="primary", use_container_width=True)
                        
                        with btn_col2:
                            validate_edit = st.form_submit_button("✓ Validate", use_container_width=True)
                        
                        with btn_col3:
                            export_edit = st.form_submit_button("📥 Export", use_container_width=True)
                        
                        with btn_col4:
                            delete_submitted = st.form_submit_button("🗑️ Delete", use_container_width=True)
                        
                        if update_submitted:
                            try:
                                # Update all fields including email number
                                st.session_state.worksheet.update(f'A{row_index}:D{row_index}', 
                                    [[int(edit_email_number), edit_title, edit_subject, edit_html]])
                                
                                st.success(f"✅ Newsletter Week {edit_selected} updated successfully!")
                                log_activity("Update", f"Updated Week {edit_selected}: {edit_title}")
                                st.session_state.df = None
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error updating: {str(e)}")
                                log_activity("Error", f"Failed to update Week {edit_selected}: {str(e)}")
                        
                        if validate_edit:
                            issues = validate_html(edit_html)
                            if issues[0].startswith("✓"):
                                st.success("✅ HTML validation passed!")
                            else:
                                st.warning("⚠️ Issues found:")
                                for issue in issues:
                                    st.markdown(f"- {issue}")
                        
                        if export_edit:
                            html_bytes = export_email_html(email_data)
                            st.download_button(
                                label="💾 Download HTML",
                                data=html_bytes,
                                file_name=f"newsletter_week_{edit_selected}.html",
                                mime="text/html",
                                key="export_edit_dl"
                            )
                        
                        if delete_submitted:
                            st.warning(f"⚠️ Are you sure you want to delete Week {edit_selected}?")
                            confirm_col1, confirm_col2 = st.columns(2)
                            
                            with confirm_col1:
                                if st.form_submit_button("✅ Yes, Delete", type="primary", use_container_width=True):
                                    try:
                                        st.session_state.worksheet.delete_rows(row_index)
                                        st.success(f"✅ Week {edit_selected} deleted!")
                                        log_activity("Delete", f"Deleted Week {edit_selected}")
                                        st.session_state.df = None
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error deleting: {str(e)}")
                            
                            with confirm_col2:
                                st.form_submit_button("❌ Cancel", use_container_width=True)
                
                # Duplicate functionality
                if duplicate_btn and edit_selected:
                    st.info(f"💡 To duplicate Week {edit_selected}, go to 'Create New Email' tab and use the content as a template.")
            
            else:
                st.info("📭 No newsletters available to edit. Create your first newsletter in the 'Create New Email' tab!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 4: Analytics & Reports
        with tab4:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown("## 📊 Analytics & Reports")
            st.caption("Insights and statistics about your email campaign")
            
            # Overall campaign health
            st.markdown("### 🎯 Campaign Health")
            
            health_col1, health_col2, health_col3 = st.columns(3)
            
            with health_col1:
                completion_pct = (stats['completed'] / 52) * 100
                health_color = "#28a745" if completion_pct > 75 else "#ffc107" if completion_pct > 50 else "#dc3545"
                st.markdown(f"""
                <div style="background: {health_color}; padding: 2rem; border-radius: 12px; color: white; text-align: center;">
                    <h2>{completion_pct:.1f}%</h2>
                    <p>Campaign Completion</p>
                </div>
                """, unsafe_allow_html=True)
            
            with health_col2:
                avg_quality = "High" if stats['avg_html_length'] > 5000 else "Medium" if stats['avg_html_length'] > 2000 else "Low"
                quality_color = "#28a745" if avg_quality == "High" else "#ffc107" if avg_quality == "Medium" else "#dc3545"
                st.markdown(f"""
                <div style="background: {quality_color}; padding: 2rem; border-radius: 12px; color: white; text-align: center;">
                    <h2>{avg_quality}</h2>
                    <p>Content Quality</p>
                </div>
                """, unsafe_allow_html=True)
            
            with health_col3:
                weeks_ahead = stats['completed'] - (datetime.now().isocalendar()[1] % 52)
                ahead_color = "#28a745" if weeks_ahead > 4 else "#ffc107" if weeks_ahead > 0 else "#dc3545"
                st.markdown(f"""
                <div style="background: {ahead_color}; padding: 2rem; border-radius: 12px; color: white; text-align: center;">
                    <h2>{abs(weeks_ahead)}</h2>
                    <p>Weeks {'Ahead' if weeks_ahead >= 0 else 'Behind'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Detailed statistics
            st.markdown("### 📈 Detailed Statistics")
            
            stat_tab1, stat_tab2, stat_tab3 = st.tabs(["📊 Overview", "📅 Timeline", "📝 Content Analysis"])
            
            with stat_tab1:
                overview_col1, overview_col2 = st.columns(2)
                
                with overview_col1:
                    st.markdown("#### Campaign Progress")
                    
                    progress_data = {
                        "Status": ["Completed", "Pending", "Not Created"],
                        "Count": [stats['completed'], stats['pending'], 52 - stats['total']]
                    }
                    progress_df = pd.DataFrame(progress_data)
                    
                    st.dataframe(progress_df, use_container_width=True, hide_index=True)
                    
                    st.markdown("#### Content Metrics")
                    st.metric("Total HTML Content", f"{df['Complete_HTML_Code'].astype(str).str.len().sum():,} chars")
                    st.metric("Average per Email", f"{stats['avg_html_length']:,} chars")
                    st.metric("Largest Email", f"{df['Complete_HTML_Code'].astype(str).str.len().max():,} chars")
                    st.metric("Smallest Email", f"{df[df['Complete_HTML_Code'].astype(str).str.strip() != '']['Complete_HTML_Code'].astype(str).str.len().min():,} chars" if stats['completed'] > 0 else "N/A")
                
                with overview_col2:
                    st.markdown("#### Subject Line Analysis")
                    
                    # Emoji usage
                    emoji_count = sum(1 for title in df['Title'] if any(char for char in str(title) if ord(char) > 127))
                    st.metric("Emails with Emojis", f"{emoji_count} / {len(df)}")
                    
                    # Average title length
                    avg_title_len = df['Title'].astype(str).str.len().mean()
                    st.metric("Avg Title Length", f"{avg_title_len:.0f} chars")
                    
                    # Average subject length
                    avg_subject_len = df['Subject_Line'].astype(str).str.len().mean()
                    st.metric("Avg Subject Length", f"{avg_subject_len:.0f} chars")
                    
                    st.markdown("#### Most Common Words in Titles")
                    all_titles = " ".join(df['Title'].astype(str).tolist()).lower()
                    words = re.findall(r'\b[a-z]+\b', all_titles)
                    common_words = pd.Series(words).value_counts().head(10)
                    
                    if len(common_words) > 0:
                        for word, count in common_words.items():
                            st.markdown(f"- **{word}**: {count} times")
            
            with stat_tab2:
                st.markdown("#### 📅 Weekly Completion Timeline")
                
                # Create timeline view
                weeks_data = []
                for week in range(1, 53):
                    if week in df['Email_Number'].values:
                        email = df[df['Email_Number'] == week].iloc[0]
                        has_content = str(email['Complete_HTML_Code']).strip() != ''
                        status = "✅ Completed" if has_content else "📝 Draft"
                        weeks_data.append({
                            "Week": week,
                            "Title": email['Title'],
                            "Status": status
                        })
                    else:
                        weeks_data.append({
                            "Week": week,
                            "Title": "Not Created",
                            "Status": "❌ Missing"
                        })
                
                timeline_df = pd.DataFrame(weeks_data)
                
                # Display in groups of 13 (quarters)
                for quarter in range(4):
                    start_week = quarter * 13 + 1
                    end_week = min((quarter + 1) * 13, 52)
                    
                    st.markdown(f"**Q{quarter + 1}: Weeks {start_week}-{end_week}**")
                    quarter_df = timeline_df[(timeline_df['Week'] >= start_week) & (timeline_df['Week'] <= end_week)]
                    st.dataframe(quarter_df, use_container_width=True, hide_index=True, height=300)
            
            with stat_tab3:
                st.markdown("#### 📝 HTML Content Analysis")
                
                if stats['completed'] > 0:
                    # Analyze HTML patterns
                    completed_emails = df[df['Complete_HTML_Code'].astype(str).str.strip() != '']
                    
                    analysis_col1, analysis_col2 = st.columns(2)
                    
                    with analysis_col1:
                        st.markdown("**HTML Structure Patterns**")
                        
                        # Count common HTML elements
                        total_divs = completed_emails['Complete_HTML_Code'].astype(str).str.count('<div').sum()
                        total_ps = completed_emails['Complete_HTML_Code'].astype(str).str.count('<p').sum()
                        total_links = completed_emails['Complete_HTML_Code'].astype(str).str.count('<a ').sum()
                        total_images = completed_emails['Complete_HTML_Code'].astype(str).str.count('<img').sum()
                        
                        st.metric("Total <div> tags", int(total_divs))
                        st.metric("Total <p> tags", int(total_ps))
                        st.metric("Total <a> links", int(total_links))
                        st.metric("Total <img> images", int(total_images))
                    
                    with analysis_col2:
                        st.markdown("**Content Density**")
                        
                        # Calculate averages per email
                        st.metric("Avg divs per email", f"{total_divs/len(completed_emails):.1f}")
                        st.metric("Avg paragraphs per email", f"{total_ps/len(completed_emails):.1f}")
                        st.metric("Avg links per email", f"{total_links/len(completed_emails):.1f}")
                        st.metric("Avg images per email", f"{total_images/len(completed_emails):.1f}")
                    
                    st.markdown("---")
                    st.markdown("**HTML Quality Checks**")
                    
                    quality_issues = 0
                    for idx, email in completed_emails.iterrows():
                        issues = validate_html(str(email['Complete_HTML_Code']))
                        if not issues[0].startswith("✓"):
                            quality_issues += 1
                    
                    if quality_issues == 0:
                        st.success(f"✅ All {len(completed_emails)} completed emails passed validation!")
                    else:
                        st.warning(f"⚠️ {quality_issues} email(s) have validation issues")
                else:
                    st.info("Complete some newsletters to see content analysis")
            
            st.markdown("---")
            
            # Export reports
            st.markdown("### 📥 Export Reports")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                if st.button("📊 Export Statistics CSV", use_container_width=True):
                    stats_data = {
                        "Metric": ["Total Emails", "Completed", "Pending", "Progress %", "Avg HTML Length"],
                        "Value": [stats['total'], stats['completed'], stats['pending'], 
                                f"{stats['progress']:.1f}%", stats['avg_html_length']]
                    }
                    stats_export_df = pd.DataFrame(stats_data)
                    csv = stats_export_df.to_csv(index=False)
                    
                    st.download_button(
                        "💾 Download Stats CSV",
                        csv,
                        "newsletter_statistics.csv",
                        "text/csv",
                        key='download-stats-csv'
                    )
            
            with export_col2:
                if st.button("📧 Export All Emails List", use_container_width=True):
                    export_df = df[['Email_Number', 'Title', 'Subject_Line']].copy()
                    export_df['Status'] = df['Complete_HTML_Code'].apply(
                        lambda x: 'Completed' if str(x).strip() != '' else 'Pending'
                    )
                    csv = export_df.to_csv(index=False)
                    
                    st.download_button(
                        "💾 Download Email List",
                        csv,
                        "newsletter_list.csv",
                        "text/csv",
                        key='download-list-csv'
                    )
            
            with export_col3:
                if st.button("📋 Generate Full Report", use_container_width=True):
                    report = f"""
# 52 Week Email Newsletter Campaign Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Campaign Overview
- Total Emails Created: {stats['total']}
- Completed Emails: {stats['completed']}
- Pending Emails: {stats['pending']}
- Overall Progress: {stats['progress']:.1f}%
- Completion Rate: {stats['completion_rate']:.1f}%

## Content Metrics
- Total HTML Content: {df['Complete_HTML_Code'].astype(str).str.len().sum():,} characters
- Average HTML per Email: {stats['avg_html_length']:,} characters
- Emails with Emojis: {sum(1 for title in df['Title'] if any(char for char in str(title) if ord(char) > 127))}

## Campaign Health
- Weeks Behind/Ahead: {stats['completed'] - (datetime.now().isocalendar()[1] % 52)}
- Content Quality: {'High' if stats['avg_html_length'] > 5000 else 'Medium' if stats['avg_html_length'] > 2000 else 'Low'}

## Newsletter List
"""
                    for idx, email in df.iterrows():
                        status = "✅" if str(email['Complete_HTML_Code']).strip() != '' else "⏳"
                        report += f"\n{status} Week {email['Email_Number']}: {email['Title']}"
                    
                    st.download_button(
                        "💾 Download Report",
                        report,
                        "newsletter_full_report.txt",
                        "text/plain",
                        key='download-report-txt'
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 5: Bulk Operations
        with tab5:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.markdown("## ⚙️ Bulk Operations")
            st.caption("Perform operations on multiple newsletters at once")
            
            bulk_tab1, bulk_tab2, bulk_tab3 = st.tabs(["🔄 Bulk Update", "📥 Import/Export", "🗑️ Bulk Delete"])
            
            with bulk_tab1:
                st.markdown("### 🔄 Bulk Update Operations")
                st.info("💡 Select multiple newsletters and apply changes to all at once")
                
                # Multi-select
                selected_weeks = st.multiselect(
                    "Select weeks to update:",
                    options=df['Email_Number'].tolist(),
                    format_func=lambda x: f"Week {x} - {df[df['Email_Number']==x]['Title'].iloc[0]}"
                )
                
                if selected_weeks:
                    st.success(f"✅ {len(selected_weeks)} newsletters selected")
                    
                    # Bulk operations
                    st.markdown("#### Choose Operation:")
                    
                    bulk_operation = st.selectbox(
                        "Operation type:",
                        ["Add prefix to titles", "Add suffix to titles", "Update HTML header", "Update HTML footer", "Find and replace"]
                    )
                    
                    if bulk_operation == "Add prefix to titles":
                        prefix = st.text_input("Enter prefix to add:", placeholder="e.g., [UPDATED] ")
                        
                        if st.button("Apply Prefix", type="primary"):
                            try:
                                for week in selected_weeks:
                                    email = df[df['Email_Number'] == week].iloc[0]
                                    row_idx = df[df['Email_Number'] == week].index[0] + 2
                                    new_title = prefix + email['Title']
                                    st.session_state.worksheet.update(f'B{row_idx}', [[new_title]])
                                
                                st.success(f"✅ Updated {len(selected_weeks)} newsletters!")
                                log_activity("Bulk Update", f"Added prefix to {len(selected_weeks)} titles")
                                st.session_state.df = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    elif bulk_operation == "Add suffix to titles":
                        suffix = st.text_input("Enter suffix to add:", placeholder="e.g., - 2025")
                        
                        if st.button("Apply Suffix", type="primary"):
                            try:
                                for week in selected_weeks:
                                    email = df[df['Email_Number'] == week].iloc[0]
                                    row_idx = df[df['Email_Number'] == week].index[0] + 2
                                    new_title = email['Title'] + suffix
                                    st.session_state.worksheet.update(f'B{row_idx}', [[new_title]])
                                
                                st.success(f"✅ Updated {len(selected_weeks)} newsletters!")
                                log_activity("Bulk Update", f"Added suffix to {len(selected_weeks)} titles")
                                st.session_state.df = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    elif bulk_operation == "Find and replace":
                        find_col, replace_col = st.columns(2)
                        with find_col:
                            find_text = st.text_input("Find text:", placeholder="Text to find")
                        with replace_col:
                            replace_text = st.text_input("Replace with:", placeholder="Replacement text")
                        
                        target_field = st.selectbox(
                            "Apply to field:",
                            ["Title", "Subject_Line", "Complete_HTML_Code"]
                        )
                        
                        if st.button("Find and Replace", type="primary"):
                            if find_text:
                                try:
                                    updated_count = 0
                                    for week in selected_weeks:
                                        email = df[df['Email_Number'] == week].iloc[0]
                                        row_idx = df[df['Email_Number'] == week].index[0] + 2
                                        
                                        if target_field == "Title":
                                            new_value = str(email['Title']).replace(find_text, replace_text)
                                            st.session_state.worksheet.update(f'B{row_idx}', [[new_value]])
                                            updated_count += 1
                                        elif target_field == "Subject_Line":
                                            new_value = str(email['Subject_Line']).replace(find_text, replace_text)
                                            st.session_state.worksheet.update(f'C{row_idx}', [[new_value]])
                                            updated_count += 1
                                        elif target_field == "Complete_HTML_Code":
                                            new_value = str(email['Complete_HTML_Code']).replace(find_text, replace_text)
                                            st.session_state.worksheet.update(f'D{row_idx}', [[new_value]])
                                            updated_count += 1
                                    
                                    st.success(f"✅ Updated {updated_count} newsletters!")
                                    log_activity("Bulk Find/Replace", f"Replaced '{find_text}' in {updated_count} emails")
                                    st.session_state.df = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.warning("Please enter text to find")
                else:
                    st.info("Select newsletters above to perform bulk operations")
            
            with bulk_tab2:
                st.markdown("### 📥 Import & Export")
                
                import_export_tabs = st.tabs(["📤 Export All", "📥 Import from CSV", "🔄 Backup & Restore"])
                
                with import_export_tabs[0]:
                    st.markdown("#### Export All Newsletters")
                    st.caption("Download all your newsletters in various formats")
                    
                    export_format = st.radio(
                        "Select export format:",
                        ["CSV (Spreadsheet)", "JSON (Data)", "HTML (Individual Files)"],
                        horizontal=True
                    )
                    
                    if export_format == "CSV (Spreadsheet)":
                        if st.button("📥 Export to CSV", type="primary"):
                            csv_data = df.to_csv(index=False)
                            st.download_button(
                                "💾 Download CSV File",
                                csv_data,
                                "newsletters_export.csv",
                                "text/csv",
                                key='bulk-export-csv'
                            )
                            log_activity("Export", "Exported all newsletters to CSV")
                    
                    elif export_format == "JSON (Data)":
                        if st.button("📥 Export to JSON", type="primary"):
                            json_data = df.to_json(orient='records', indent=2)
                            st.download_button(
                                "💾 Download JSON File",
                                json_data,
                                "newsletters_export.json",
                                "application/json",
                                key='bulk-export-json'
                            )
                            log_activity("Export", "Exported all newsletters to JSON")
                    
                    elif export_format == "HTML (Individual Files)":
                        st.info("💡 This will create a ZIP file with individual HTML files for each newsletter")
                        if st.button("📥 Prepare HTML Export", type="primary"):
                            st.warning("⚠️ HTML bulk export functionality requires additional setup. Use the individual export feature in the Edit tab for now.")
                
                with import_export_tabs[1]:
                    st.markdown("#### Import Newsletters from CSV")
                    st.caption("Upload a CSV file to add multiple newsletters at once")
                    
                    st.markdown("""
                    **CSV Format Requirements:**
                    - Columns: `Email_Number`, `Title`, `Subject_Line`, `Complete_HTML_Code`
                    - Email_Number must be between 1-52
                    - No duplicate Email_Numbers
                    """)
                    
                    uploaded_csv = st.file_uploader("Upload CSV file", type=['csv'], key="csv_import")
                    
                    if uploaded_csv:
                        try:
                            import_df = pd.read_csv(uploaded_csv)
                            
                            st.markdown("**Preview:**")
                            st.dataframe(import_df.head(), use_container_width=True)
                            
                            st.markdown(f"**Found {len(import_df)} newsletters to import**")
                            
                            # Validate
                            required_cols = ['Email_Number', 'Title', 'Subject_Line', 'Complete_HTML_Code']
                            missing_cols = [col for col in required_cols if col not in import_df.columns]
                            
                            if missing_cols:
                                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                            else:
                                # Check for duplicates with existing data
                                existing_numbers = set(df['Email_Number'].tolist())
                                import_numbers = set(import_df['Email_Number'].tolist())
                                duplicates = existing_numbers.intersection(import_numbers)
                                
                                if duplicates:
                                    st.warning(f"⚠️ Warning: These weeks already exist: {sorted(duplicates)}")
                                    overwrite = st.checkbox("Overwrite existing newsletters?")
                                else:
                                    overwrite = False
                                
                                if st.button("🚀 Import Newsletters", type="primary"):
                                    try:
                                        imported = 0
                                        skipped = 0
                                        
                                        for idx, row in import_df.iterrows():
                                            week_num = row['Email_Number']
                                            
                                            if week_num in existing_numbers and not overwrite:
                                                skipped += 1
                                                continue
                                            
                                            if week_num in existing_numbers and overwrite:
                                                # Update existing
                                                row_idx = df[df['Email_Number'] == week_num].index[0] + 2
                                                st.session_state.worksheet.update(f'B{row_idx}:D{row_idx}', 
                                                    [[row['Title'], row['Subject_Line'], row['Complete_HTML_Code']]])
                                            else:
                                                # Add new
                                                st.session_state.worksheet.append_row([
                                                    int(week_num), row['Title'], row['Subject_Line'], row['Complete_HTML_Code']
                                                ])
                                            
                                            imported += 1
                                        
                                        st.success(f"✅ Imported {imported} newsletters! (Skipped {skipped})")
                                        log_activity("Import", f"Imported {imported} newsletters from CSV")
                                        st.session_state.df = None
                                        st.balloons()
                                        st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"❌ Import error: {str(e)}")
                        
                        except Exception as e:
                            st.error(f"❌ Error reading CSV: {str(e)}")
                
                with import_export_tabs[2]:
                    st.markdown("#### Backup & Restore")
                    st.caption("Create backups of your entire newsletter database")
                    
                    backup_col1, backup_col2 = st.columns(2)
                    
                    with backup_col1:
                        st.markdown("**Create Backup**")
                        
                        if st.button("💾 Create Full Backup", type="primary", use_container_width=True):
                            backup_data = {
                                'backup_date': datetime.now().isoformat(),
                                'total_newsletters': len(df),
                                'data': df.to_dict('records')
                            }
                            
                            backup_json = json.dumps(backup_data, indent=2)
                            
                            st.download_button(
                                "📥 Download Backup File",
                                backup_json,
                                f"newsletter_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                "application/json",
                                key='create-backup'
                            )
                            log_activity("Backup", "Created full backup")
                    
                    with backup_col2:
                        st.markdown("**Restore from Backup**")
                        
                        backup_file = st.file_uploader("Upload backup file", type=['json'], key="restore_backup")
                        
                        if backup_file:
                            try:
                                backup_data = json.load(backup_file)
                                
                                st.info(f"📅 Backup Date: {backup_data.get('backup_date', 'Unknown')}")
                                st.info(f"📊 Contains: {backup_data.get('total_newsletters', 0)} newsletters")
                                
                                if st.button("⚠️ Restore Backup", type="primary", use_container_width=True):
                                    st.warning("This will overwrite all current data!")
                                    st.info("Restore functionality requires careful implementation. Please export current data first!")
                            
                            except Exception as e:
                                st.error(f"Error reading backup: {str(e)}")
            
            with bulk_tab3:
                st.markdown("### 🗑️ Bulk Delete")
                st.warning("⚠️ **Warning:** Bulk delete operations are permanent!")
                
                delete_options = st.radio(
                    "Delete options:",
                    ["Delete selected newsletters", "Delete all pending", "Delete all completed", "Delete by week range"],
                    key="delete_options"
                )
                
                if delete_options == "Delete selected newsletters":
                    selected_delete = st.multiselect(
                        "Select newsletters to delete:",
                        options=df['Email_Number'].tolist(),
                        format_func=lambda x: f"Week {x} - {df[df['Email_Number']==x]['Title'].iloc[0]}"
                    )
                    
                    if selected_delete:
                        st.error(f"⚠️ You are about to delete {len(selected_delete)} newsletters!")
                        
                        confirm_text = st.text_input("Type 'DELETE' to confirm:")
                        
                        if confirm_text == "DELETE":
                            if st.button("🗑️ Confirm Delete", type="primary"):
                                try:
                                    # Sort in descending order to delete from bottom up
                                    for week in sorted(selected_delete, reverse=True):
                                        row_idx = df[df['Email_Number'] == week].index[0] + 2
                                        st.session_state.worksheet.delete_rows(row_idx)
                                    
                                    st.success(f"✅ Deleted {len(selected_delete)} newsletters!")
                                    log_activity("Bulk Delete", f"Deleted {len(selected_delete)} newsletters")
                                    st.session_state.df = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                
                elif delete_options == "Delete all pending":
                    pending_count = len(df[df['Complete_HTML_Code'].astype(str).str.strip() == ''])
                    
                    if pending_count > 0:
                        st.error(f"⚠️ This will delete {pending_count} pending newsletters!")
                        
                        confirm_text = st.text_input("Type 'DELETE PENDING' to confirm:")
                        
                        if confirm_text == "DELETE PENDING":
                            if st.button("🗑️ Delete All Pending", type="primary"):
                                st.info("This operation should be performed carefully. Consider exporting data first!")
                    else:
                        st.success("✅ No pending newsletters to delete!")
                
                elif delete_options == "Delete by week range":
                    range_col1, range_col2 = st.columns(2)
                    
                    with range_col1:
                        start_week = st.number_input("Start week:", min_value=1, max_value=52, value=1)
                    with range_col2:
                        end_week = st.number_input("End week:", min_value=1, max_value=52, value=52)
                    
                    if start_week <= end_week:
                        affected = df[(df['Email_Number'] >= start_week) & (df['Email_Number'] <= end_week)]
                        
                        st.error(f"⚠️ This will delete {len(affected)} newsletters (Weeks {start_week}-{end_week})!")
                        
                        if len(affected) > 0:
                            st.dataframe(affected[['Email_Number', 'Title']], use_container_width=True)
                            
                            confirm_text = st.text_input("Type 'DELETE RANGE' to confirm:")
                            
                            if confirm_text == "DELETE RANGE":
                                if st.button("🗑️ Delete Range", type="primary"):
                                    st.info("Range delete should be implemented with caution. Export your data first!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.error("❌ Failed to load data from Google Sheets. Please check your connection and try again.")

else:
    # Not authenticated - Welcome screen
    st.markdown("""
    <div class="info-box">
        <h2>👋 Welcome to the 52 Week Email Newsletter Manager Pro!</h2>
        <p>This comprehensive platform helps you manage your entire year of email newsletters in one place.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features showcase
    st.markdown("## ✨ Key Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        ### 📚 Library Management
        - Browse all 52 newsletters
        - Advanced search & filtering
        - Card, table, and list views
        - Live HTML preview
        - Export individual emails
        """)
    
    with feature_col2:
        st.markdown("""
        ### ✏️ Content Creation
        - Rich HTML editor
        - Template library
        - Live preview modes
        - HTML validation
        - Split-screen editing
        """)
    
    with feature_col3:
        st.markdown("""
        ### 📊 Analytics & Reporting
        - Campaign progress tracking
        - Content quality metrics
        - Timeline visualization
        - Export reports
        - Activity logging
        """)
    
    st.markdown("---")
    
    # Setup instructions
    with st.expander("🚀 Getting Started - Setup Instructions", expanded=True):
        st.markdown("""
        ### Step-by-Step Setup Guide
        
        #### 1️⃣ Create a Google Cloud Project
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Click "New Project" and give it a name
        3. Wait for the project to be created
        
        #### 2️⃣ Enable Required APIs
        1. In your project, go to **"APIs & Services"** > **"Library"**
        2. Search for and enable:
           - **Google Sheets API**
           - **Google Drive API**
        
        #### 3️⃣ Create Service Account
        1. Go to **"APIs & Services"** > **"Credentials"**
        2. Click **"Create Credentials"** > **"Service Account"**
        3. Fill in the service account details
        4. Click **"Create and Continue"**
        5. Skip the optional steps and click **"Done"**
        
        #### 4️⃣ Generate JSON Key
        1. Click on the service account you just created
        2. Go to the **"Keys"** tab
        3. Click **"Add Key"** > **"Create new key"**
        4. Select **JSON** format
        5. Click **"Create"** - the JSON file will download automatically
        
        #### 5️⃣ Share Your Spreadsheet
        1. Open your Google Sheets: [Your Sheet]({SHEET_URL})
        2. Click the **"Share"** button
        3. Paste the service account email (found in the JSON file as `client_email`)
        4. Give it **"Editor"** permissions
        5. Click **"Send"**
        
        #### 6️⃣ Upload JSON to This App
        1. Use the file uploader in the sidebar (👈)
        2. Select the JSON file you downloaded
        3. Wait for authentication to complete
        4. Start managing your newsletters! 🎉
        """)
    
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **Q: Is my data secure?**  
        A: Yes! All authentication happens through Google's secure OAuth2 system. Your credentials are never stored.
        
        **Q: Can multiple people use this?**  
        A: Yes! Share the Google Sheet with multiple service accounts or use the same JSON file across your team.
        
        **Q: What happens if I lose my JSON file?**  
        A: You can generate a new key from the Google Cloud Console, but you'll need to re-authenticate.
        
        **Q: Can I use this with multiple spreadsheets?**  
        A: Currently configured for one spreadsheet. You can modify the SHEET_ID in the code to switch spreadsheets.
        
        **Q: How do I backup my data?**  
        A: Use the "Bulk Operations" tab to create full backups in JSON format.
        
        **Q: What if I accidentally delete a newsletter?**  
        A: Regular backups are recommended. Google Sheets also has version history you can access.
        """)
    
    with st.expander("💡 Tips & Best Practices"):
        st.markdown("""
        - **Create templates:** Use the template system to maintain consistent branding
        - **Regular backups:** Export your data weekly using the Bulk Operations tab
        - **HTML validation:** Always validate your HTML before sending
        - **Preview on devices:** Test mobile, tablet, and desktop views
        - **Use emojis wisely:** They increase open rates but don't overuse them
        - **Keep it organized:** Use clear, descriptive titles for easy searching
        - **Track progress:** Check the Analytics tab regularly to stay on schedule
        - **Activity log:** Review the sidebar activity log to track changes
        """)
    
    st.markdown("---")
    
    # Connection info
    st.markdown("## 🔗 Spreadsheet Information")
    st.info(f"""
    **Connected Spreadsheet:**  
    🔗 [{SHEET_ID[:30]}...]({SHEET_URL})
    
    Click the link above to view your Google Sheet directly.
    """)
    
    st.markdown("---")
    
    # Call to action
    st.markdown("""
    <div class="info-box" style="text-align: center;">
        <h2>👈 Ready to Get Started?</h2>
        <p>Upload your Google Cloud service account JSON file in the sidebar to begin managing your newsletters!</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3>📧 52 Week Email Newsletter Manager Pro</h3>
    <p>Built with ❤️ using Streamlit | Powered by Google Sheets API</p>
    <p>Version 2.0 | © 2025 All Rights Reserved</p>
    <p style="margin-top: 1rem; font-size: 0.9rem;">
        <strong>Quick Links:</strong> 
        <a href="https://docs.google.com/spreadsheets" target="_blank">Google Sheets</a> | 
        <a href="https://console.cloud.google.com" target="_blank">Google Cloud</a> | 
        <a href="https://streamlit.io" target="_blank">Streamlit Docs</a>
    </p>
</div>
""", unsafe_allow_html=True)
