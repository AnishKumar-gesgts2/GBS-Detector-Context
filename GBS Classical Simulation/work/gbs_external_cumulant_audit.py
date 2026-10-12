"""Reproduce independent/vacuum-limit checks of the supplied implementation.

Only the inspected piecewise_zero_probability function is extracted; importing
or executing the external benchmark's main program is unnecessary.
"""
import argparse
import ast
import hashlib
import itertools
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.read_text(encoding='utf-8')
    tree = ast.parse(source)
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'piecewise_zero_probability')
    namespace = {'itertools': itertools}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(args.source), 'exec'), namespace)
    checks = []
    for name, singles in [('vacuum', [1.0, 1.0]), ('independent', [0.8, 0.7])]:
        cumulants = {(0,): 2*singles[0]-1, (1,): 2*singles[1]-1, (0, 1): 0.0}
        joint, denominator = namespace['piecewise_zero_probability']([0], cumulants, singles, 3)
        implemented = joint/denominator
        checks.append({'case': name, 'expected_second_no_click': singles[1],
                       'implemented_second_no_click': implemented,
                       'absolute_error': abs(implemented-singles[1])})
    assert all(abs(row['absolute_error']-0.5) < 1e-12 for row in checks)
    report = {'scope': 'deterministic limit tests of the supplied function; no corrected implementation or benchmark rerun',
              'source_basename': args.source.name, 'source_sha256_lf': hashlib.sha256(source.replace('\r\n', '\n').encode()).hexdigest(),
              'function_line': function.lineno, 'checks': checks,
              'decision': 'the supplied implementation fails vacuum and independent limits; published-baseline fidelity and method rejection are unsupported'}
    out = Path(__file__).resolve().parents[1]/'outputs'/'bounded_context_screen_v1'
    out.mkdir(parents=True, exist_ok=True)
    (out/'supplied_implementation_audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
