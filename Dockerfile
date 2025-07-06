# Tento soubor říká Dockeru, jak má sestavit obraz pro naši Django aplikaci.
# FINÁLNÍ OPRAVA: Používáme spolehlivou metodu pro instalaci Dockeru.

# Začneme s oficiálním obrazem Pythonu
FROM python:3.11-slim

# --- Instalace Docker CLI a Docker Compose ---
# Přidáme oficiální repozitář Dockeru pro spolehlivou instalaci
RUN apt-get update && apt-get install -y ca-certificates curl
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get install -y docker-ce-cli docker-compose-plugin
# --- Konec instalace Dockeru ---


# Nastavíme pracovní adresář uvnitř kontejneru
WORKDIR /app

# Zkopírujeme soubor se závislostmi
COPY requirements.txt .

# Nainstalujeme závislosti
RUN pip install --no-cache-dir -r requirements.txt

# Zkopírujeme zbytek kódu naší aplikace
COPY ./app .

# Tento příkaz se spustí, když kontejner nastartuje
# Spustí Gunicorn, což je produkční server pro Python aplikace
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "adman.wsgi:application"]
