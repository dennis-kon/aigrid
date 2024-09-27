# app.py

import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Attempt to import OpenAIError, fallback to Exception if not available
try:
    from openai.error import OpenAIError
except ImportError:
    OpenAIError = Exception

# Function to read API key from file
def load_api_key(file_path='api_key.txt'):
    try:
        with open(file_path, 'r') as file:
            key = file.read().strip()
            return key
    except FileNotFoundError:
        st.error(f"API key file '{file_path}' not found. Please ensure it exists.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the API key file: {e}")
        st.stop()

# Load the OpenAI API key
openai_api_key = load_api_key()

# Set the OpenAI API key
openai.api_key = openai_api_key

# Set page configuration
st.set_page_config(
    page_title="Excel Analyzer with ChatGPT",
    layout="wide",
)

# Optional: Apply custom CSS (if you created styles.css)
# Uncomment the following lines if you have a styles.css file
# def local_css(file_name):
#     with open(file_name) as f:
#         st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# local_css("styles.css")

# Title of the App
st.title("📊 Excel Analyzer with ChatGPT")

# File upload
uploaded_file = st.file_uploader(
    "Upload your Excel file",
    type=["xlsx", "xls"],
    help="Upload an Excel file to analyze.",
)

if uploaded_file is not None:
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)
        st.success("✅ Excel file successfully uploaded and read!")
        st.dataframe(df.head())

        # Input for questions
        st.header("📝 Define Your Questions")
        st.write("Enter the questions you want ChatGPT to analyze based on the Excel data.")
        questions = st.text_area(
            "Questions",
            value="1. Provide a summary of the data.\n2. Identify any trends or patterns.\n3. Highlight any anomalies.",
            height=150,
        )

        if st.button("Analyze with ChatGPT"):
            with st.spinner("🔍 Processing..."):
                try:
                    # Sample data if too large
                    if len(df) > 500:
                        df_sampled = df.sample(n=500)
                        st.warning("⚠️ Data is large! using a sample of 500 rows for analysis.")
                    else:
                        df_sampled = df

                    # Convert DataFrame to CSV string
                    csv_buffer = BytesIO()
                    df_sampled.to_csv(csv_buffer, index=False)
                    csv_string = csv_buffer.getvalue().decode()

                    # Prepare the prompt
                    prompt = (
                        "You are an analytical assistant. Based on the following data and questions, provide comprehensive findings.\n\n"
                        f"Data:\n{csv_string}\n\n"
                        f"Questions:\n{questions}\n\n"
                        "Findings:"
                    )

                    # Call OpenAI API
                    response = openai.ChatCompletion.create(
                        model="gpt-4",  # Ensure the model name is correct
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=2000,
                        temperature=0.6,
                    )

                    # Parse the response
                    findings = response['choices'][0]['message']['content'].strip()

                    st.header("🔍 Findings")
                    st.write(findings)

                except OpenAIError as e:
                    logger.error(f"OpenAI API error: {e}")
                    st.error(f"❌ OpenAI API returned an error: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    st.error(f"❌ An unexpected error occurred: {e}")

    except Exception as e:
        logger.error(f"Error reading the Excel file: {e}")
        st.error(f"❌ Error reading the Excel file: {e}")
else:
    st.info("📂 Awaiting Excel file upload.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        <p>© 2024 Excel Analyzer App. Powered by <a href="https://openai.com/" target="_blank">OpenAI</a> and <a href="https://streamlit.io/" target="_blank">Streamlit</a>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
