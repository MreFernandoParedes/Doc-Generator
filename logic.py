import os
from io import BytesIO
import docx
from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

def load_text_from_file(uploaded_file):
    """Extract text from uploaded PDF, DOCX, or TXT files."""
    text = ""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    try:
        if file_extension == ".pdf":
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        
        elif file_extension == ".docx":
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        
        elif file_extension == ".txt":
            # Try decoding as utf-8, fallback to latin-1
            text = uploaded_file.read().decode("utf-8", errors="replace")
            
    except Exception as e:
        return f"Error reading file {uploaded_file.name}: {e}"

    return text

def generate_policy_document(reference_text, user_requirements, api_key):
    """
    Generates a policy document based on reference text and user requirements.
    Uses OpenAI Chat model.
    """
    if not api_key:
        return "Error: Por favor ingresa tu API Key de OpenAI."

    try:
        llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o", openai_api_key=api_key)
        
        # Limiting context size naively for now - in production use RAG
        # Truncating to approx 100k characters to stay within broad limits if using GPT-4o
        truncated_reference = reference_text[:100000] 
        
        system_prompt = """Eres un experto redactor de documentos legales y administrativos para entidades gubernamentales, 
        específicamente para el Ministerio de Relaciones Exteriores del Perú.
        Tu tarea es redactar documentos formales, precisos y bien estructurados basados en los insumos proporcionados."""
        
        user_prompt = f"""
        Instrucciones:
        Redacta un documento (por ejemplo, una Política, Guía o Reglamento) siguiendo estas especificaciones:
        
        OBJETIVO DEL DOCUMENTO:
        {user_requirements}
        
        INFORMACIÓN DE REFERENCIA Y GUÍA (Úsala como base para el tono, estructura y normativas):
        {truncated_reference}
        
        El documento debe tener un tono formal, usar terminología adecuada para la administración pública peruana, 
        y estar listo para revisión final. Incluye secciones claras.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        return f"Ocurrió un error al generar el documento: {str(e)}"

def extract_requirements(reference_text, api_key):
    """
    Analyzes the reference text to extract key requirements and obligations.
    """
    if not api_key:
        return ["Error: Falta API Key"]
    
    try:
        llm = ChatOpenAI(temperature=0, model_name="gpt-4o", openai_api_key=api_key)
        
        # Truncate context to avoid errors
        truncated_reference = reference_text[:80000]

        system_prompt = "Eres un analista legal experto."
        user_prompt = f"""
        Analiza el siguiente texto de referencia (leyes, guías, normativas) y extrae una lista concisa de los REQUISITOS OBLIGATORIOS, 
        PROHIBICIONES y PRINCIPIOS CLAVE que deben cumplirse en cualquier documento derivado.
        
        Devuelve SOLO la lista en formato de puntos, sin introducción ni despedida.
        
        REFERENCIA:
        {truncated_reference}
        """

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        response = llm.invoke(messages)
        
        # Simple parsing: split by newlines and clean up bullets
        lines = response.content.split('\n')
        requirements = [line.strip().lstrip('- ').lstrip('* ').strip() for line in lines if line.strip()]
        return requirements
        
    except Exception as e:
        return [f"Error al extraer requisitos: {str(e)}"]

def generate_structure(requirements, user_instructions, model_text, api_key):
    """
    Proposes a document structure based on requirements, user intent, and OPTIONAL model documents.
    """
    if not api_key:
        return [{"title": "Error", "description": "Falta API Key"}]

    try:
        llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o", openai_api_key=api_key)
        
        reqs_text = "\n".join([f"- {r}" for r in requirements])
        truncated_model = model_text[:50000] if model_text else "No hay documentos modelo."
        
        system_prompt = "Eres un arquitecto de la información experto en redacción administrativa."
        user_prompt = f"""
        Diseña la estructura (índice) detallada para un documento oficial, basándote en los requisitos obligatorios.
        
        Si se proporciona un TEXTO MODELO, úsalo como guía para el estilo de los títulos y la organización, pero adáptalo a lo solicitado.
        
        TEXTO MODELO (Referencia de Estructura):
        {truncated_model}

        REQUISITOS OBLIGATORIOS A CUBRIR:
        {reqs_text}
        
        SOLICITUD DEL USUARIO (TIPO DE DOCUMENTO Y OBJETIVO):
        {user_instructions}
        
        INSTRUCCIONES CLAVE:
        - Debes proponer una estructura completa con Títulos de Secciones y Subsecciones.
        - Si el Modelo tiene una buena estructura, imítala pero adáptala a los nuevos requisitos.
        - Asegúrate de cubrir todos los requisitos obligatorios en las secciones correspondientes.
        
        Devuelve SOLO una lista de secciones en el siguiente formato JSON estricto:
        [
            {{"title": "1. Título de la Sección", "description": "Descripción del contenido"}},
            {{"title": "2. Título de la Sección", "description": "..."}},
            {{"title": "2.1. Subsección", "description": "..."}}
        ]
        """
        
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        response = llm.invoke(messages)
        
        import json
        content = response.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "")
        
        structure = json.loads(content)
        return structure

    except Exception as e:
        return [{"title": "Error", "description": str(e)}]

def generate_section_content(section, requirements, normative_text, model_text, api_key):
    """
    Generates content for a SINGLE section to ensure depth and detail using Norms for rules and Model for style.
    """
    if not api_key:
        return "Error: Falta API Key"
        
    try:
        llm = ChatOpenAI(temperature=0.4, model_name="gpt-4o", openai_api_key=api_key)
        
        reqs_str = "\n".join(requirements)
        truncated_norm = normative_text[:50000] 
        truncated_model = model_text[:30000] if model_text else ""
        
        system_prompt = "Eres un redactor experto en políticas públicas y documentos normativos del MRE."
        user_prompt = f"""
        Escribe el CONTENIDO COMPLETO para la siguiente sección de un documento oficial.
        
        TÍTULO DE LA SECCIÓN: {section['title']}
        DESCRIPCIÓN/CONTENIDO ESPERADO: {section['description']}
        
        NORMATIVA VIGENTE (FUENTE DE VERDAD - OBLIGATORIO):
        {truncated_norm}
        
        MODELO/EJEMPLO (DIRECTRIZ DE ESTILO Y TONO):
        {truncated_model}
        
        REQUISITOS OBLIGATORIOS GENERALES:
        {reqs_str}
        
        INSTRUCCIONES DE REDACCIÓN:
        - Extiéndete en detalle. No resumas.
        - Usa un tono formal, legal y administrativo.
        - Desarrolla párrafos completos, artículos numerados o listas según corresponda al título.
        - Si es una sección de "Principios" o "Lineamientos", detalla cada uno.
        - NO escribas el título de la sección de nuevo (ya se agregará automáticamente), solo el contenido.
        """
        
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        return f"Error al generar sección: {str(e)}"
