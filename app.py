import streamlit as st
import google.generativeai as genai
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from pypdf import PdfReader, PdfWriter
import os
import time
import base64


def page_setup():
    st.header("Chat with different types of media/files!", anchor=False, divider="blue")

    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


def get_typeofpdf():
    st.sidebar.header("Select type of Media", divider='orange')
    typepdf = st.sidebar.radio("Choose one:",
                               ("PDF files",
                                "Images",
                                "Video, mp4 file",
                                "Audio files"))
    return typepdf


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


def main():
    page_setup()
    typepdf = get_typeofpdf()
    model, temperature, top_p, max_tokens = get_llminfo()
    
    if typepdf == "PDF files":
        uploaded_files = st.file_uploader("Choose 1 or more files", accept_multiple_files=True)
        
        if uploaded_files:
            # Temporary path to store uploaded files
            path_to_files = '/tmp/'  # Replace with your appropriate path
            os.makedirs(path_to_files, exist_ok=True)
            writer = PdfWriter()

            for file in uploaded_files:
                file_name = file.name
                with open(os.path.join(path_to_files, file_name), "wb") as f:
                    f.write(file.getbuffer())
                
                reader = PdfReader(os.path.join(path_to_files, file_name))
                for page in reader.pages:
                    writer.add_page(page)

            fullfile = os.path.join(path_to_files, "merged_all_pages.pdf")
            with open(fullfile, "wb") as f:
                writer.write(f)

            st.write("Merged PDF created:", fullfile)

            with open(fullfile, "rb") as file_1:
                encoded_string = base64.b64encode(file_1.read()).decode()
                part = Part.from_data(
                    mime_type="application/pdf",
                    data=base64.b64decode(encoded_string)
                )

                generation_config = {
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_output_tokens": max_tokens,
                }

                model_instance = GenerativeModel(
                    model_name=model,
                    generation_config=generation_config,
                )

                st.write(f"Total tokens submitted: {model_instance.count_tokens(part)}")

                question = st.text_input("Enter your question and hit return.")
                if question:
                    response = model_instance.generate_content([question, part])
                    st.markdown(response.text)

    elif typepdf == "Images":
        image_file_name = st.file_uploader("Upload your image file.")
        if image_file_name:
            path3 = '/tmp/'  # Temporary file path for image
            fpath = image_file_name.name
            fpath2 = os.path.join(path3, fpath)
            with open(fpath2, "wb") as f:
                f.write(image_file_name.getbuffer())

            image_file = genai.upload_file(path=fpath2)

            while image_file.state.name == "PROCESSING":
                time.sleep(10)
                image_file = genai.get_file(image_file.name)

            if image_file.state.name == "FAILED":
                raise ValueError(image_file.state.name)

            prompt2 = st.text_input("Enter your prompt.")
            if prompt2:
                generation_config = {
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_output_tokens": max_tokens,
                }

                model_instance = genai.GenerativeModel(model_name=model, generation_config=generation_config)
                response = model_instance.generate_content([image_file, prompt2], request_options={"timeout": 600})
                st.markdown(response.text)

                genai.delete_file(image_file.name)

    elif typepdf == "Video, mp4 file":
        video_file_name = st.file_uploader("Upload your video")
        if video_file_name:
            path3 = '/tmp/'  # Temporary file path for video
            fpath = video_file_name.name
            fpath2 = os.path.join(path3, fpath)
            with open(fpath2, "wb") as f:
                f.write(video_file_name.getbuffer())

            video_file = genai.upload_file(path=fpath2)

            while video_file.state.name == "PROCESSING":
                time.sleep(10)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                raise ValueError(video_file.state.name)

            prompt3 = st.text_input("Enter your prompt.")
            if prompt3:
                model_instance = genai.GenerativeModel(model_name=model)
                st.write("Making LLM inference request...")
                response = model_instance.generate_content([video_file, prompt3], request_options={"timeout": 600})
                st.markdown(response.text)

                genai.delete_file(video_file.name)

    elif typepdf == "Audio files":
        audio_file_name = st.file_uploader("Upload your audio")
        if audio_file_name:
            path3 = '/tmp/'  # Temporary file path for audio
            fpath = audio_file_name.name
            fpath2 = os.path.join(path3, fpath)
            with open(fpath2, "wb") as f:
                f.write(audio_file_name.getbuffer())

            audio_file = genai.upload_file(path=fpath2)

            while audio_file.state.name == "PROCESSING":
                time.sleep(10)
                audio_file = genai.get_file(audio_file.name)

            if audio_file.state.name == "FAILED":
                raise ValueError(audio_file.state.name)

            prompt3 = st.text_input("Enter your prompt.")
            if prompt3:
                model_instance = genai.GenerativeModel(model_name=model)
                response = model_instance.generate_content([audio_file, prompt3], request_options={"timeout": 600})
                st.markdown(response.text)

                genai.delete_file(audio_file.name)


if __name__ == '__main__':
    project_id = os.environ.get('project_id')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    vertexai.init(project=project_id, location="asia-south1")
    main()

