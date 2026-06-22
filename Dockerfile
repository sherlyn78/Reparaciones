# 1. Trae una imagen oficial de Python basada en Linux
FROM python:3.11-slim

# 2. Crea una carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copia el archivo de requisitos e instala las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia el resto del código de tu API de Flask
COPY . .

# 5. Expone el puerto donde corre Flask
EXPOSE 5000

# 6. Comando para arrancar tu API
CMD ["python", "app.py"]