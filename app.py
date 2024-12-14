import streamlit as st
import google.generativeai as genai
import os
import time


def page_setup():
    st.header("Chat with Audio, Video, or Image Files!", anchor=False, divider="blue")

    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def get_typeofmedia():
    st.sidebar.header("Select type of Media", divider='orange')
    typemedia = st.sidebar.radio("Choose one:",
                                 ("Images",
                                  "Video, mp4 file",
                                  "Audio files"))
    return typemedia

def get_llminfo():
    st.sidebar.header("Options", divider='rainbow')
    tip1 = "Select a model you want to use."
    model = st.sidebar.radio("Choose LLM:",
                              ("gemini-1.5-flash",
                               "gemini-1.5-pro",
                               ), help=tip1)
    tip2 = "Lower temperatures are good for prompts that require a less open-ended or creative response, while higher temperatures can lead to more diverse or creative results. A temperature of 0 means that the highest probability tokens are always selected."
    temp = st.sidebar.slider("Temperature:", min_value=0.0,
                                max_value=2.0, value=1.0, step=0.25, help=tip2)
    tip3 = "Used for nucleus sampling. Specify a lower value for less random responses and a higher value for more random responses."
    topp = st.sidebar.slider("Top P:", min_value=0.0,
                             max_value=1.0, value=0.94, step=0.01, help=tip3)
    tip4 = "Number of response tokens, 8194 is limit."
    maxtokens = st.sidebar.slider("Maximum Tokens:", min_value=100,
                                  max_value=5000, value=2000, step=100, help=tip4)
    return model, temp, topp, maxtokens

def process_file(file, file_type, model, generation_config):
    path3 = '/tmp/'  # Temporary file path
    fpath = file.name
    fpath2 = os.path.join(path3, fpath)
    with open(fpath2, "wb") as f:
        f.write(file.getbuffer())

    uploaded_file = genai.upload_file(path=fpath2)

    while uploaded_file.state.name == "PROCESSING":
        time.sleep(10)
        uploaded_file = genai.get_file(uploaded_file.name)

    if uploaded_file.state.name == "FAILED":
        raise ValueError(uploaded_file.state.name)

    prompt = st.text_input(f"Enter your prompt for the {file_type}:")
    if prompt:
        model_instance = genai.GenerativeModel(model_name=model, generation_config=generation_config)
        response = model_instance.generate_content([uploaded_file, prompt], request_options={"timeout": 600})
        st.markdown(response.text)

        genai.delete_file(uploaded_file.name)

def main():
    page_setup()
    typemedia = get_typeofmedia()
    model, temperature, top_p, max_tokens = get_llminfo()

    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "max_output_tokens": max_tokens,
    }

    if typemedia == "Images":
        image_file = st.file_uploader("Upload your image file.")
        if image_file:
            process_file(image_file, "image", model, generation_config)

    elif typemedia == "Video, mp4 file":
        video_file = st.file_uploader("Upload your video file.")
        if video_file:
            process_file(video_file, "video", model, generation_config)

    elif typemedia == "Audio files":
        audio_file = st.file_uploader("Upload your audio file.")
        if audio_file:
            process_file(audio_file, "audio", model, generation_config)

if __name__ == '__main__':
    project_id = os.environ.get('project_id')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    main()


      
