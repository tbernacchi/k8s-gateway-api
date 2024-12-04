#!/usr/bin/env python3
import subprocess
import json
import yaml
import os

def get_ingresses():
    cmd = "kubectl get ingress -A -o json"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    return json.loads(result.stdout)["items"]

def main():
    ingresses = get_ingresses()
    
    # Cria diretório para os manifestos se não existir
    output_dir = "ingress-manifests"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for ing in ingresses:
        # Remove campos gerenciados pelo kubernetes
        if 'status' in ing:
            del ing['status']
        if 'metadata' in ing:
            for field in ['creationTimestamp', 'generation', 'resourceVersion', 'uid', 'managedFields']:
                if field in ing['metadata']:
                    del ing['metadata'][field]
        
        # Gera nome do arquivo baseado no namespace e nome do ingress
        filename = f"{output_dir}/{ing['metadata']['namespace']}-{ing['metadata']['name']}.yaml"
        
        # Salva cada ingress em um arquivo separado com uma linha em branco no final
        with open(filename, 'w') as f:
            yaml.dump(ing, f, default_flow_style=False)
            f.write('\n')  # Adiciona uma linha em branco no final
        
        print(f"Created: {filename}")

if __name__ == "__main__":
    main()
