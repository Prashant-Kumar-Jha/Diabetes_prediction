from django.shortcuts import render, redirect, get_object_or_404
import joblib
import traceback
from .models import PredictionRecord
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from collections import Counter
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User

# Load ML model
import os
import joblib
import traceback
from django.conf import settings

# ✅ Correct platform-independent path
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

                # Save to PredictionRecord with feedback = 'pending'
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
def history(request):
    if request.user.is_staff or request.user.is_superuser:
        records = PredictionRecord.objects.all().order_by('-timestamp')  # Admin sees all
    else:
        records = PredictionRecord.objects.filter(user=request.user).order_by('-timestamp')  # Normal user sees their own

    # Chart summary data
    result_counts = Counter(record.result for record in records)
    chart_data = {
        'labels': list(result_counts.keys()),
        'values': list(result_counts.values())
    }

    return render(request, 'history.html', {
        'records': records,
        'chart_data': chart_data
    })

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


from django.http import HttpResponseForbidden

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
