import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from logic import load_text_from_file, extract_requirements, generate_structure, generate_section_content

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Generador de Documentos Normativos - MRE", page_icon="📄", layout="wide")

st.title("📄 Generador de Documentos Oficiales - MRE")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    
    # Get API key from env or empty string
    env_key = os.getenv("OPENAI_API_KEY", "")
    
    api_key = st.text_input("OpenAI API Key", value=env_key, type="password", help="Ingresa tu clave de API de OpenAI")
    
    st.divider()
    st.subheader("1. Subir Normativa (Obligatorio)")
    st.info("Sube leyes, reglamentos o directivas vigentes. Se usarán para extraer los **requisitos legales**.")
    uploaded_norms = st.file_uploader("Normativa (PDF, DOCX, TXT)", 
                                    type=["pdf", "docx", "txt"], 
                                    accept_multiple_files=True,
                                    key="norms_uploader")
    
    st.subheader("2. Subir Modelos (Opcional)")
    st.info("Sube ejemplos o documentos de referencia. Se usarán para copiar el **estilo y estructura**.")
    uploaded_models = st.file_uploader("Modelos (PDF, DOCX, TXT)", 
                                    type=["pdf", "docx", "txt"], 
                                    accept_multiple_files=True,
                                    key="models_uploader")
    
    if st.button("Reiniciar Proceso", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.divider()
    with st.expander("📘 Ayuda / Documentación"):
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                st.markdown(f.read())
        except:
            st.info("Archivo README.md no encontrado.")

# --- Session State Initialization ---
if 'step' not in st.session_state:
    st.session_state['step'] = 1
if 'requirements' not in st.session_state:
    st.session_state['requirements'] = []
if 'structure' not in st.session_state:
    st.session_state['structure'] = []
    
if 'normative_text' not in st.session_state:
    st.session_state['normative_text'] = ""
if 'model_text' not in st.session_state:
    st.session_state['model_text'] = ""

# --- Helper to load text ---
def process_uploads():
    norm_text = ""
    model_text = ""
    
    if uploaded_norms:
        for f in uploaded_norms:
            content = load_text_from_file(f)
            norm_text += f"\n--- INICIO NORMA: {f.name} ---\n{content}\n--- FIN NORMA: {f.name} ---\n"
            
    if uploaded_models:
        for f in uploaded_models:
            content = load_text_from_file(f)
            model_text += f"\n--- INICIO MODELO: {f.name} ---\n{content}\n--- FIN MODELO: {f.name} ---\n"
            
    return norm_text, model_text

# --- STEP 1: DEFINITION & ANALYSIS ---
if st.session_state['step'] == 1:
    st.subheader("Paso 1: Definición y Análisis")
    
    user_requirements = st.text_area(
        "¿Qué documento deseas generar y cuál es su objetivo?",
        height=150,
        placeholder="Ejemplo: Redactar una 'Política de Uso de IA'. Debe ser estricta con la privacidad..."
    )
    
    if st.button("Analizar Documentos y Extraer Requisitos", type="primary"):
        if not api_key:
            st.error("⚠️ Falta API Key.")
        elif not uploaded_norms:
            st.error("⚠️ Sube al menos un documento de NORMATIVA.")
        elif not user_requirements:
            st.error("⚠️ Describe el objetivo del documento.")
        else:
            with st.spinner("Leyendo y analizando documentos..."):
                norm_text, model_text = process_uploads()
                st.session_state['normative_text'] = norm_text
                st.session_state['model_text'] = model_text
                st.session_state['user_intent'] = user_requirements
                
                # Call Logic - ONLY Norms for Requirements
                reqs = extract_requirements(st.session_state['normative_text'], api_key)
                st.session_state['requirements'] = reqs
                st.session_state['step'] = 2
                st.rerun()

# --- STEP 2: REVIEW REQUIREMENTS ---
elif st.session_state['step'] == 2:
    st.subheader("Paso 2: Revisión de Requisitos Detectados")
    st.info("Selecciona los requisitos (extraídos de la Normativa) que deseas mantener.")
    
    # Prepare DF with selection column
    if not isinstance(st.session_state['requirements'][0], dict):
        reqs_data = [{"Incluir": True, "Requisito": r} for r in st.session_state['requirements']]
    else:
        reqs_data = st.session_state['requirements']

    df_reqs = pd.DataFrame(reqs_data)
    
    column_config = {
        "Incluir": st.column_config.CheckboxColumn(
            "¿Incluir?",
            help="Desmarca para ignorar este requisito",
            default=True,
        ),
        "Requisito": st.column_config.TextColumn(
            "Requisito (Editable)",
            width="large",
        )
    }

    edited_df = st.data_editor(
        df_reqs, 
        column_config=column_config, 
        num_rows="dynamic", 
        width="stretch",
        hide_index=True
    )
    
    col_back, col_next = st.columns([1, 4])
    if col_back.button("⬅️ Atrás"):
        st.session_state['step'] = 1
        st.rerun()
        
    if col_next.button("Aprobar Requisitos y Diseñar Estructura ➡️", type="primary"):
        # Filter only included rows
        selected_rows = edited_df[edited_df["Incluir"] == True]
        updated_reqs = selected_rows["Requisito"].tolist()
        
        if not updated_reqs:
            st.error("⚠️ Debes seleccionar al menos un requisito para continuar.")
        else:
            st.session_state['requirements'] = updated_reqs
            
            with st.spinner("Diseñando la estructura (usando referencias de Modelos)..."):
                # Call Logic - use Model Text for structure
                struct = generate_structure(updated_reqs, st.session_state['user_intent'], st.session_state['model_text'], api_key)
                st.session_state['structure'] = struct
                st.session_state['step'] = 3
                st.rerun()

# --- STEP 3: REVIEW STRUCTURE ---
elif st.session_state['step'] == 3:
    st.subheader("Paso 3: Diseño de la Plantilla (Estructura)")
    st.info("Esta es la estructura propuesta. Desmarca las secciones que no desees incluir.")
    
    # Prepare DF with selection column
    if not isinstance(st.session_state['structure'][0], dict):
         # Just in case structure is malformed, though logic.py ensures list of dicts
         st.error("Error en el formato de la estructura.")
    else:
        # Add Include col if not present
        struct_data = []
        for s in st.session_state['structure']:
            row = s.copy()
            if "Incluir" not in row:
                row["Incluir"] = True
            struct_data.append(row)

    df_struct = pd.DataFrame(struct_data)
    
    column_config_struct = {
        "Incluir": st.column_config.CheckboxColumn(
            "¿Incluir?",
            default=True,
            width="small"
        ),
        "title": st.column_config.TextColumn(
            "Título Sección",
            width="medium",
        ),
        "description": st.column_config.TextColumn(
            "Descripción",
            width="large",
        )
    }

    edited_struct_df = st.data_editor(
        df_struct, 
        column_config=column_config_struct,
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True
    )
    
    col_back, col_next = st.columns([1, 4])
    if col_back.button("⬅️ Atrás"):
        st.session_state['step'] = 2
        st.rerun()
        
    if col_next.button("Generar Documento Final ➡️", type="primary"):
        # Filter included
        selected_rows = edited_struct_df[edited_struct_df["Incluir"] == True]
        
        if selected_rows.empty:
             st.error("⚠️ Debes mantener al menos una sección.")
        else:
            # Reconstruct structure list from DF
            updated_struct = selected_rows.drop(columns=["Incluir"]).to_dict('records')
            st.session_state['structure'] = updated_struct
            
            final_doc = ""
            total_sections = len(updated_struct)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, section in enumerate(updated_struct):
                status_text.text(f"Redactando sección {i+1}/{total_sections}: {section['title']}...")
                
                content = generate_section_content(
                    section, 
                    st.session_state['requirements'], 
                    st.session_state['normative_text'],
                    st.session_state['model_text'], 
                    api_key
                )
                
                final_doc += f"\n\n# {section['title']}\n\n"
                final_doc += content
                
                # Update progress
                progress_bar.progress((i + 1) / total_sections)
            
            status_text.text("¡Finalizado!")
            st.session_state['generated_doc'] = final_doc
            st.session_state['step'] = 4
            st.rerun()

# --- STEP 4: FINAL RESULT ---
elif st.session_state['step'] == 4:
    st.subheader("Paso 4: Documento Generado")
    st.success("¡Documento finalizado!")
    
    st.text_area("Vista Final", value=st.session_state.get('generated_doc', ''), height=600)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Descargar como .txt",
            data=st.session_state['generated_doc'],
            file_name="borrador_oficial.txt",
            mime="text/plain"
        )
    with col2:
        if st.button("⬅️ Volver a Editar Estructura"):
            st.session_state['step'] = 3
            st.experimental_rerun()
