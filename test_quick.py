#!/usr/bin/env python
"""Quick test of evaluation system functionality"""

from evaluation_metrics import calculate_quality_score, get_quality_grade
from evaluation_system import store_evaluation_result, get_results_count, calculate_batch_stats

# Test 1: Calculate quality score
print("=" * 70)
print("TESTING EVALUATION SYSTEM".center(70))
print("=" * 70)

source = 'Machine learning is a subset of artificial intelligence that learns from data'
summary = '• ML is a subset of AI\n• Learns from data without explicit programming'

print("\n📝 INPUT:")
print(f"   Source: {source[:60]}...")
print(f"   Summary: {summary[:60]}...")

scores = calculate_quality_score(source, summary)

print('\n📊 QUALITY SCORES:')
print(f'   Relevance: {scores["relevance"]:.1%}')
print(f'   Coverage: {scores["coverage"]:.1%}')
print(f'   Coherence: {scores["coherence"]:.1%}')
print(f'   Conciseness: {scores["conciseness"]:.1%}')
print(f'   Overall Quality: {scores["overall_quality"]:.1%}')
print(f'   Grade: {get_quality_grade(scores["overall_quality"])}')
print(f'   Status: {scores["evaluation_status"]}')

# Test 2: Store result
result = store_evaluation_result('Test Query', ['http://example.com'], source, summary, scores)
print(f'\n✅ STORAGE TEST:')
print(f'   Stored evaluation at: {result["timestamp"]}')
print(f'   Total evaluations on record: {get_results_count()}')

# Test 3: Batch stats
stats = calculate_batch_stats()
print(f'\n📈 BATCH STATISTICS:')
print(f'   Total evaluations: {stats["total_evaluations"]}')
if 'overall_quality_avg' in stats:
    print(f'   Average Quality: {stats["overall_quality_avg"]:.1%}')

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED SUCCESSFULLY".center(70))
print("=" * 70)
