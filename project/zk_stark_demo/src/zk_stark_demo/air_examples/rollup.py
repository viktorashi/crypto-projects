from __future__ import annotations
from typing import List, Tuple, Dict, Any
from ..algebra.field import FieldElement
from ..stark.air import AIR

class RollupAIR(AIR):
    """
    Proves the validity of a batch of transactions between N users.
    
    Trace Design:
    To support N users, we can't have N columns if N is large (trace width would be huge).
    Instead, we use a slightly more complex layout or simplify for the demo.
    
    Simplified "Account" approach for Demo:
    We verify a list of transactions sequentially.
    Width = 4 (SenderIdx, ReceiverIdx, Amount, BalanceChecksum?)
    No, this requires Merkle Roots for state which is complex (Merkle roots in field arithmetic).
    
    Approach B (Fixed N, optimized):
    If N is small (e.g. 10), we can validly have N columns. 
    Let's aim for N=10 users.
    
    Trace:
    Columns 0..N-1: Balances of User i
    Column N: Sender Index (Witness)
    Column N+1: Receiver Index (Witness)
    Column N+2: Amount (Witness)
    
    Transition Constraint:
    For every col k in 0..N-1:
        Next_Bal[k] = Curr_Bal[k] 
                      - Amount * (Sender == k) 
                      + Amount * (Receiver == k)
                      
    This uses "Selectors".
    Is (Sender == k) expressible as low degree?
    Lagrange polynomial L_k(x). If Sender is x, L_k(x) = 1 if x=k else 0.
    Since Sender is an integer 0..N-1, we can compute L_k(Sender).
    Degree of selector is N-1.
    
    This increases constraint degree to ~N.
    StarkProver handles high degree, but it gets slower.
    For N=10, Degree=10. This is manageable but heavy.
    
    Let's implement this for N users.
    """
    def __init__(self, trace_length: int, num_users: int, initial_balances: List[int], final_balances: List[int]) -> None:
        self.length = trace_length
        self.num_users = num_users
        self.initial_balances = [FieldElement(x) for x in initial_balances]
        self.final_balances = [FieldElement(x) for x in final_balances]
        
    def trace_width(self) -> int:
        # width = N + 3 (Sender, Receiver, Amount)
        return self.num_users + 3

    def get_public_inputs(self) -> Dict[str, Any]:
        return {
            'length': self.length,
            'num_users': self.num_users,
            'initial_balances': [x.val for x in self.initial_balances],
            'final_balances': [x.val for x in self.final_balances]
        }
        
    def constraint_degree(self) -> int:
        # P(x) involves Selector * Amount. Selector degree N-1. Total N.
        return self.num_users
        
    def generate_trace(self, transactions: List[Dict[str, int]]) -> List[List[FieldElement]]:
        """
        transactions: List of {'from': i, 'to': j, 'amount': k}
        """
        trace = []
        
        # Current balances
        balances = [b for b in self.initial_balances]
        
        # Pad transactions with no-ops (from=0, to=0, amount=0)
        # Note: from=to is a no-op that satisfies constraints (bal - x + x = bal)
        padded_txs = transactions + [{'from':0, 'to':0, 'amount':0}] * (self.length - 1 - len(transactions))
        
        for tx in padded_txs:
            row = []
            # User balances
            for b in balances:
                row.append(b)
                
            sender = tx['from']
            receiver = tx['to']
            amount = FieldElement(tx['amount'])
            
            row.append(FieldElement(sender))
            row.append(FieldElement(receiver))
            row.append(amount)
            
            trace.append(row)
            
            # Update state
            balances[sender] = balances[sender] - amount
            balances[receiver] = balances[receiver] + amount
            
        # Final row (state only, witnesses irrelevant but typical to fill 0)
        last_row = [b for b in balances] + [FieldElement(0), FieldElement(0), FieldElement(0)]
        trace.append(last_row)
        
        return trace
        
    def trace_length(self) -> int:
        return self.length

    def get_boundary_constraints(self) -> List[Tuple[int, int, FieldElement]]:
        constraints = []
        # Start State
        for i in range(self.num_users):
            constraints.append((0, i, self.initial_balances[i]))
            
        # End State
        for i in range(self.num_users):
            constraints.append((self.length - 1, i, self.final_balances[i]))
            
        return constraints

    def evaluate_transition_constraints(
        self, 
        current_step: List[FieldElement], 
        next_step: List[FieldElement]
    ) -> List[FieldElement]:
        # Columns: [0..N-1] Balances, [N] Sender, [N+1] Receiver, [N+2] Amount
        
        sender = current_step[self.num_users]
        receiver = current_step[self.num_users + 1]
        amount = current_step[self.num_users + 2]
        
        res_constraints = []
        
        # Pre-compute lagrange selectors?
        # L_k(x) is 1 if x=k, 0 if x!=k (for x in 0..N-1)
        # We can implement this naively:
        # L_k(x) = prod_{j!=k} (x - j) / prod_{j!=k} (k - j)
        
        # Helper to compute product for selector
        def selector(target_idx: int, variable: FieldElement) -> FieldElement:
            # If N is small, naive is fine.
            numerator = FieldElement(1)
            denominator = FieldElement(1)
            
            # Loop 0 to N-1
            for j in range(self.num_users):
                if j == target_idx: continue
                
                j_fe = FieldElement(j)
                numerator = numerator * (variable - j_fe)
                denominator = denominator * (FieldElement(target_idx) - j_fe)
                
            return numerator / denominator
            
        # Optimization: We compute 'is_sender[k]' and 'is_receiver[k]'
        # This is expensive inside the constraint loop (called N*blowup times).
        # But this is Python demo.
        
        for k in range(self.num_users):
             # Next_Bal[k] = Curr_Bal[k] - Amount * (Sender==k) + Amount * (Receiver==k)
             
             is_sender = selector(k, sender)
             is_receiver = selector(k, receiver)
             
             delta = amount * (is_receiver - is_sender)
             
             expected_next = current_step[k] + delta
             constraint = next_step[k] - expected_next
             
             res_constraints.append(constraint)
             
        return res_constraints
