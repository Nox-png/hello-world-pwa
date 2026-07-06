########################## BUILD IMAGE  ##########################
FROM python:3.14-alpine

# 1.1 System-Pakete für den Build
RUN apk add --no-cache \
      build-base \
      mariadb-connector-c-dev \
      pkgconfig

# Erstelle das App Verzeichnis
RUN mkdir -p /app
# Kopiere das Verzeichnis "App" vom Projektordner ins Dockerimage
COPY app /app
# Veröffentliche Port 8000
EXPOSE 8000
# Ändere das Arbeitsverzeichnis
WORKDIR /app
# Führe PIP Installationen anhand der requirements aus ohne cache
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# CMD python3 Startlog/Nachricht & python3 /app/manage.py migrate && Start via gunicorn
CMD python3 -c 'import re, pathlib; t = pathlib.Path("web/context_processors.py").read_text(encoding="utf-8"); v = re.search(r"versionNumber\s*=\s*\"([^\"]+)\"", t); b = re.search(r"buildNumber\s*=\s*\"([^\"]+)\"", t); print("[startup] version={} build={}".format(v.group(1) if v else "unknown", b.group(1) if b else "unknown"), flush=True)' && python3 manage.py collectstatic --noinput && python3 manage.py migrate && gunicorn helloworldpwa.wsgi --bind 0.0.0.0:8000 --workers 9 --timeout 1200
