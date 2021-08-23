
import re

from spacy.tokens import Span #type: ignore
import pytest 

from skweak.analysis import LFAnalysis


@pytest.fixture(scope="session")
def analysis_doc(nlp):
    """ Generate a sample document with conflicts, agreements, and overlaps.
    """
    spacy_doc = nlp(
        re.sub("\\s+", " ", """This is a test for Pierre Lison from the
                     Norwegian Computing Center. Pierre is living in Oslo."""))
    spacy_doc.spans["name_1"] = [
        Span(spacy_doc, 5, 7, label="PERSON"),
        Span(spacy_doc, 13, 14, label="PERSON")
    ]
    spacy_doc.spans["name_2"] = [
        Span(spacy_doc, 5, 7, label="PERSON")
    ] 
    spacy_doc.spans["org_1"] = [
        Span(spacy_doc, 9, 12, label="ORG")
    ]
    spacy_doc.spans["org_2"] = [
        Span(spacy_doc, 9, 11, label="ORG"), 
        Span(spacy_doc, 17, 18, label="ORG"),
    ]
    spacy_doc.spans["place_2"] = [
        Span(spacy_doc, 9, 10, label="NORP"),
        Span(spacy_doc, 17, 18, label="GPE")
    ]
    return spacy_doc


# ---------------------
# LABEL CONFLICT TESTS
# ---------------------
def test_conflicts_with_strict_match_labels_with_prefixes(analysis_doc):
    """ Test expected conflicts across below spans:
  
    Spans:
        "name_1": Pierre (B-PERSON), Lison (L-PERSON), Pierre(U-PERSON)
        "name_2": Pierre (B-PERSON), Lison (L-PERSON)
        "org_1": Norwegian (B-ORG), Computing (I-ORG), Center(L-ORG)
        "org_2": Norwegian (B-ORG), Computing (L-ORG), Oslo (U-ORG)
        "place_2": Norwegian (U-NORP), Oslo (U-GPE)

    Conflicts:
        B-PERSON: 0 Conflicts / 1 Token = 0.0
        L-PERSON: 0 Conflicts / 1 Token = 0.0
        U-PERSON: 0 Conflicts / 1 Token = 0.0
        B-ORG: 1 Conflict / 1 Token = 1.0
            (1 Conflict: Norwegian - B-ORG/U-NORP)
        I-ORG: 1 Conflict / 1 Token = 1.0
            (1 Conflict: Computing - I-ORG/L-ORG)
        L-ORG: 1 Conflict / 2 Tokens = 0.5
            (1 Conflict: Computing - I-ORG/L-ORG )
        U-ORG: 1 Conflict / 1 Token = 1.0
            (1 Conflict: Oslo - U-ORG/U-GPE)
        U-NORP: 1 Conflict / 1 Token = 1.0
            (1 Conflict: Norwegian - B-ORG/U-NORP)
        U-GPE: 1 Conflict / 1 Token = 1.0
            (1 Conflict: Oslo - U-ORG/U-GPE)
    """
    labels = ["O"]
    labels += [
        "%s-%s"%(p,l) for l in ["GPE", "NORP", "ORG", "PERSON"] for p in "BILU"
    ]
    lf_analysis = LFAnalysis(
        [analysis_doc],
        labels,
        strict_match=True
    )
    result = lf_analysis.label_conflict()
    assert result['conflict']['B-PERSON'] == 0.0
    assert result['conflict']['L-PERSON'] == 0.0
    assert result['conflict']['U-PERSON'] == 0.0
    assert result['conflict']['B-ORG'] == 1.0
    assert result['conflict']['I-ORG'] == 1.0
    assert result['conflict']['L-ORG'] == 0.5
    assert result['conflict']['U-ORG'] == 1.0
    assert result['conflict']['U-NORP'] == 1.0
    assert result['conflict']['U-GPE'] == 1.0


def test_conflicts_without_strict_match_labels_with_prefixes(analysis_doc):
    """ Test expected conflicts across below spans:
  
    Spans:
        "name_1": Pierre (PERSON), Lison (PERSON), Pierre(PERSON)
        "name_2": Pierre (PERSON), Lison (PERSON)
        "org_1": Norwegian (ORG), Computing (ORG), Center(ORG)
        "org_2": Norwegian (ORG), Computing (ORG), Oslo (ORG)
        "place_2": Norwegian (NORP), Oslo (GPE)

    Conflicts:
        PERSON: 0 Conflicts / 3 Tokens = 0.0
        ORG: 2 Conflicts / 4 Tokens = 0.5
            (2 Conflicts: Norwegian - ORG/NORP, Oslo - ORG/GPE)
        NORP: 1 Conflict / 1 Token = 1.0
             (1 Conflict: Norweigan - ORG/NORP)
        GPE: 1 Conflict / 1 Token = 1.0
            (1 Conflict : Oslo - ORG/GPE)
    """
    labels = ["O"]
    labels += [
        "%s-%s"%(p,l) for l in ["GPE", "NORP", "ORG", "PERSON"] for p in "BILU"
    ]
    lf_analysis = LFAnalysis(
        [analysis_doc],
        labels,
        strict_match=False
    )
    result = lf_analysis.label_conflict()
    assert result['conflict']['PERSON'] == 0.0
    assert result['conflict']['ORG'] == 0.5
    assert result['conflict']['NORP'] == 1.0
    assert result['conflict']['GPE'] == 1.0


def test_conflicts_without_strict_match_labels_without_prefixes(analysis_doc):
    """ Test expected conflicts across below spans:
  
    Spans:
        "name_1": Pierre (PERSON), Lison (PERSON), Pierre(PERSON)
        "name_2": Pierre (PERSON), Lison (PERSON)
        "org_1": Norwegian (ORG), Computing (ORG), Center(ORG)
        "org_2": Norwegian (ORG), Computing (ORG), Oslo (ORG)
        "place_2": Norwegian (NORP), Oslo (GPE)

    Conflicts:
        PERSON: 0 Conflicts / 3 Tokens = 0.0
        ORG: 2 Conflicts / 4 Tokens = 0.5
            (2 Conflicts: Norwegian - ORG/NORP, Oslo - ORG/GPE)
        NORP: 1 Conflict / 1 Token = 1.0
             (1 Conflict: Norweigan - ORG/NORP)
        GPE: 1 Conflict / 1 Token = 1.0
            (1 Conflict : Oslo - ORG/GPE)
    """
    labels = ["O", "GPE", "NORP", "ORG", "PERSON"]
    lf_analysis = LFAnalysis(
        [analysis_doc],
        labels,
        strict_match=False
    )
    result = lf_analysis.label_conflict()
    assert result['conflict']['PERSON'] == 0.0
    assert result['conflict']['ORG'] == 0.5
    assert result['conflict']['NORP'] == 1.0
    assert result['conflict']['GPE'] == 1.0

# ---------------------
# LABEL OVERLAP TESTS
# ---------------------
def test_overlaps_with_strict_match_labels_with_prefixes(analysis_doc):
    """ Test expected overlaps across below spans:
  
    Spans:
        "name_1": Pierre (B-PERSON), Lison (L-PERSON), Pierre(U-PERSON)
        "name_2": Pierre (B-PERSON), Lison (L-PERSON)
        "org_1": Norwegian (B-ORG), Computing (I-ORG), Center(L-ORG)
        "org_2": Norwegian (B-ORG), Computing (L-ORG), Oslo (U-ORG)
        "place_2": Norwegian (U-NORP), Oslo (U-GPE)

    Overlaps:
        B-PERSON: 1 Overlap / 1 Token = 1.0
        L-PERSON: 1 Overlap / 1 Token = 1.0
        U-PERSON: 0 Overlap / 1 Token = 0.0
        B-ORG: 1 Overlap / 1 Token = 1.0
        I-ORG: 1 Overlap / 1 Token = 1.0
        L-ORG: 1 Overlap / 2 Tokens = 0.5
        U-ORG: 1 Overlap / 1 Token = 1.0
        U-NORP: 1 Overlap / 1 Token = 1.0
        U-GPE: 1 Overlap / 1 Token = 1.0
    """
    labels = ["O"]
    labels += [
        "%s-%s"%(p,l) for l in ["GPE", "NORP", "ORG", "PERSON"] for p in "BILU"
    ]
    lf_analysis = LFAnalysis(
        [analysis_doc],
        labels,
        strict_match=True
    )
    result = lf_analysis.label_overlap()
    assert result['overlap']['B-PERSON'] == 1.0
    assert result['overlap']['L-PERSON'] == 1.0
    assert result['overlap']['U-PERSON'] == 0.0
    assert result['overlap']['B-ORG'] == 1.0
    assert result['overlap']['I-ORG'] == 1.0
    assert result['overlap']['L-ORG'] == 0.5
    assert result['overlap']['U-ORG'] == 1.0
    assert result['overlap']['U-NORP'] == 1.0
    assert result['overlap']['U-GPE'] == 1.0


def test_overlaps_without_strict_match_labels_with_prefixes(analysis_doc):
    """ Test expected overlaps across below spans:
  
    Spans:
        "name_1": Pierre (PERSON), Lison (PERSON), Pierre(PERSON)
        "name_2": Pierre (PERSON), Lison (PERSON)
        "org_1": Norwegian (ORG), Computing (ORG), Center(ORG)
        "org_2": Norwegian (ORG), Computing (ORG), Oslo (ORG)
        "place_2": Norwegian (NORP), Oslo (GPE)

    Overlaps:
        PERSON: 2 Overlaps / 3 Tokens = 0.66
        ORG: 3 Overlaps / 4 Tokens = 0.75
        NORP: 1 Overlap / 1 Token = 1.0
        GPE: 1 Overlap / 1 Token = 1.0
    """
    labels = ["O"]
    labels += [
        "%s-%s"%(p,l) for l in ["GPE", "NORP", "ORG", "PERSON"] for p in "BILU"
    ]
    lf_analysis = LFAnalysis(
        [analysis_doc],
        labels,
        strict_match=False
    )
    result = lf_analysis.label_overlap()
    assert result['overlap']['PERSON'] == 2/3
    assert result['overlap']['ORG'] == 3/4
    assert result['overlap']['NORP'] == 1.0
    assert result['overlap']['GPE'] == 1.0


def test_overlaps_without_strict_match_labels_without_prefixes(analysis_doc):
    """ Test expected overlaps across below spans:
  
    Spans:
        "name_1": Pierre (PERSON), Lison (PERSON), Pierre(PERSON)
        "name_2": Pierre (PERSON), Lison (PERSON)
        "org_1": Norwegian (ORG), Computing (ORG), Center(ORG)
        "org_2": Norwegian (ORG), Computing (ORG), Oslo (ORG)
        "place_2": Norwegian (NORP), Oslo (GPE)

    Overlaps:
        PERSON: 2 Overlaps / 3 Tokens = 0.66
        ORG: 3 Overlaps / 4 Tokens = 0.75
        NORP: 1 Overlap / 1 Token = 1.0
        GPE: 1 Overlap / 1 Token = 1.0
    """
    labels = ["O", "GPE", "NORP", "ORG", "PERSON"]
    lf_analysis = LFAnalysis(
        [analysis_doc],
        labels,
        strict_match=False
    )
    result = lf_analysis.label_overlap()
    assert result['overlap']['PERSON'] == 2/3
    assert result['overlap']['ORG'] == 3/4
    assert result['overlap']['NORP'] == 1.0
    assert result['overlap']['GPE'] == 1.0