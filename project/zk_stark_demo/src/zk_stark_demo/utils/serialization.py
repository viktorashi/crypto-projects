
import json
from base64 import b64encode, b64decode
from ..algebra.field import FieldElement

def serialize_proof(proof):
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

def deserialize_proof(data):
    """
    Converts back to internal types.
    Strict schema is hard since we don't know what is FieldElement vs int.
    But for FieldElements, usually they appear in 'val' fields or specific lists.
    
    Actually, easiest way: 
    - Convert hex strings to bytes (if they look like hex? dangerous).
    - Convert specific keys.
    """
    # Just return the dict, and let the components convert when needed?
    # StarkVerifier expects FieldElements in some places (like final constant).
    # And FriVerifier expects it.
    
    # We'll implement a helper that reconstructs specific structures if needed.
    # But recursively mapping back is ambiguous.
    
    # Strategy: Leave as primitives (int/hex-str) and modify Verifier to handle them?
    # Or implement a smarter deserializer that knows the schema.
    
    # Schema-aware deserialization:
    # trace_root: hex -> bytes
    # fri_commitments: list of hex -> bytes
    # fri_final: int -> FieldElement
    # fri_layer_proofs: list of list of dicts:
    #    val: int -> FieldElement
    #    path: list of hex -> bytes
    # ...
    
    new_proof = {}
    new_proof['trace_root'] = bytes.fromhex(data['trace_root'])
    new_proof['fri_commitments'] = [bytes.fromhex(x) for x in data['fri_commitments']]
    new_proof['fri_final'] = FieldElement(data['fri_final'])
    
    new_proof['fri_layer_proofs'] = []
    for layer in data['fri_layer_proofs']:
        new_layer = []
        for q in layer:
            item = {}
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

def save_proof(proofdict, filename):
    json_ready = serialize_proof(proofdict)
    with open(filename, 'w') as f:
        json.dump(json_ready, f, indent=2)
        
def load_proof(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return deserialize_proof(data)
