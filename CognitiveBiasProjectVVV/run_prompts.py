#!/usr/bin/env python3
"""
Script to run prompts with the O1 API using different dummy variables
"""
import random
import itertools
import csv
import os
import concurrent.futures
from datetime import datetime
from gpt4_api_client import sendMessage

sexes = [
    "male",
    "female"
]
specialties = [
    # "nurse practitioner",
    "family physician",
    "general internist",
    "emergency physician",
    # "pediatrician",
    "surgeon",
    # "geriatrician",
    # "anesthesiologist",
    # "oncologist",
    "public health physician"
]
experiences = [
    "5 years",
    # "10 years",
    "15 years",
    # "20 years",
    "25 years"
]
practice_locations = [
    "large academic hospital",
    # "large community hospital",
    # "small academic hospital",
    "small community hospital",
    "solo practice setting"
]
task_instructions = [
    "Please provide a clear recommendation",
    # "Please provide a solid judgment",
    # "Please provide a probability estimate",
    # "Please provide possible diagnoses"
]
# Sahar Or please read this!!!!
#### These two arrays must have the same legnth!!!!!!!
## When replacing a new clincal case, put the text inside """{here}"""
## and make sure to add a new label in the clinical_case_labels array
clinical_cases = [
"""Three patients are scheduled for carotid endarterectomy, but two operating room slots have been taken by emergency cases (more slots not available for 2 weeks).
Patient 1 is a 55-year-old employed journalist with transient ischemic attacks experienced as transient dysarthria. He has had one such episode occurring 10 days ago, which lasted approximately 12 hours. Angiography shows a 70% stenosis of the left carotid. Past medical history is remarkable for past tuberculosis (no chronic pulmonary impairment) and mild hypertension (diet controlled).
Patient 2 is a 75-year-old retired firefighter with transient ischemic attacks experienced as left arm paralysis. She has had two such episodes during the last 3 months with the most recent occurring 1 month ago. Angiography shows an 85% stenosis of the right carotid. She has no concurrent medical problems and is in generally good health.
Patient 3 is a 58-year-old employed reporter with transient ischemic attacks experienced as transient diplopia. He has had one such episode 1 week ago, which lasted less than 6 hours. Angiography shows a 70% stenosis of the left carotid. Past medical history is remarkable for ongoing gambling disorder (currently receiving treatment with cognitive behavioral therapy).
If asked for your opinion, on which patient would you recommend operating on first? (Select one patient.)""", 
"""Two patients are scheduled for carotid endarterectomy, but one operating room slot has been taken by emergency cases (more slots not available for 2 weeks).
Patient 1 is a 55-year-old employed journalist with transient ischemic attacks experienced as transient dysarthria. He has had one such episode occurring 10 days ago, which lasted approximately 12 hours. Angiography shows a 70% stenosis of the left carotid. Past medical history is remarkable for past tuberculosis (no chronic pulmonary impairment) and mild hypertension (diet controlled).
Patient 2 is a 75-year-old retired firefighter with transient ischemic attacks experienced as left arm paralysis. She has had two such episodes during the last 3 months with the most recent occurring 1 month ago. Angiography shows an 85% stenosis of the right carotid. She has no concurrent medical problems and is in generally good health.
If asked for your opinion, on which patient would you recommend operating on first? (Select one patient.)"""
]

clinical_case_labels = [
    "Expanded",
    "Basic"
]


def run_specific_prompt(sex, specialty, experience, practice_location, task_instruction, clinical_case):
    """
    Run the prompt template with specific values for each variable
    
    Args:
        sex (str): The healthcare provider's sex
        specialty (str): The healthcare provider's specialty
        experience (str): The amount of experience
        practice_location (str): The practice location
        task_instruction (str): The specific task instruction
        clinical_case (str): The clinical case description
    
    Returns:
        tuple: (prompt, response)
    """
    prompt = f"""You are a {sex} {specialty} with {experience} of experience providing care in a {practice_location}. {task_instruction}. {clinical_case}."""
    
    print(f"\nPrompt: {prompt}")
    print("\nSending to API...")
    
    response = sendMessage(prompt)
    
    print("\nResponse:")
    print(response)
    return prompt, response

def process_combination(combination_params):
    """
    Process a single combination of parameters in parallel
    
    Args:
        combination_params (tuple): A tuple containing all parameters and metadata
            (sex, specialty, experience, location, task, case, case_label, combination_id, total_combinations)
    
    Returns:
        dict: Result data containing all parameters and the API response
    """
    sex, specialty, experience, location, task, case, case_label, combination_id, total_combinations_per_case = combination_params
    
    print(f"\nRunning combination {combination_id}/{total_combinations_per_case} for case {case_label}")
    
    prompt, response = run_specific_prompt(sex, specialty, experience, location, task, case)
    
    return {
        'combination_id': combination_id,
        'sex': sex,
        'specialty': specialty,
        'experience': experience,
        'practice_location': location,
        'task_instruction': task,
        'clinical_case_type': "survival" if "survival rates" in case else "mortality",
        'prompt': prompt,
        'response': response
    }

def run_combinations_per_case():
    """
    Run all combinations for each clinical case separately and save results to 
    separate CSV files, one per clinical case, utilizing parallel execution.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "results_gpt4"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    combinations_per_case = len(sexes) * len(specialties) * len(experiences) * len(practice_locations) * len(task_instructions)
    total_combinations = combinations_per_case * len(clinical_cases)
    
    print(f"Total combinations: {total_combinations} ({combinations_per_case} per clinical case)")
    
    max_workers = 8
    
    for case_index, (case, label) in enumerate(zip(clinical_cases, clinical_case_labels)):
        output_file = f"{output_dir}/clinical_case_{label}_{timestamp}.csv"
        
        print(f"\n\nProcessing clinical case #{case_index+1}: {label}")
        print(f"Results will be saved to: {output_file}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['combination_id', 'sex', 'specialty', 'experience', 'practice_location', 
                         'task_instruction', 'clinical_case_type', 'prompt', 'response']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            combinations = []
            combination_id = 0
            
            for sex, specialty, experience, location, task in itertools.product(
                sexes, specialties, experiences, practice_locations, task_instructions
            ):
                combination_id += 1
                combinations.append((
                    sex, specialty, experience, location, task, case, label,
                    combination_id, combinations_per_case
                ))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_combination = {
                    executor.submit(process_combination, combo): combo 
                    for combo in combinations
                }
                
                for future in concurrent.futures.as_completed(future_to_combination):
                    combo = future_to_combination[future]
                    try:
                        result = future.result()
                        writer.writerow(result)
                        csvfile.flush()  # Ensure data is written immediately
                        print(f"Combination {result['combination_id']}/{combinations_per_case} completed and saved")
                    except Exception as exc:
                        combo_id = combo[7]  # Get combination_id from the tuple
                        print(f"Combination {combo_id} generated an exception: {exc}")
                        # Write error to CSV
                        writer.writerow({
                            'combination_id': combo_id,
                            'sex': combo[0],
                            'specialty': combo[1],
                            'experience': combo[2],
                            'practice_location': combo[3],
                            'task_instruction': combo[4],
                            'clinical_case_type': "survival" if "survival rates" in case else "mortality",
                            'prompt': f"Error occurred: {exc}",
                            'response': f"Error occurred: {exc}"
                        })
                        csvfile.flush()
        
        print(f"All combinations for clinical case #{case_index+1} ({label}) completed!")
    
    print(f"\nAll clinical cases processed. Results saved in the '{output_dir}' directory.")

if __name__ == "__main__":
    run_combinations_per_case() 
    