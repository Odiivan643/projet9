from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Exam(models.Model):
    """Modèle pour représenter un examen"""
    title = models.CharField(max_length=200, verbose_name="Titre de l'examen")
    description = models.TextField(verbose_name="Description")
    duration = models.IntegerField(help_text="Durée en minutes", verbose_name="Durée")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    passing_score = models.IntegerField(default=60, verbose_name="Score de réussite (%)")
    
    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Examens"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def total_questions(self):
        """Retourne le nombre total de questions"""
        return self.questions.count()
    
    @property
    def total_points(self):
        """Retourne le total de points de l'examen"""
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """Modèle pour représenter une question d'examen"""
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE, 
        related_name='questions',
        verbose_name="Examen"
    )
    text = models.TextField(verbose_name="Question")
    points = models.IntegerField(default=1, verbose_name="Points")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.exam.title} - Q{self.order}: {self.text[:50]}"
    
    @property
    def correct_choice(self):
        """Retourne la bonne réponse"""
        return self.choices.filter(is_correct=True).first()


class Choice(models.Model):
    """Modèle pour représenter un choix de réponse"""
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='choices',
        verbose_name="Question"
    )
    text = models.CharField(max_length=500, verbose_name="Choix")
    is_correct = models.BooleanField(default=False, verbose_name="Bonne réponse")
    
    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"
    
    def __str__(self):
        return f"{self.text} {'✓' if self.is_correct else ''}"


class ExamSession(models.Model):
    """Modèle pour représenter une session d'examen d'un utilisateur"""
    STATUS_CHOICES = [
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('abandoned', 'Abandonné'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='exam_sessions',
        verbose_name="Utilisateur"
    )
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="Examen"
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Commencé le")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminé le")
    score = models.FloatField(null=True, blank=True, verbose_name="Score (%)")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='in_progress',
        verbose_name="Statut"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    
    class Meta:
        verbose_name = "Session d'examen"
        verbose_name_plural = "Sessions d'examen"
        unique_together = ['user', 'exam']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.status})"
    
    @property
    def duration(self):
        """Retourne la durée de l'examen en minutes"""
        if self.finished_at:
            delta = self.finished_at - self.started_at
            return round(delta.total_seconds() / 60, 2)
        return None
    
    @property
    def is_passed(self):
        """Vérifie si l'utilisateur a réussi l'examen"""
        if self.score is not None:
            return self.score >= self.exam.passing_score
        return False
    
    def calculate_score(self):
        """Calcule le score de la session"""
        total_points = self.exam.total_points
        if total_points == 0:
            return 0
        
        earned_points = 0
        for answer in self.answers.all():
            if answer.choice.is_correct:
                earned_points += answer.question.points
        
        self.score = (earned_points / total_points) * 100
        return self.score
    
    def finish(self):
        """Termine la session d'examen"""
        self.finished_at = timezone.now()
        self.status = 'completed'
        self.calculate_score()
        self.save()


class Answer(models.Model):
    """Modèle pour représenter une réponse d'un utilisateur"""
    session = models.ForeignKey(
        ExamSession, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name="Session"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        verbose_name="Question"
    )
    choice = models.ForeignKey(
        Choice, 
        on_delete=models.CASCADE,
        verbose_name="Choix"
    )
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Répondu le")
    
    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        unique_together = ['session', 'question']
        ordering = ['answered_at']
    
    def __str__(self):
        return f"{self.session.user.username} - {self.question.text[:30]}"
    
    @property
    def is_correct(self):
        """Vérifie si la réponse est correcte"""
        return self.choice.is_correct


class RequestLog(models.Model):
    """Modèle pour logger les requêtes HTTP (pour démonstration des middlewares)"""
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Utilisateur"
    )
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name="Méthode")
    path = models.CharField(max_length=500, verbose_name="Chemin")
    status_code = models.IntegerField(verbose_name="Code de statut")
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")
    response_time = models.FloatField(null=True, blank=True, verbose_name="Temps de réponse (s)")
    
    class Meta:
        verbose_name = "Log de requête"
        verbose_name_plural = "Logs de requêtes"
        ordering = ['-timestamp']
    
    def __str__(self):
        user_str = self.user.username if self.user else "Anonyme"
        return f"[{self.status_code}] {self.method} {self.path} - {user_str}"