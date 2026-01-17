from typing import List
from .field import FieldElement

def fft(vals: List[FieldElement], root_of_unity: FieldElement) -> List[FieldElement]:
    """
    Computes the FFT of vals using the given root_of_unity.
    vals length must be a power of 2.
    root_of_unity must have order effectively covering the length.
    """
    n = len(vals)
    if n == 1:
        return vals

    # Splitting into evens and odds
    # In standard FFT (Cooley-Tukey), we split coefficients.
    # A(x) = A_even(x^2) + x * A_odd(x^2)
    evens = vals[0::2]
    odds = vals[1::2]
    
    root_squared = root_of_unity * root_of_unity
    
    left = fft(evens, root_squared)
    right = fft(odds, root_squared)
    
    result = [FieldElement.zero()] * n
    current_root = FieldElement.one()
    
    half_n = n // 2
    for i in range(half_n):
        # A(x_i) = A_even(x_i^2) + x_i * A_odd(x_i^2)
        # x_{i + N/2} = -x_i
        
        # val = left[i] + current_root * right[i]
        # val_plus_half = left[i] - current_root * right[i] (since x_{i+N/2} = -current_root)
        
        # In our field, is it guaranteed that root^(N/2) = -1?
        # Yes if root is primitive N-th root of unity.
        
        term = current_root * right[i]
        result[i] = left[i] + term
        result[i + half_n] = left[i] - term
        
        current_root = current_root * root_of_unity
        
    return result

def ifft(vals: List[FieldElement], root_of_unity: FieldElement) -> List[FieldElement]:
    """
    Inverse FFT.
    Interpolates values to coefficients.
    """
    inverse_root = root_of_unity.inv()
    result = fft(vals, inverse_root)
    
    n_inv = FieldElement(len(vals)).inv()
    return [r * n_inv for r in result]
