import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# Page configuration
st.set_page_config(
    page_title="VIDeMI Email Newsletter Manager",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []
if 'service_account_info' not in st.session_state:
    st.session_state.service_account_info = None
if 'df' not in st.session_state:
    st.session_state.df = None

# Activity logging function
def log_activity(action, details):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.activity_log.append({
        'timestamp': timestamp,
        'action': action,
        'details': details
    })

# Header
st.markdown('<div class="main-header">📧 VIDeMI Email Newsletter Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Manage your 52-week email sequence with ease</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Google Sheets Setup
    st.markdown("### 🔗 Google Sheets Connection")
    
    with st.expander("📖 Setup Instructions", expanded=False):
        st.markdown("""
        **Steps to connect:**
        1. Create a Google Cloud project
        2. Enable Google Sheets API
        3. Create a service account
        4. Download the JSON key file
        5. Share your Google Sheet with the service account email
        6. Upload the JSON file below
        """)
    
    # Service account upload
    service_account_file = st.file_uploader(
        "Upload Service Account JSON",
        type=['json'],
        key="service_account_uploader",
        help="Upload your Google Cloud service account JSON file"
    )
    
    if service_account_file is not None:
        try:
            service_account_info = json.load(service_account_file)
            st.session_state.service_account_info = service_account_info
            st.success("✅ Service account loaded!")
        except Exception as e:
            st.error(f"❌ Error loading service account: {str(e)}")
    
    # Google Sheets URL
    sheets_url = st.text_input(
        "Google Sheets URL",
        value="https://docs.google.com/spreadsheets/d/1vzihyp5r1voFX6A7s2JPFAn1mMmSy75PRvLWQ0Y_6-s/edit?gid=2100751315#gid=2100751315",
        help="Paste your Google Sheets URL here"
    )
    
    # Extract spreadsheet ID and sheet ID
    if sheets_url:
        try:
            # Extract spreadsheet ID
            spreadsheet_id = sheets_url.split('/d/')[1].split('/')[0]
            
            # Extract sheet ID (gid)
            if 'gid=' in sheets_url:
                sheet_id = sheets_url.split('gid=')[1].split('#')[0].split('&')[0]
            else:
                sheet_id = '0'
            
            st.info(f"📊 Spreadsheet ID: `{spreadsheet_id[:20]}...`")
            st.info(f"📄 Sheet ID: `{sheet_id}`")
        except:
            st.warning("⚠️ Could not parse URL")
    
    # Image URLs
    st.markdown("---")
    st.markdown("### 🖼️ Email Images")
    
    header_img = st.text_input(
        "Header Image URL",
        value="https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-20-39.jpg"
    )
    
    footer_img = st.text_input(
        "Footer Image URL",
        value="https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-31-56.jpg"
    )
    
    # Pull from Google Sheets button
    st.markdown("---")
    if st.button("🔄 Pull from Google Sheets", type="primary", use_container_width=True):
        if not st.session_state.service_account_info:
            st.error("❌ Please upload service account JSON first!")
        elif not sheets_url:
            st.error("❌ Please enter Google Sheets URL!")
        else:
            try:
                with st.spinner("Loading data from Google Sheets..."):
                    # Setup credentials
                    scopes = [
                        'https://www.googleapis.com/auth/spreadsheets.readonly',
                        'https://www.googleapis.com/auth/drive.readonly'
                    ]
                    
                    creds = Credentials.from_service_account_info(
                        st.session_state.service_account_info,
                        scopes=scopes
                    )
                    
                    # Connect to Google Sheets
                    client = gspread.authorize(creds)
                    
                    # Open spreadsheet
                    spreadsheet = client.open_by_key(spreadsheet_id)
                    
                    # Get worksheet by ID
                    worksheet = None
                    for sheet in spreadsheet.worksheets():
                        if str(sheet.id) == sheet_id:
                            worksheet = sheet
                            break
                    
                    if not worksheet:
                        worksheet = spreadsheet.get_worksheet(0)
                    
                    # Get all values (to avoid truncation)
                    all_values = worksheet.get_all_values()
                    
                    if len(all_values) < 2:
                        st.error("❌ Sheet is empty or has no data rows!")
                    else:
                        # First row is headers
                        headers = all_values[0]
                        data_rows = all_values[1:]
                        
                        # Create dataframe
                        df = pd.DataFrame(data_rows, columns=headers)
                        
                        # Convert Email_Number to int
                        df['Email_Number'] = pd.to_numeric(df['Email_Number'], errors='coerce')
                        df = df.dropna(subset=['Email_Number'])
                        df['Email_Number'] = df['Email_Number'].astype(int)
                        
                        # Sort by email number
                        df = df.sort_values('Email_Number')
                        
                        # Store in session state
                        st.session_state.df = df
                        
                        st.success(f"✅ Loaded {len(df)} emails from Google Sheets!")
                        log_activity("Google Sheets", f"Loaded {len(df)} emails")
                        
                        # Show first email HTML length for debugging
                        if len(df) > 0:
                            first_html = str(df.iloc[0]['Complete_HTML_Code'])
                            st.info(f"📏 First email HTML length: {len(first_html):,} characters")
                        
                        st.rerun()
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                log_activity("Error", f"Failed to load from Google Sheets: {str(e)}")

# Main content
if st.session_state.df is None:
    st.info("👆 Please connect to Google Sheets using the sidebar to get started.")
    st.markdown("---")
    st.markdown("""
    ### 📋 Getting Started
    
    1. **Upload Service Account JSON** - Get this from Google Cloud Console
    2. **Enter Google Sheets URL** - Your email sequence spreadsheet
    3. **Click "Pull from Google Sheets"** - Load your email data
    
    Your Google Sheet should have these columns:
    - `Email_Number` - Sequential number (1-52)
    - `Title` - Email title for reference
    - `Subject_Line` - Email subject line
    - `Complete_HTML_Code` - Full HTML email content
    """)
else:
    df = st.session_state.df
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📚 Newsletter Library", 
        "👁️ Email Preview", 
        "📊 Analytics", 
        "⚙️ Bulk Operations",
        "📅 Schedule Calculator",
        "📦 JSON Export"
    ])
    
    with tab1:
        st.markdown("## 📚 Email Newsletter Library")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search emails", placeholder="Search by title or subject...")
        with col2:
            filter_status = st.selectbox("Filter by status", ["All", "Has Content", "Empty"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Email Number", "Title"])
        
        # Filter dataframe
        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[
                filtered_df['Title'].str.contains(search_term, case=False, na=False) |
                filtered_df['Subject_Line'].str.contains(search_term, case=False, na=False)
            ]
        
        if filter_status == "Has Content":
            filtered_df = filtered_df[filtered_df['Complete_HTML_Code'].notna() & (filtered_df['Complete_HTML_Code'] != '')]
        elif filter_status == "Empty":
            filtered_df = filtered_df[filtered_df['Complete_HTML_Code'].isna() | (filtered_df['Complete_HTML_Code'] == '')]
        
        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} emails**")
        st.markdown("---")
        
        for idx, row in filtered_df.iterrows():
            email_num = int(row['Email_Number'])
            title = str(row['Title'])
            subject = str(row['Subject_Line'])
            html_code = str(row['Complete_HTML_Code']).strip()
            has_content = bool(html_code and html_code != 'nan')
            
            with st.expander(f"📧 Email #{email_num}: {title}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Subject:** {subject}")
                    st.markdown(f"**Status:** {'✅ Has Content' if has_content else '⚠️ Empty'}")
                    if has_content:
                        html_length = len(html_code)
                        word_count = len(html_code.split())
                        st.markdown(f"**Length:** {html_length:,} characters, ~{word_count:,} words")
                
                with col2:
                    if has_content:
                        if st.button(f"👁️ Preview", key=f"preview_{email_num}"):
                            st.session_state.preview_email_num = email_num
                            st.rerun()
                
                if has_content:
                    with st.expander("📄 View HTML Source", expanded=False):
                        st.code(html_code[:1000] + ("..." if len(html_code) > 1000 else ""), language='html')
    
    with tab2:
        st.markdown("## 👁️ Email Preview")
        
        email_numbers = df['Email_Number'].tolist()
        
        # Check if preview was triggered from library
        default_index = 0
        if 'preview_email_num' in st.session_state:
            try:
                default_index = email_numbers.index(st.session_state.preview_email_num)
            except ValueError:
                pass
        
        selected_email_num = st.selectbox(
            "Select email to preview:",
            email_numbers,
            index=default_index,
            format_func=lambda x: f"Email #{x}: {df[df['Email_Number']==x]['Title'].iloc[0]}"
        )
        
        # Get selected email data
        selected_row = df[df['Email_Number'] == selected_email_num].iloc[0]
        email_title = str(selected_row['Title'])
        email_subject = str(selected_row['Subject_Line'])
        email_html = str(selected_row['Complete_HTML_Code']).strip()
        
        st.markdown(f"### {email_title}")
        st.markdown(f"**Subject:** {email_subject}")
        st.markdown("---")
        
        if email_html and email_html != 'nan':
            preview_tab1, preview_tab2 = st.tabs(["🖼️ Rendered Email", "📝 HTML Source"])
            
            with preview_tab1:
                st.markdown("#### Email Preview (as recipients will see it)")
                components.html(email_html, height=1400, scrolling=True)
            
            with preview_tab2:
                st.markdown("#### HTML Source Code")
                st.code(email_html, language='html')
                
                # Download button
                st.download_button(
                    label="📥 Download HTML",
                    data=email_html.encode('utf-8'),
                    file_name=f"email_{selected_email_num}_{email_title.replace(' ', '_')}.html",
                    mime="text/html",
                    use_container_width=True
                )
        else:
            st.warning("⚠️ This email has no content yet.")
    
    with tab3:
        st.markdown("## 📊 Analytics Dashboard")
        
        total_emails = len(df)
        emails_with_content = len(df[df['Complete_HTML_Code'].notna() & (df['Complete_HTML_Code'] != '')])
        emails_empty = total_emails - emails_with_content
        completion_rate = (emails_with_content / total_emails * 100) if total_emails > 0 else 0
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Emails", total_emails)
        with col2:
            st.metric("With Content", emails_with_content)
        with col3:
            st.metric("Empty", emails_empty)
        with col4:
            st.metric("Completion", f"{completion_rate:.1f}%")
        
        st.markdown("---")
        
        # Content statistics
        st.markdown("### 📝 Content Statistics")
        
        content_stats = []
        for idx, row in df.iterrows():
            html_code = str(row['Complete_HTML_Code']).strip()
            if html_code and html_code != 'nan':
                char_count = len(html_code)
                word_count = len(html_code.split())
                # Estimate reading time (200 words per minute)
                reading_time = word_count / 200
                
                content_stats.append({
                    'Email': int(row['Email_Number']),
                    'Title': str(row['Title']),
                    'Characters': char_count,
                    'Words': word_count,
                    'Reading Time (min)': round(reading_time, 1)
                })
        
        if content_stats:
            stats_df = pd.DataFrame(content_stats)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Average Statistics")
                avg_chars = stats_df['Characters'].mean()
                avg_words = stats_df['Words'].mean()
                avg_reading = stats_df['Reading Time (min)'].mean()
                
                st.metric("Avg Characters", f"{avg_chars:,.0f}")
                st.metric("Avg Words", f"{avg_words:,.0f}")
                st.metric("Avg Reading Time", f"{avg_reading:.1f} min")
            
            with col2:
                st.markdown("#### Content Range")
                min_words = stats_df['Words'].min()
                max_words = stats_df['Words'].max()
                
                st.metric("Shortest Email", f"{min_words:,} words")
                st.metric("Longest Email", f"{max_words:,} words")
            
            st.markdown("---")
            st.markdown("#### Detailed Statistics")
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        else:
            st.info("No content statistics available yet.")
        
        # Validation
        st.markdown("---")
        st.markdown("### ✅ Validation Check")
        
        validation_issues = []
        for idx, row in df.iterrows():
            email_num = int(row['Email_Number'])
            subject = str(row['Subject_Line'])
            html_code = str(row['Complete_HTML_Code']).strip()
            
            # Check for issues
            if not subject or subject == 'nan':
                validation_issues.append(f"Email #{email_num}: Missing subject line")
            elif len(subject) > 100:
                validation_issues.append(f"Email #{email_num}: Subject line too long ({len(subject)} chars)")
            
            if not html_code or html_code == 'nan':
                validation_issues.append(f"Email #{email_num}: Missing HTML content")
        
        if validation_issues:
            st.warning(f"⚠️ Found {len(validation_issues)} issues:")
            for issue in validation_issues:
                st.markdown(f"- {issue}")
        else:
            st.success("✅ All emails passed validation!")
    
    with tab4:
        st.markdown("## ⚙️ Bulk Operations")
        
        st.markdown("### 🔄 Bulk Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export Options")
            
            if st.button("📥 Export All as CSV Summary", use_container_width=True):
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="videmi_email_summary.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                log_activity("CSV Export", "Exported all emails as CSV")
            
            if st.button("📊 Generate Statistics Report", use_container_width=True):
                report = f"""
# VIDeMI Email Sequence Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Emails: {len(df)}
- With Content: {emails_with_content}
- Empty: {emails_empty}
- Completion Rate: {completion_rate:.1f}%

## Email List
"""
                for idx, row in df.iterrows():
                    email_num = int(row['Email_Number'])
                    title = str(row['Title'])
                    subject = str(row['Subject_Line'])
                    has_content = bool(str(row['Complete_HTML_Code']).strip() and str(row['Complete_HTML_Code']).strip() != 'nan')
                    report += f"\n{email_num}. {title}\n   Subject: {subject}\n   Status: {'✅ Complete' if has_content else '⚠️ Empty'}\n"
                
                st.download_button(
                    label="Download Report",
                    data=report.encode('utf-8'),
                    file_name="videmi_email_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                log_activity("Report", "Generated statistics report")
        
        with col2:
            st.markdown("#### Data Management")
            
            if st.button("🔄 Refresh from Google Sheets", use_container_width=True):
                st.rerun()
            
            if st.button("📋 View Activity Log", use_container_width=True):
                st.session_state.show_activity_log = True
        
        # Activity log display
        if st.session_state.get('show_activity_log', False):
            st.markdown("---")
            st.markdown("### 📋 Recent Activity")
            
            if st.session_state.activity_log:
                for activity in reversed(st.session_state.activity_log[-20:]):
                    st.markdown(f"**{activity['timestamp']}** - {activity['action']}: {activity['details']}")
            else:
                st.info("No activity logged yet.")
            
            if st.button("Close Activity Log"):
                st.session_state.show_activity_log = False
                st.rerun()
    
    with tab5:
        st.markdown("## 📅 Schedule Calculator")
        
        st.markdown("Calculate when each email will be sent based on a start date.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Campaign Start Date:",
                value=datetime.now().date()
            )
        
        with col2:
            interval_days = st.number_input(
                "Days between emails:",
                min_value=1,
                max_value=30,
                value=7,
                help="Default is 7 days (weekly)"
            )
        
        if st.button("📅 Calculate Schedule", type="primary", use_container_width=True):
            schedule_data = []
            
            for idx, row in df.iterrows():
                email_num = int(row['Email_Number'])
                title = str(row['Title'])
                subject = str(row['Subject_Line'])
                
                # Calculate send date
                days_offset = (email_num - 1) * interval_days
                send_date = start_date + timedelta(days=days_offset)
                
                schedule_data.append({
                    'Email #': email_num,
                    'Title': title,
                    'Subject': subject,
                    'Send Date': send_date.strftime('%Y-%m-%d'),
                    'Day of Week': send_date.strftime('%A'),
                    'Days from Start': days_offset
                })
            
            schedule_df = pd.DataFrame(schedule_data)
            
            st.markdown("---")
            st.markdown("### 📅 Email Schedule")
            st.dataframe(schedule_df, use_container_width=True, hide_index=True)
            
            # Download schedule
            csv_schedule = schedule_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Schedule as CSV",
                data=csv_schedule,
                file_name=f"videmi_email_schedule_{start_date}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Summary
            end_date = start_date + timedelta(days=(len(df) - 1) * interval_days)
            total_days = (end_date - start_date).days
            
            st.markdown("---")
            st.markdown("### 📊 Campaign Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Start Date", start_date.strftime('%Y-%m-%d'))
            with col2:
                st.metric("End Date", end_date.strftime('%Y-%m-%d'))
            with col3:
                st.metric("Total Duration", f"{total_days} days")
            
            log_activity("Schedule", f"Calculated schedule starting {start_date}")
    
    with tab6:
        st.markdown("## 📦 JSON Export")
        st.markdown("Export your email sequence in the exact JSON format for email automation systems.")
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            export_count = st.selectbox(
                "Number of emails to export:",
                [3, 5, 10, 21, 52, "All"],
                index=5
            )
        
        with col2:
            json_format = st.selectbox(
                "JSON Format:",
                ["Pretty (Readable)", "Compact (Minified)"],
                index=0
            )
        
        st.markdown("---")
        
        # Generate JSON button
        if st.button("🔄 Generate JSON", type="primary", use_container_width=True):
            try:
                # Determine how many emails to export
                if export_count == "All":
                    export_df = df.copy()
                else:
                    export_df = df.head(export_count)
                
                # Build JSON structure
                emails_list = []
                
                for idx, row in export_df.iterrows():
                    email_num = int(row['Email_Number'])
                    html_code = str(row['Complete_HTML_Code']).strip()
                    
                    # Calculate delay (weekly sequence: 0, 7, 14, 21, etc.)
                    delay_days = (email_num - 1) * 7
                    
                    # Determine status
                    status = "active" if (html_code and html_code != 'nan') else "draft"
                    
                    email_obj = {
                        "id": email_num,
                        "subject": str(row['Subject_Line']),
                        "email_body": html_code if (html_code and html_code != 'nan') else "",
                        "delay_days": delay_days,
                        "status": status
                    }
                    
                    emails_list.append(email_obj)
                
                # Create final JSON structure
                json_data = {
                    "emails": emails_list
                }
                
                # Format JSON
                if json_format == "Pretty (Readable)":
                    json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
                else:
                    json_string = json.dumps(json_data, ensure_ascii=False)
                
                # Store in session state
                st.session_state.generated_json = json_string
                st.session_state.json_email_count = len(emails_list)
                
                st.success(f"✅ Successfully generated JSON with {len(emails_list)} emails!")
                log_activity("JSON Export", f"Generated JSON with {len(emails_list)} emails")
                
            except Exception as e:
                st.error(f"❌ Error generating JSON: {str(e)}")
                log_activity("Error", f"JSON generation failed: {str(e)}")
        
        # Display and download JSON
        if 'generated_json' in st.session_state:
            st.markdown("---")
            st.markdown("### 📄 Generated JSON")
            
            # Stats
            json_size = len(st.session_state.generated_json)
            email_count = st.session_state.json_email_count
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric("Emails", email_count)
            with stat_col2:
                st.metric("Size", f"{json_size:,} chars")
            with stat_col3:
                st.metric("Format", json_format.split()[0])
            
            # Preview
            with st.expander("👁️ Preview JSON", expanded=False):
                st.code(st.session_state.generated_json[:2000] + ("..." if json_size > 2000 else ""), language='json')
                if json_size > 2000:
                    st.caption(f"Showing first 2,000 of {json_size:,} characters")
            
            # Download button
            st.download_button(
                label="📥 Download JSON File",
                data=st.session_state.generated_json.encode('utf-8'),
                file_name=f"videmi_email_sequence_{email_count}_emails.json",
                mime="application/json",
                type="primary",
                use_container_width=True
            )
