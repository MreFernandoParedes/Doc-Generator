try:
    import streamlit
    import langchain
    import pypdf
    print("INSTALLATION_VERIFIED")
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
