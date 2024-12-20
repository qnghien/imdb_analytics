def generate_financials_url(movie_id):
    """
    Generates the Box Office Mojo URL for financials.
    """
    base_url = "https://www.boxofficemojo.com/title/{}/"
    return base_url.format(movie_id)


def generate_production_url(movie_id):
    """
    Generates the Box Office Mojo URL for production.
    """
    base_url = "https://www.boxofficemojo.com/title/{}/credits/?ref_=bo_tt_tab"
    return base_url.format(movie_id)


def generate_articles_url(movie_id):
    """
    Generates the Box Office Mojo URL for articles.
    """
    base_url = "https://www.boxofficemojo.com/title/{}/news/?ref_=bo_tt_tab"
    return base_url.format(movie_id)
