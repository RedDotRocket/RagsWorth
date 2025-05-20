from fastapi import APIRouter, HTTPException
from ..models.api import ChatRequestModel, ChatResponseModel, DocumentModel
from ..pipeline import ChatRequest, Pipeline
from ..config.logging_config import get_logger

logger = get_logger("routes.chat")

router = APIRouter(tags=["chat"])

class ChatRouter:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        
    def create_router(self):
        """Create a configured router with chat endpoints."""
        
        @router.post("/chat", response_model=ChatResponseModel)
        async def chat(request: ChatRequestModel) -> ChatResponseModel:
            """Process a chat request."""
            try:
                # Create chat request
                chat_request = ChatRequest(
                    session_id=request.session_id,
                    user_message=request.user_message,
                    metadata={"context": request.context} if request.context else {}
                )

                # Process through pipeline
                response = await self.pipeline.process(chat_request)

                # Debug information
                logger.info(f"Processing chat request completed, source documents: {len(response.source_documents)}")
                if response.source_documents:
                    for i, doc in enumerate(response.source_documents[:3]):  # Show first 3 documents
                        logger.debug(f"Source doc {i+1}: id={doc.id}, score={doc.score}")

                # Convert to response model
                source_docs = []
                for doc in response.source_documents:
                    if hasattr(doc, 'content') and doc.content:
                        # Extract a meaningful snippet
                        content = doc.content.strip()
                        snippet = content[:200] + "..." if len(content) > 200 else content

                        # Get the score (or default to 0)
                        score = doc.score if hasattr(doc, 'score') and doc.score is not None else 0

                        source_docs.append(
                            DocumentModel(
                                id=doc.id,
                                score=score,
                                snippet=snippet
                            )
                        )

                return ChatResponseModel(
                    session_id=response.session_id,
                    bot_reply=response.bot_reply,
                    source_documents=source_docs
                )

            except Exception as e:
                logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
                
        return router 