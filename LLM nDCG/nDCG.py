import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class nDCGCalculator:
    """
    Calculates Normalized Discounted Cumulative Gain (nDCG) for skills evaluation.
    """
    
    def __init__(self, ideal_ranking: List[str]):
        """
        Initialize with the ideal ranking of skills from most to least important.
        
        Args:
            ideal_ranking: List of skills in order of importance (most to least)
        """
        self.ideal_ranking = [skill.lower().strip() for skill in ideal_ranking]
        self.ideal_gains = self._calculate_ideal_gains()
        
    def _calculate_ideal_gains(self) -> List[float]:
        """Calculate the ideal gains for the perfect ranking."""
        gains = []
        for i, skill in enumerate(self.ideal_ranking):
            # Use log2(i+2) for discounting, where i+2 ensures log2(1) = 0 for first item
            gain = 1.0 / np.log2(i + 2)
            gains.append(gain)
        return gains
    
    def _normalize_skill_name(self, skill: str) -> str:
        """Normalize skill names for better matching."""
        skill = skill.lower().strip()
        
        # Handle common variations
        skill_mappings = {
            'python (flask)': 'python',
            'flask': 'python',
            'python': 'python',
            'golang': 'golang',
            'go (golang)': 'golang',
            'go': 'golang',
            'restful api': 'rest api',
            'rest api design': 'rest api',
            'rest api design & optimization': 'rest api',
            'rest api': 'rest api',
            'microservices': 'microservices architecture',
            'microservices architecture': 'microservices architecture',
            'distributed systems': 'distributed systems',
            'distributed systems design': 'distributed systems',
            'databases (mysql, postgres, mongodb)': 'databases (mysql, postgres, mongodb)',
            'mysql': 'databases (mysql, postgres, mongodb)',
            'postgresql': 'databases (mysql, postgres, mongodb)',
            'postgres': 'databases (mysql, postgres, mongodb)',
            'mongodb': 'databases (mysql, postgres, mongodb)',
            'sql': 'sql',
            'sql proficiency': 'sql',
            'sql proficiency (mysql, postgresql)': 'sql',
            'nosql': 'nosql',
            'nosql databases': 'nosql',
            'nosql databases (mongodb, etc.)': 'nosql',
            'aws': 'aws',
            'aws / azure': 'aws',
            'azure': 'aws',
            'cloud services (aws or azure)': 'aws',
            'cloud platforms (aws, gcp, azure)': 'aws',
            'cloud platforms': 'aws',
            'docker': 'docker',
            'containerization': 'docker',
            'containerization (docker)': 'docker',
            'kubernetes (k8s)': 'kubernetes (k8s)',
            'kubernetes': 'kubernetes (k8s)',
            'orchestration': 'kubernetes (k8s)',
            'orchestration (kubernetes)': 'kubernetes (k8s)',
            'ci/cd': 'ci/cd',
            'ci/cd pipeline': 'ci/cd',
            'ci/cd pipeline development': 'ci/cd',
            'kafka': 'kafka',
            'amazon sqs': 'kafka',
            'messaging systems': 'kafka',
            'messaging systems (amazon sqs, kafka)': 'kafka',
            'terraform': 'terraform',
            'infrastructure as code': 'terraform',
            'infrastructure as code (terraform)': 'terraform',
            'technical lead': 'technical lead',
            'technical leadership': 'technical lead',
            'technical leadership & mentorship': 'technical lead',
            'mentorship': 'technical lead'
        }
        
        return skill_mappings.get(skill, skill)
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from the extracted keywords text."""
        if pd.isna(text) or text == '':
            return []
        
        # Split by semicolon and clean up
        skills = [skill.strip() for skill in text.split(';')]
        skills = [skill for skill in skills if skill]  # Remove empty strings
        
        # Normalize each skill
        normalized_skills = [self._normalize_skill_name(skill) for skill in skills]
        
        return normalized_skills
    
    def calculate_dcg(self, ranked_skills: List[str]) -> float:
        """
        Calculate Discounted Cumulative Gain for a ranked list of skills.
        
        Args:
            ranked_skills: List of skills in the order they appear
            
        Returns:
            DCG score
        """
        dcg = 0.0
        for i, skill in enumerate(ranked_skills):
            # Find the position of this skill in the ideal ranking
            try:
                ideal_position = self.ideal_ranking.index(skill)
                # Calculate gain based on ideal position
                gain = 1.0 / np.log2(ideal_position + 2)
            except ValueError:
                # Skill not in ideal ranking, assign minimal gain
                gain = 0.1 / np.log2(i + 2)
            
            # Apply discounting based on current position
            dcg += gain / np.log2(i + 2)
        
        return dcg
    
    def calculate_idcg(self) -> float:
        """Calculate the ideal DCG for perfect ranking."""
        return sum(self.ideal_gains)
    
    def calculate_ndcg(self, ranked_skills: List[str]) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain.
        
        Args:
            ranked_skills: List of skills in the order they appear
            
        Returns:
            nDCG score between 0 and 1
        """
        dcg = self.calculate_dcg(ranked_skills)
        idcg = self.calculate_idcg()
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def analyze_skills_ranking(self, ranked_skills: List[str]) -> Dict:
        """
        Analyze the ranking of skills and provide detailed insights.
        
        Args:
            ranked_skills: List of skills in the order they appear
            
        Returns:
            Dictionary with analysis results
        """
        normalized_skills = [self._normalize_skill_name(skill) for skill in ranked_skills]
        
        # Calculate nDCG
        ndcg_score = self.calculate_ndcg(normalized_skills)
        
        # Find matches with ideal ranking
        matches = []
        mismatches = []
        
        for i, skill in enumerate(normalized_skills):
            try:
                ideal_position = self.ideal_ranking.index(skill)
                if i == ideal_position:
                    matches.append({
                        'skill': skill,
                        'position': i,
                        'ideal_position': ideal_position,
                        'status': 'perfect_match'
                    })
                else:
                    mismatches.append({
                        'skill': skill,
                        'position': i,
                        'ideal_position': ideal_position,
                        'status': 'misplaced'
                    })
            except ValueError:
                mismatches.append({
                    'skill': skill,
                    'position': i,
                    'ideal_position': -1,
                    'status': 'not_in_ideal'
                })
        
        return {
            'ndcg_score': ndcg_score,
            'total_skills': len(normalized_skills),
            'matches': matches,
            'mismatches': mismatches,
            'match_count': len(matches),
            'mismatch_count': len(mismatches),
            'coverage_percentage': len([s for s in normalized_skills if s in self.ideal_ranking]) / len(self.ideal_ranking) * 100
        }

def main():
    """Main function to process the CSV and calculate nDCG scores."""
    
    # Define the ideal ranking of skills from most to least important
    ideal_skills_ranking = [
        "Python",
        "Golang",
        "REST API",
        "Microservices Architecture",
        "Distributed Systems",
        "Databases (MySQL, Postgres, MongoDB)",
        "SQL",
        "NoSQL",
        "AWS",
        "Docker",
        "Kubernetes (K8s)",
        "CI/CD",
        "Kafka",
        "Terraform",
        "Technical Lead"
    ]
    
    # Initialize nDCG calculator
    calculator = nDCGCalculator(ideal_skills_ranking)
    
    # Read the CSV file
    try:
        df = pd.read_csv('gemini_results.csv')
        logger.info(f"Successfully loaded CSV with {len(df)} rows")
    except FileNotFoundError:
        logger.error("CSV file not found. Please ensure 'gemini_results.csv' is in the current directory.")
        return
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return
    
    # Check if 'Extracted Keywords' column exists
    if 'Extracted Keywords' not in df.columns:
        logger.error("'Extracted Keywords' column not found in the CSV file.")
        logger.info(f"Available columns: {list(df.columns)}")
        return
    
    # Process each row and calculate nDCG scores
    results = []
    
    for idx, row in df.iterrows():
        extracted_keywords = row['Extracted Keywords']
        
        # Extract skills from the text
        skills = calculator._extract_skills_from_text(extracted_keywords)
        
        # Calculate nDCG and analyze ranking
        analysis = calculator.analyze_skills_ranking(skills)
        
        # Create result row
        result_row = {
            'Row_Index': idx,
            'Test_Run_Number': row.get('Test Run Number', ''),
            'Thinking_Budget_Tokens': row.get('Thinking Budget (Tokens)', ''),
            'Analysis_Dimension': row.get('Analysis Dimension', ''),
            'nDCG_Score': round(analysis['ndcg_score'], 4),
            'Total_Skills_Extracted': analysis['total_skills'],
            'Skills_Coverage_Percentage': round(analysis['coverage_percentage'], 2),
            'Perfect_Matches': analysis['match_count'],
            'Misplaced_Skills': analysis['mismatch_count'],
            'Extracted_Skills': '; '.join(skills),
            'Ideal_Ranking': '; '.join(calculator.ideal_ranking),
            'Analysis_Details': str(analysis)
        }
        
        results.append(result_row)
        
        # Log progress
        if (idx + 1) % 50 == 0:
            logger.info(f"Processed {idx + 1} rows...")
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results to CSV
    output_filename = 'ndcg_analysis_results.csv'
    results_df.to_csv(output_filename, index=False)
    
    # Print summary statistics
    logger.info(f"\n=== nDCG Analysis Summary ===")
    logger.info(f"Total rows processed: {len(results_df)}")
    logger.info(f"Average nDCG score: {results_df['nDCG_Score'].mean():.4f}")
    logger.info(f"Median nDCG score: {results_df['nDCG_Score'].median():.4f}")
    logger.info(f"Min nDCG score: {results_df['nDCG_Score'].min():.4f}")
    logger.info(f"Max nDCG score: {results_df['nDCG_Score'].max():.4f}")
    logger.info(f"Standard deviation: {results_df['nDCG_Score'].std():.4f}")
    
    # Show top 5 and bottom 5 results
    logger.info(f"\n=== Top 5 nDCG Scores ===")
    top_5 = results_df.nlargest(5, 'nDCG_Score')[['Row_Index', 'nDCG_Score', 'Total_Skills_Extracted', 'Skills_Coverage_Percentage']]
    for _, row in top_5.iterrows():
        logger.info(f"Row {row['Row_Index']}: nDCG={row['nDCG_Score']}, Skills={row['Total_Skills_Extracted']}, Coverage={row['Skills_Coverage_Percentage']}%")
    
    logger.info(f"\n=== Bottom 5 nDCG Scores ===")
    bottom_5 = results_df.nsmallest(5, 'nDCG_Score')[['Row_Index', 'nDCG_Score', 'Total_Skills_Extracted', 'Skills_Coverage_Percentage']]
    for _, row in bottom_5.iterrows():
        logger.info(f"Row {row['Row_Index']}: nDCG={row['nDCG_Score']}, Skills={row['Total_Skills_Extracted']}, Coverage={row['Skills_Coverage_Percentage']}%")
    
    logger.info(f"\nResults saved to: {output_filename}")
    
    return results_df

if __name__ == "__main__":
    main()
