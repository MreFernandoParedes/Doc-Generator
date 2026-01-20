# Walkthrough - Generador de Documentos Mejora Interactiva

Se ha implementado un nuevo flujo de trabajo interactivo de 3 pasos para mejorar la precisión y control en la generación de documentos.

## Cambios Realizados

### 1. Nuevo Flujo en 3 Pasos (Wizard)
La aplicación ahora guía al usuario por fases secuenciales en lugar de intentar hacer todo en un solo paso.

1.  **Paso 1: Análisis**: Subes los documentos y la IA extrae los "Requisitos Obligatorios".
2.  **Paso 2: Estructura**: Revisas y editas los requisitos. Luego, la IA propone una estructura (Índice) para el documento.
3.  **Paso 3: Generación**: Revisas y editas la estructura (añades/quitas secciones) y generas el documento final.

### 2. Diferenciación de Contexto (Nuevo)
Ahora puedes subir documentos en dos categorías distintas para mejorar la precisión:
- **Normativa (Obligatorio)**: Leyes y reglamentos. La IA los usará para extraer requisitos legales estrictos.
- **Modelos (Opcional)**: Ejemplos de otros documentos. La IA los usará para copiar el estilo y proponer la estructura, pero no mezclará sus reglas con la normativa.

### 3. Generación Iterativa
Para garantizar documentos extensos y detallados:
- El sistema ahora redacta **sección por sección** en lugar de todo de una vez.
- Verás una barra de progreso indicando qué capítulo se está escribiendo.
- Esto permite generar políticas de múltiples páginas con mayor profundidad.

### 3. Edición Interactiva
Se ha incorporado tablas editables (`st.data_editor`) para que puedas:
- Modificar textos de requisitos extraídos incorrectamente.
- Eliminar requisitos que no apliquen.
- Renombrar títulos de secciones o cambiar sus descripciones antes de que la IA escriba el contenido.

## Cómo Probarlo

1.  Ejecuta la app: `streamlit run app.py`
2.  Ingresa tu **OpenAI API Key**.
3.  Sube un archivo de prueba.
4.  Escribe el objetivo (ej: "Política de Privacidad").
5.  Sigue los botones "Siguiente" y verifica que puedes editar las tablas en cada paso.
