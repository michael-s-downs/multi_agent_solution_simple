import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from multi_agent_system import run_multi_agent

# Load environment variables
load_dotenv()

def main():
    st.title("Multi-Agent System - Web App Generator")
    st.write("Welcome to the Multi-Agent System that creates web applications!")
    
    # Sidebar for configuration
    st.sidebar.title("Configuration")
    st.sidebar.write("Make sure your Azure OpenAI credentials are configured in the .env file")
    
    # Check if environment variables are set
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}")
        st.stop()
    
    # Main interface
    st.header("Project Requirements")
    user_input = st.text_area(
        "Describe the web application you want to create:",
        placeholder="Example: Create a simple calculator app with buttons for basic arithmetic operations...",
        height=150
    )
    
    # Submit button
    if st.button("Generate Web Application", type="primary"):
        if not user_input.strip():
            st.warning("Please enter your requirements for the web application.")
            return
        
        # Show progress
        with st.spinner("Multi-agent system is working on your request..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Run the multi-agent system
                status_text.text("Initializing agents...")
                progress_bar.progress(10)
                
                status_text.text("Business Analyst analyzing requirements...")
                progress_bar.progress(30)
                
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                status_text.text("Software Engineer coding the application...")
                progress_bar.progress(60)
                
                history = loop.run_until_complete(run_multi_agent(user_input))
                
                status_text.text("Product Owner reviewing the code...")
                progress_bar.progress(90)
                
                progress_bar.progress(100)
                status_text.text("Complete!")
                
                st.success("Multi-agent system has completed the task!")
                
                # Display conversation history
                st.header("Agent Conversation History")
                for message in history:
                    with st.expander(f"{message.role} - {message.name or 'System'}"):
                        st.write(message.content)
                
                # Check if HTML file was generated
                if os.path.exists('index.html'):
                    st.success("✅ HTML file generated successfully!")
                    
                    # Show HTML preview
                    with open('index.html', 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    st.header("Generated HTML Code")
                    st.code(html_content, language='html')
                    
                    # Download button
                    st.download_button(
                        label="Download HTML File",
                        data=html_content,
                        file_name="index.html",
                        mime="text/html"
                    )
                    
                    # Show GitHub push script status
                    if os.path.exists('push_to_github.sh'):
                        st.info("📁 GitHub push script created: push_to_github.sh")
                        st.code("chmod +x push_to_github.sh && ./push_to_github.sh", language='bash')
                
                loop.close()
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()