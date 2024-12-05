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
    
    # Create dir if does not exist.
    output_dir = "ingress-manifests"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for ing in ingresses:
        # Remove fields managed by kubernetes
        if 'status' in ing:
            del ing['status']
        if 'metadata' in ing:
            for field in ['creationTimestamp', 'generation', 'resourceVersion', 'uid', 'managedFields']:
                if field in ing['metadata']:
                    del ing['metadata'][field]
        
        # Generate name of the file based on namespace and ingress name.
        filename = f"{output_dir}/{ing['metadata']['namespace']}-{ing['metadata']['name']}.yaml"
        
        # Save each ingress in a separate file 
        with open(filename, 'w') as f:
            # Add a separator in the beginning of the file.
            f.write("---\n")
            yaml.dump(ing, f, default_flow_style=False)
            f.write('\n')  # Add an empty line in the end of the files.
        
        print(f"Created: {filename}")

if __name__ == "__main__":
    main()
