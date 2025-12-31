from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load model saat aplikasi dimulai (HANYA model, tanpa preprocessor)
model = None
model_path = 'models/employee_attrition_xgboost_model.pkl'

if os.path.exists(model_path):
    try:
        model = joblib.load(model_path)
        print("✅ Model berhasil dimuat")
    except Exception as e:
        print(f"❌ Error memuat model: {e}")
        model = None
else:
    print(f"❌ File model tidak ditemukan: {model_path}")

# Default values
DEFAULT_VALUES = {
    'Age': 35, 'DailyRate': 850, 'DistanceFromHome': 15, 'Education': 3,
    'EnvironmentSatisfaction': 2, 'HourlyRate': 50, 'JobInvolvement': 3,
    'JobLevel': 2, 'JobSatisfaction': 2, 'MonthlyIncome': 4500,
    'MonthlyRate': 18000, 'NumCompaniesWorked': 2, 'PercentSalaryHike': 12,
    'PerformanceRating': 3, 'RelationshipSatisfaction': 3, 'StockOptionLevel': 1,
    'TotalWorkingYears': 8, 'TrainingTimesLastYear': 2, 'WorkLifeBalance': 2,
    'YearsAtCompany': 5, 'YearsInCurrentRole': 3, 'YearsSinceLastPromotion': 1,
    'YearsWithCurrManager': 2,
    
    # Kategorikal (akan di-handle manual)
    'BusinessTravel': 'Travel_Rarely',
    'Department': 'Research & Development',
    'EducationField': 'Life Sciences',
    'Gender': 'Male',
    'JobRole': 'Research Scientist',
    'MaritalStatus': 'Married',
    'OverTime': 'Yes'
}

CATEGORY_OPTIONS = {
    'BusinessTravel': ['Travel_Rarely', 'Travel_Frequently', 'Non-Travel'],
    'Department': ['Research & Development', 'Sales', 'Human Resources'],
    'EducationField': ['Life Sciences', 'Medical', 'Marketing', 'Technical Degree', 'Human Resources', 'Other'],
    'Gender': ['Male', 'Female'],
    'JobRole': ['Sales Executive', 'Research Scientist', 'Laboratory Technician', 'Manufacturing Director', 
                'Healthcare Representative', 'Manager', 'Sales Representative', 'Research Director', 'Human Resources'],
    'MaritalStatus': ['Married', 'Single', 'Divorced'],
    'OverTime': ['Yes', 'No']
}

def preprocess_input(data: pd.DataFrame) -> np.ndarray:
    """Preprocessing manual tanpa ColumnTransformer"""
    df = data.copy()
    
    # Konversi Gender ke numerik: Male=1, Female=0
    df['Gender_Male'] = df['Gender'].map({'Male': 1, 'Female': 0})
    
    # Buang kolom Gender asli
    df = df.drop('Gender', axis=1)
    
    # Urutan kolom HARUS sesuai dengan training (XGBoost sensitif terhadap urutan!)
    numeric_columns = [
        'Age', 'DailyRate', 'DistanceFromHome', 'Education', 'EnvironmentSatisfaction',
        'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobSatisfaction', 'MonthlyIncome',
        'MonthlyRate', 'NumCompaniesWorked', 'PercentSalaryHike', 'PerformanceRating',
        'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
        'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
        'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager',
        'Gender_Male'
    ]
    
    return df[numeric_columns].values

@app.route('/')
def home():
    return render_template('index.html', 
                          default_values=DEFAULT_VALUES,
                          category_options=CATEGORY_OPTIONS)

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model tidak tersedia. Pastikan file model ada di folder models/'}), 500
    
    try:
        form_data = request.form.to_dict()
        
        # Isi dengan default jika tidak diisi
        input_data = {}
        for feature, default in DEFAULT_VALUES.items():
            input_data[feature] = form_data.get(feature, default)
        
        input_df = pd.DataFrame([input_data])
        processed_data = preprocess_input(input_df)
        
        prediction = model.predict(processed_data)
        probability = model.predict_proba(processed_data)[0][1]
        
        risk_level = "High" if probability > 0.7 else "Medium" if probability > 0.4 else "Low"
        risk_color = "#dc3545" if risk_level == "High" else "#ffc107" if risk_level == "Medium" else "#28a745"
        
        result = {
            'prediction': "Yes" if prediction[0] == 1 else "No",
            'probability': f"{probability:.2%}",
            'risk_level': risk_level,
            'risk_color': risk_color,
            'recommendation': get_recommendation(risk_level, input_data)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

def get_recommendation(risk_level, employee_data):
    if risk_level == "High":
        return [
            f"🚨 Segera lakukan intervensi untuk {employee_data.get('JobRole', 'karyawan')} ini!",
            "• Jadwalkan sesi 1-on-1 dengan manajer untuk diskusi karir",
            "• Evaluasi kompensasi dan pertimbangkan penyesuaian gaji",
            "• Tawarkan program pengembangan keterampilan atau sertifikasi"
        ]
    elif risk_level == "Medium":
        return [
            f"⚠️ Pantau karyawan ini:",
            "• Lakukan survei kepuasan kerja secara berkala",
            "• Berikan pengakuan atas kontribusi dan pencapaian",
            "• Diskusikan tujuan karir jangka panjang"
        ]
    else:
        return [
            f"✅ Karyawan ini memiliki risiko resign rendah:",
            "• Pertahankan keterlibatan dengan proyek menantang",
            "• Berikan penghargaan atas kinerja konsisten",
            "• Siapkan rencana pengembangan karir jangka panjang"
        ]

if __name__ == '__main__':
    os.makedirs('models', exist_ok=True)
    app.run(debug=True)