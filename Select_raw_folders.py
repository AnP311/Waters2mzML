import os
import glob

import dotenv
import streamlit as st

from Waters2mzML import get_config, process_all_raw, ms_convert, annotate


def _set_default_config(default_value, env_key):
    if os.getenv(env_key) is None:
        os.environ[env_key] = default_value
        dotenv.set_key(dotenv_file, env_key, os.environ[env_key])


def _get_raw_checkbox_state(raw, select_all, select_none):
    if select_all:
        return True

    if select_none:
        return False

    if f'raw_checkbox_{raw}' in st.session_state:
        return st.session_state[f'raw_checkbox_{raw}']

    return False


def _get_selected_raws():
    return [x.replace('raw_checkbox_', '') for x in st.session_state.keys() if x.startswith('raw_checkbox_') and st.session_state[x]]


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
    st.stop()

st.markdown(f'''Copy your Waters .raw folders to `{os.getenv('RAW_FILES_FOLDER')}` for conversion.  
mzML files will be saved to `{os.getenv('MZML_FILES_FOLDER')}`.''')  
st.caption('Use the Setup page on the left to configure these locations')

st.subheader('Select .raw folders to convert')
columns = st.columns(8)
columns[0].button('Refresh the list')
select_all = columns[1].button('Select All')
select_none = columns[2].button('Select None')

all_raw = glob.glob('*.raw', root_dir=os.getenv('RAW_FILES_FOLDER'))
for raw in all_raw:
    st.checkbox(raw, key=f'raw_checkbox_{raw}', value=_get_raw_checkbox_state(raw, select_all, select_none))

centroid = st.sidebar.checkbox('Centroid profiled data?')
_, right = st.sidebar.columns(2)
process = right.button('Start conversion')
if process:
    raws_to_process = [os.path.join(os.getenv('RAW_FILES_FOLDER'), x) for x in _get_selected_raws()]
    ms2 = process_all_raw(os.getenv('RAW_FILES_FOLDER'), raws_to_process)
    ms_convert(os.getenv('RAW_FILES_FOLDER'), os.getenv('MSCONVERT_EXE'), raws_to_process, get_config(centroid))
    annotate(os.getenv('RAW_FILES_FOLDER'), os.getenv('MZML_FILES_FOLDER'), ms2)
