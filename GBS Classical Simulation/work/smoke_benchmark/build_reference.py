"""Generate reference-side forced paths from the pinned author's sampler.

Sampling still calls the unmodified original generate_samples. This derived
function is used only to score its exact induced small-system distribution.
MIT license and original provenance accompany the generated local include.
"""
import argparse
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--frugal',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
source=(args.frugal/'include/fgbs/cpu/cpu_sampler.hpp').read_text()
start=source.index('template<usize N, typename T>\nSampleResult<N, T> generate_sample(')
end=source.index('\ntemplate<usize N>\nResult<std::vector<Bitstring<N>>> generate_samples',start)
function=source[start:end]
old='SampleResult<N, T> generate_sample('
assert function.count(old)==1
function=function.replace(old,'double reference_path(')
old='T* FGBS_INTERNAL_RESTRICT double_elided_marginal_arr) {'
assert function.count(old)==1
function=function.replace(old,'T* FGBS_INTERNAL_RESTRICT double_elided_marginal_arr, std::uint64_t forced) {')
function=function.replace('SampleResult<N, T> result{};','double path_probability=1.0;')
old='update_result<N>(rand, result, prev_prob, parity_arr, i, zero_next_prob);'
assert function.count(old)==1
function=function.replace(old,'''
        const auto pzero=clamped_prob(zero_next_prob/prev_prob);
        const auto clicked=(forced>>i)&1;
        path_probability*=clicked?1-pzero:pzero;
        if(path_probability==0) return 0;
        parity_arr[i]=clicked?-get_half<T>():get_half<T>();
        prev_prob=clicked?prev_prob-zero_next_prob:zero_next_prob;
''')
function=function.replace('return result;','return path_probability;')
license=(args.frugal/'LICENSE.md').read_text()
header='/* Derived solely for reference scoring from FrugalGBS cpu_sampler.hpp.\n'+license+'\n*/\n'
args.output.write_text(header+'namespace fgbs { namespace cpu {\n#define FGBS_INTERNAL_RESTRICT __restrict__\n'+function+'\n#undef FGBS_INTERNAL_RESTRICT\n}}\n')
print('Generated reference-only forced-path evaluator; original sampling unchanged.')
