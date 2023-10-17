import subprocess
import json

# class Server():
#         def __init__(self):
#                 self.name = serverJson["name"]
#                 self.description = serverJson["description"]
def nix_to_json(nix_file_path):
        output = subprocess.check_output(['nix-instantiate', '--eval', '--json', "--verbose" , "--strict" , nix_file_path])
        return output

def format_json(input_json):
        json_output = json.loads(input_json)
        formatted_output = json.dumps(json_output, indent=4)
        return formatted_output

serverJson = (format_json(nix_to_json("server.nix")))

funny = json.loads(serverJson)
print(serverJson)

