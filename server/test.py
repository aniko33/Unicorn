from os import path
from importlib import import_module

payload_name: str = "template_agent"
payload_output: str = "test.exe"

"""
{
    "ip": "127.0.0.1",
    "port": 6666,
    ...
}
"""
config_dict: dict = {
    "ip": "1.1.1.1",
    "port": 1111,
} 

if not path.exists(path.join("payload", payload_name)):
    quit()

payload_path = "/".join(("payload", payload_name))
payload_builder = import_module(".".join(("payload", payload_name, "setup")))

line_parameters = []

for k, v in config_dict.items():
    if isinstance(v, str):
        v = "\"{}\"".format(v)

    line_parameters.append("{}={}".format(k, v))

config_obj = getattr(payload_builder, "Config")
config_instance = config_obj(output=payload_output, cpath=payload_path)

exec(f"config_instance.run({','.join(line_parameters)})")
