st.markdown("---")
        
        # Main tabs
        tab1, tab2, tab3 = st.tabs(["📚 Newsletter Library", "👁️ Email Preview", "📦 JSON Export"])
        
        with tab1:
            st.markdown("## 📚 Email Newsletter Library")
            
        
        with tab2:
            st.markdown("## 👁️ Email Preview")
            
        
        with tab3:
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
                    
                    ```json
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
