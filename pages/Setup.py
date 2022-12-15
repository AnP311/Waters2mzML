import os
import tkinter as tk
from tkinter import filedialog

import dotenv

import streamlit as st

st.markdown("""
<style>
.appview-container>section:first-child>div:first-child, .reportview-container>section:first-child>div:first-child {
    background-color: #3377dd;
}

.appview-container>section:first-child>div:first-child li span, .reportview-container>section:first-child>div:first-child li span {
    color: white;
}

.appview-container>section:first-child>div:first-child button, .reportview-container>section:first-child>div:first-child button{
    background-color: #553388;
    color: white;
}
}</style>""", unsafe_allow_html=True)

def _user_env_config(container, button_caption, get_new_value_fn, env_key):
    with container:
        st.write('')
        st.write('')
        get_new_value = st.button(button_caption)
        if get_new_value:
            new_value = get_new_value_fn(os.getenv(env_key))
            if new_value:
                os.environ[env_key] = new_value
                dotenv.set_key(dotenv_file, env_key, os.environ[env_key])

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

st.title('Waters2mzML Setup')

# Configure msconvert.exe location
left, right = st.columns(2)
_user_env_config(
    right, 'Find msconvert.exe', lambda x: filedialog.askopenfilename(master=root, initialfile=x), 'MSCONVERT_EXE'
)
with left:
    st.markdown('**msconvert.exe location:**')
    st.text(os.getenv('MSCONVERT_EXE'))

# Choose RAW folders to convert
left, right = st.columns(2)
_user_env_config(
    right, 'Change .raw folders location', lambda x: filedialog.askdirectory(master=root, initialdir=x), 'RAW_FILES_FOLDER'
)

with left:
    st.markdown('**Copy your Waters .raw folders to the following directory for conversion:**')
    st.text(os.getenv('RAW_FILES_FOLDER'))

# Configure output mzml file location
left, right = st.columns(2)
_user_env_config(
    right, 'Change mzml files location', lambda x: filedialog.askdirectory(master=root, initialdir=x), 'MZML_FILES_FOLDER'
)
with left:
    st.markdown('**The software will save mzml files in the following directory:**')
    st.text(os.getenv('MZML_FILES_FOLDER'))
