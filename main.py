import uvicorn
from ragsworth.app import create_app

if __name__ == "__main__":
    """
    Main entry point for running the RagsWorth API service.
    
    This script creates the FastAPI application with components initialized
    and runs it using Uvicorn server.
    """
    # Always initialize components at startup for best user experience
    app = create_app(init_components=True)
    
    # Run the app
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    ) 