from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from elevenlabs import generate, set_api_key

import os
import streamlit as st

load_dotenv()

class StoryGenerator():
    def __init__(self, openai_api_key, openai_model, model_temperature) -> None:
        self.OPENAI_API_KEY = openai_api_key
        self.OPENAI_MODEL = openai_model
        self.MODEL_TEMPERATURE = model_temperature

    def generate_story(self, scenario):
        
        print('Generating story ...')

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in storytelling for children; you can 
             craft short, funny, pleasant, and educational stories from a simple 
             narrative provided. The stories you create are intended to be read as 
             daily episodes on the Guumel Kids Podcast. At the beginning of each 
             story, you should greet the audience and welcome them to the podcast. 
             Your story should take more than 1 minute but less than 3 minutes to 
             read.
            """),
            ("user", "{input}")
            ])

        llm = ChatOpenAI(openai_api_key=self.OPENAI_API_KEY,
                        model=self.OPENAI_MODEL, 
                        temperature=self.MODEL_TEMPERATURE
        )
        output_parser = StrOutputParser()

        story_chain = prompt | llm | output_parser

        try:
            story = story_chain.invoke({"input": scenario})
        except Exception as e:
            print(f"An error occurred while generating the story: {e}")
            raise Exception(e)

        print(f"Done, story = ```{story}```.")
        print("*************")
        return story
        
class AudioGenerator():
    
    def __init__(self, elevenlabs_api_key, model_name, voice_name):
        super().__init__()
        self.elevenlabs_api_key = elevenlabs_api_key
        self.voice_name = voice_name
        self.model_name = model_name

    def generate_audio(self, story):
        """Generate an audio from a text (story)"""
        podcast_audio_filename = "story.mp3"
        
        print(f"## Processing audio ...")

        try:
            set_api_key(self.elevenlabs_api_key)
            audio = generate(
                text=story,
                voice=self.voice_name,
                model=self.model_name
            )
            with open(podcast_audio_filename, 'wb') as file:
                file.write(audio)
            print(f"Audio saved as {podcast_audio_filename}")
        except Exception as e:
            print(f"An error occurred while processing the audio: {e}")
            raise Exception(e.message)


############################################
####           STREAMLIT APP            ####
############################################      

st.set_page_config(page_title = "AI story Teller", page_icon ="🤖")
st.header("We turn draft stories to podcast!")

with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", 
        key="openai_api_key", 
        type="password"
    )

    elevenlab_api_key = st.text_input(
        "11Labs API Key", 
        key="elevenlab_api_key", 
        type="password"
    )

    "[View the code](https://github.com/streamlit/llm-examples/blob/main/pages/1_File_Q%26A.py)"
    "[Open in GitHub](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")

story_generator = StoryGenerator(
    openai_api_key=openai_api_key,
    openai_model=os.getenv("OPENAI_MODEL"),
    model_temperature=os.getenv("OPENAI_TEMPERATURE"),

)

draft_snario = st.text_input(
        "Your draft story goes here:",
        placeholder="Please provide a short draft of your story.",
        disabled=not openai_api_key
    )

if draft_snario and openai_api_key:
    story = None
    try:
        # create a story
        story = story_generator.generate_story(draft_snario) 
    except Exception as e:
        print(e)
        st.error(e.message, icon="🚨")
    if story:
        # display scenario and story
        with st.expander("Draft scenario"):
            st.write(draft_snario, disabled=not openai_api_key)

        with st.expander("Story"):
            st.write(story)
        
    if elevenlab_api_key and story:
        audioGenerator = AudioGenerator(
            elevenlab_api_key,
            os.getenv("ELEVENLABS_MODEL_NAME"),
            os.getenv("ELEVENLABS_VOICE_NAME")
        )

        try:
            audio = audioGenerator.generate_audio(story)
            with st.expander("Podcast"):# display the audio - people can listen
                st.audio("story.mp3")
        except Exception as e:
            print(e)
            st.error(e, icon="🚨")
