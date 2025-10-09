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
                        status = "active" if html_code else "draft"
                        
                        email_obj = {
                            "id": email_num,
                            "subject": str(row['Subject_Line']),
                            "email_body": html_code if html_code else "",
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
                
                st.markdown("---")
                
                # JSON structure info
                with st.expander("ℹ️ JSON Structure Information"):
                    st.markdown("""
                    ### JSON Format
                    
                    The exported JSON follows this exact structure:
                    
                    \`\`\`json
                    {
                      "emails": [
                        {
                          "id": 1,
                          "subject": "Email subject line",
                          "email_body": "Complete HTML code",
                          "delay_days": 0,
                          "status": "active"
                        }
                      ]
                    }
                    """)
