#!/usr/bin/env python3
import yaml
import os
from typing import Dict, List

def convert_ingress_to_httproute(ingress_yaml: Dict) -> Dict:
    """Convert a single Ingress manifest to HTTPRoute manifest."""
    
    # Initialize HTTPRoute structure
    httproute = {
        "apiVersion": "gateway.networking.k8s.io/v1beta1",
        "kind": "HTTPRoute",
        "metadata": {
            "name": ingress_yaml["metadata"]["name"],
            "namespace": ingress_yaml["metadata"].get("namespace", "default")
        },
        "spec": {
            "parentRefs": [{
                "name": "kong",  # Default gateway name, you might want to make this configurable
                "kind": "Gateway",
                "namespace": "default"  # Default namespace, you might want to make this configurable
            }],
            "rules": []
        }
    }
    
    # Convert rules
    if "rules" in ingress_yaml["spec"]:
        for rule in ingress_yaml["spec"]["rules"]:
            if "http" in rule:
                for path in rule["http"]["paths"]:
                    httproute_rule = {
                        "matches": [{
                            "path": {
                                "type": "PathPrefix" if path["path"].endswith("/*") else "Exact",
                                "value": path["path"].replace("/*", "")
                            }
                        }],
                        "backendRefs": [{
                            "name": path["backend"]["service"]["name"],
                            "port": path["backend"]["service"]["port"]["number"]
                        }]
                    }
                    
                    # Add hostname matching if specified
                    if "host" in rule:
                        httproute_rule["matches"][0]["hostname"] = rule["host"]
                    
                    httproute["spec"]["rules"].append(httproute_rule)
    
    return httproute

def process_directory(input_dir: str, output_dir: str):
    """Process all YAML files in the input directory and convert them to HTTPRoutes."""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each YAML file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(('.yaml', '.yml')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"httproute-{filename}")
            
            with open(input_path, 'r') as f:
                ingress_docs = list(yaml.safe_load_all(f))
            
            httproutes = []
            for doc in ingress_docs:
                if doc and doc.get('kind') == 'Ingress':
                    httproute = convert_ingress_to_httproute(doc)
                    httproutes.append(httproute)
            
            if httproutes:
                with open(output_path, 'w') as f:
                    f.write("---\n")  # Add YAML document separator at the top
                    yaml.dump_all(httproutes, f)
                print(f"Converted {input_path} to {output_path}")

if __name__ == "__main__":
    # Example usage
    input_directory = "ingress-manifests"  # Directory containing your Ingress YAML files
    output_directory = "httproute-manifests"  # Directory where HTTPRoute manifests will be saved
    
    process_directory(input_directory, output_directory)
