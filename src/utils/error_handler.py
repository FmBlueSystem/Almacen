"""
Módulo de manejo centralizado de errores para la aplicación
"""

import logging
import time
from typing import Optional, Callable, Any
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class LoadingCircuitBreaker:
    """
    Circuit breaker para prevenir re-entrada en operaciones de carga
    """
    
    def __init__(self, cooldown: float = 2.0):
        """
        Inicializar circuit breaker
        
        Args:
            cooldown: Tiempo en segundos para esperar después de un error
        """
        self._loading = False
        self._last_error_time: Optional[float] = None
        self._cooldown = cooldown
        
    def can_execute(self) -> bool:
        """
        Verificar si se puede ejecutar una operación
        
        Returns:
            bool: True si se puede ejecutar, False si está en cooldown o cargando
        """
        if self._loading:
            return False
            
        if self._last_error_time and (time.time() - self._last_error_time) < self._cooldown:
            return False
            
        return True
    
    def start_loading(self) -> bool:
        """
        Marcar inicio de carga si es posible
        
        Returns:
            bool: True si se pudo iniciar, False si no es posible
        """
        if not self.can_execute():
            return False
            
        self._loading = True
        return True
    
    def finish_loading(self, success: bool = True):
        """
        Marcar fin de carga
        
        Args:
            success: Si la operación fue exitosa o no
        """
        self._loading = False
        if not success:
            self._last_error_time = time.time()
    
    def reset_error_state(self):
        """Resetear el estado de error para permitir nuevos intentos"""
        self._last_error_time = None


class DebouncedEmitter(QObject):
    """
    Emisor de señales con debouncing para prevenir eventos excesivos
    """
    
    signal_emitted = pyqtSignal(str, str, str)  # title, artist, genre
    
    def __init__(self, delay_ms: int = 300):
        """
        Inicializar emisor con debouncing
        
        Args:
            delay_ms: Retraso en milisegundos para el debouncing
        """
        super().__init__()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._emit_signal)
        self._delay = delay_ms
        self._pending_args: Optional[tuple] = None
        
    def emit_debounced(self, title: str, artist: str, genre: str):
        """
        Emitir señal con debouncing
        
        Args:
            title: Filtro de título
            artist: Filtro de artista  
            genre: Filtro de género
        """
        self._pending_args = (title, artist, genre)
        self._timer.stop()
        self._timer.start(self._delay)
        
    def _emit_signal(self):
        """Emitir la señal pendiente"""
        if self._pending_args:
            self.signal_emitted.emit(*self._pending_args)
            self._pending_args = None


class ErrorHandler:
    """
    Manejador centralizado de errores con logging estructurado
    """
    
    @staticmethod
    def setup_logging(logger_name: str, level: int = logging.INFO) -> logging.Logger:
        """
        Configurar logging para un módulo
        
        Args:
            logger_name: Nombre del logger
            level: Nivel de logging
            
        Returns:
            logging.Logger: Logger configurado
        """
        logger = logging.getLogger(logger_name)
        
        if not logger.handlers:
            # Configurar handler de consola
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Formato para el log
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.setLevel(level)
            
        return logger
    
    @staticmethod
    def handle_db_error(logger: logging.Logger, error: Exception, context: str = "") -> str:
        """
        Manejar errores de base de datos
        
        Args:
            logger: Logger para registrar el error
            error: Excepción capturada
            context: Contexto donde ocurrió el error
            
        Returns:
            str: Mensaje amigable para mostrar al usuario
        """
        context_msg = f" in {context}" if context else ""
        logger.error(f"Database error{context_msg}: {error}", exc_info=True)
        return "Error de conexión a la base de datos. Ver logs para detalles."
    
    @staticmethod
    def handle_general_error(logger: logging.Logger, error: Exception, context: str = "") -> str:
        """
        Manejar errores generales
        
        Args:
            logger: Logger para registrar el error
            error: Excepción capturada
            context: Contexto donde ocurrió el error
            
        Returns:
            str: Mensaje amigable para mostrar al usuario
        """
        context_msg = f" in {context}" if context else ""
        logger.error(f"General error{context_msg}: {error}", exc_info=True)
        return "Error inesperado. Ver logs para detalles."
    
    @staticmethod
    def handle_loading_error(logger: logging.Logger, error: Exception, page: int) -> str:
        """
        Manejar errores específicos de carga de datos
        
        Args:
            logger: Logger para registrar el error
            error: Excepción capturada
            page: Página que se intentaba cargar
            
        Returns:
            str: Mensaje amigable para mostrar al usuario
        """
        logger.error(f"Error loading page {page}: {error}", exc_info=True)
        return f"Error cargando página {page}. Ver logs para detalles."


def with_error_handling(circuit_breaker: LoadingCircuitBreaker, 
                       logger: logging.Logger,
                       context: str = ""):
    """
    Decorador para funciones que necesitan manejo de errores y circuit breaker
    
    Args:
        circuit_breaker: Circuit breaker para controlar la ejecución
        logger: Logger para errores
        context: Contexto de la operación
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            if not circuit_breaker.start_loading():
                logger.warning(f"Operation blocked by circuit breaker in {context}")
                return None
                
            try:
                result = func(*args, **kwargs)
                circuit_breaker.finish_loading(success=True)
                return result
            except Exception as e:
                circuit_breaker.finish_loading(success=False)
                ErrorHandler.handle_general_error(logger, e, context)
                raise
                
        return wrapper
    return decorator
