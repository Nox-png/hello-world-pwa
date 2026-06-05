import os, sys
import django
from django.apps import apps
from django.conf import settings

# Django-Settings initialisieren, falls nötig
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helloworldpwa.settings")
django.setup()

EXCLUDE_MODELS = {
    "LogEntry",
    "Permission",
    "Group",
    "User",
    "ContentType",
    "Session",
    "Token",
    "TokenProxy",
}

def get_model_fields(model):
    fields = []
    for field in model._meta.get_fields():
        if hasattr(field, 'verbose_name'):
            fields.append({
                'name': field.name,
                'type': field.get_internal_type(),
                # 'verbose_name': field.verbose_name,
                'null': getattr(field, 'null', False),
                'blank': getattr(field, 'blank', False),
                'default': getattr(field, 'default', None),
                'max_length': getattr(field, 'max_length', None),
                'help_text': getattr(field, 'help_text', ''),
            })
    return fields

def generate_html_doc():
    html = """
    <html>
    <head>
        <title>Tabellen Dokumentation</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background: #f4f6fa;
                color: #222;
                margin: 0;
                padding: 0 0 40px 0;
            }
            h1 {
                background: #2a5298;
                color: #fff;
                padding: 24px 32px 16px 32px;
                margin: 0 0 32px 0;
                box-shadow: 0 2px 8px #0001;
            }
            h2 {
                color: #2a5298;
                margin: 32px 0 8px 32px;
            }
            table {
                border-collapse: collapse;
                margin: 0 0 32px 32px;
                background: #fff;
                box-shadow: 0 2px 8px #0001;
                border-radius: 8px;
                overflow: hidden;
            }
            th, td {
                padding: 10px 18px;
                border-bottom: 1px solid #e0e6ed;
            }
            th {
                background: #e3ecfa;
                color: #2a5298;
                font-weight: 600;
            }
            tr:last-child td {
                border-bottom: none;
            }
            tr:nth-child(even) td {
                background: #f7fafd;
            }
            tr:hover td {
                background: #d0e2ff;
            }
            .field-true {
                color: #388e3c;
                font-weight: bold;
            }
            .field-false {
                color: #d32f2f;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>Hello World PWA Datenmodell Dokumentation</h1>
    """
    for model in apps.get_models():
        if model.__name__ in EXCLUDE_MODELS:
            continue
        html += f"<h2>{model.__name__} - Modul: {model._meta.app_config.name}</h2>"
        html += """
        <table>
            <tr>
                <th>Feldname</th>
                <th>Datentyp - (Länge)</th>
                <!-- <th>Verbose Name</th> -->
                <th>Null</th>
                <th>Leer</th>
                <th>Standardwert</th>
                <th>Beschreibung</th>
            </tr>
        """
        for field in get_model_fields(model):
            null_class = "field-true" if field['null'] else "field-false"
            blank_class = "field-true" if field['blank'] else "field-false"
            datentyp = field['type']
            if field['max_length'] is not None:
                datentyp += f" ({field['max_length']})"
            html += (
                f"<tr>"
                f"<td>{field['name']}</td>"
                f"<td>{datentyp}</td>"
                # f"<td>{field['verbose_name']}</td>"
                f"<td class='{null_class}'>{field['null']}</td>"
                f"<td class='{blank_class}'>{field['blank']}</td>"
                f"<td>{field['default']}</td>"
                f"<td>{field['help_text']}</td>"
                f"</tr>"
            )
        html += "</table>"
    html += "</body></html>"
    return html

if __name__ == "__main__":
    html = generate_html_doc()
    # Gehe eine Ebene über das aktuelle Verzeichnis (app)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    filePath = os.path.join(base_dir, "docs", "model", "rel_HelloWorldPWA.html")
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    with open(filePath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dokumentation wurde als {filePath} erstellt.")