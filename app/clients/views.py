from django.shortcuts import render, redirect
import os
import subprocess
import shutil
import docker # <-- Nový import

# Zobrazí hlavní dashboard se seznamem klientů a jejich stavem
def dashboard(request):
    clients_dir = '/srv/clients'
    clients_data = []
    docker_client = docker.from_env() # Vytvoříme klienta pro komunikaci s Dockerem

    try:
        client_names = [name for name in os.listdir(clients_dir) if os.path.isdir(os.path.join(clients_dir, name))]
        
        for name in client_names:
            # Zjistíme stav kontejnerů pro daného klienta
            try:
                # Najdeme všechny kontejnery, které patří k tomuto projektu (složitější, ale spolehlivější)
                # Pro zjednodušení budeme hledat kontejner, jehož jméno začíná názvem klienta
                containers = docker_client.containers.list(filters={'name': f'^{name}-'})
                status = 'Běží' if any(c.status == 'running' for c in containers) else 'Zastaveno'
            except docker.errors.APIError:
                status = 'Neznámý'

            clients_data.append({'name': name, 'status': status})

    except FileNotFoundError:
        pass

    context = {
        'clients': clients_data
    }
    return render(request, 'clients/dashboard.html', context)

# Ostatní funkce (client_detail, create_client, atd.) zůstávají stejné...
# (Zde by byl zbytek kódu z předchozí verze, ale pro přehlednost ho vynecháváme)
# DŮLEŽITÉ: Ujistěte se, že máte v souboru i ostatní funkce (client_detail, atd.)!
# Pro jistotu je zde znovu uvádím všechny:

def client_detail(request, client_name):
    context = {
        'client_name': client_name
    }
    return render(request, 'clients/client_detail.html', context)

def create_client(request):
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_domain = request.POST.get('client_domain')
        if client_name and client_domain:
            client_path = os.path.join('/srv/clients', client_name)
            try:
                os.makedirs(client_path, exist_ok=True)
                template_path = '/app/client_templates/base_template.yml'
                with open(template_path, 'r') as f:
                    template_content = f.read()
                new_content = template_content.replace('{{CLIENT_NAME}}', client_name)
                new_content = new_content.replace('{{CLIENT_DOMAIN}}', client_domain)
                new_compose_path = os.path.join(client_path, 'docker-compose.yml')
                with open(new_compose_path, 'w') as f:
                    f.write(new_content)
                subprocess.run(['docker', 'compose', '-f', new_compose_path, 'up', '-d'], check=True)
            except Exception as e:
                print(f"Error: {e}")
            return redirect('dashboard')
    return render(request, 'clients/create_client.html')

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
