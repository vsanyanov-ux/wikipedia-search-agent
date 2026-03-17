import wikipedia

def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for the given query and return a summary of the most relevant page.
    
    CRITICAL INSTRUCTIONS FOR USE:
    1. The 'query' MUST be a specific, well-formed noun or entity. Do not send vague questions or conversational filler.
    2. If the query is ambiguous, this tool WILL FAIL and throw a DisambiguationError. It is YOUR responsibility to provide a search term that points to a single, definitive article.
    3. If no article matches the query, a PageError will be raised. Do not guess; ensure the entity actually exists in the real world.
    4. The output is a string containing the first few sentences of the Wikipedia article. If you need more information, you'll have to find another tool or try a different article.
    
    Args:
        query (str): The EXACT title of the Wikipedia article to retrieve. Must be a string. Do not include quotes unless they are part of the title.

    Returns:
        str: A summary of the Wikipedia article if found.
        
    Raises:
        ValueError: If the search results in an error (e.g., disambiguation or page not found), the error message will be returned as a string starting with "ERROR: ".
    """
    try:
        # Use first=True to get the most relevant page summary
        return wikipedia.summary(query, sentences=3, auto_suggest=False)
    except wikipedia.DisambiguationError as e:
        return f"ERROR: Ambiguous query. Possible options are: {', '.join(e.options[:5])}. Please be more specific."
    except wikipedia.PageError:
        return f"ERROR: Page '{query}' not found. Please check your spelling or try a more common name for this entity."
    except Exception as e:
        return f"ERROR: An unexpected error occurred: {str(e)}"
