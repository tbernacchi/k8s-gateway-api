#!/usr/bin/env python3
import yaml
import os
import argparse
from typing import Dict, List
from collections import OrderedDict

def convert_ingress_to_httproute(ingress_yaml: Dict, gateway_name: str) -> Dict:
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
            "hostnames": [ingress_yaml["spec"]["rules"][0]["host"]],
            "parentRefs": [{
                "name": gateway_name,
                "kind": "Gateway",
                "namespace": "default"
            }],
            "rules": []
        }
    }
    
    # Convert rules using the exact path and pathType from the Ingress
    if "rules" in ingress_yaml["spec"]:
        for rule in ingress_yaml["spec"]["rules"]:
            if "http" in rule:
                for path in rule["http"]["paths"]:
                    # Mapeamento de pathType do Ingress para Gateway API
                    path_type = path.get("pathType", "Prefix")
                    if path_type == "ImplementationSpecific":
                        path_type = "PathPrefix"
                    elif path_type == "Prefix":
                        path_type = "PathPrefix"
                    elif path_type == "Exact":
                        path_type = "Exact"
                    
                    httproute_rule = OrderedDict()
                    
                    # Adicionando na ordem exata que queremos
                    httproute_rule["backendRefs"] = [{
                        "name": path["backend"]["service"]["name"],
                        "port": path["backend"]["service"]["port"]["number"]
                    }]
                    
                    httproute_rule["matches"] = [{
                        "path": {
                            "type": path_type,
                            "value": path["path"].split("(/|$)")[0]
                        }
                    }]
                    
                    httproute["spec"]["rules"].append(httproute_rule)
    
    return httproute

def process_directory(input_dir: str, output_dir: str, gateway_name: str):
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
                    httproute = convert_ingress_to_httproute(doc, gateway_name)
                    httproutes.append(httproute)
            
            if httproutes:
                with open(output_path, 'w') as f:
                    f.write("---\n")  # Add YAML document separator at the top
                    yaml.dump_all(httproutes, f, default_flow_style=False, sort_keys=False)
                print(f"Converted {input_path} to {output_path}")

if __name__ == "__main__":
    # Configurar o YAML para tratar OrderedDict como dict normal
    yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_dict(dict(data)))
    
    parser = argparse.ArgumentParser(description="Convert Ingress YAML to HTTPRoute YAML.")
    parser.add_argument("gateway_name", help="Name of the gateway to use in HTTPRoute manifests")
    
    args = parser.parse_args()
    
    input_directory = "ingress-manifests"
    output_directory = "httproute-manifests"
    
    process_directory(input_directory, output_directory, args.gateway_name)
