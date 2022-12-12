import streamlit as st
import streamlit.web.bootstrap as bootstrap

if __name__ == '__main__':
    st._is_running_with_streamlit = True
    bootstrap.run('Waters2mzML-ui.py', 'streamlit run', args=[], flag_options={})
