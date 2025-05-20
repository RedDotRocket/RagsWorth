import os
import click
import uvicorn
import asyncio

from .config.app_config import AppConfig
from .app import RagsWorthApp
from .rag.document_processor import DocumentProcessor
from .config.logging_config import get_logger

logger = get_logger("cli")

@click.group()
def cli():
    """RagsWorth CLI - A RAG-powered chatbot."""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
@click.option('--lazy-load', is_flag=True, help='Lazy load components on first request instead of startup')
@click.option('--log-level', type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']), 
              default='info', help='Set logging level')
@click.option('--log-file', type=click.Path(), help='Path to log file')
def serve(host: str, port: int, reload: bool, config: str, lazy_load: bool, log_level: str, log_file: str):
    """Run the RagsWorth server."""
    if config:
        os.environ['RAGSWORTH_CONFIG'] = str(config)

    # Set logging environment variables
    if log_level:
        os.environ['RAGSWORTH_LOG_LEVEL'] = log_level
    if log_file:
        os.environ['RAGSWORTH_LOG_FILE'] = log_file

    # Initialize app with components by default, unless lazy-load flag is set
    RagsWorthApp(init_components=not lazy_load)

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "ragsworth:app",
        host=host,
        port=port,
        reload=reload
    )

@cli.command()
@click.argument('docs_dir', type=click.Path(exists=True))
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
@click.option('--output', '-o', default='data/vectorstore',
              help='Directory to save vector store (default: data/vectorstore)')
@click.option('--recursive', '-r', is_flag=True,
              help='Recursively load documents from subdirectories')
@click.option('--milvus-uri', help='Milvus server URI (overrides config)')
@click.option('--milvus-collection', help='Milvus collection name (overrides config)')
@click.option('--embedding-provider', type=click.Choice(['openai', 'ollama']),
              help='Force a specific provider for embeddings (required when using Anthropic)')
@click.option('--ollama-url', help='Ollama API URL (overrides config)')
@click.option('--log-level', type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']), 
              default='info', help='Set logging level')
@click.option('--log-file', type=click.Path(), help='Path to log file')
def load(docs_dir: str, config: str, output: str, recursive: bool,
         milvus_uri: str = None, milvus_collection: str = None,
         embedding_provider: str = None, ollama_url: str = None,
         log_level: str = None, log_file: str = None):
    """Load documents into the vector store."""
    if config:
        os.environ['RAGSWORTH_CONFIG'] = str(config)

    # Set logging environment variables
    if log_level:
        os.environ['RAGSWORTH_LOG_LEVEL'] = log_level
    if log_file:
        os.environ['RAGSWORTH_LOG_FILE'] = log_file

    # Load configuration
    app_config = AppConfig()
    config_dict = app_config.config

    # Override config with command line options
    if milvus_uri or milvus_collection:
        if "milvus" not in config_dict["retrieval"]["vector_store"]:
            config_dict["retrieval"]["vector_store"]["milvus"] = {}
        if milvus_uri:
            config_dict["retrieval"]["vector_store"]["milvus"]["uri"] = milvus_uri
        if milvus_collection:
            config_dict["retrieval"]["vector_store"]["milvus"]["collection_name"] = milvus_collection

    if ollama_url:
        config_dict["llm"]["base_url"] = ollama_url

    if embedding_provider:
        config_dict["llm"]["embedding_provider"] = embedding_provider

    # Initialize document processor
    processor = DocumentProcessor(config_dict)

    # Process documents
    logger.info(f"Loading documents from {docs_dir}")
    asyncio.run(processor.process_documents(docs_dir, recursive=recursive))

    # Save vector store
    processor.save_vector_store(output)
    logger.info("Document loading completed successfully!")

@cli.command()
def help():
    """Show help information."""
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    commands = cli.list_commands(ctx)
    for cmd in commands:
        if cmd != 'help':
            click.echo(f"\n{cmd} command:")
            cmd_obj = cli.get_command(ctx, cmd)
            click.echo(cmd_obj.get_help(ctx))

@cli.command()
@click.option('--milvus-uri', required=True, help='Milvus server URI')
@click.option('--milvus-collection', required=True, help='Name of the collection to drop')
@click.option('--log-level', type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']), 
              default='info', help='Set logging level')
def drop_collection(milvus_uri: str, milvus_collection: str, log_level: str = None):
    """Drop a Milvus collection."""
    # Set logging environment variables
    if log_level:
        os.environ['RAGSWORTH_LOG_LEVEL'] = log_level
    
    # Load configuration to initialize logging
    AppConfig()
    
    from pymilvus import MilvusClient

    try:
        client = MilvusClient(uri=milvus_uri)
        client.drop_collection(milvus_collection)
        logger.info(f"Successfully dropped collection '{milvus_collection}'")
    except Exception as e:
        logger.error(f"Error dropping collection: {e}")
        raise click.Abort()

if __name__ == '__main__':
    cli()