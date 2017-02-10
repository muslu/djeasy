import subprocess
import json
from termcolor import cprint
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
import configparser

class EasyInstall():
    """ Package Install and Settings """
    def __init__(self,project_name,server_name_or_ip,static_url):
        self.project_name = project_name
        self.server_name_or_ip = server_name_or_ip
        self.static_url = static_url

        #package.json read.
        with open("{}/client/package.json".format(BASE_DIR)) as data_file:
            self.data = json.load(data_file)

    def __call__(self, *args, **kwargs):
        #all package.json loading...
        config = configparser.ConfigParser()
        config.sections()
        config.read('settings.ini')

        if(config['Sites']['created']):
            subprocess.call("sudo systemctl daemon reload", shell=True)
            subprocess.call("sudo systemctl restart nginx", shell=True)
        else:
            cprint("Django client - Uploading packages.", 'red', attrs=['bold'])
            for package in self.data['package']:
                subprocess.call(package['name'], shell=True)

    def __add__(self):
        #gunicorn file save and move
        with open("{}/client/gunicorn.service".format(BASE_DIR)) as gunicorn_files:
            gunicorn = gunicorn_files.read().format(self.project_name)
            file_gunicorn = open('{}/package/gunicorn.service'.format(BASE_DIR), 'w')
            file_gunicorn.write(gunicorn)
            file_gunicorn.flush()
            file_gunicorn.close()
            cprint("Gunicorn.service file created.", 'red', attrs=['bold'])
            subprocess.call("cp {}/package/gunicorn.service /etc/systemd/system/".format(BASE_DIR), shell=True)

        #nginx file save and move
        with open("{}/client/DjangoProject".format(BASE_DIR)) as nginx_files:
            nginx = nginx_files.read().format(self.server_name_or_ip, self.static_url, self.project_name)
            nginx_file = nginx.replace('[','{').replace(']','}')

            file_nignx = open("{}/package/DjangoProject".format(BASE_DIR), 'w')
            file_nignx.write(nginx_file)
            file_nignx.flush()
            file_nignx.close()
            cprint("nginx file created.", 'red', attrs=['bold'])
            subprocess.call("cp {}/package/DjangoProject /etc/nginx/sites-available/".format(BASE_DIR), shell=True)


    def __copy__(self):
        #Gunicorn
        for gunicorn_package in self.data['gunicorn']:
            cprint(gunicorn_package['message'], 'white', 'on_red', attrs=['bold'])
            subprocess.call(gunicorn_package['name'], shell=True)
            cprint("Gunicorn successful!", 'green', attrs=['bold'])


        #Nginx
        for nginx_package in self.data['nginx']:
            cprint(nginx_package['message'], 'white', 'on_red', attrs=['bold'])
            subprocess.call(nginx_package['name'], shell=True)
            cprint("Nginx successful!", 'green', attrs=['bold'])


    def extra(self):
        subprocess.call('pip3 install -r /home/{}/requirements.txt'.format(self.project_name), shell=True)

    def save(self):
        with open('{}/client/server.info'.format(BASE_DIR)) as server_file:
            server_file = server_file.read().format(self.server_name_or_ip, self.static_url, self.project_name)
            file = open('/home/server.info', 'w')
            file.write(server_file)
            file.flush()
            file.close()
            cprint("/home/server.info file created.", 'red', attrs=['bold'])
            cprint("all successful!", 'green', attrs=['bold'])

    def settings(self):
        with open('{}/client/settings.ini'.format(BASE_DIR)) as settings_file:
            settings_file = settings_file.read().format(self.server_name_or_ip,self.project_name,self.static_url,"True")
            file = open('{}/package/settings.ini', 'w')
            file.write(settings_file)
            file.flush()
            file.close()


def collectstatic():
    with open("{}/client/server.info".format(BASE_DIR)) as collect_file:
        subprocess.call("python3 /home/{}/manage.py collectstatic".format(collect_file['project_name']), shell=True)

def makemigrations():
    with open("{}/client/server.info".format(BASE_DIR)) as makemigrations_file:
        subprocess.call("python3 /home/{}/manage.py makemigrations".format(makemigrations_file['project_name']), shell=True)

def migrate():
    with open("{}/client/server.info".format(BASE_DIR)) as migrate_file:
        subprocess.call("python3 /home/{}/manage.py migrate".format(migrate_file['project_name']), shell=True)


def RunEasy():
    while True:
        cprint("Please type in the server ip or domain address.)", 'red', attrs=['bold'])
        server_name_or_ip = str(input('server ip or domain = '))
        if (server_name_or_ip == ""):
            cprint("Please do not leave blank, try again...)", 'red', attrs=['bold'])
            continue

        cprint("Write your STATIC_URL", 'red', attrs=['bold'])
        static_url = str(input('STATIC_URL = '))
        if (static_url == ""):
            cprint("Please do not leave blank, try again...)", 'red', attrs=['bold'])
            continue

        cprint("Write your project name", 'red', attrs=['bold'])
        project_name = str(input('Project name = '))
        if (project_name == ""):
            cprint("Please do not leave blank, try again...)", 'red', attrs=['bold'])
            continue

        else:
            break


    Easy = EasyInstall(project_name,server_name_or_ip,static_url)
    Easy.__call__()
    Easy.__add__()
    Easy.__copy__()
    Easy.extra()
    Easy.save()
    Easy.save()


def main():
    message = """
Options:
  --create                 A new site
  --collectstatic          static file
  --makemigrations         database makemigrations
  --migrate                database migrate
"""

    if (len(sys.argv)) > 1:

        if (sys.argv[1] == "--create"):
            RunEasy()

        if (sys.argv[1] == "--collectstatic"):
            collectstatic()

        if (sys.argv[1] == "--makemigrations"):
            makemigrations()

        if (sys.argv[1] == "--migrate"):
            migrate()

    else:
        print(message)


if __name__ == '__main__':
    main()