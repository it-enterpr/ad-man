from django.shortcuts import render, redirect
from .models import Client
from .forms import ClientForm
import os
import subprocess
import shutil
import docker

def dashboard(request):
    clients = Client.objects.all() # Získáme všechny klienty z databáze
    clients_data = []
    docker_client = docker.from_env()

    for client in clients:
        try:
            containers = docker_client.containers.list(filters={'name': f'^{client.internal_name}-'})
            status = 'Běží' if any(c.status == 'running' for c in containers) else 'Zastaveno'
        except docker.errors.APIError:
            status = 'Neznámý'
        clients_data.append({'client': client, 'status': status})

    context = {
        'clients_data': clients_data
    }
    return render(request, 'clients/dashboard.html', context)

def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save() # Uložíme data z formuláře do databáze
            
            # Zbytek logiky pro vytvoření složky a souborů zůstává
            client_path = os.path.join('/srv/clients', client.internal_name)
            try:
                os.makedirs(client_path, exist_ok=True)
                template_path = '/app/client_templates/base_template.yml'
                with open(template_path, 'r') as f:
                    template_content = f.read()
                
                new_content = template_content.replace('{{CLIENT_NAME}}', client.internal_name)
                new_content = new_content.replace('{{CLIENT_DOMAIN}}', client.domain)
                
                new_compose_path = os.path.join(client_path, 'docker-compose.yml')
                with open(new_compose_path, 'w') as f:
                    f.write(new_content)

                subprocess.run(['docker', 'compose', '-f', new_compose_path, 'up', '-d'], check=True)
            except Exception as e:
                print(f"Error creating client files: {e}")
                # Zde by mělo být lepší zpracování chyb

            return redirect('dashboard')
    else:
        form = ClientForm()

    return render(request, 'clients/create_client.html', {'form': form})

# Ostatní funkce (start, stop, delete) zatím necháme pracovat se jménem složky
def stop_client(request, client_name):
    client_path = os.path.join('/srv/clients', client_name)
    compose_file = os.path.join(client_path, 'docker-compose.yml')
    if os.path.exists(compose_file):
        try:
            subprocess.run(['docker', 'compose', '-f', compose_file, 'down'], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error stopping client {client_name}: {e.stderr}")
    return redirect('dashboard')

def start_client(request, client_name):
    client_path = os.path.join('/srv/clients', client_name)
    compose_file = os.path.join(client_path, 'docker-compose.yml')
    if os.path.exists(compose_file):
        try:
            subprocess.run(['docker', 'compose', '-f', compose_file, 'up', '-d'], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error starting client {client_name}: {e.stderr}")
    return redirect('dashboard')

def delete_client(request, client_name):
    # Nejprve smažeme záznam z databáze
    try:
        client = Client.objects.get(internal_name=client_name)
        client.delete()
    except Client.DoesNotExist:
        pass # Klient v databázi neexistuje, pokračujeme dál

    # Poté smažeme soubory a kontejnery
    client_path = os.path.join('/srv/clients', client_name)
    compose_file = os.path.join(client_path, 'docker-compose.yml')
    if os.path.exists(compose_file):
        try:
            subprocess.run(['docker', 'compose', '-f', compose_file, 'down', '-v'], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error deleting client containers {client_name}: {e.stderr}")
    if os.path.exists(client_path):
        try:
            shutil.rmtree(client_path)
        except OSError as e:
            print(f"Error deleting client directory {client_name}: {e}")
    return redirect('dashboard')