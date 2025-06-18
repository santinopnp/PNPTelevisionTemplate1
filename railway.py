# Crear archivo railway.json para definir configuración de despliegue
railway_config = {
    "build": {
        "env": {
            "PYTHON_VERSION": "3.11"
        }
    },
    "start": "python run_bot.py",
    "deploy": {
        "restartPolicyType": "ON_FAILURE"
    }
}

import json
railway_path = "railway.json"
with open(railway_path, "w") as f:
    json.dump(railway_config, f, indent=4)

railway_path
