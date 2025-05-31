import spacy
from random import sample, shuffle
from typing import List, Tuple, Dict
from pathlib import Path
from app.models.quiz import QuizCreate
from app.models.option import OptionBase

# Cargar modelo de lenguaje en español
nlp = spacy.load("es_core_news_lg")

class QuizGenerator:
    def __init__(self):
        # Plantillas de preguntas organizadas por tipo de palabra clave
        self.question_templates = {
            "NOUN": [
                "¿Qué se menciona sobre {phrase} en el texto?",
                "Según el documento, ¿cómo se define {phrase}?",
                "¿Cuál es la función principal de {phrase}?",
                "¿Qué característica destaca de {phrase}?"
            ],
            "VERB": [
                "¿Cómo se lleva a cabo {phrase} según el texto?",
                "¿Qué implica {phrase} en este contexto?",
                "Describa el proceso de {phrase}"
            ],
            "DEFAULT": [
                "¿Qué información relevante se proporciona sobre {phrase}?",
                "Explique la importancia de {phrase} en el documento"
            ]
        }

    def generate_quizzes(
        self,
        text: str,
        num_questions: int = 5,
        num_options: int = 4
    ) -> List[QuizCreate]:
        """
        Genera quizzes a partir de un texto usando NLP.
        
        Args:
            text (str): Texto extraído del documento
            num_questions (int): Número de preguntas a generar
            num_options (int): Opciones por pregunta
            
        Returns:
            List[QuizCreate]: Lista de quizzes con preguntas y opciones
        """
        doc = nlp(text)
        quizzes = []
        
        # 1. Extraer frases clave
        key_phrases = self._extract_key_phrases(doc)
        
        # 2. Seleccionar frases para preguntas (evitando duplicados)
        selected_phrases = sample(
            list(set(key_phrases)),  # Eliminar duplicados
            min(num_questions, len(key_phrases))
        )
        
        # 3. Generar pregunta para cada frase clave
        for phrase, phrase_type in selected_phrases:
            question_text = self._generate_question_text(phrase, phrase_type)
            options = self._generate_options(phrase, text, num_options)
            
            quizzes.append(QuizCreate(
                questionText=question_text,  # Usa el alias JSON
                context=self._extract_context(phrase, text),
                difficulty=self._estimate_difficulty(phrase, doc),
                options=options
            ))
        
        return quizzes

    def _extract_key_phrases(self, doc) -> List[Tuple[str, str]]:
        """
        Extrae frases clave del texto con su tipo gramatical.
        
        Returns:
            List[Tuple[texto, tipo]]: Lista de frases clave con su tipo
        """
        phrases = []
        
        # Extraer entidades nombradas (personas, organizaciones, lugares)
        for ent in doc.ents:
            if ent.label_ in ["PER", "ORG", "LOC", "MISC"]:
                phrases.append((ent.text, "NOUN"))
        
        # Extraer sustantivos importantes
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 4:  # Ignorar palabras muy cortas
                phrases.append((chunk.text, "NOUN"))
        
        # Extraer verbos relevantes
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_ not in ["ser", "estar", "haber"]:
                phrases.append((token.text, "VERB"))
        
        return phrases

    def _generate_question_text(self, phrase: str, phrase_type: str) -> str:
        """Genera el texto de la pregunta usando plantillas."""
        templates = self.question_templates.get(phrase_type, self.question_templates["DEFAULT"])
        template = sample(templates, 1)[0]
        
        # Adaptar la frase a la plantilla
        if phrase_type == "VERB":
            phrase = f"el proceso de {phrase.rstrip('ar')}ar"  # Para verbos infinitivos
        elif phrase_type == "NOUN":
            if not phrase.startswith(("el ", "la ", "los ", "las ")):
                phrase = f"el {phrase}" if phrase[-1] != 's' else f"los {phrase}"
        
        return template.format(phrase=phrase)

    def _generate_options(
        self,
        correct_phrase: str,
        full_text: str,
        num_options: int
    ) -> List[OptionBase]:
        """
        Genera opciones de respuesta con:
        - 1 respuesta correcta (extraída del contexto)
        - n-1 distractores plausibles
        """
        # 1. Respuesta correcta (en contexto)
        correct_answer = self._extract_answer(correct_phrase, full_text)
        options = [OptionBase(text=correct_answer, is_correct=True)]
        
        # 2. Generar distractores
        distractors = self._generate_distractors(correct_phrase, full_text, num_options-1)
        options.extend([OptionBase(text=d, is_correct=False) for d in distractors])
        
        # 3. Mezclar aleatoriamente
        shuffle(options)
        return options

    def _extract_answer(self, phrase: str, text: str) -> str:
        """Extrae la respuesta correcta del contexto."""
        doc = nlp(text)
        for sent in doc.sents:
            if phrase in sent.text:
                # Limitar longitud y limpiar
                return sent.text[:150].strip() + "..."
        return f"El texto menciona: {phrase}"

    def _generate_distractors(
        self,
        correct_phrase: str,
        full_text: str,
        num_distractors: int
    ) -> List[str]:
        """Genera opciones incorrectas pero plausibles."""
        doc = nlp(full_text)
        distractors = []
        
        # 1. Distractores de frases similares
        similar_phrases = [
            p for p in self._extract_key_phrases(doc) 
            if p[0] != correct_phrase
        ]
        distractors.extend(sample(
            [p[0] for p in similar_phrases],
            min(num_distractors, len(similar_phrases))
        ))
        
        # 2. Distractores genéricos si faltan
        generic_distractors = [
            "No se menciona explícitamente en el texto",
            "Es un concepto secundario en el documento",
            "La información proporcionada es insuficiente",
            "El texto no aborda este tema en profundidad"
        ]
        
        while len(distractors) < num_distractors:
            distractors.append(sample(generic_distractors, 1)[0])
        
        return distractors[:num_distractors]

    def _extract_context(self, phrase: str, text: str) -> str:
        """Extrae el contexto alrededor de la frase clave."""
        start_idx = max(0, text.find(phrase) - 100)
        end_idx = min(len(text), text.find(phrase) + len(phrase) + 100)
        return text[start_idx:end_idx].strip()

    def _estimate_difficulty(self, phrase: str, doc) -> float:
        """Estima dificultad basada en características lingüísticas."""
        # 1. Basado en longitud
        difficulty = min(5, len(phrase.split()) * 0.5)
        
        # 2. Ajustar por términos técnicos
        technical_terms = {"algoritmo", "modelo", "paradigma", "heurística"}
        if any(term in phrase.lower() for term in technical_terms):
            difficulty = min(5, difficulty + 1.5)
        
        return max(1, round(difficulty, 1))

# Instancia global para reutilizar el modelo cargado
quiz_generator = QuizGenerator()