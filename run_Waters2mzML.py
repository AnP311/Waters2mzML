import streamlit as st
import streamlit.web.bootstrap as bootstrap

if __name__ == '__main__':
    st._is_running_with_streamlit = True
    bootstrap.run('Select_raw_folders.py', 'streamlit run', args=[], flag_options={})
