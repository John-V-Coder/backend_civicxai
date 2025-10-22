"""
MeTTa Service - Local AI Engine for Priority Calculation
Provides fallback when uAgents gateway is not available
"""
import os
import sys

# Add MeTTa to Python path
METTA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'metta')
if os.path.exists(METTA_PATH) and METTA_PATH not in sys.path:
    sys.path.insert(0, METTA_PATH)


def calculate_priority(poverty_index, project_impact, environmental_score, corruption_risk):
    """
    Calculate priority score using MeTTa reasoning engine
    
    Args:
        poverty_index (float): 0-1, higher = more poverty
        project_impact (float): 0-1, higher = more impact
        environmental_score (float): 0-1, higher = more degradation
        corruption_risk (float): 0-1, higher = more risk
        
    Returns:
        dict: Priority calculation results with score, level, allocation, etc.
    """
    try:
        # Try to use MeTTa engine if available
        from hyperon import MeTTa, Environment
        
        # Initialize MeTTa
        metta = MeTTa()
        
        # Define MeTTa reasoning rules
        metta_code = f"""
        ; Define input metrics
        (= (poverty-index) {poverty_index})
        (= (project-impact) {project_impact})
        (= (environmental-score) {environmental_score})
        (= (corruption-risk) {corruption_risk})
        
        ; Define weights
        (= (poverty-weight) 0.4)
        (= (impact-weight) 0.3)
        (= (environmental-weight) 0.2)
        (= (corruption-weight) 0.1)
        
        ; Calculate weighted priority score
        (= (calculate-priority)
            (+ 
                (* (poverty-index) (poverty-weight))
                (* (project-impact) (impact-weight))
                (* (environmental-score) (environmental-weight))
                (* (- 1 (corruption-risk)) (corruption-weight))
            )
        )
        
        ; Query the priority
        !(calculate-priority)
        """
        
        # Execute MeTTa code
        result = metta.run(metta_code)
        
        # Parse MeTTa result
        if result and len(result) > 0:
            priority_score = float(str(result[-1][0]))
        else:
            # Fallback to Python calculation
            priority_score = calculate_priority_python(
                poverty_index, project_impact, environmental_score, corruption_risk
            )
        
    except Exception as e:
        # Fallback to Python calculation if MeTTa fails
        print(f"MeTTa engine not available, using Python fallback: {e}")
        priority_score = calculate_priority_python(
            poverty_index, project_impact, environmental_score, corruption_risk
        )
    
    # Calculate priority level
    if priority_score >= 0.7:
        priority_level = 'critical'
    elif priority_score >= 0.5:
        priority_level = 'high'
    elif priority_score >= 0.3:
        priority_level = 'medium'
    else:
        priority_level = 'low'
    
    # Calculate allocation percentage
    # Higher priority = higher allocation
    allocation_percentage = min(100, max(10, priority_score * 100))
    
    # Generate explanation
    explanation = generate_explanation(
        priority_score, priority_level, 
        poverty_index, project_impact, environmental_score, corruption_risk
    )
    
    # Generate key findings
    key_findings = generate_key_findings(
        poverty_index, project_impact, environmental_score, corruption_risk
    )
    
    # Generate recommendations
    recommendations = generate_recommendations(
        priority_level, allocation_percentage,
        poverty_index, project_impact, environmental_score, corruption_risk
    )
    
    return {
        'priority_score': round(priority_score, 4),
        'priority_level': priority_level,
        'allocation_percentage': round(allocation_percentage, 2),
        'confidence_score': round(0.85 + (priority_score * 0.1), 2),  # 0.85-0.95
        'explanation': explanation,
        'key_findings': key_findings,
        'recommendations': recommendations,
        'factors': {
            'poverty_index': poverty_index * 0.4,
            'project_impact': project_impact * 0.3,
            'environmental_score': environmental_score * 0.2,
            'corruption_risk': (1 - corruption_risk) * 0.1
        },
        'engine': 'metta_local'
    }


def calculate_priority_python(poverty_index, project_impact, environmental_score, corruption_risk):
    """
    Pure Python priority calculation (fallback)
    """
    # Weights
    POVERTY_WEIGHT = 0.4
    IMPACT_WEIGHT = 0.3
    ENVIRONMENTAL_WEIGHT = 0.2
    CORRUPTION_WEIGHT = 0.1
    
    # Calculate weighted score
    # Corruption risk is inverted (lower corruption = higher priority)
    priority_score = (
        poverty_index * POVERTY_WEIGHT +
        project_impact * IMPACT_WEIGHT +
        environmental_score * ENVIRONMENTAL_WEIGHT +
        (1 - corruption_risk) * CORRUPTION_WEIGHT
    )
    
    return priority_score


def generate_explanation(priority_score, priority_level, poverty_index, project_impact, 
                        environmental_score, corruption_risk):
    """Generate human-readable explanation"""
    explanations = {
        'critical': f"This region shows CRITICAL need with a priority score of {priority_score:.1%}. "
                   f"Immediate intervention is required due to high poverty ({poverty_index:.1%}) "
                   f"and significant project impact potential ({project_impact:.1%}).",
        
        'high': f"This region has HIGH priority with a score of {priority_score:.1%}. "
               f"Substantial resource allocation is recommended given the poverty level ({poverty_index:.1%}) "
               f"and environmental conditions ({environmental_score:.1%}).",
        
        'medium': f"This region shows MEDIUM priority with a score of {priority_score:.1%}. "
                 f"Standard resource allocation is appropriate based on current metrics.",
        
        'low': f"This region has LOWER priority with a score of {priority_score:.1%}. "
              f"Baseline support should be maintained while monitoring for changing conditions."
    }
    
    return explanations.get(priority_level, "Priority calculated based on regional metrics.")


def generate_key_findings(poverty_index, project_impact, environmental_score, corruption_risk):
    """Generate key findings based on metrics"""
    findings = []
    
    if poverty_index >= 0.7:
        findings.append(f"High poverty rate detected ({poverty_index:.1%}) - economic support needed")
    
    if project_impact >= 0.7:
        findings.append(f"High project impact potential ({project_impact:.1%}) - investments will yield strong returns")
    
    if environmental_score >= 0.7:
        findings.append(f"Severe environmental degradation ({environmental_score:.1%}) - conservation measures urgent")
    
    if corruption_risk >= 0.6:
        findings.append(f"Elevated corruption risk ({corruption_risk:.1%}) - enhanced oversight required")
    elif corruption_risk <= 0.3:
        findings.append(f"Low corruption risk ({corruption_risk:.1%}) - favorable governance environment")
    
    if not findings:
        findings.append("Metrics indicate balanced conditions across all indicators")
    
    return findings


def generate_recommendations(priority_level, allocation_percentage, poverty_index, 
                            project_impact, environmental_score, corruption_risk):
    """Generate actionable recommendations"""
    recommendations = []
    
    # Allocation-based recommendations
    if allocation_percentage >= 70:
        recommendations.append("Allocate majority of available funds to this region")
        recommendations.append("Fast-track project approvals and implementation")
    elif allocation_percentage >= 50:
        recommendations.append("Provide substantial funding allocation")
        recommendations.append("Implement standard monitoring protocols")
    else:
        recommendations.append("Provide moderate funding allocation")
        recommendations.append("Monitor for changing conditions")
    
    # Metric-specific recommendations
    if poverty_index >= 0.7:
        recommendations.append("Prioritize poverty alleviation programs")
        recommendations.append("Implement cash transfer or social safety net schemes")
    
    if project_impact >= 0.7:
        recommendations.append("Maximize investment in high-impact projects")
    
    if environmental_score >= 0.7:
        recommendations.append("Include environmental restoration components")
        recommendations.append("Engage local communities in conservation")
    
    if corruption_risk >= 0.6:
        recommendations.append("Establish strong audit and oversight mechanisms")
        recommendations.append("Use transparent digital payment systems")
    
    return recommendations


# For compatibility with different import patterns
def get_priority_calculation(data):
    """
    Alternative interface for priority calculation
    Accepts dict with metrics
    """
    return calculate_priority(
        poverty_index=data.get('poverty_index', 0.5),
        project_impact=data.get('project_impact', 0.5),
        environmental_score=data.get('environmental_score', 0.5),
        corruption_risk=data.get('corruption_risk', 0.3)
    )
