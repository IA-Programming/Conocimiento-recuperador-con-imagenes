# First
import os
import openai 
import streamlit as st
from app import generate_answer
from app import get_markdown_from_url
from app import create_index_from_text

if 'OpenAI_api_key' not in st.session_state:
    st.session_state.OpenAI_api_key = ''
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

st.set_page_config(
   page_title="WebChat Gpt App",
   page_icon="💻",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.title("Online Resources ChatBot:books:")
st.write("Enter multiple URL links and ask questions to the embedded data.")

#get user input for URLs
num_links = st.number_input("Enter the number of URLs:",min_value=1, max_value=1,value=1,step=1)

url_inputs = []
for i in range(num_links):
    url = st.text_input(f"Enter URL {i+1}:",key=f'url_{i}')
    url_inputs.append(url)

with st.sidebar:
    st.title('👋😁💬 Webchat App')
    if st.session_state['OpenAI_api_key'] not in st.session_state:
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
                st.info("Please add your OpenAI API key Correctly to continue.")
            except Exception as e:
                print(e)
                openai.api_key = ''
                st.session_state.OpenAI_api_key =''
                st.session_state.widget = ''

        APIKEY = st.text_input('OpenAI API Key', key='widget', on_change=submit, type="password")
        if st.button('Advanced Configuration 🚀') and APIKEY:
            with st.spinner('🚀 Ingresando en...'):
                st.experimental_rerun()        
    else:
        with st.expander('ℹ️ Configuracion Avanzada'):
            models = ["gpt-3.5-turbo","gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k" , "gpt-3.5-turbo-16k-0613", "gpt-4", "gpt-4-0613", "gpt-4-32k-0613"]
            modelos = openai.Model.list()
            # Extract the 'id' values from the JSON data
            model_ids = [entry["id"] for entry in modelos["data"]]

            # Create a new list with models that exist in the JSON data
            models = [model for model in models if model in model_ids]
            if 'model' not in st.session_state:
                st.session_state['model'] = st.selectbox('🔌 models', models, index=0)
            else:
                if st.session_state['model'] == "gpt-3.5-turbo":
                    st.session_state['model'] = st.selectbox('🔌 models', models, index=models.index(st.session_state['model']))

            temperature = st.slider('🌡 Temperatura', min_value=0.1, max_value=1.0, value=0.5, step=0.01)
            top_p = st.slider('💡 Top P', min_value=0.1, max_value=1.0, value=0.95, step=0.01)
            repetition_penalty = st.slider('🖌 Castigo por Repeticion', min_value=1.0, max_value=2.0, value=1.2, step=0.01)
            top_k = st.slider('❄️ Top K', min_value=1, max_value=100, value=50, step=1)
            max_new_tokens = st.slider('📝 Maximo token Nuevos', min_value=1, max_value=1024, value=1024, step=1)
            st.experimental_rerun()


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Write here your message", disabled=not st.session_state.OpenAI_api_key):

    st.write(models)

    # for item in url_inputs:
    #     markdown = get_markdown_from_url(item)
    #     index = create_index_from_text(markdown)

    # st.session_state.messages.append({"role": "user", "content": prompt})
    # st.chat_message("user").write(prompt)
    # response = generate_answer(prompt,index)
    # st.session_state.messages.append(response)
    # st.chat_message("assistant").write(response)