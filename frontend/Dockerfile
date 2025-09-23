# Utiliza la imagen oficial de Python como base
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos e instala las dependencias
# Se copian primero para aprovechar el cache de Docker si no cambian
COPY ./frontend/requirements.txt ./frontend/requirements.txt

# Instala los paquetes de Python
RUN pip install --no-cache-dir -r ./frontend/requirements.txt

# Copia el código del frontend y los recursos compartidos
COPY ./frontend ./frontend
COPY ./resources ./resources

# Expone el puerto que usa Streamlit por defecto
EXPOSE 8501

# Comando para ejecutar la aplicación de Streamlit
CMD ["streamlit", "run", "frontend/main.py"]