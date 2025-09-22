# Utiliza la imagen oficial de Python como base
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos e instala las dependencias
COPY ./requirements.txt .

# Instala los paquetes de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código del frontend al directorio de trabajo
COPY . .

# Expone el puerto que usa Streamlit por defecto
EXPOSE 8501

# Comando para ejecutar la aplicación de Streamlit
CMD ["streamlit", "run", "main.py"]