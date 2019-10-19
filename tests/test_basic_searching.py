from perdu import search_naics, search_gs1, search_corrector_naics, search_corrector_gs1
import pytest


def test_search_gs1():
    assert search_gs1("toys")


def test_search_naics():
    assert search_naics("toys")


def test_correct_gs1():
    assert "cosmetic" in search_corrector_gs1("cosmet")[0]


def test_correct_naics():
    assert "cosmetic" in search_corrector_naics("cosmet")[0]
