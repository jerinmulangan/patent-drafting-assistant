#!/usr/bin/env python3
"""
Test script to verify document-level aggregation of chunk-level search results.
"""

import sys
from search_service import (
    SearchRequest, SearchResult, ChunkDetail, 
    aggregate_chunk_results_by_document, compute_hybrid_score
)


def test_compute_hybrid_score():
    """Test hybrid score computation."""
    print("Testing compute_hybrid_score()...")
    
    # Test case 1: Perfect match
    score = compute_hybrid_score(1.0, 1.0)
    assert score == 1.0, f"Expected 1.0, got {score}"
    print(f"  ✓ Perfect match: {score}")
    
    # Test case 2: Max score higher than avg
    score = compute_hybrid_score(0.9, 0.7)
    expected = (0.9 * 0.7) + (0.7 * 0.3)
    assert abs(score - expected) < 0.001, f"Expected {expected}, got {score}"
    print(f"  ✓ Max > Avg: {score} (expected {expected})")
    
    # Test case 3: Zero scores
    score = compute_hybrid_score(0.0, 0.0)
    assert score == 0.0, f"Expected 0.0, got {score}"
    print(f"  ✓ Zero scores: {score}")
    
    print("✓ compute_hybrid_score tests passed!\n")


def test_aggregation():
    """Test document aggregation."""
    print("Testing aggregate_chunk_results_by_document()...")
    
    # Create mock chunk-level results for the same document
    chunks = [
        SearchResult(
            doc_id="US123456A_chunk_0",
            score=0.89,
            title="Smart Device System",
            doc_type="grant",
            source_file="grants.jsonl",
            snippet="Smart device with AI capabilities",
            base_doc_id="US123456A",
            chunk_count=1
        ),
        SearchResult(
            doc_id="US123456A_chunk_1",
            score=0.81,
            title="Smart Device System",
            doc_type="grant",
            source_file="grants.jsonl",
            snippet="Machine learning for device control",
            base_doc_id="US123456A",
            chunk_count=1
        ),
        SearchResult(
            doc_id="US123456A_chunk_2",
            score=0.75,
            title="Smart Device System",
            doc_type="grant",
            source_file="grants.jsonl",
            snippet="Neural network implementation",
            base_doc_id="US123456A",
            chunk_count=1
        ),
        SearchResult(
            doc_id="US654321B_chunk_0",
            score=0.72,
            title="IoT Platform",
            doc_type="application",
            source_file="applications.jsonl",
            snippet="IoT connectivity framework",
            base_doc_id="US654321B",
            chunk_count=1
        ),
    ]
    
    # Aggregate
    result = aggregate_chunk_results_by_document(chunks)
    
    print(f"  Input: {len(chunks)} chunks")
    print(f"  Output: {len(result)} documents")
    
    # Verify
    assert len(result) == 2, f"Expected 2 documents, got {len(result)}"
    
    # Check first document (US123456A)
    doc1 = result[0]
    assert doc1.doc_id == "US123456A", f"Expected US123456A, got {doc1.doc_id}"
    assert doc1.max_score == 0.89, f"Expected max_score=0.89, got {doc1.max_score}"
    assert abs(doc1.avg_score - (0.89 + 0.81 + 0.75) / 3) < 0.001, "avg_score mismatch"
    assert doc1.chunk_count == 3, f"Expected 3 chunks, got {doc1.chunk_count}"
    
    expected_hybrid = (0.89 * 0.7) + (((0.89 + 0.81 + 0.75) / 3) * 0.3)
    assert abs(doc1.score - expected_hybrid) < 0.001, f"Hybrid score mismatch: {doc1.score} vs {expected_hybrid}"
    
    print(f"  ✓ Document 1 (US123456A):")
    print(f"      - max_score: {doc1.max_score}")
    print(f"      - avg_score: {doc1.avg_score:.3f}")
    print(f"      - hybrid_score: {doc1.score:.3f}")
    print(f"      - chunk_count: {doc1.chunk_count}")
    print(f"      - chunk_details: {len(doc1.chunk_details)}")
    
    # Check second document (US654321B)
    doc2 = result[1]
    assert doc2.doc_id == "US654321B", f"Expected US654321B, got {doc2.doc_id}"
    assert doc2.max_score == 0.72, f"Expected max_score=0.72, got {doc2.max_score}"
    assert doc2.chunk_count == 1, f"Expected 1 chunk, got {doc2.chunk_count}"
    
    print(f"  ✓ Document 2 (US654321B):")
    print(f"      - max_score: {doc2.max_score}")
    print(f"      - avg_score: {doc2.avg_score:.3f}")
    print(f"      - hybrid_score: {doc2.score:.3f}")
    print(f"      - chunk_count: {doc2.chunk_count}")
    
    # Verify sorting (should be sorted by hybrid score descending)
    assert result[0].score >= result[1].score, "Results not sorted by hybrid score"
    print(f"  ✓ Results sorted by hybrid score descending")
    
    # Verify chunk details
    assert len(doc1.chunk_details) == 3, f"Expected 3 chunk details, got {len(doc1.chunk_details)}"
    assert doc1.chunk_details[0].chunk_id == "US123456A_chunk_0", "Chunks not sorted by score"
    assert doc1.chunk_details[0].chunk_score == 0.89, "Chunk score mismatch"
    print(f"  ✓ Chunk details correctly attached and sorted")
    
    print("✓ aggregation tests passed!\n")


def test_search_result_to_dict():
    """Test SearchResult.to_dict() with aggregation data."""
    print("Testing SearchResult.to_dict() with aggregation...")
    
    chunk1 = ChunkDetail(
        chunk_id="US123456A_chunk_0",
        chunk_score=0.89,
        chunk_snippet="Test snippet"
    )
    
    result = SearchResult(
        doc_id="US123456A",
        score=0.85,
        title="Test Patent",
        doc_type="grant",
        source_file="test.jsonl",
        base_doc_id="US123456A",
        chunk_details=[chunk1],
        max_score=0.89,
        avg_score=0.82,
        chunk_count=2
    )
    
    data = result.to_dict()
    
    assert data["doc_id"] == "US123456A", "doc_id mismatch"
    assert data["max_score"] == 0.89, "max_score mismatch"
    assert data["avg_score"] == 0.82, "avg_score mismatch"
    assert data["chunk_count"] == 2, "chunk_count mismatch"
    assert len(data["chunk_details"]) == 1, "chunk_details length mismatch"
    assert data["chunk_details"][0]["chunk_id"] == "US123456A_chunk_0", "chunk detail mismatch"
    
    print(f"  ✓ to_dict() produces correct structure")
    print(f"  ✓ chunk_details serialized correctly")
    print("✓ to_dict tests passed!\n")


if __name__ == "__main__":
    try:
        test_compute_hybrid_score()
        test_aggregation()
        test_search_result_to_dict()
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nDocument-level aggregation is working correctly!")
        print("\nKey features verified:")
        print("  • Chunks grouped by document_id")
        print("  • Hybrid scores computed (0.7 * max + 0.3 * avg)")
        print("  • Documents sorted by hybrid score")
        print("  • Chunk details preserved and sorted by score")
        print("  • Data serializable to JSON via to_dict()")
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
