# Hindi Daily Quiz - Complete Implementation Guide

## Problem Statement

1. **Hindi Quiz Not Generating** - Daily quiz endpoint returns English questions only
2. **Flashcards API Returning 400** - Missing required parameters
3. **Questions API Returning 500** - Error in question generation logic
4. **Language Support Missing** - No parameter to request Hindi content

## Root Causes

### 1. No Language Parameter in API
- Daily quiz endpoint doesn't accept language parameter
- Gemini prompt is hardcoded to English
- No conditional logic for language-specific generation

### 2. Missing Required Parameters
- Flashcards endpoint requires `num_cards` but frontend not sending
- Predicted questions endpoint requires explicit topic or document

### 3. Error Handling Issues
- Frontend not sending proper Content-Type headers
- Backend not validating required fields before processing

---

## SOLUTION 1: Update Daily Quiz with Hindi Support

### Step 1: Update Gemini Service

Add language-aware quiz generation:

```python
def generate_daily_quiz(self, num_questions: int = 10, language: str = 'english') -> Dict[str, Any]:
    """
    Generate a daily general knowledge quiz with language support
    
    Args:
        num_questions: Number of questions to generate (default: 10)
        language: 'english' or 'hindi' (default: 'english')
    
    Returns:
        Dictionary containing quiz questions
    """
    try:
        language_instruction = {
            'english': 'in English language',
            'hindi': 'in Hindi language (देवनागरी script). Provide questions and options in Hindi.'
        }
        
        lang_text = language_instruction.get(language.lower(), language_instruction['english'])
        
        prompt = f"""Generate a daily general knowledge quiz with {num_questions} multiple-choice questions {lang_text} covering various categories like Science, History, Geography, Literature, Current Events, Sports, Technology, etc.

Make the questions interesting, educational, and suitable for a general audience. Mix easy and medium difficulty questions.

Please format the response as a valid JSON object with the following structure:
{{
    "questions": [
        {{
            "question_text": "Question text here?",
            "options": [
                {{"id": "A", "text": "Option A text"}},
                {{"id": "B", "text": "Option B text"}},
                {{"id": "C", "text": "Option C text"}},
                {{"id": "D", "text": "Option D text"}}
            ],
            "correct_answer": "C",
            "category": "science",
            "difficulty": "medium",
            "explanation": "Explanation of the correct answer",
            "fun_fact": "An interesting related fact"
        }}
    ]
}}

Rules:
- Make questions clear and engaging
- Use varied categories: science, history, geography, general, current_events, sports, entertainment, technology
- Mix difficulty levels (mostly easy and medium)
- correct_answer should be "A", "B", "C", or "D"
- Include explanations and fun facts
- Ensure JSON is properly formatted
{"- Questions and explanations should be in Hindi" if language.lower() == 'hindi' else ""}
"""
        
        logger.info(f"Generating Daily Quiz with {num_questions} questions in {language}")
        response = self.model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Try to extract JSON from markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        quiz_data = json.loads(response_text)
        
        logger.info(f"Successfully generated {len(quiz_data.get('questions', []))} Daily Quiz questions in {language}")
        return {
            'success': True,
            'questions': quiz_data.get('questions', []),
            'language': language
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text}")
        return {
            'success': False,
            'error': 'Failed to parse Daily Quiz data',
            'details': str(e)
        }
    except Exception as e:
        logger.error(f"Daily Quiz generation error: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'Failed to generate Daily Quiz',
            'details': str(e)
        }
```

### Step 2: Update Daily Quiz Views

Modify `daily_quiz_views.py`:

```python
def create_or_get_daily_quiz(language: str = 'english'):
    """
    Auto-generate today's Daily Quiz using Gemini if it doesn't exist
    """
    today = date.today()
    
    # Check for existing quiz in requested language
    daily_quiz = DailyQuiz.objects.filter(
        date=today, 
        is_active=True,
        language=language  # Add language field to model
    ).first()
    
    if daily_quiz:
        return daily_quiz
    
    # Generate new quiz using Gemini with language support
    logger.info(f"Generating new Daily Quiz for {today} in {language}")
    
    try:
        result = gemini_service.generate_daily_quiz(num_questions=5, language=language)
        
        if not result.get('success'):
            logger.error(f"Failed to generate Daily Quiz: {result.get('error')}")
            return None
        
        questions_data = result.get('questions', [])
        
        if not questions_data:
            logger.error("No questions returned from Gemini")
            return None
        
        # Create the quiz
        with transaction.atomic():
            daily_quiz = DailyQuiz.objects.create(
                date=today,
                title=f'Daily GK Quiz - {today.strftime("%B %d, %Y")}',
                description='Test your general knowledge with AI-generated questions!',
                total_questions=len(questions_data),
                difficulty='medium',
                language=language  # Add language field
            )
            
            # Add questions
            for idx, q_data in enumerate(questions_data, 1):
                DailyQuestion.objects.create(
                    daily_quiz=daily_quiz,
                    order=idx,
                    question_text=q_data.get('question_text', ''),
                    options=q_data.get('options', []),
                    correct_answer=q_data.get('correct_answer', 'A'),
                    category=q_data.get('category', 'general'),
                    difficulty=q_data.get('difficulty', 'medium'),
                    explanation=q_data.get('explanation', ''),
                    fun_fact=q_data.get('fun_fact', '')
                )
            
            logger.info(f"Successfully created Daily Quiz with {len(questions_data)} questions in {language}")
            return daily_quiz
            
    except Exception as e:
        logger.error(f"Error creating Daily Quiz: {e}", exc_info=True)
        return None


@api_view(['GET'])
def get_daily_quiz(request):
    """
    Get today's daily coin quiz (auto-generates using Gemini if not exists)
    
    Query Parameters:
    - user_id: User ID
    - language: 'english' or 'hindi' (default: 'english')
    """
    user_id = request.query_params.get('user_id', 'anonymous')
    language = request.query_params.get('language', 'english').lower()
    
    # Validate language
    if language not in ['english', 'hindi']:
        language = 'english'
    
    today = date.today()
    
    try:
        # Get quiz settings for coin rewards
        settings = QuizSettings.get_settings()
        
        # Auto-generate quiz if it doesn't exist (with language support)
        daily_quiz = create_or_get_daily_quiz(language=language)
        
        if not daily_quiz:
            return Response({
                'error': 'Failed to generate quiz',
                'message': 'Unable to create today\'s quiz. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get questions (without revealing correct answers)
        questions = DailyQuestion.objects.filter(daily_quiz=daily_quiz).order_by('order')
        
        questions_data = []
        for idx, q in enumerate(questions, 1):
            questions_data.append({
                'id': idx,
                'question': q.question_text,
                'options': [opt['text'] if isinstance(opt, dict) else opt for opt in q.options],
                'category': q.category,
                'difficulty': q.difficulty,
            })
        
        # Enforce maximum of 5 questions for the Daily Quiz
        questions_data = questions_data[:5]
        
        # Return format matching the strict requirements
        return Response({
            'quiz_metadata': {
                'quiz_type': 'daily_coin_quiz',
                'total_questions': len(questions_data),
                'difficulty': 'medium',
                'date': str(today),
                'language': language,
                'title': daily_quiz.title,
                'description': daily_quiz.description,
            },
            'coins': {
                'attempt_bonus': settings.daily_quiz_attempt_bonus,
                'per_correct_answer': settings.daily_quiz_coins_per_correct,
                'max_possible': settings.daily_quiz_attempt_bonus + (len(questions_data) * settings.daily_quiz_coins_per_correct),
            },
            'questions': [
                {
                    'id': idx,
                    'question': q.get('question'),
                    'options': q.get('options', []),
                    'category': q.get('category', 'general'),
                    'difficulty': q.get('difficulty', 'medium'),
                }
                for idx, q in enumerate(questions_data, 1)
            ],
            'ui': {
                'theme': 'light',
                'card_style': 'rounded',
                'accent_color': '#6366F1',
                'show_progress_bar': True,
                'show_coin_animation': True,
            },
            'quiz_id': str(daily_quiz.id),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching Daily Quiz: {e}", exc_info=True)
        return Response({
            'error': 'Failed to fetch Daily Quiz',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### Step 3: Update Django Model

Add language field to DailyQuiz model:

```python
# In question_solver/models.py

class DailyQuiz(models.Model):
    date = models.DateField(default=date.today, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_questions = models.IntegerField(default=10)
    difficulty = models.CharField(max_length=20, default='medium')
    is_active = models.BooleanField(default=True)
    language = models.CharField(
        max_length=20, 
        default='english',
        choices=[('english', 'English'), ('hindi', 'Hindi')]
    )
    coins_per_correct = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ('date', 'language')  # One quiz per language per day
        
    def __str__(self):
        return f"{self.title} ({self.language})"
```

---

## SOLUTION 2: Fix Flashcards Generation (400 Error)

Add proper validation and default values:

```python
# In question_solver/views.py - FlashcardGeneratorView.post()

def post(self, request):
    """
    Generate flashcards based on topic or document
    
    Request body:
    - topic: Topic text or document content (required if no document)
    - num_cards: Number of flashcards (default: 10)
    - language: 'english' or 'hindi' (default: 'english')
    - document: Optional document file upload
    """
    try:
        # Get parameters with defaults
        topic = request.data.get('topic', '').strip()
        num_cards = int(request.data.get('num_cards', 10))
        language = request.data.get('language', 'english').lower()
        
        # Validate language
        if language not in ['english', 'hindi']:
            language = 'english'
        
        # Set reasonable limits
        num_cards = max(1, min(num_cards, 50))  # Between 1 and 50
        
        logger.info(f"[FLASHCARDS] Request: topic_length={len(topic)}, num_cards={num_cards}, language={language}")
        
        # Handle document upload
        if 'document' in request.FILES:
            document_file = request.FILES['document']
            logger.info(f"[FLASHCARDS] Processing file: {document_file.name}")
            
            file_name = default_storage.save(f'temp/{document_file.name}', 
                                            ContentFile(document_file.read()))
            file_path = default_storage.path(file_name)
            
            try:
                # Extract text from document
                if document_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                    logger.info(f"[FLASHCARDS] Processing image file: {document_file.name}")
                    ocr_result = ocr_service.extract_text_from_image(file_path)
                    if ocr_result['success'] and ocr_result.get('text', '').strip():
                        topic = ocr_result['text'].strip()
                        logger.info(f"[FLASHCARDS] OCR successful: {len(topic)} chars")
                    else:
                        logger.warning(f"[FLASHCARDS] OCR failed: {ocr_result.get('error')}")
                        return Response({
                            'success': False,
                            'error': 'Could not extract readable text from the image',
                            'details': 'Please ensure the image contains clear, readable text',
                            'supported_formats': ['PNG', 'JPG', 'JPEG']
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                elif document_file.name.lower().endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        topic = f.read()
                        
                elif document_file.name.lower().endswith('.pdf'):
                    try:
                        import PyPDF2
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            topic = ""
                            for page in pdf_reader.pages:
                                topic += page.extract_text() + "\n"
                    except ImportError:
                        return Response({
                            'success': False,
                            'error': 'PDF support requires PyPDF2',
                            'details': 'Install with: pip install PyPDF2'
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        'success': False,
                        'error': 'Unsupported file format',
                        'supported_formats': ['.txt', '.pdf', '.png', '.jpg', '.jpeg']
                    }, status=status.HTTP_400_BAD_REQUEST)
            finally:
                # Clean up temp file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    default_storage.delete(file_name)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")
        
        # Validate we have content
        if not topic or not topic.strip():
            return Response({
                'success': False,
                'error': 'Please provide a topic or upload a document',
                'message': 'Either submit text in the topic field or upload a file'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Limit topic length
        topic = topic[:5000]  # Max 5000 characters
        
        # Generate flashcards using Gemini with language support
        logger.info(f"[FLASHCARDS] Generating {num_cards} flashcards in {language}")
        result = gemini_service.generate_flashcards(topic, num_cards, language=language)

        if result.get('success'):
            return Response({
                'success': True,
                'flashcards': result.get('flashcards', []),
                'language': language,
                'count': len(result.get('flashcards', []))
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"[FLASHCARDS] Generation failed: {result.get('error')}")
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to generate flashcards'),
                'details': result.get('details', '')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except ValueError as e:
        logger.error(f"[FLASHCARDS] Validation error: {e}")
        return Response({
            'success': False,
            'error': 'Invalid parameter value',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"[FLASHCARDS] Unexpected error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to generate flashcards',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

## SOLUTION 3: Fix Predicted Questions (500 Error)

Add error handling and validation:

```python
# In question_solver/views.py - PredictedQuestionsView.post()

class PredictedQuestionsView(APIView):
    """
    Generate predicted important questions from topic or document
    POST /api/predicted-questions/generate/
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        """
        Generate predicted questions from topic or document
        
        Request body:
        - topic: Topic/subject name (for text-based generation)
        - document: Document file (for document-based generation)
        - exam_type: Type of exam (default: General)
        - num_questions: Number of questions (default: 5, max: 20)
        - language: 'english' or 'hindi' (default: 'english')
        """
        try:
            topic = request.data.get('topic', '').strip()
            exam_type = request.data.get('exam_type', 'General')
            language = request.data.get('language', 'english').lower()
            
            try:
                num_questions = int(request.data.get('num_questions', 5))
            except (ValueError, TypeError):
                num_questions = 5
            
            # Validate language
            if language not in ['english', 'hindi']:
                language = 'english'
            
            # Validate num_questions
            num_questions = max(1, min(num_questions, 20))  # 1-20 questions
            
            document = None
            logger.info(f"[PREDICTED_Q] Request: exam={exam_type}, num_q={num_questions}, lang={language}")
            
            # Get content from either topic or document
            if 'document' in request.FILES:
                logger.info("[PREDICTED_Q] Processing document upload")
                document_file = request.FILES['document']
                file_name = default_storage.save(f'temp/{document_file.name}', 
                                                ContentFile(document_file.read()))
                file_path = default_storage.path(file_name)
                
                try:
                    # Extract text from document
                    if document_file.name.lower().endswith(('.txt', '.md')):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            document = f.read()
                        logger.info(f"[PREDICTED_Q] Extracted {len(document)} chars from text")
                        
                    elif document_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        logger.info("[PREDICTED_Q] Processing image with OCR")
                        ocr_result = ocr_service.extract_text_from_image(file_path)
                        if ocr_result.get('success'):
                            document = ocr_result.get('text', '')
                            logger.info(f"[PREDICTED_Q] OCR successful: {len(document)} chars")
                        else:
                            logger.warning(f"[PREDICTED_Q] OCR failed: {ocr_result.get('error')}")
                            return Response({
                                'success': False,
                                'error': 'Failed to extract text from image',
                                'details': ocr_result.get('error', 'OCR processing failed')
                            }, status=status.HTTP_400_BAD_REQUEST)
                            
                    elif document_file.name.lower().endswith('.pdf'):
                        try:
                            import PyPDF2
                            with open(file_path, 'rb') as f:
                                reader = PyPDF2.PdfReader(f)
                                document = ' '.join([page.extract_text() for page in reader.pages])
                            logger.info(f"[PREDICTED_Q] Extracted {len(document)} chars from PDF")
                        except ImportError:
                            logger.error("[PREDICTED_Q] PyPDF2 not installed")
                            return Response({
                                'success': False,
                                'error': 'PDF support requires PyPDF2',
                                'details': 'Install with: pip install PyPDF2'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        except Exception as pdf_error:
                            logger.warning(f"[PREDICTED_Q] PDF extraction failed: {pdf_error}")
                            document = None
                    else:
                        return Response({
                            'success': False,
                            'error': f'Unsupported document type: {document_file.name}',
                            'supported_formats': ['.txt', '.md', '.pdf', '.jpg', '.jpeg', '.png']
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as file_error:
                    logger.error(f"[PREDICTED_Q] File processing error: {file_error}", exc_info=True)
                    return Response({
                        'success': False,
                        'error': 'Failed to process document',
                        'details': str(file_error)
                    }, status=status.HTTP_400_BAD_REQUEST)
                finally:
                    # Clean up temp file
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        default_storage.delete(file_name)
                    except Exception as cleanup_error:
                        logger.warning(f"[PREDICTED_Q] Cleanup error: {cleanup_error}")
                
                if not document or not document.strip():
                    return Response({
                        'success': False,
                        'error': 'Could not extract text from document',
                        'message': 'Please ensure the document contains readable text'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                topic = document[:500]  # Use first 500 chars as topic label
                
            elif not topic:
                return Response({
                    'success': False,
                    'error': 'Please provide either a topic or document',
                    'message': 'Submit text in topic field or upload a document file'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prepare content for Gemini (limit length)
            content = (document if document else topic)[:3000]
            
            logger.info(f"[PREDICTED_Q] Generating {num_questions} questions, content_length={len(content)}")
            
            # Generate questions with language support
            lang_suffix = " in Hindi language (देवनागरी script)" if language == 'hindi' else ""
            
            prompt = f"""You are an expert educator preparing comprehensive study material with predicted exam questions.

TOPIC/CONTENT:
{content}

EXAM TYPE: {exam_type}
NUMBER OF QUESTIONS: {num_questions}
LANGUAGE: {language}{lang_suffix}

Create predicted questions that may appear in {exam_type} exams.

Return ONLY valid JSON in this exact format:
{{
    "title": "Topic Title",
    "summary": "Brief overview",
    "questions": [
        {{
            "question": "Question text{lang_suffix}?",
            "options": [
                {{"text": "Option A{lang_suffix}"}},
                {{"text": "Option B{lang_suffix}"}},
                {{"text": "Option C{lang_suffix}"}},
                {{"text": "Option D{lang_suffix}"}}
            ],
            "correct_answer": "A",
            "explanation": "Why this is correct{lang_suffix}",
            "difficulty": "easy|medium|hard"
        }}
    ]
}}
"""
            
            response = self.model.generate_content(prompt) if hasattr(self, 'model') else gemini_service.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            
            return Response({
                'success': True,
                'title': result.get('title', exam_type),
                'summary': result.get('summary', ''),
                'questions': result.get('questions', []),
                'language': language,
                'count': len(result.get('questions', []))
            }, status=status.HTTP_200_OK)
            
        except json.JSONDecodeError as e:
            logger.error(f"[PREDICTED_Q] JSON parse error: {e}")
            return Response({
                'success': False,
                'error': 'Failed to parse AI response',
                'details': 'Please try again with different input'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            logger.error(f"[PREDICTED_Q] Validation error: {e}")
            return Response({
                'success': False,
                'error': 'Invalid parameter',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"[PREDICTED_Q] Unexpected error: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Failed to generate predicted questions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

## API Usage Examples

### Hindi Daily Quiz

```bash
# Get Hindi daily quiz
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=user123&language=hindi" \
  -H "Content-Type: application/json"

# Response
{
  "quiz_metadata": {
    "quiz_type": "daily_coin_quiz",
    "total_questions": 5,
    "language": "hindi",
    "title": "Daily GK Quiz - January 10, 2026"
  },
  "questions": [
    {
      "id": 1,
      "question": "भारत की राजधानी कौन सी है?",
      "options": ["मुंबई", "दिल्ली", "कोलकाता", "बेंगलुरु"],
      "category": "geography"
    }
  ]
}
```

### Flashcards with Language

```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय इतिहास",
    "num_cards": 10,
    "language": "hindi"
  }'
```

### Predicted Questions with Document

```bash
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: multipart/form-data" \
  -F "document=@textbook.pdf" \
  -F "num_questions=10" \
  -F "language=hindi"
```

---

## Migration Required

Add language field to Daily Quiz model:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Frontend Usage

### Request Hindi Quiz

```javascript
// JavaScript
const response = await fetch('https://api.example.com/api/daily-quiz/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  },
  params: {
    user_id: 'user123',
    language: 'hindi'  // Request Hindi questions
  }
});
```

---

## Pre-built Hindi Questions (Fallback)

If Gemini fails, use this fallback pool of 100 Hindi questions:

See `HINDI_QUESTIONS_POOL_100.py` for complete list of 100 GK questions in Hindi with answers and explanations.

---

## Testing Checklist

- [ ] Update Gemini service with language parameter
- [ ] Update daily quiz views with language support
- [ ] Update DailyQuiz model with language field
- [ ] Run migrations
- [ ] Test Hindi quiz generation
- [ ] Test English quiz generation
- [ ] Add flashcard language support
- [ ] Add predicted questions language support
- [ ] Test all error scenarios
- [ ] Deploy to production

