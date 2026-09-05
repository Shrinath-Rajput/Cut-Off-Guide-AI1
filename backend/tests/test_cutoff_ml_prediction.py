import asyncio

from app.schemas.cutoff import CutoffSearchRequest
from app.services.cutoff_service import search_cutoffs


static_suggestions = {
    'PCCOE Pune / VIT Pune / DYPCOE Akurdi (AI & Data Science)',
    'PCCOE Pune / VIT Pune / DYPCOE Akurdi',
    'PCCOE Pune / VIT Pune / DYPCOE Akurdi (AI & Data Science)'
}


def test_search_cutoffs_uses_model_instead_of_hardcoded_result():
    request = CutoffSearchRequest(
        exam='MHT-CET',
        score='92.5',
        category='Open/General',
        gender='Male',
        university='Mumbai University',
        course='Computer Engineering',
        location='Pune',
        round='Round 1',
    )

    result = asyncio.run(search_cutoffs(None, request))

    assert result.cutoff.endswith('%ile')
    assert result.rank
    assert result.suggestion not in static_suggestions
    assert 'PCCOE' not in result.suggestion
    assert 'VIT' not in result.suggestion
    assert 'DYPCOE' not in result.suggestion
