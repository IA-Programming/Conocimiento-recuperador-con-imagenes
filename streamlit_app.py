# First
import openai 
import streamlit as st


if 'OpenAI_api_key' not in st.session_state:
    st.session_state.OpenAI_api_key = ''
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

st.set_page_config(
   page_title="WebChat Gpt App",
   page_icon="🤖",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.title("Online Resources ChatBot:books:")
st.write("Enter multiple URL links and ask questions to the embedded data.")

#get user input for URLs
num_links = st.number_input("Enter the number of URLs:",min_value=1, max_value=3,value=1,step=1)

url_inputs = []
for i in range(num_links):
    url = st.text_input(f"Enter URL {i+1}:",key=f'url_{i}')
    url_inputs.append(url)

with st.sidebar:
    def submit():
        try:
            st.session_state.OpenAI_api_key = st.session_state.widget
            openai.api_key = st.session_state.OpenAI_api_key
            respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
            )
        except Exception as e:
            print(e)
            st.session_state.widget = ''
            st.info("Please add your OpenAI API key Correctly to continue.")


    st.text_input('OpenAI API Key', key='widget', on_change=submit, type="password")


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Write here your message", disabled=not st.session_state.OpenAI_api_key):

    openai.api_key = st.session_state.OpenAI_api_key
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = interpreter.chat(prompt)
    st.session_state.messages.append(response)
    st.chat_message("assistant").write(response)