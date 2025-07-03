from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import PredictionRecord

import pandas as pd
import traceback
import joblib
import os
import io
from collections import Counter
from django.conf import settings

# Load ML model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'diabetes_model_clean.pkl')
print("Model path used:", MODEL_PATH)

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print("Model failed to load:", e)
    traceback.print_exc()
    model = None


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')


@login_required
def predict(request):
    result = None
    if request.method == 'POST':
        try:
            if model is None:
                result = "Model not loaded. Try again later."
            else:
                patient_name = request.POST.get('patient_name') or "Unknown"
                patient_id = request.POST.get('patient_id') or "N/A"

                data = [
                    float(request.POST.get('pregnancies')),
                    float(request.POST.get('glucose')),
                    float(request.POST.get('bloodpressure')),
                    float(request.POST.get('skinthickness')),
                    float(request.POST.get('insulin')),
                    float(request.POST.get('bmi')),
                    float(request.POST.get('dpf')),
                    float(request.POST.get('age')),
                ]

                prediction = model.predict([data])[0]
                result = "Diabetic" if prediction == 1 else "Not Diabetic"

                PredictionRecord.objects.create(
                    user=request.user,
                    patient_name=patient_name,
                    patient_id=patient_id,
                    pregnancies=data[0], glucose=data[1], bloodpressure=data[2],
                    skinthickness=data[3], insulin=data[4], bmi=data[5],
                    dpf=data[6], age=data[7], result=result,
                    feedback='pending'
                )
        except Exception as e:
            traceback.print_exc()
            result = f"Error: {str(e)}"
    return render(request, 'predict.html', {'result': result})




@login_required
@require_POST
def submit_feedback(request, result_id):
    record = get_object_or_404(PredictionRecord, id=result_id, user=request.user)
    feedback = request.POST.get('feedback')
    if feedback in ['correct', 'incorrect']:
        record.feedback = feedback
        record.save()
    return redirect('history')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'signup.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def admin_portal(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Access Denied: Admins only.")

    all_records = PredictionRecord.objects.all().order_by('-timestamp')
    total_users = User.objects.count()
    total_predictions = all_records.count()
    diabetic_count = all_records.filter(result='Diabetic').count()
    non_diabetic_count = all_records.filter(result='Not Diabetic').count()

    return render(request, 'admin_portal.html', {
        'all_records': all_records,
        'total_users': total_users,
        'total_predictions': total_predictions,
        'diabetic_count': diabetic_count,
        'non_diabetic_count': non_diabetic_count,
    })


@staff_member_required
def admin_user_management(request):
    users = User.objects.all()
    return render(request, 'admin_user_management.html', {'users': users})


@staff_member_required
@csrf_protect
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_superuser:
        user.delete()
    return redirect('admin_user_management')


# --------------------
# 📤 EXCEL EXPORT VIEW
# --------------------
import io
import xlsxwriter
from django.http import HttpResponse
from .models import PredictionRecord


def generate_explanation(record):
    risk_factors = []

    if record.glucose > 140:
        risk_factors.append("high glucose")
    if record.bmi > 30:
        risk_factors.append("high BMI")
    if record.age > 45:
        risk_factors.append("age over 45")

    if risk_factors:
        return "This prediction was influenced by " + ", ".join(risk_factors) + "."
    else:
        return "No major risk factors detected based on input values."


def download_excel(request):
    output = io.BytesIO()

    # Create a workbook and worksheet
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Prediction History")

    # Define header format
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#DCE6F1',
        'border': 1
    })

    # Define headers including the new "Explanation" column
    headers = [
        'Patient Name', 'Patient ID', 'Pregnancies', 'Glucose', 'Blood Pressure',
        'Skin Thickness', 'Insulin', 'BMI', 'DPF', 'Age', 'Result', 'Time',
        'Feedback', 'Explanation'
    ]

    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Fetch all records
    records = PredictionRecord.objects.all()

    # Write data
    for row_idx, record in enumerate(records, start=1):
        explanation = generate_explanation(record)

        worksheet.write(row_idx, 0, record.patient_name)
        worksheet.write(row_idx, 1, record.patient_id)
        worksheet.write(row_idx, 2, record.pregnancies)
        worksheet.write(row_idx, 3, record.glucose)
        worksheet.write(row_idx, 4, record.bloodpressure)
        worksheet.write(row_idx, 5, record.skinthickness)
        worksheet.write(row_idx, 6, record.insulin)
        worksheet.write(row_idx, 7, record.bmi)
        worksheet.write(row_idx, 8, record.dpf)
        worksheet.write(row_idx, 9, record.age)
        worksheet.write(row_idx, 10, record.result)
        worksheet.write(row_idx, 11, record.timestamp.strftime('%Y-%m-%d %H:%M'))
        worksheet.write(row_idx, 12, record.feedback or "pending")
        worksheet.write(row_idx, 13, explanation)

    workbook.close()

    # Return response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=prediction_history.xlsx'
    return response



# --------------------
# 🧾 PDF EXPORT VIEW
# --------------------
def shorten(text, max_length=20):
    return (text[:max_length] + '...') if len(text) > max_length else text


@staff_member_required
def download_pdf(request):
    records = PredictionRecord.objects.all().order_by('-timestamp')

    # Optional truncation for layout
    for record in records:
        record.patient_name = shorten(record.patient_name, 20)
        record.patient_id = shorten(record.patient_id, 15)

    template = get_template('pdf_template.html')
    html = template.render({'records': records})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prediction_report.pdf"'

    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=result)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    response.write(result.getvalue())
    return response

from django.shortcuts import get_object_or_404, redirect
from .models import PredictionRecord

from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

@csrf_protect
def delete_record(request, record_id):
    record = get_object_or_404(PredictionRecord, id=record_id)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Record deleted successfully.")
    return redirect('history')


@login_required
def history(request):
    # Admins see all, users see their own
    if request.user.is_staff or request.user.is_superuser:
        records = PredictionRecord.objects.all().order_by('-timestamp')
    else:
        records = PredictionRecord.objects.filter(user=request.user).order_by('-timestamp')

    # Explanation logic
    for record in records:
        explanation = []

        if record.glucose > 125:
            explanation.append("High glucose levels are a major risk factor.")
        if record.bmi > 30:
            explanation.append("BMI above 30 indicates obesity.")
        if record.age > 45:
            explanation.append("Older age increases diabetes risk.")
        if record.insulin < 50:
            explanation.append("Low insulin levels may indicate poor glucose control.")
        if record.dpf > 0.8:
            explanation.append("Genetic risk is high due to Diabetes Pedigree Function.")

        if not explanation:
            explanation.append("No strong risk factors, but borderline indicators may exist.")

        record.explanation = explanation

    # Chart data
    from collections import Counter
    result_counts = Counter(record.result for record in records)
    chart_data = {
        'labels': list(result_counts.keys()),
        'values': list(result_counts.values())
    }

    return render(request, 'history.html', {
        'records': records,
        'chart_data': chart_data
    })
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def bmi_calculator(request):
    bmi_result = None
    category = None

    if request.method == 'POST':
        try:
            weight = float(request.POST.get('weight'))
            height = float(request.POST.get('height')) / 100  # cm to meters
            bmi = weight / (height * height)
            bmi_result = round(bmi, 2)

            if bmi < 18.5:
                category = "Underweight"
            elif 18.5 <= bmi < 25:
                category = "Normal weight"
            elif 25 <= bmi < 30:
                category = "Overweight"
            else:
                category = "Obese"
        except:
            bmi_result = "Invalid input"

    return render(request, 'bmi_calculator.html', {
        'bmi_result': bmi_result,
        'category': category
    })
