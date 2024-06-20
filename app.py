from flask import Flask, render_template, request, jsonify, session
import os
from supabase import create_client, Client
import requests
from flask_cors import CORS
# import google.generativeai as genai

# genai.configure(api_key=os.environ["API_KEY"])

SUPABASE_URL = 'https://zqxdgopzsaoyhctnghaa.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxeGRnb3B6c2FveWhjdG5naGFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY1NjkzNDEsImV4cCI6MjAzMjE0NTM0MX0.2kOPWjNeeEQQyXzfC_ORHOV1UZMoNXJg5pYOPoKlUgM'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)
CORS(app)
app.secret_key = 'teribkc69'

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    session['user_id'] = user_id 
    return render_template('index.html')

@app.route('/next_question', methods=['POST'])
def next_question():
    current_answers = request.json
    next_q = get_next_question(current_answers)
    return jsonify(next_q)

def get_next_question(answers):
    if not answers:
        return {"question": "What is your name?", "options": [], "key": "name"}
    if "name" in answers and "age" not in answers:
        return {"question": "What is your age?", "options": [], "key": "age"}
    if "age" in answers and "gender" not in answers:
        return {"question": "What is your gender?", "options": ["Male", "Female", "Other"], "key": "gender"}
    if "gender" in answers and "medical_history" not in answers:
        return {"question": "Do you have any relevant medical history?", "options": ["Yes", "No"], "key": "medical_history"}
    if "medical_history" in answers and answers["medical_history"] == "Yes" and "medical_details" not in answers:
        return {"question": "Please describe your medical history.", "options": [], "key": "medical_details"}
    if "medical_history" in answers and "diagnosed" not in answers:
        return {"question": "Have you been diagnosed with breast cancer?", "options": ["Yes", "No"], "key": "diagnosed"}
    if answers.get("diagnosed") == "Yes":
        if "diagnosed_stage" not in answers:
            return {"question": "What is the diagnosed stage?", "options": [], "key": "diagnosed_stage"}
        if "diagnosed_stage" in answers and "type_of_specimen" not in answers:
            return {"question": "Please describe the type of specimen.", "options": [], "key": "type_of_specimen"}
        if "type_of_specimen" in answers and "location_of_specimen" not in answers:
            return {"question": "Please describe the location of the specimen.", "options": [], "key": "location_of_specimen"}
        if "location_of_specimen" in answers and "size_of_specimen" not in answers:
            return {"question": "Please enter the size of the specimen.", "options": [], "key": "size_of_specimen"}
        if "size_of_specimen" in answers and "weight_of_specimen" not in answers:
            return {"question": "Please enter the weight of the specimen.", "options": [], "key": "weight_of_specimen"}
        if "weight_of_specimen" in answers and "histologic_type" not in answers:
            return {"question": "Please describe the Histologic Type.", "options": [], "key": "histologic_type"}
        if "histologic_type" in answers and "histologic_grade" not in answers:
            return {"question": "Please enter the Histologic Grade.", "options": [], "key": "histologic_grade"}
        if "histologic_grade" in answers and "tumor_size" not in answers:
            return {"question": "Please describe the Tumor Size.", "options": [], "key": "tumor_size", "type": "number"}
        if "tumor_size" in answers and "lymphovascular_invasion" not in answers:
            return {"question": "Is there Lymphovascular Invasion?", "options": ["Yes", "No"], "key": "lymphovascular_invasion"}
        if "lymphovascular_invasion" in answers and "her2_status" not in answers:
            return {"question": "What is the HER2/neu (Human Epidermal Growth Factor Receptor 2) Status?", "options": ["Positive", "Negative", "Equivocal"], "key": "her2_status"}
        if "her2_status" in answers and "menopause_status" not in answers:
            return {"question": "What is your Menopause Status?", "options": ["Pre-menopausal", "Post-menopausal"], "key": "menopause_status"}
        if "menopause_status" in answers and "ki67_index" not in answers:
            return {"question": "What is the Ki-67 Proliferation Index?", "options": [], "key": "ki67_index"}
        if "ki67_index" in answers and "num_lymph_nodes_examined" not in answers:
            return {"question": "How many Lymph Nodes were Examined?", "options": [], "key": "num_lymph_nodes_examined", "type": "number"}
        if "num_lymph_nodes_examined" in answers and "num_lymph_nodes_involved" not in answers:
            return {"question": "How many Lymph Nodes were Involved with Cancer?", "options": [], "key": "num_lymph_nodes_involved", "type": "number"}
        if "num_lymph_nodes_involved" in answers and "size_largest_metastasis" not in answers:
            return {"question": "What is the Size of the Largest Metastasis in a Lymph Node?", "options": [], "key": "size_largest_metastasis", "type": "number"}
        if "size_largest_metastasis" in answers and "genetic_mutations" not in answers:
            return {"question": "Are there any Genetic Mutations?", "options": [], "key": "genetic_mutations"}
        if "genetic_mutations" in answers and "pathology_report" not in answers:
            return {"question": "Please upload your Pathology Report.", "options": [], "key": "pathology_report", "type": "file"}
    
    if answers.get("diagnosed") == "No":
        if "last_screening" not in answers:
            return {"question": "When was your last screening?", "options": [], "key": "last_screening"}
        if "last_screening" in answers and "screening_frequency" not in answers:
            return {"question": "How frequently do you get screened?", "options": ["Annually", "Every 2 years", "Every 5 years", "Never"], "key": "screening_frequency"}

    save_to_supabase(answers)
    return {"question": "Thank you for completing the survey!", "options": [], "key": None}

def save_to_supabase(answers):
    userId = session.get('user_id')
    data = {
    "user_id": userId ,
    "name": answers.get("name"),
    "age": answers.get("age"),
    "gender": answers.get("gender"),
    "medical_history": answers.get("medical_history", ""),
    "medical_details": answers.get("medical_details", ""),
    "diagnosed": answers.get("diagnosed"),
    "diagnosed_stage": answers.get("diagnosed_stage"),
    "type_of_specimen": answers.get("type_of_specimen"),
    "location_of_specimen": answers.get("location_of_specimen"),
    "size_of_specimen": answers.get("size_of_specimen"),
    "weight_of_specimen": answers.get("weight_of_specimen"),
    "histologic_type": answers.get("histologic_type"),
    "histologic_grade": answers.get("histologic_grade"),
    "tumor_size": answers.get("tumor_size"),
    "lymphovascular_invasion": answers.get("lymphovascular_invasion"),
    "her2_status": answers.get("her2_status"),
    "menopause_status": answers.get("menopause_status"),
    "ki67_index": answers.get("ki67_index"),
    "num_lymph_nodes_examined": answers.get("num_lymph_nodes_examined"),
    "num_lymph_nodes_involved": answers.get("num_lymph_nodes_involved"),
    "size_largest_metastasis": answers.get("size_largest_metastasis"),
    "genetic_mutations": answers.get("genetic_mutations"),
    "pathology_report": answers.get("pathology_report"),
    "last_screening": answers.get("last_screening"),
    "screening_frequency": answers.get("screening_frequency"),
}

    supabase.table('survey').insert(data).execute()

# @app.route('/submit_answers', methods=['POST'])
# def submit_answers():
#     answers = request.json
#     # Call Gemini API to generate response
#     gemini_response = generate_gemini_response(answers)
#     # Extract tags from the first line of Gemini response
#     first_line, md_content = gemini_response.split('\n', 1)
#     tags = first_line.strip()
#     # Save tags to Supabase
#     save_tags_to_supabase(answers['user_id'], tags)
#     # Return the formatted markdown content
#     return jsonify({"markdown": md_content})

# def generate_gemini_response(answers):
#     prompt = generate_gemini_prompt(answers)
#     model = genai.GenerativeModel('gemini-1.0-pro')
#     response = model.generate_content(prompt)
#     return response.text

# def generate_gemini_prompt(answers):
#     prompt = """
#     You are an expert doctor specializing in breast cancer treatment. Below are the question answers based on a patient's pathology report. Explain the available treatment options and why these treatment options would be effective. Your response should be beautifully formatted using markdown (md) and should be in simple, easy-to-understand English. Additionally, provide the most relevant tags from the list below, categorized under different types. The tags should be comma-separated and placed on the first line of your answer.

#     > Demographic Tags
#     - Age Group
#       - 20s
#       - 30s
#       - 40s
#       - 50s
#       - 60s
#       - 70+
#     > Medical Status Tags
#     - Stages of Cancer
#       - Stage 0
#       - Stage I
#       - Stage II
#       - Stage III
#       - Stage IV
#     - Menopause Status
#       - Pre-menopausal
#       - Peri-menopausal
#       - Post-menopausal
#     - Genetic Factors
#       - BRCA1
#       - BRCA2
#       - HER2-positive
#     - Cancer Type
#       - Ductal Carcinoma In Situ (DCIS)
#       - Invasive Ductal Carcinoma (IDC)
#       - Invasive Lobular Carcinoma (ILC)
#       - Triple-Negative Breast Cancer (TNBC)
#     > Treatment Tags
#     - Treatment Type
#       - Surgery
#       - Chemotherapy
#       - Radiation Therapy
#       - Hormone Therapy
#       - Targeted Therapy
#       - Immunotherapy
#     """
#     return prompt

# def save_tags_to_supabase(user_id, tags):
#     supabase.table('survey').update({"tags": tags}).eq("user_id", request.args.get('user_id')).execute()

if __name__ == '__main__':
    app.run(debug=True)
