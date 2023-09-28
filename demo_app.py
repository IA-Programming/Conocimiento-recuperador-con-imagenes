import os
import openai
import random
import shutil
import string
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit as st
from streamlit.components.v1 import html
from app import get_markdown_from_url
from app import create_nodes_from_text
from llama_index import VectorStoreIndex
from datetime import datetime
now = datetime.now()

def prompt4conversation(prompt,context):
    final_prompt = f"""INFORMACION GENERAL : ( hoy es {now.strftime('%d/%m/%Y %H:%M:%S')} , Tu fuiste creado por IA-Programming el propietario de BlazzmoCompany
                    INSTRUCCION : EN TU RESPUESTA NUNCA INCLUYAS LA PREGUNTA DEL USUARIO O MENSAJE , ESCRIBE SIEMPRE SOLO UNA EXACTA RESPUESTA!
                    PREVIOS MENSAJES : ({context})
                    AHORA LA PREGUNTA DEL USUARIO : {prompt}) .
                    ESCRIBE LA RESPUESTA : """ 
    return final_prompt

def prompt4Context(prompt, context, solution):
    final_prompt = f"""INFORMACIÓN GENERAL: Usted está construido por IA-Programming, el propietario de BlazzmoCompany
                    INSTRUCCIÓN : EN SU RESPUESTA NUNCA INCLUYA LA PREGUNTA O MENSAJE DEL USUARIO, ¡ESCRIBA SIEMPRE SOLO SU RESPUESTA PRECISA!
                    MENSAJE ANTERIOR : ({context})
                    AHORA EL USUARIO PREGUNTA : {prompt}
                    ESTA ES LA RESPUESTA CORRECTA : ({solution})
                    SIN CAMBIAR NADA DE LA RESPUESTA CORRECTA, HAGA LA RESPUESTA MÁS DETALLADA:"""
    return final_prompt

st.set_page_config(
   page_title="WebChat App",
   page_icon="💻",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.markdown('<style>.css-w770g5{\
            width: 100%;}\
            .css-b3z5c9{    \
            width: 100%;}\
            .stButton>button{\
            width: 100%;}\
            .stDownloadButton>button{\
            width: 100%;}\
            </style>', unsafe_allow_html=True)

st.markdown('<style>.stChatMessage.stMarkdown{\
            overflow:hidden;\
            width:100%;}\
            img{\
            max-width: 100%;\
            height: auto\
            }\
            </style>', unsafe_allow_html=True)

# Sidebar contents for logIN, choose plugin, and export chat
with st.sidebar:
    st.title('👋😁💬 Webchat App')
    
    if 'openai_api_key' not in st.session_state:
        with st.expander("ℹ️ Coloca tu OpenAI API", expanded=True):
            st.write("⚠️ Tu necesitas colocar tu OpenAI Apikey. puedes conseguirlo [aqui](https://platform.openai.com/account/api-keys).")
            st.header('OpenAI API Key')
            def submit():
                
                if not (st.session_state.widget.startswith('sk-') and len(st.session_state.widget)==51):
                    st.session_state.widget = ''
                    openai.api_key = ''
                    st.warning('Please enter your credentials!', icon='⚠️')
                else:
                    st.success('Proceed to entering your prompt message!', icon='👉')

            openai_api_key = st.text_input('Enter OpenAI API token:', key='widget', on_change=submit, type="password")
            if st.button('Validate 🚀') and openai_api_key: 
                with st.spinner('🚀 Validando en...'):
                    st.session_state['openai_api_key']=st.session_state.widget

                    try:
                        openai.api_key = st.session_state.openai_api_key
                        respuesta = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-16k-0613",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "Hello!"}
                        ]
                        )
                        
                    except Exception as e:
                        st.error(e)
                        st.info("⚠️ Por favor revisa tus credenciales y intenta otra vez.")
                        st.warning("⚠️ Si tu no tienes una cuenta, te puedes registrar [here](https://platform.openai.com/account/api-keys).")
                        from time import sleep
                        sleep(3)
                        del st.session_state['openai_api_key']
                        st.rerun()
                    
                    st.rerun()
                    
    else:
        with st.expander("ℹ️ Configuracion Avanzada"):
            os.environ["OPENAI_API_KEY"] = st.session_state['openai_api_key']

            # Generate empty lists for generated and past.
            ## generated stores AI generated responses
            if 'generated' not in st.session_state:
                st.session_state['generated'] = ["Yo soy **IA ITALIA chat**, Como puedo ayudarte? "]
            ## past stores User's questions
            if 'past' not in st.session_state:
                st.session_state['past'] = ['Hola!']

            st.session_state['LLM'] =  ChatOpenAI()

            models = ["gpt-3.5-turbo","gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k" , "gpt-3.5-turbo-16k-0613", "gpt-4", "gpt-4-0613", "gpt-4-32k-0613"]
            modelos = openai.Model.list(api_key=st.session_state['openai_api_key'])
            # Extract the 'id' values from the JSON data
            model_ids = [entry["id"] for entry in modelos["data"]]

            # Create a new list with models that exist in the JSON data
            models = [model for model in models if model in model_ids]
            model = "gpt-3.5-turbo"
            model = st.selectbox('🔌 models', models, index=models.index(model))

            temperature = st.slider('🌡 Temperatura', min_value=0.1, max_value=1.0, value=0.5, step=0.01)
            top_p = st.slider('💡 Top P', min_value=0.1, max_value=1.0, value=0.95, step=0.01)
            repetition_penalty = st.slider('🖌 Castigo por Repeticion', min_value=1.0, max_value=2.0, value=1.2, step=0.01)
            Presence_penalty = st.slider('❄️ Presence penalty', min_value=1.0, max_value=2.0, value=1.2, step=0.01)
            max_new_tokens = st.slider('📝 Maximo token Nuevos', min_value=1, max_value=1024, value=1024, step=1)

        st.session_state['chatbot'] = ChatOpenAI(model=model, temperature=temperature, max_tokens=max_new_tokens, model_kwargs= {'top_p':top_p, 'frequency_penalty': repetition_penalty, 'presence_penalty': Presence_penalty}, verbose=True)
        
        #plugins for conversation
        plugins = ["🛑 No PLUGIN", "🔗 Habla usando links"]
        if 'plugin' not in st.session_state:
            st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=0)
        else:
            if st.session_state['plugin'] == "🛑 No PLUGIN":
                st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=plugins.index(st.session_state['plugin']))

# WEBSITE PLUGIN
        if st.session_state['plugin'] == "🔗 Habla usando links" and 'web_sites' not in st.session_state:
            with st.expander("🔗 Habla usando links", expanded=True):
                #get user input for URLs
                num_links = st.number_input("Enter the number of URLs(max 5 urls):", min_value=1, max_value=5, value=1,step=1)

                url_inputs = []
                for i in range(num_links):
                    url = st.text_input(f"Enter URL {i+1}:",key=f'url_{i}')
                    if url:
                        url_inputs.append(url)
                if url_inputs is not None and st.button('🔗✅ Añade website al contexto'):
                    if url_inputs != []:
                        #max 10 websites
                        Markdown = []
                        with st.spinner('🔗 Extrayendo TEXTO de Websites ...'):
                            for url in url_inputs:
                                Markdown.append(get_markdown_from_url(url))

                            nodes = create_nodes_from_text(Markdown,url)
                            
                            text = [node.text for node in nodes]
                            # creating a vectorstore

                        with st.spinner('🔗 Creando Vectorstore...'):
                            # Create a vectorstore from documents
                            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                            # build index
                            db = VectorStoreIndex(nodes=nodes)
                            # random_str = 'T0YMOIBZCF'
                            # from llama_index import StorageContext, load_index_from_storage
                            # # rebuild storage context
                            # storage_context = StorageContext.from_defaults(persist_dir="./storage" + random_str)
                            # # load index
                            # db = load_index_from_storage(storage_context)
                            print("Index created!")
                        with st.spinner('🔗 Salvando Vectorstore...'):
                            # save vectorstore
                            db.storage_context.persist(persist_dir="./storage" + random_str)
                            #create .zip file of directory to download
                            shutil.make_archive("./storage" + random_str, 'zip', "./storage" + random_str)
                            # save in session state and download
                            st.session_state['db'] = "./storage" + random_str + ".zip" 
                        
                        with st.spinner('🔗 Creando cadena de QA...'):
                            # Create retriever interface
                            st.session_state['retriever'] = db.as_retriever()
                            # Create QA chain
                            template = """
                            CONTEXT: {docs}
                            You are a helpful assistant, above is some context, 
                            Please answer the question, and make sure you follow ALL of the rules below:
                            1. Answer the questions only based on context provided, do not make things up
                            2. Answer questions in a helpful manner that straight to the point, with clear structure & all relevant information that might help users answer the question
                            3. Anwser should be formatted in Markdown
                            4. If there are relevant images, video, links, they are very important reference data, please include them as part of the answer
                            5: ***You always answer, to my question in the language that the answer is formulate it***.

                            QUESTION: {query}
                            ANSWER (formatted in Markdown):
                            """
                            prompt = ChatPromptTemplate.from_template(template)
                            qa = prompt | st.session_state['LLM']
                            st.session_state['web_sites'] = qa
                            st.session_state['web_text'] = text
                        st.rerun()
        
        if st.session_state['plugin'] == "🔗 Habla usando links":
            if 'db' in st.session_state:
                # leave ./ from name for download
                file_name = st.session_state['db'][2:]
                st.download_button(
                    label="📩 Descargar vectorstore",
                    data=open(file_name, 'rb').read(),
                    file_name=file_name,
                    mime='application/zip'
                )

            if st.button('🛑🔗 Remover Website del contexto'):
                if 'web_sites' in st.session_state:
                    del st.session_state['db']
                    del st.session_state['retriever']
                    del st.session_state['web_sites']
                    del st.session_state['web_text']
                del st.session_state['plugin']
                st.rerun()


# END OF PLUGIN
    add_vertical_space(4)
    if 'openaiapikey' in st.session_state:
        if st.button('🗑 Salir'):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.rerun()
    add_vertical_space(1)

    html_chat = '<center><h6>🤗 Soporta el proyecto con una donación para el desarrollo de nuevas Características 🤗</h6>'
    st.markdown(html_chat, unsafe_allow_html=True)
    button = '<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="blazzmocompany" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>'
    html(button, height=70, width=220)
    iframe = '<style>iframe[width="220"]{position: absolute; top: 50%;left: 50%;transform: translate(-50%, -50%);margin:26px 0}</style>'
    st.markdown(iframe, unsafe_allow_html=True)
    add_vertical_space(2)
    st.write('<center><h6>Hecho con ❤️ por <a href="mailto:blazzmo.company@gmail.com">AI-Programming</a></h6>',unsafe_allow_html=True)

##### End of sidebar


# User input
# Layout of input/response containers
input_container = st.container()
response_container = st.container()
data_view_container = st.container()
loading_container = st.container()


## Applying the User input box
with input_container:
    if 'openai_api_key' in st.session_state:
        input_text = st.chat_input("🧑‍💻 Escribe aqui 👇", key="input", disabled=not st.session_state['openai_api_key'])
    else:
        input_text = st.chat_input("🧑‍💻 Escribe aqui 👇", key="input", disabled=True)

with data_view_container:
    if 'web_text' in st.session_state:
        with st.expander("🤖 View the **Website content**"):
            st.write(st.session_state['web_text'])

# Response output
## Function for taking User prompt as input followed by producing AI generated responses
def generate_response(prompt):
    final_prompt =  ""
    make_better = True
    source = ""

    with loading_container:

        if st.session_state['plugin'] == "🔗 Habla usando links" and 'web_sites' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Usando herramienta para conseguir informacion...'):
                nodes = st.session_state['retriever'].retrieve(prompt)
                texts = [node.node.text for node in nodes]
                print("Retrieved texts!")
                result = st.session_state['web_sites'].invoke({"docs": texts, "query": prompt})
                solution = result.content
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if len(texts) > 0:
                        final_prompt += "\n\n✅Fuente:\n" 
                        for d in texts:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Context(prompt, context, solution)
                    if len(texts) > 0:
                        source += "\n\n✅Fuente:\n"
                        for d in texts:
                            source += "- " + str(d) + "\n"
                    
        else:
            #get last message if exists
            if len(st.session_state['past']) == 1:
                context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            else:
                context = f"User: {st.session_state['past'][-2]}\nBot: {st.session_state['generated'][-2]}\nUser: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"

            final_prompt = prompt4conversation(prompt, context)

        if make_better:
            with st.spinner('🚀 Generando respuesta...'):
                response = st.session_state['chatbot'](messages=[SystemMessage(content="You always answer polite and helpful, **your answers are in the language of the user question**"),HumanMessage(content=final_prompt)])
                response = response.content
                response += source
        else:
            response = final_prompt

    return response

## Conditional display of AI generated responses as a function of User provided prompts
with response_container:
    if st.session_state['input'] and 'openai_api_key' in st.session_state:
        st.write(st.session_state)
        response = generate_response(input_text)
        st.session_state.past.append(input_text)
        st.session_state.generated.append(response)

    #print message in normal order, frist User then bot
    if 'generated' in st.session_state:
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                with st.chat_message(name="user"):
                    st.markdown(st.session_state['past'][i])
                
                with st.chat_message(name="assistant"):
                    if len(st.session_state['generated'][i].split("✅Fuente:")) > 1:
                        source = st.session_state['generated'][i].split("✅Fuente:")[1]
                        mess = st.session_state['generated'][i].split("✅Fuente:")[0]

                        st.markdown(mess)
                        with st.expander("📚 Numero fuente de mensaje " + str(i+1)):
                            st.markdown(source)

                    else:
                        st.markdown(st.session_state['generated'][i])

            st.markdown('', unsafe_allow_html=True)
            
    else:
        st.info("👋 Hey , estamos muy Feliz por verte aqui 🤗")
        st.info("👉 El objetivo de esta app es de poder visualizar las imagenes en tus respuesta de los sitios webs que uses como referencia para tu base de datos 🚀")
        st.error("👉 Coloca tu OpenAI API Key 🤗")