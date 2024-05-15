import streamlit as st
from openai import OpenAI

api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Hello! I'm your Finance Bot, an expert in stock market analysis. "
                                        "I specialize in detailed technical and fundamental analysis to provide precise insights. "
                                        "Whether you need help understanding stock charts, predicting upcoming market trends, "
                                        "analyzing company financials, or seeking personalized investment strategies, I'm here to assist. "
                                        "Please tell me about your current financial interests or ask a question directly related to your investment needs."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    st.title('Finance Chatbot with OpenAI GPT')
    user_input = st.text_input("Enter your question:", placeholder="Ask me about stocks, market trends, etc.")
    
    if st.button('Submit'):
        with st.spinner('Generating response...'):
            response = chat_with_gpt(user_input)
            st.write("Chatbot:", response)

if __name__ == "_main_":
    main()