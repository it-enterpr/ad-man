from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client
from .forms import ClientForm
import os
import subprocess
import shutil
import docker
import yaml

@login_required
def dashboard(request):
    clients = Client.objects.all().order_by('-created_at')
    clients_data = []
    try:
        docker_client = docker.from_env()
        is_docker_running = True
    except Exception:
        docker_client = None
        is_docker_running = False

    for client in clients:
        client_info = {'client': client, 'services': [], 'status': 'Neznámý'}
        if is_docker_running:
            client_path = os.path.join('/srv/clients', client.internal_name)
            compose_file = os.path.join(client_path, 'docker-compose.yml')
            if os.path.exists(compose_file):
                try:
                    with open(compose_file, 'r') as f:
                        compose_data = yaml.safe_load(f)
                        services = compose_data.get('services', {})
                        running_services = 0
                        for service_name in services.keys():
                            container_name = f"{client.internal_name}-{service_name}"
                            try:
                                container = docker_client.containers.get(container_name)
                                status = 'Běží' if container.status == 'running' else 'Zastaveno'
                                if container.status == 'running': running_services += 1
                            except docker.errors.NotFound:
                                status = 'Zastaveno'
                            client_info['services'].append({'name': service_name, 'status': status})
                    if running_services > 0:
                        client_info['status'] = 'Běží'
                    else:
                        client_info['status'] = 'Zastaveno'
                except Exception as e:
                    print(f"Error processing client {client.internal_name}: {e}")
        clients_data.append(client_info)
    context = {'clients_data': clients_data}
    return render(request, 'clients/dashboard.html', context)

@login_required
def manage_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    paths = {}
    if client.has_odoo or client.has_odoo_enterprise:
        paths['Odoo Addons'] = f"https://files.adman.it-enterprise.solutions/files/{client.internal_name}/addons"
        paths['Odoo Config'] = f"https://files.adman.it-enterprise.solutions/files/{client.internal_name}/config"
    if client.has_nextcloud:
        paths['Nextcloud Data'] = f"https://files.adman.it-enterprise.solutions/files/{client.internal_name}/data/nextcloud_data"
    context = {'client': client, 'paths': paths}
    return render(request, 'clients/manage_client.html', context)

@login_required
def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            client_path = os.path.join('/srv/clients', client.internal_name)
            try:
                final_compose = {'version': '3.9', 'services': {}, 'networks': {'proxy': {'external': True}, 'internal': {'driver': 'bridge'}}}
                
                if client.has_odoo:
                    with open('/app/client_templates/odoo_service.yml', 'r') as f: final_compose['services'].update(yaml.safe_load(f))
                if client.has_odoo_enterprise:
                    with open('/app/client_templates/odoo_enterprise_service.yml', 'r') as f: final_compose['services'].update(yaml.safe_load(f))
                if client.has_nextcloud:
                    with open('/app/client_templates/nextcloud_service.yml', 'r') as f: final_compose['services'].update(yaml.safe_load(f))
                if client.has_duplicati:
                    with open('/app/client_templates/duplicati_service.yml', 'r') as f: final_compose['services'].update(yaml.safe_load(f))
                
                compose_str = yaml.dump(final_compose)
                compose_str = compose_str.replace('{{CLIENT_NAME}}', client.internal_name)
                compose_str = compose_str.replace('{{CLIENT_DOMAIN}}', client.domain)

                os.makedirs(os.path.join(client_path, 'data'), exist_ok=True)
                os.makedirs(os.path.join(client_path, 'addons'), exist_ok=True)
                os.makedirs(os.path.join(client_path, 'config'), exist_ok=True)
                new_compose_path = os.path.join(client_path, 'docker-compose.yml')
                with open(new_compose_path, 'w') as f: f.write(new_compose_path)

                subprocess.run(['docker', 'compose', '-f', new_compose_path, 'up', '-d'], check=True, capture_output=True, text=True)
                messages.success(request, f"Klient '{client.company_name}' byl úspěšně vytvořen a spuštěn.")
            except Exception as e:
                messages.error(request, f"Chyba při vytváření klienta: {e}")
            return redirect('dashboard')
    else:
        form = ClientForm()
    return render(request, 'clients/create_client.html', {'form': form})

@login_required
def update_system(request):
    try:
        project_dir = "/srv/ad-man"
        pull_result = subprocess.run(['git', 'pull'], cwd=project_dir, check=True, capture_output=True, text=True)
        messages.success(request, f"Systém úspěšně aktualizován z Gitu: {pull_result.stdout}")
        
        subprocess.run(['docker', 'compose', 'up', '-d', '--build', '--force-recreate'], cwd=project_dir, check=True, capture_output=True, text=True)
        messages.info(request, "Aplikace Ad-Man se restartuje s novými změnami...")
    except subprocess.CalledProcessError as e:
        messages.error(request, f"Chyba při aktualizaci: {e.stderr}")
    except Exception as e:
        messages.error(request, f"Nastala neočekávaná chyba: {e}")
    return redirect('dashboard')

@login_required
def start_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    compose_file = os.path.join('/srv/clients', client.internal_name, 'docker-compose.yml')
    if os.path.exists(compose_file):
        try:
            subprocess.run(['docker', 'compose', '-f', compose_file, 'up', '-d'], check=True, capture_output=True, text=True)
            messages.success(request, f"Služby pro klienta '{client.company_name}' byly úspěšně spuštěny.")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Chyba při spouštění klienta {client.internal_name}: {e.stderr}")
    return redirect('dashboard')

@login_required
def stop_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    compose_file = os.path.join('/srv/clients', client.internal_name, 'docker-compose.yml')
    if os.path.exists(compose_file):
        try:
            subprocess.run(['docker', 'compose', '-f', compose_file, 'down'], check=True, capture_output=True, text=True)
            messages.warning(request, f"Služby pro klienta '{client.company_name}' byly zastaveny.")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Chyba při zastavování klienta {client.internal_name}: {e.stderr}")
    return redirect('dashboard')

@login_required
def delete_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    client_path = os.path.join('/srv/clients', client.internal_name)
    compose_file = os.path.join(client_path, 'docker-compose.yml')
    if os.path.exists(compose_file):
        try:
            subprocess.run(['docker', 'compose', '-f', compose_file, 'down', '-v'], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error deleting client containers {client.internal_name}: {e.stderr}")
    if os.path.exists(client_path):
        try:
            shutil.rmtree(client_path)
        except OSError as e:
            print(f"Error deleting client directory {client.internal_name}: {e}")
    client.delete()
    messages.error(request, f"Klient '{client.company_name}' a všechna jeho data byla smazána.")
    return redirect('dashboard')
