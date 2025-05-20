from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer

from .config.app_config import AppConfig
from .factory.component_factory import ComponentFactory
from .pipeline import Pipeline
from .stages import InputSanitizer, LLMStage, OutputSanitizer, PIIBlocker, Retriever
from .routes.auth import create_auth_router, get_current_user_dependency
from .routes.chat import ChatRouter
from .routes.users import create_user_router
from .routes.protected import ProtectedRouter
from .routes.health import router as health_router

class RagsWorthApp:
    """Main RagsWorth application class."""

    def __init__(self, init_components: bool = True):
        # Load configuration
        self.config = AppConfig().config
        self.factory = ComponentFactory(self.config)

        # Create FastAPI app
        self.app = FastAPI(
            title="RagsWorth API",
            description="API for the RagsWorth chatbot with RAG capabilities",
            version="0.1.0"
        )

        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup OAuth2 scheme
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

        # Create database
        self.db = self.factory.db

        # Mount static files
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

        if init_components:
            self.initialize_components()

        # Register routes
        self.register_routes()

    def initialize_components(self):
        """Initialize RagsWorth components."""
        # Initialize components
        self.llm_client = self.factory.create_llm_client()
        self.vector_store = self.factory.create_vector_store()
        self.pii_detector = self.factory.create_pii_detector()

        # Create pipeline
        self.pipeline = Pipeline([
            InputSanitizer(),
            PIIBlocker(self.pii_detector),
            Retriever(self.vector_store, self.llm_client),
            LLMStage(self.llm_client),
            OutputSanitizer(self.pii_detector)
        ])

    def register_routes(self):
        """Register API routes."""
        # Create API prefix
        api_prefix = "/api/v1"

        # Create get_current_user dependency
        get_current_user = get_current_user_dependency(self.oauth2_scheme, self.db)

        # Create authentication router
        auth_router = create_auth_router(self.db)
        self.app.include_router(auth_router, prefix=api_prefix)

        # Create user router
        user_router = create_user_router(self.db, get_current_user)
        self.app.include_router(user_router, prefix=api_prefix)

        # Register health check routes
        self.app.include_router(health_router, prefix=api_prefix)

        # Only include routes that require components if they're initialized
        if hasattr(self, 'pipeline'):
            # Create chat router
            chat_router = ChatRouter(self.pipeline).create_router()
            self.app.include_router(chat_router, prefix=api_prefix)

            # Create protected router
            protected_router = ProtectedRouter(self.vector_store).create_router(get_current_user)
            self.app.include_router(protected_router, prefix=api_prefix)

# Create application instance
def create_app(init_components: bool = False) -> FastAPI:
    """Create and configure the FastAPI application."""
    return RagsWorthApp(init_components=init_components).app