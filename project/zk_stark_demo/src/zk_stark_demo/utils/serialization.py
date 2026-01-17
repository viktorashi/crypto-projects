from __future__ import annotations
import json
from typing import Any, Dict, List, Union
from ..algebra.field import FieldElement

def serialize_proof(proof: Any) -> Any:
    """
    Recursively converts proof object to JSON-friendly format.
    FieldElement -> int
    bytes -> hex string
    """
    if isinstance(proof, FieldElement):
        return proof.val
    elif isinstance(proof, bytes):
        return proof.hex()
    elif isinstance(proof, list):
        return [serialize_proof(item) for item in proof]
    elif isinstance(proof, dict):
        return {k: serialize_proof(v) for k, v in proof.items()}
    else:
        return proof

def deserialize_proof(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts back to internal types.
    """
    new_proof: Dict[str, Any] = {}
    new_proof['trace_root'] = bytes.fromhex(data['trace_root'])
    new_proof['fri_commitments'] = [bytes.fromhex(x) for x in data['fri_commitments']]
    new_proof['fri_final'] = FieldElement(data['fri_final'])
    
    new_proof['fri_layer_proofs'] = []
    for layer in data['fri_layer_proofs']:
        new_layer: List[Dict[str, Any]] = []
        for q in layer:
            item: Dict[str, Any] = {}
            item['idx'] = q['idx']
            item['val'] = FieldElement(q['val'])
            item['path'] = [bytes.fromhex(x) for x in q['path']]
            item['partner_idx'] = q['partner_idx']
            item['partner_val'] = FieldElement(q['partner_val'])
            item['partner_path'] = [bytes.fromhex(x) for x in q['partner_path']]
            new_layer.append(item)
        new_proof['fri_layer_proofs'].append(new_layer)
        
    new_proof['trace_queries'] = []
    for q in data['trace_queries']:
        item = {}
        item['idx'] = q['idx']
        item['val'] = [FieldElement(x) for x in q['val']]
        item['path'] = [bytes.fromhex(x) for x in q['path']]
        item['next_idx'] = q['next_idx']
        item['next_val'] = [FieldElement(x) for x in q['next_val']]
        item['next_path'] = [bytes.fromhex(x) for x in q['next_path']]
        new_proof['trace_queries'].append(item)
        
    if 'boundary_proofs' in data:
        new_proof['boundary_proofs'] = []
        for q in data['boundary_proofs']:
            item = {}
            item['step_idx'] = q['step_idx']
            item['lde_idx'] = q['lde_idx']
            item['reg_idx'] = q['reg_idx']
            item['val'] = FieldElement(q['val'])
            item['trace_val'] = FieldElement(q['trace_val'])
            item['trace_row'] = [FieldElement(x) for x in q['trace_row']]
            item['path'] = [bytes.fromhex(x) for x in q['path']]
            new_proof['boundary_proofs'].append(item)
        
    return new_proof

def save_proof(proofdict: Dict[str, Any], filename: str) -> None:
    json_ready = serialize_proof(proofdict)
    with open(filename, 'w') as f:
        json.dump(json_ready, f, indent=2)
        
def load_proof(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as f:
        data = json.load(f)
    return deserialize_proof(data)
