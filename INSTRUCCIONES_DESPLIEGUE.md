# Instrucciones de Despliegue y Uso

Este proyecto es un Generador de Documentos Oficiales basado en IA (OpenAI + LangChain + Streamlit).

## 1. Verificación de Seguridad (Antes de subir a GitHub)
Asegúrate de que el archivo `.gitignore` exista en la carpeta raíz y contenga:
```
.env
__pycache__/
```
**Importante:** Nunca subas tu archivo `.env` o publiques tu API Key directamente en el código.

## 2. Ejecución Local (Para Desarrolladores)
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Configurar credenciales:
   - Asegúrate de tener el archivo `.env` con tu clave: `OPENAI_API_KEY=sk-...`
3. Ejecutar la aplicación:
   ```bash
   streamlit run app.py
   ```

## 3. Publicación en Streamlit Community Cloud (Recomendado)
Es la forma más fácil y gratuita de compartir la app.

1. **Subir a GitHub**:
   - Crea un repositorio nuevo en GitHub.
   - Sube los archivos: `app.py`, `logic.py`, `requirements.txt`, `.gitignore` y `README.md`.
   - **NO** subas `.env`.

2. **Desplegar**:
   - Ve a [share.streamlit.io](https://share.streamlit.io/).
   - Conecta tu cuenta de GitHub y selecciona tu repositorio.
   - En la configuración de despliegue ("Advanced Settings" -> "Secrets"), añade tu clave API así:
     ```toml
     OPENAI_API_KEY = "sk-proj-tu-clave-aqui..."
     ```
   - Dale a "Deploy".

## 4. Publicación en Railway (Alternativa Docker)
Si prefieres un servidor privado o Docker:

1. Crea un repositorio en GitHub (igual que arriba).
2. Conecta el repo a Railway.app.
3. Railway detectará Python.
4. En la pestaña "Variables", añade `OPENAI_API_KEY` y el valor de tu clave.
5. En "Settings" -> "Start Command", usa: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
