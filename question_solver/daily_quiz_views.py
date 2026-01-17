from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import date
from .static_questions_bank import get_random_questions
from .models import UserCoins, CoinTransaction, QuizSettings
import logging
import random
import uuid

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_daily_quiz(request):
    user_id = request.query_params.get('user_id', 'anonymous')
    language = request.query_params.get('language', 'english').lower()
    today = date.today()
    
    try:
        # Get 5 TRULY RANDOM questions from static bank - no seeding, no consistency
        all_static = get_random_questions(language=language, count=100)
        selected_questions = random.sample(all_static, min(5, len(all_static)))
        
        if not selected_questions:
            logger.error(f"[DAILY_QUIZ] ❌ No questions available for language: {language}")
            return Response({
                'error': 'Quiz unavailable',
                'message': 'No questions available for this language.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"[DAILY_QUIZ] ✅ Generated random quiz with {len(selected_questions)} questions ({language}) for {user_id}")
        
        # Store the questions in session for validation during submission
        request.session['quiz_questions'] = [
            {
                'id': idx + 1,
                'correct': q.get('correct'),
                'question': q.get('question')
            }
            for idx, q in enumerate(selected_questions)
        ]
        request.session.modified = True
        
        # Generate unique quiz_id for this session
        quiz_id = str(uuid.uuid4())
        request.session['quiz_id'] = quiz_id
        request.session.modified = True
        
        return Response({
            'quiz_id': quiz_id,
            'quiz_metadata': {
                'quiz_type': 'random_questions',
                'total_questions': len(selected_questions),
                'difficulty': 'medium',
                'date': str(today),
                'title': f'Random GK Quiz',
                'description': 'Test your general knowledge! Get random questions every time.',
                'language': language,
                'question_bank_size': 100,
                'questions_shown': len(selected_questions),
            },
            'questions': [
                {
                    'id': idx + 1,
                    'question': q.get('question', ''),
                    'options': q.get('options', []),
                    'category': q.get('category', 'general'),
                    'difficulty': q.get('difficulty', 'medium'),
                }
                for idx, q in enumerate(selected_questions)
            ],
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"[DAILY_QUIZ] ❌ Error in get_daily_quiz: {e}", exc_info=True)
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def start_daily_quiz(request):
    """
    Mark the Daily Quiz as started for a user
    """
    try:
        user_id = request.data.get('user_id', 'anonymous')
        language = request.data.get('language', 'english').lower()
        
        logger.info(f"[START_DAILY_QUIZ] User {user_id} started quiz ({language})")
        
        return Response({
            'success': True,
            'message': 'Quiz started. Answer the questions and submit.',
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"[START_DAILY_QUIZ] Error: {e}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def submit_daily_quiz(request):
    """
    Submit daily quiz answers and calculate coins
    Validates against the questions stored in session from the get_daily_quiz call
    """
    try:
        user_id = request.data.get('user_id', 'anonymous')
        language = request.data.get('language', 'english').lower()
        answers = request.data.get('answers', {})  # {question_id: answer_index}
        
        if not answers:
            return Response({
                'error': 'No answers provided',
                'message': 'answers field is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"[SUBMIT_DAILY_QUIZ] User {user_id} submitting quiz ({language})")
        
        # Get the questions that were sent to the user from session
        quiz_questions = request.session.get('quiz_questions', [])
        if not quiz_questions:
            return Response({
                'error': 'Quiz session expired',
                'message': 'Please reload the quiz and try again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        correct_count = 0
        results = []
        
        for idx, q_data in enumerate(quiz_questions):
            user_answer = answers.get(str(idx + 1), answers.get(idx + 1, -1))
            
            try:
                user_answer_idx = int(user_answer) if user_answer != -1 else -1
            except:
                user_answer_idx = -1
            
            correct_idx = q_data.get('correct', -1)
            is_correct = user_answer_idx == correct_idx
            
            if is_correct:
                correct_count += 1
            
            results.append({
                'question_id': idx + 1,
                'user_answer': user_answer_idx,
                'correct_answer': correct_idx,
                'is_correct': is_correct,
            })
        
        logger.info(f"[SUBMIT_DAILY_QUIZ] User {user_id}: {correct_count}/{len(quiz_questions)} correct")
        
        settings = QuizSettings.get_settings()
        coins_earned = correct_count * settings.daily_quiz_coins_per_correct
        
        # Store coins in DB
        with transaction.atomic():
            user_coins, created = UserCoins.objects.get_or_create(
                user_id=user_id,
                defaults={'total_coins': 0, 'lifetime_coins': 0}
            )
            user_coins.add_coins(coins_earned, reason=f"Daily Quiz completion ({language}) - {correct_count}/{len(quiz_questions)} correct")
        
        # Clear the session questions after submission
        if 'quiz_questions' in request.session:
            del request.session['quiz_questions']
            request.session.modified = True
        
        return Response({
            'success': True,
            'message': f'Quiz submitted! You got {correct_count}/{len(quiz_questions)} correct and earned {coins_earned} coins.',
            'correct_count': correct_count,
            'total_questions': len(quiz_questions),
            'coins_earned': coins_earned,
            'results': results,
        }, status=status.HTTP_200_OK)

    
    except Exception as e:
        logger.error(f"[SUBMIT_DAILY_QUIZ] Error: {e}", exc_info=True)
        return Response({
            'error': 'Error submitting quiz',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user_coins(request):
    """
    Get user's coin balance and stats
    """
    user_id = request.query_params.get('user_id', 'anonymous')
    
    try:
        user_coins = UserCoins.objects.filter(user_id=user_id).first()
        
        if not user_coins:
            return Response({
                'user_id': user_id,
                'total_coins': 0,
                'lifetime_coins': 0,
                'coins_spent': 0,
            }, status=status.HTTP_200_OK)
        
        # Get recent transactions
        recent_transactions = CoinTransaction.objects.filter(
            user_coins=user_coins
        ).order_by('-created_at')[:10]
        
        transactions_data = [{
            'amount': t.amount,
            'type': t.transaction_type,
            'reason': t.reason,
            'created_at': t.created_at,
        } for t in recent_transactions]
        
        return Response({
            'user_id': user_id,
            'total_coins': user_coins.total_coins,
            'lifetime_coins': user_coins.lifetime_coins,
            'coins_spent': user_coins.coins_spent,
            'recent_transactions': transactions_data,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_quiz_history(request):
    user_id = request.query_params.get('user_id', 'anonymous')
    limit = int(request.query_params.get('limit', 30))
    
    try:
        attempts = UserDailyQuizAttempt.objects.filter(
            user_id=user_id
        ).select_related('daily_quiz').order_by('-started_at')[:limit]
        
        history_data = []
        for attempt in attempts:
            history_data.append({
                'date': attempt.daily_quiz.date,
                'quiz_title': attempt.daily_quiz.title,
                'correct_count': attempt.correct_count,
                'total_questions': attempt.total_questions,
                'score_percentage': attempt.score_percentage,
                'coins_earned': attempt.coins_earned,
                'completed_at': attempt.completed_at,
            })
        
        total_attempts = attempts.count()
        total_coins_earned = sum(a.coins_earned for a in attempts)
        avg_score = sum(a.score_percentage for a in attempts) / total_attempts if total_attempts > 0 else 0
        
        return Response({
            'user_id': user_id,
            'history': history_data,
            'stats': {
                'total_attempts': total_attempts,
                'total_coins_earned': total_coins_earned,
                'average_score': round(avg_score, 2),
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_daily_quiz_attempt_detail(request):
    user_id = request.query_params.get('user_id', 'anonymous')
    quiz_id = request.query_params.get('quiz_id')

    if not quiz_id:
        return Response({'error': 'quiz_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        daily_quiz = DailyQuiz.objects.get(id=quiz_id, is_active=True)
        attempt = UserDailyQuizAttempt.objects.filter(daily_quiz=daily_quiz, user_id=user_id).first()

        if not attempt or not attempt.completed_at:
            return Response({'error': 'No completed attempt found for this user and quiz'}, status=status.HTTP_404_NOT_FOUND)

        questions = list(DailyQuestion.objects.filter(daily_quiz=daily_quiz).order_by('order')[:attempt.total_questions])
        results = []
        for idx, q in enumerate(questions, 1):
            user_answer_idx = attempt.answers.get(str(idx), -1)
            correct_idx = ord(q.correct_answer.upper()) - ord('A') if q.correct_answer else -1
            options = q.options if isinstance(q.options, list) else []
            user_answer_text = options[user_answer_idx] if 0 <= user_answer_idx < len(options) else 'No answer'
            correct_answer_text = options[correct_idx] if 0 <= correct_idx < len(options) else q.correct_answer

            results.append({
                'question_id': idx,
                'question': q.question_text,
                'options': options,
                'user_answer': user_answer_text,
                'user_answer_index': user_answer_idx,
                'correct_answer': correct_answer_text,
                'correct_answer_index': correct_idx,
                'is_correct': (user_answer_idx == correct_idx),
                'explanation': q.explanation,
                'fun_fact': q.fun_fact or '',
                'category': q.category,
            })

        return Response({
            'success': True,
            'quiz_id': str(daily_quiz.id),
            'date': str(daily_quiz.date),
            'results': results,
            'correct_count': attempt.correct_count,
            'total_questions': attempt.total_questions,
            'score_percentage': attempt.score_percentage,
            'coins_earned': attempt.coins_earned,
            'completed_at': attempt.completed_at,
        }, status=status.HTTP_200_OK)

    except DailyQuiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error fetching attempt detail: {e}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_quiz_settings(request):
    try:
        try:
            from .models import QuizSettings
            settings = QuizSettings.get_settings()
        except Exception as e:
            logger.warning(f"QuizSettings model not yet initialized: {e}")
            settings = None
        
        if settings:
            return Response({
                'success': True,
                'settings': {
                    'daily_quiz': {
                        'attempt_bonus': settings.daily_quiz_attempt_bonus,
                        'coins_per_correct': settings.daily_quiz_coins_per_correct,
                        'perfect_score_bonus': settings.daily_quiz_perfect_score_bonus,
                    },
                    'pair_quiz': {
                        'enabled': settings.pair_quiz_enabled,
                        'session_timeout': settings.pair_quiz_session_timeout,
                        'max_questions': settings.pair_quiz_max_questions,
                    },
                    'coin_system': {
                        'coin_to_currency_rate': float(settings.coin_to_currency_rate),
                        'min_coins_for_redemption': settings.min_coins_for_redemption,
                    }
                },
                'updated_at': settings.updated_at.isoformat() if settings.updated_at else None,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': True,
                'settings': {
                    'daily_quiz': {
                        'attempt_bonus': 5,
                        'coins_per_correct': 5,
                        'perfect_score_bonus': 10,
                    },
                    'pair_quiz': {
                        'enabled': True,
                        'session_timeout': 30,
                        'max_questions': 20,
                    },
                    'coin_system': {
                        'coin_to_currency_rate': 0.10,
                        'min_coins_for_redemption': 10,
                    }
                },
                'updated_at': None,
                'note': 'Using default settings - database not fully initialized',
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching quiz settings: {e}", exc_info=True)
        return Response({
            'success': True,
            'settings': {
                'daily_quiz': {
                    'attempt_bonus': 5,
                    'coins_per_correct': 5,
                    'perfect_score_bonus': 10,
                },
                'pair_quiz': {
                    'enabled': True,
                    'session_timeout': 30,
                    'max_questions': 20,
                },
                'coin_system': {
                    'coin_to_currency_rate': 0.10,
                    'min_coins_for_redemption': 10,
                }
            },
            'updated_at': None,
            'note': 'Using fallback default settings',
        }, status=status.HTTP_200_OK)
