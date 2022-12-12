import os
import glob
import tkinter as tk
from tkinter import filedialog

import pandas as pd
import dotenv

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

from Waters2mzML import get_config, process_all_raw, ms_convert, annotate


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

def _set_default_config(default_value, env_key):
    if os.getenv(env_key) is None:
        os.environ[env_key] = default_value
        dotenv.set_key(dotenv_file, env_key, os.environ[env_key])


st.set_page_config(layout="wide")

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
_set_default_config(os.path.join(os.path.dirname(os.path.realpath(__file__)),'raw_files'), 'RAW_FILES_FOLDER')
_set_default_config(os.path.join(os.path.dirname(os.path.realpath(__file__)),'mzml_files'), 'MZML_FILES_FOLDER')

root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

st.title('Waters2mzML')

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

    all_raw = pd.DataFrame(glob.glob('*.raw', root_dir=os.getenv('RAW_FILES_FOLDER')), columns=["RAW Folder"])
    grid_builder = GridOptionsBuilder.from_dataframe(all_raw)
    grid_builder.configure_default_column(filterable=False, sorteable=False)
    grid_builder.configure_selection(selection_mode='multiple', use_checkbox=True)
    raw_grid = AgGrid(
        data=all_raw, editable=False, gridOptions=grid_builder.build(), data_return_mode=DataReturnMode.FILTERED,
        height=200, update_mode=GridUpdateMode.SELECTION_CHANGED, theme="streamlit"
    )

# Configure output mzml file location
left, right = st.columns(2)
_user_env_config(
    right, 'Change mzml files location', lambda x: filedialog.askdirectory(master=root, initialdir=x), 'MZML_FILES_FOLDER'
)
with left:
    st.markdown('**The software will save mzml files in the following directory:**')
    st.text(os.getenv('MZML_FILES_FOLDER'))

# Do It!
centroid = st.checkbox('Centroid profiled data?')
process = st.button('Start conversion')
if process:
    raws_to_process = [os.path.join(os.getenv('RAW_FILES_FOLDER'), x['RAW Folder']) for x in raw_grid['selected_rows']]
    ms2 = process_all_raw(os.getenv('RAW_FILES_FOLDER'), raws_to_process)
    ms_convert(os.getenv('RAW_FILES_FOLDER'), os.getenv('MSCONVERT_EXE'), raws_to_process, get_config(centroid))
    annotate(os.getenv('RAW_FILES_FOLDER'), os.getenv('MZML_FILES_FOLDER'), ms2)
