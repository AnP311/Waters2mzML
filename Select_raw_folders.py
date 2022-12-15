import os
import glob

import pandas as pd
import dotenv

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

from Waters2mzML import get_config, process_all_raw, ms_convert, annotate


def _set_default_config(default_value, env_key):
    if os.getenv(env_key) is None:
        os.environ[env_key] = default_value
        dotenv.set_key(dotenv_file, env_key, os.environ[env_key])


st.set_page_config(layout="wide")

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

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
_set_default_config(os.path.join(os.path.dirname(os.path.realpath(__file__)),'raw_files'), 'RAW_FILES_FOLDER')
_set_default_config(os.path.join(os.path.dirname(os.path.realpath(__file__)),'mzml_files'), 'MZML_FILES_FOLDER')

st.title('Waters2mzML')

if os.getenv('MSCONVERT_EXE') is None:
    st.error('Missing `msconvert.exe`. Use the Setup page on the left to browse to this file.')

st.markdown(f'''Copy your Waters .raw folders to `{os.getenv('RAW_FILES_FOLDER')}` for conversion.  
mzML files will be saved to `{os.getenv('MZML_FILES_FOLDER')}`.''')  
st.caption('Use the Setup page on the left to configure these locations')

st.subheader('Select .raw folders to convert')
st.button('Refresh the list')
all_raw = pd.DataFrame(glob.glob('*.raw', root_dir=os.getenv('RAW_FILES_FOLDER')), columns=["RAW Folder"])
grid_builder = GridOptionsBuilder.from_dataframe(all_raw)
grid_builder.configure_default_column(filterable=False, sorteable=False)
grid_builder.configure_selection(selection_mode='multiple', use_checkbox=True)
raw_grid = AgGrid(
    data=all_raw, editable=False, gridOptions=grid_builder.build(), data_return_mode=DataReturnMode.FILTERED,
    height=200, update_mode=GridUpdateMode.SELECTION_CHANGED, theme="streamlit"
)

centroid = st.checkbox('Centroid profiled data?')
process = st.button('Start conversion')
if process:
    raws_to_process = [os.path.join(os.getenv('RAW_FILES_FOLDER'), x['RAW Folder']) for x in raw_grid['selected_rows']]
    ms2 = process_all_raw(os.getenv('RAW_FILES_FOLDER'), raws_to_process)
    ms_convert(os.getenv('RAW_FILES_FOLDER'), os.getenv('MSCONVERT_EXE'), raws_to_process, get_config(centroid))
    annotate(os.getenv('RAW_FILES_FOLDER'), os.getenv('MZML_FILES_FOLDER'), ms2)
