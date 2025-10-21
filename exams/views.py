from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg
from .models import Exam, Question, ExamSession, Answer, RequestLog
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse


def home(request):
    """Page d'accueil"""
    context = {
        'total_exams': Exam.objects.filter(is_active=True).count(),
        'total_students': ExamSession.objects.values('user').distinct().count(),
    }
    return render(request, 'exams/home.html', context)


def register(request):
    """Vue pour l'inscription d'un nouvel utilisateur"""
    if request.user.is_authenticated:
        return redirect('exam_list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé avec succès.")
            return redirect('exam_list')
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez corriger les erreurs.")
    else:
        form = UserCreationForm()
    
    return render(request, 'exams/register.html', {'form': form})


def user_login(request):
    """Vue pour la connexion d'un utilisateur"""
    if request.user.is_authenticated:
        return redirect('exam_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Stocker l'IP dans la session pour le middleware de sécurité
            request.session['session_ip'] = get_client_ip(request)
            
            messages.success(request, f"Bon retour {user.username} !")
            next_url = request.GET.get('next', 'exam_list')
            return redirect(next_url)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'exams/login.html', {'form': form})


@login_required
def user_logout(request):
    """Vue pour la déconnexion"""
    username = request.user.username
    logout(request)
    messages.info(request, f"Au revoir {username}, à bientôt !")
    return redirect('login')


@login_required
def exam_list(request):
    """Liste de tous les examens disponibles"""
    exams = Exam.objects.filter(is_active=True).annotate(
        num_questions=Count('questions')
    )
    
    # Récupérer les sessions de l'utilisateur
    user_sessions = ExamSession.objects.filter(user=request.user)
    completed_exam_ids = user_sessions.filter(status='completed').values_list('exam_id', flat=True)
    
    context = {
        'exams': exams,
        'completed_exam_ids': list(completed_exam_ids),
    }
    return render(request, 'exams/exam_list.html', context)


@login_required
def exam_detail(request, exam_id):
    """Détails d'un examen"""
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    
    # Vérifier si l'utilisateur a déjà une session pour cet examen
    existing_session = ExamSession.objects.filter(user=request.user, exam=exam).first()
    
    context = {
        'exam': exam,
        'existing_session': existing_session,
    }
    return render(request, 'exams/exam_detail.html', context)


@login_required
def start_exam(request, exam_id):
    """Démarrer un examen"""
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    
    # Vérifier si l'utilisateur a déjà une session
    existing_session = ExamSession.objects.filter(user=request.user, exam=exam).first()
    
    if existing_session:
        if existing_session.status == 'completed':
            messages.warning(request, "Vous avez déjà passé cet examen.")
            return redirect('exam_result', session_id=existing_session.id)
        else:
            # Reprendre la session en cours
            session = existing_session
    else:
        # Créer une nouvelle session
        session = ExamSession.objects.create(
            user=request.user,
            exam=exam,
            ip_address=get_client_ip(request)
        )
        messages.info(request, f"Examen démarré : {exam.title}")
    
    # Stocker l'ID de session dans la session Django
    request.session['current_exam_session_id'] = session.id
    request.session['exam_start_time'] = str(timezone.now())
    
    return redirect('take_exam', exam_id=exam.id)


@login_required
def take_exam(request, exam_id):
    """Passer un examen"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Récupérer la session en cours
    session_id = request.session.get('current_exam_session_id')
    if not session_id:
        messages.error(request, "Aucune session d'examen en cours.")
        return redirect('exam_detail', exam_id=exam.id)
    
    session = get_object_or_404(ExamSession, id=session_id, user=request.user, exam=exam)
    
    if session.status == 'completed':
        messages.warning(request, "Cet examen est déjà terminé.")
        return redirect('exam_result', session_id=session.id)
    
    if request.method == 'POST':
        # Traiter les réponses
        for question in exam.questions.all():
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                choice = get_object_or_404(question.choices, id=choice_id)
                
                # Créer ou mettre à jour la réponse
                Answer.objects.update_or_create(
                    session=session,
                    question=question,
                    defaults={'choice': choice}
                )
        
        # Terminer la session
        session.finish()
        
        # Nettoyer la session Django
        if 'current_exam_session_id' in request.session:
            del request.session['current_exam_session_id']
        if 'exam_start_time' in request.session:
            del request.session['exam_start_time']
        
        messages.success(request, "Examen terminé avec succès !")
        return redirect('exam_result', session_id=session.id)
    
    # Récupérer les réponses déjà données
    answered_questions = Answer.objects.filter(session=session).values_list('question_id', 'choice_id')
    answered_dict = dict(answered_questions)
    
    questions = exam.questions.prefetch_related('choices').all()
    
    context = {
        'exam': exam,
        'questions': questions,
        'session': session,
        'answered_dict': answered_dict,
    }
    return render(request, 'exams/take_exam.html', context)


@login_required
def exam_result(request, session_id):
    """Afficher les résultats d'un examen"""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    
    # Récupérer toutes les réponses avec les questions et choix
    answers = session.answers.select_related('question', 'choice').all()
    
    # Créer une liste de résultats détaillés
    results = []
    for answer in answers:
        results.append({
            'question': answer.question,
            'user_choice': answer.choice,
            'correct_choice': answer.question.correct_choice,
            'is_correct': answer.is_correct,
            'points': answer.question.points if answer.is_correct else 0,
        })
    
    context = {
        'session': session,
        'results': results,
        'total_questions': len(results),
        'correct_answers': sum(1 for r in results if r['is_correct']),
    }
    return render(request, 'exams/result.html', context)


@login_required
def my_results(request):
    """Afficher tous les résultats de l'utilisateur"""
    sessions = ExamSession.objects.filter(
        user=request.user,
        status='completed'
    ).select_related('exam').order_by('-finished_at')
    
    context = {
        'sessions': sessions,
    }
    return render(request, 'exams/my_results.html', context)


@login_required
def dashboard(request):
    """Tableau de bord de l'utilisateur"""
    # Statistiques de l'utilisateur
    total_exams_taken = ExamSession.objects.filter(user=request.user, status='completed').count()
    total_exams_passed = ExamSession.objects.filter(
        user=request.user, 
        status='completed',
        score__gte=60
    ).count()
    
    # Moyenne des scores
    avg_score = ExamSession.objects.filter(
        user=request.user,
        status='completed'
    ).aggregate(Avg('score'))['score__avg'] or 0
    
    # Dernières sessions
    recent_sessions = ExamSession.objects.filter(
        user=request.user
    ).select_related('exam').order_by('-started_at')[:5]
    
    context = {
        'total_exams_taken': total_exams_taken,
        'total_exams_passed': total_exams_passed,
        'avg_score': round(avg_score, 2),
        'recent_sessions': recent_sessions,
    }
    return render(request, 'exams/dashboard.html', context)


# Fonction utilitaire pour récupérer l'IP du client
def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Vue pour la démonstration des middlewares
@login_required
def middleware_demo(request):
    """Page de démonstration des middlewares"""
    # Récupérer les derniers logs
    recent_logs = RequestLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    # Informations sur la session
    session_info = {
        'session_key': request.session.session_key,
        'last_activity': request.session.get('last_activity'),
        'session_ip': request.session.get('session_ip'),
        'exam_in_progress': 'current_exam_session_id' in request.session,
    }
    
    context = {
        'recent_logs': recent_logs,
        'session_info': session_info,
    }
    return render(request, 'exams/middleware_demo.html', context)