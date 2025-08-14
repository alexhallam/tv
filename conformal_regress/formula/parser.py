"""
Formula parser for R-style regression formulas.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import formulaic
import re


@dataclass
class ParsedFormula:
    """Parsed formula object."""
    response: str
    terms: List[str]
    interactions: List[Tuple[str, str]]
    transformations: Dict[str, str]
    original_formula: str
    
    def __str__(self) -> str:
        return self.original_formula


class FormulaParser:
    """
    Parser for R-style regression formulas.
    
    Supports:
    - Linear terms: y ~ x1 + x2
    - Interactions: y ~ x1 * x2
    - Transformations: y ~ I(x^2) + log(z)
    - GLM families: y ~ x1 + x2 (family="gaussian")
    """
    
    def __init__(self):
        self.transformations = {
            'log': np.log,
            'sqrt': np.sqrt,
            'exp': np.exp,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
        }
    
    def parse(self, formula: str) -> ParsedFormula:
        """
        Parse an R-style formula.
        
        Parameters
        ----------
        formula : str
            R-style formula (e.g., "y ~ x1 + x2")
            
        Returns
        -------
        ParsedFormula
            Parsed formula object
            
        Examples
        --------
        >>> parser = FormulaParser()
        >>> parsed = parser.parse("sales ~ price + advertising")
        >>> parsed.response
        'sales'
        >>> parsed.terms
        ['price', 'advertising']
        """
        # Clean formula
        formula = formula.strip()
        
        # Split into response and predictors
        if '~' not in formula:
            raise ValueError(f"Formula must contain '~': {formula}")
        
        response, predictors = formula.split('~', 1)
        response = response.strip()
        predictors = predictors.strip()
        
        # Parse predictors
        terms, interactions, transformations = self._parse_predictors(predictors)
        
        return ParsedFormula(
            response=response,
            terms=terms,
            interactions=interactions,
            transformations=transformations,
            original_formula=formula
        )
    
    def _parse_predictors(self, predictors: str) -> Tuple[List[str], List[Tuple[str, str]], Dict[str, str]]:
        """Parse predictor terms."""
        terms = []
        interactions = []
        transformations = {}
        
        # Split by + and handle interactions
        parts = [p.strip() for p in predictors.split('+')]
        
        for part in parts:
            if '*' in part:
                # Handle interactions
                vars_in_interaction = [v.strip() for v in part.split('*')]
                for i, var1 in enumerate(vars_in_interaction):
                    for var2 in vars_in_interaction[i+1:]:
                        interactions.append((var1, var2))
                terms.extend(vars_in_interaction)
            else:
                # Handle single terms and transformations
                term, transformation = self._parse_term(part)
                if transformation:
                    transformations[term] = transformation
                terms.append(term)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms, interactions, transformations
    
    def _parse_term(self, term: str) -> Tuple[str, Optional[str]]:
        """Parse a single term for transformations."""
        # Check for I() transformations
        if term.startswith('I(') and term.endswith(')'):
            inner = term[2:-1]
            # For now, just return the inner expression
            # In a full implementation, this would parse the expression
            return inner, None
        
        # Check for function transformations
        for func_name in self.transformations.keys():
            if term.startswith(f"{func_name}(") and term.endswith(')'):
                inner = term[len(func_name)+1:-1]
                return inner, func_name
        
        return term, None
    
    def create_design_matrix(self, formula: ParsedFormula, data: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """
        Create design matrix from parsed formula and data.
        
        Parameters
        ----------
        formula : ParsedFormula
            Parsed formula object
        data : pd.DataFrame
            Input data
            
        Returns
        -------
        Tuple[np.ndarray, List[str]]
            Design matrix and feature names
        """
        # Use formulaic to create the design matrix
        formulaic_formula = self._to_formulaic_formula(formula)
        
        # Create design matrix using formulaic
        from formulaic import model_matrix
        design_matrix = model_matrix(formulaic_formula, data)
        
        return design_matrix.values, design_matrix.columns.tolist()
    
    def _to_formulaic_formula(self, formula: ParsedFormula) -> str:
        """Convert ParsedFormula to formulaic-compatible string."""
        terms = []
        
        # Add main terms
        for term in formula.terms:
            if term in formula.transformations:
                trans = formula.transformations[term]
                terms.append(f"{trans}({term})")
            else:
                terms.append(term)
        
        # Add interactions
        for var1, var2 in formula.interactions:
            terms.append(f"{var1}:{var2}")
        
        # Add intercept
        terms.insert(0, "1")
        
        return " + ".join(terms)
    
    def validate_formula(self, formula: str, data: pd.DataFrame) -> bool:
        """
        Validate that a formula can be applied to the given data.
        
        Parameters
        ----------
        formula : str
            Formula string to validate
        data : pd.DataFrame
            Data to validate against
            
        Returns
        -------
        bool
            True if formula is valid for the data
        """
        try:
            parsed = self.parse(formula)
            
            # Check if response variable exists
            if parsed.response not in data.columns:
                return False
            
            # Check if all predictor variables exist
            for term in parsed.terms:
                if term not in data.columns:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def suggest_corrections(self, formula: str, data: pd.DataFrame) -> List[str]:
        """
        Suggest corrections for invalid formulas.
        
        Parameters
        ----------
        formula : str
            Invalid formula string
        data : pd.DataFrame
            Available data
            
        Returns
        -------
        List[str]
            List of suggested corrections
        """
        suggestions = []
        
        try:
            parsed = self.parse(formula)
            
            # Check response variable
            if parsed.response not in data.columns:
                similar = self._find_similar_columns(parsed.response, data.columns)
                if similar:
                    suggestions.append(f"Response variable '{parsed.response}' not found. Did you mean: {', '.join(similar)}?")
            
            # Check predictor variables
            missing_vars = []
            for term in parsed.terms:
                if term not in data.columns:
                    missing_vars.append(term)
            
            if missing_vars:
                suggestions.append(f"Missing predictor variables: {', '.join(missing_vars)}")
                suggestions.append(f"Available variables: {', '.join(data.columns)}")
            
        except ValueError as e:
            suggestions.append(f"Formula syntax error: {str(e)}")
            suggestions.append("Expected format: 'response ~ predictor1 + predictor2'")
        
        return suggestions
    
    def _find_similar_columns(self, target: str, columns: List[str], threshold: float = 0.8) -> List[str]:
        """Find columns similar to target using fuzzy matching."""
        import difflib
        similar = []
        
        for col in columns:
            similarity = difflib.SequenceMatcher(None, target.lower(), col.lower()).ratio()
            if similarity >= threshold:
                similar.append(col)
        
        return similar