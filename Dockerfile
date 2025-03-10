# Usamos a imagem oficial do Python
FROM python:3.11

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask (mas o Nginx será a interface principal)
EXPOSE 8000

# Comando de inicialização: Gunicorn servindo o Flask
CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
