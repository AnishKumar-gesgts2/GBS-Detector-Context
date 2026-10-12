// Thin C interface to the unmodified MIT-licensed FrugalGBS CPU implementation.
// Original implementation: https://github.com/tomdodd4598/FrugalGBS
#include "fgbs/data.hpp"
#include "fgbs/sampler.hpp"
#include <chrono>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <cstring>
#include <memory>
using namespace fgbs;
#include "fgbs_reference.inc"
static std::string last_error;
struct Base {
    virtual ~Base() = default;
    virtual void samples(std::size_t, unsigned, std::uint64_t*) = 0;
    virtual std::size_t coefficients(std::uint64_t*, double*) = 0;
    virtual void probabilities(double*) = 0;
};
template<std::size_t N> struct Model : Base {
    std::unique_ptr<BitstringLayout<N>> layout;
    SamplingTarget<N> target;
    Model(int order, const double* v, double* times) {
        auto t0 = std::chrono::steady_clock::now();
        auto lr = generate_bitstring_layout<N>(order);
        if (!lr.ok()) throw std::runtime_error(lr.error());
        layout = std::make_unique<BitstringLayout<N>>(std::move(lr.value()));
        auto cr = generate_cumulant_layout<N>(order);
        if (!cr.ok()) throw std::runtime_error(cr.error());
        auto t1 = std::chrono::steady_clock::now();
        Matrix<double> cov(2*N, 2*N);
        for (std::size_t i=0;i<2*N;++i) for(std::size_t j=0;j<2*N;++j) cov(i,j)=2*v[i*2*N+j];
        auto sr=generate_sampling_target<N>(*layout,cr.value(),cov);
        if(!sr.ok()) throw std::runtime_error(sr.error());
        target=std::move(sr.value());
        auto t2=std::chrono::steady_clock::now();
        times[0]=std::chrono::duration<double>(t1-t0).count();
        times[1]=std::chrono::duration<double>(t2-t1).count();
    }
    void samples(std::size_t count,unsigned seed,std::uint64_t* out) override {
        auto sr=generate_samples<N>(*layout,target,count,seed);
        if(!sr.ok()) throw std::runtime_error(sr.error());
        const auto& values=sr.value();
        for(std::size_t j=0;j<count;++j) {
            std::uint64_t bits=0;
            for(std::size_t i=0;i<N;++i) if(get_bit<N>(values[j],i)) bits|=(std::uint64_t(1)<<i);
            out[j]=bits;
        }
    }
    std::size_t coefficients(std::uint64_t* masks,double* values) override {
        if(masks && values) for(std::size_t j=0;j<layout->len;++j) {
            std::uint64_t bits=0;
            for(std::size_t i=0;i<N;++i) if(get_bit<N>(layout->layout_bitstring_vec[j],i)) bits|=(std::uint64_t(1)<<i);
            masks[j]=bits; values[j]=target.correlator_cumulant_vec[j];
        }
        return layout->len;
    }
    void probabilities(double* out) override {
        if constexpr(N<=16) {
            cpu::UniformRandom<cpu::Prob> random(1,0.0,1.0);
            std::vector<cpu::Prob> a(cpu::partial_marginal_arr_size<N>());
            std::vector<cpu::Prob> b(cpu::elided_marginal_arr_size<N>());
            std::vector<cpu::Prob> c(cpu::partial_elided_marginal_arr_size<N>());
            std::vector<cpu::Prob> d(cpu::double_elided_marginal_arr_size<N>());
            for(std::uint64_t bits=0;bits<(std::uint64_t(1)<<N);++bits)
                out[bits]=cpu::reference_path<N,cpu::Prob>(*layout,target,random,a.data(),b.data(),c.data(),d.data(),bits);
        } else throw std::runtime_error("Full enumeration restricted to reference sizes");
    }
};
extern "C" {
__declspec(dllexport) void* fb_prepare(int modes,int order,const double* v,double* times) {
    try {
        omp_set_num_threads(1);
        switch(modes) {
            case 2:return new Model<2>(order,v,times); case 3:return new Model<3>(order,v,times);
            case 6:return new Model<6>(order,v,times); case 8:return new Model<8>(order,v,times);
            case 10:return new Model<10>(order,v,times); case 12:return new Model<12>(order,v,times);
            case 16:return new Model<16>(order,v,times); case 24:return new Model<24>(order,v,times);
            case 32:return new Model<32>(order,v,times);
        }
        throw std::runtime_error("Unsupported mode count in smoke bridge");
    } catch(const std::exception& e) {last_error=e.what(); return nullptr;}
}
__declspec(dllexport) int fb_sample(void* p,std::size_t shots,unsigned seed,std::uint64_t* out) {
    try {static_cast<Base*>(p)->samples(shots,seed,out);return 0;}
    catch(const std::exception& e){last_error=e.what();return -1;}
}
__declspec(dllexport) std::size_t fb_coefficients(void* p,std::uint64_t* masks,double* values) {
    return static_cast<Base*>(p)->coefficients(masks,values);
}
__declspec(dllexport) void fb_free(void* p) {delete static_cast<Base*>(p);}
__declspec(dllexport) int fb_probabilities(void* p,double* out) {
    try {static_cast<Base*>(p)->probabilities(out);return 0;}
    catch(const std::exception& e){last_error=e.what();return -1;}
}
__declspec(dllexport) const char* fb_error() {return last_error.c_str();}
}
