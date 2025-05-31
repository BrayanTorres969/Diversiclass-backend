from .course import CourseCreate, CourseUpdate
from .document import DocumentCreate
from .response import CourseResponse, DocumentResponse
from .quiz import QuizResponse, QuizCreate
from .option import OptionResponse, OptionBase

__all__ = [
    'CourseCreate',
    'CourseUpdate',
    'DocumentCreate',
    'CourseResponse',
    'DocumentResponse',
    'QuizzResponse',
    'QuizzCreate',
    'OptionBase',
    'OptionResponse'
]