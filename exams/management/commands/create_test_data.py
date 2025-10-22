from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exams.models import Exam, Question, Choice


class Command(BaseCommand):
    help = 'Crée des données de test complètes pour la démonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Création des données de test...'))
        
        # ========== EXAMEN 1 : Python Débutant ==========
        exam1 = Exam.objects.create(
            title="🐍 Python - Niveau Débutant",
            description="Testez vos connaissances de base en programmation Python. Cet examen couvre les fondamentaux du langage.",
            duration=30,
            passing_score=60,
            is_active=True
        )
        
        # Question 1
        q1 = Question.objects.create(
            exam=exam1,
            text="Quelle est la syntaxe correcte pour afficher 'Hello World' en Python ?",
            points=1,
            order=1
        )
        Choice.objects.create(question=q1, text="echo 'Hello World'", is_correct=False)
        Choice.objects.create(question=q1, text="print('Hello World')", is_correct=True)
        Choice.objects.create(question=q1, text="console.log('Hello World')", is_correct=False)
        Choice.objects.create(question=q1, text="System.out.println('Hello World')", is_correct=False)
        
        # Question 2
        q2 = Question.objects.create(
            exam=exam1,
            text="Quel type de données est utilisé pour stocker True ou False ?",
            points=1,
            order=2
        )
        Choice.objects.create(question=q2, text="int", is_correct=False)
        Choice.objects.create(question=q2, text="bool", is_correct=True)
        Choice.objects.create(question=q2, text="str", is_correct=False)
        Choice.objects.create(question=q2, text="float", is_correct=False)
        
        # Question 3
        q3 = Question.objects.create(
            exam=exam1,
            text="Comment créer une liste en Python ?",
            points=1,
            order=3
        )
        Choice.objects.create(question=q3, text="list = {1, 2, 3}", is_correct=False)
        Choice.objects.create(question=q3, text="list = [1, 2, 3]", is_correct=True)
        Choice.objects.create(question=q3, text="list = (1, 2, 3)", is_correct=False)
        Choice.objects.create(question=q3, text="list = <1, 2, 3>", is_correct=False)
        
        # Question 4
        q4 = Question.objects.create(
            exam=exam1,
            text="Quelle fonction permet de connaître le type d'une variable ?",
            points=1,
            order=4
        )
        Choice.objects.create(question=q4, text="typeof()", is_correct=False)
        Choice.objects.create(question=q4, text="type()", is_correct=True)
        Choice.objects.create(question=q4, text="gettype()", is_correct=False)
        Choice.objects.create(question=q4, text="var_type()", is_correct=False)
        
        # Question 5
        q5 = Question.objects.create(
            exam=exam1,
            text="Comment créer un commentaire en Python ?",
            points=1,
            order=5
        )
        Choice.objects.create(question=q5, text="// Commentaire", is_correct=False)
        Choice.objects.create(question=q5, text="# Commentaire", is_correct=True)
        Choice.objects.create(question=q5, text="/* Commentaire */", is_correct=False)
        Choice.objects.create(question=q5, text="<!-- Commentaire -->", is_correct=False)
        
        # ========== EXAMEN 2 : Django Middlewares ==========
        exam2 = Exam.objects.create(
            title="🔧 Django - Les Middlewares",
            description="Évaluez votre compréhension des middlewares Django et de leur utilisation dans les applications web.",
            duration=20,
            passing_score=70,
            is_active=True
        )
        
        # Question 1
        q1 = Question.objects.create(
            exam=exam2,
            text="Qu'est-ce qu'un middleware dans Django ?",
            points=2,
            order=1
        )
        Choice.objects.create(question=q1, text="Une base de données", is_correct=False)
        Choice.objects.create(question=q1, text="Un composant qui traite les requêtes et réponses HTTP", is_correct=True)
        Choice.objects.create(question=q1, text="Un template HTML", is_correct=False)
        Choice.objects.create(question=q1, text="Un modèle de données", is_correct=False)
        
        # Question 2
        q2 = Question.objects.create(
            exam=exam2,
            text="Quel middleware Django gère l'authentification des utilisateurs ?",
            points=2,
            order=2
        )
        Choice.objects.create(question=q2, text="SessionMiddleware", is_correct=False)
        Choice.objects.create(question=q2, text="AuthenticationMiddleware", is_correct=True)
        Choice.objects.create(question=q2, text="CsrfMiddleware", is_correct=False)
        Choice.objects.create(question=q2, text="CommonMiddleware", is_correct=False)
        
        # Question 3
        q3 = Question.objects.create(
            exam=exam2,
            text="Quel est le rôle du CsrfViewMiddleware ?",
            points=2,
            order=3
        )
        Choice.objects.create(question=q3, text="Gérer les sessions", is_correct=False)
        Choice.objects.create(question=q3, text="Protéger contre les attaques CSRF", is_correct=True)
        Choice.objects.create(question=q3, text="Compresser les réponses", is_correct=False)
        Choice.objects.create(question=q3, text="Logger les requêtes", is_correct=False)
        
        # Question 4
        q4 = Question.objects.create(
            exam=exam2,
            text="Dans quel ordre les middlewares sont-ils exécutés ?",
            points=2,
            order=4
        )
        Choice.objects.create(question=q4, text="De bas en haut pour les requêtes", is_correct=False)
        Choice.objects.create(question=q4, text="De haut en bas pour les requêtes", is_correct=True)
        Choice.objects.create(question=q4, text="Ordre aléatoire", is_correct=False)
        Choice.objects.create(question=q4, text="Parallèlement", is_correct=False)
        
        # ========== EXAMEN 3 : HTML/CSS ==========
        exam3 = Exam.objects.create(
            title="🎨 HTML & CSS - Bases",
            description="Testez vos connaissances sur les fondamentaux du HTML et CSS.",
            duration=25,
            passing_score=65,
            is_active=True
        )
        
        # Question 1
        q1 = Question.objects.create(
            exam=exam3,
            text="Quelle balise HTML est utilisée pour créer un lien hypertexte ?",
            points=1,
            order=1
        )
        Choice.objects.create(question=q1, text="<link>", is_correct=False)
        Choice.objects.create(question=q1, text="<a>", is_correct=True)
        Choice.objects.create(question=q1, text="<href>", is_correct=False)
        Choice.objects.create(question=q1, text="<url>", is_correct=False)
        
        # Question 2
        q2 = Question.objects.create(
            exam=exam3,
            text="Comment définir une couleur de fond en CSS ?",
            points=1,
            order=2
        )
        Choice.objects.create(question=q2, text="color: red;", is_correct=False)
        Choice.objects.create(question=q2, text="background-color: red;", is_correct=True)
        Choice.objects.create(question=q2, text="bgcolor: red;", is_correct=False)
        Choice.objects.create(question=q2, text="bg-color: red;", is_correct=False)
        
        # Question 3
        q3 = Question.objects.create(
            exam=exam3,
            text="Quelle balise HTML est utilisée pour le titre principal d'une page ?",
            points=1,
            order=3
        )
        Choice.objects.create(question=q3, text="<title>", is_correct=False)
        Choice.objects.create(question=q3, text="<h1>", is_correct=True)
        Choice.objects.create(question=q3, text="<header>", is_correct=False)
        Choice.objects.create(question=q3, text="<head>", is_correct=False)
        
        # ========== EXAMEN 4 : JavaScript ==========
        exam4 = Exam.objects.create(
            title="⚡ JavaScript - Fondamentaux",
            description="Évaluez vos compétences en JavaScript et en programmation web côté client.",
            duration=35,
            passing_score=60,
            is_active=True
        )
        
        # Question 1
        q1 = Question.objects.create(
            exam=exam4,
            text="Comment déclarer une variable en JavaScript (ES6+) ?",
            points=1,
            order=1
        )
        Choice.objects.create(question=q1, text="var x = 10;", is_correct=False)
        Choice.objects.create(question=q1, text="let x = 10; ou const x = 10;", is_correct=True)
        Choice.objects.create(question=q1, text="int x = 10;", is_correct=False)
        Choice.objects.create(question=q1, text="variable x = 10;", is_correct=False)
        
        # Question 2
        q2 = Question.objects.create(
            exam=exam4,
            text="Quelle méthode permet d'ajouter un élément à la fin d'un tableau ?",
            points=1,
            order=2
        )
        Choice.objects.create(question=q2, text="append()", is_correct=False)
        Choice.objects.create(question=q2, text="push()", is_correct=True)
        Choice.objects.create(question=q2, text="add()", is_correct=False)
        Choice.objects.create(question=q2, text="insert()", is_correct=False)
        
        # Question 3
        q3 = Question.objects.create(
            exam=exam4,
            text="Comment afficher un message dans la console ?",
            points=1,
            order=3
        )
        Choice.objects.create(question=q3, text="print('message')", is_correct=False)
        Choice.objects.create(question=q3, text="console.log('message')", is_correct=True)
        Choice.objects.create(question=q3, text="echo 'message'", is_correct=False)
        Choice.objects.create(question=q3, text="alert('message')", is_correct=False)
        
        # Statistiques finales
        self.stdout.write(self.style.SUCCESS('\n✅ Données de test créées avec succès !'))
        self.stdout.write(f'  📚 {Exam.objects.count()} examens créés')
        self.stdout.write(f'  ❓ {Question.objects.count()} questions créées')
        self.stdout.write(f'  ✓ {Choice.objects.count()} choix de réponses créés')
        self.stdout.write(self.style.WARNING('\n💡 Vous pouvez maintenant tester l\'application !'))