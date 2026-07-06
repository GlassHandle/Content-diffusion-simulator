#include "montecarlo.hpp"
#include "propagation.hpp"
#include <algorithm>
#include <cmath>
using namespace std;

// confidence blend weights: floor + data history + distribution tightness
static constexpr double C_FLOOR = 0.20, C_DATA = 0.45, C_TIGHT = 0.35;

static double clamp01(double x) {
    return max(0.0, min(1.0, x));
}

SimOutput run_montecarlo(const SimContext& ctx) {
    const int N = max(1, ctx.config.runs);

    vector<long> reaches;
    reaches.reserve(N);

    vector<double> wave_sum;                  // per-wave mean audience
    vector<vector<long>> run_waves;           // every run's trajectory, for the bands
    run_waves.reserve(N);
    double reach_total = 0;
    double likes = 0, comments = 0, shares = 0, saves = 0, follows = 0;
    long viral = 0;

    for (int i = 0; i < N; ++i) {
        mt19937 rng(ctx.config.base_seed + static_cast<unsigned>(i));
        RunResult r = simulate_once(ctx, rng);
        reaches.push_back(r.total_reach);
        reach_total += static_cast<double>(r.total_reach);
        viral += r.went_viral ? 1 : 0;
        likes += r.likes; comments += r.comments; shares += r.shares;
        saves += r.saves; follows += r.follows;
        if (r.wave_sizes.size() > wave_sum.size()) wave_sum.resize(r.wave_sizes.size(), 0.0);
        for (size_t w = 0; w < r.wave_sizes.size(); w++) {
            wave_sum[w] += static_cast<double>(r.wave_sizes[w]);
        }
        run_waves.push_back(move(r.wave_sizes));
    }

    sort(reaches.begin(), reaches.end());
    auto pct = [&](double q) {
        return static_cast<double>(reaches[static_cast<size_t>(llround(q * (N - 1)))]);
    };

    SimOutput out;
    out.expected_reach = reach_total / N;
    out.reach_p10 = pct(0.10);
    out.reach_p50 = pct(0.50);
    out.reach_p90 = pct(0.90);
    out.viral_probability = static_cast<double>(viral) / N;

    double spread = (out.reach_p90 - out.reach_p10) / max(1.0, out.reach_p50);
    double data_conf = creator_data_confidence(ctx.creator);
    out.confidence = clamp01(C_FLOOR + C_DATA * data_conf + C_TIGHT / (1.0 + 0.5 * spread));

    out.mean_wave.resize(wave_sum.size());
    for (size_t w = 0; w < wave_sum.size(); ++w) {
        out.mean_wave[w] = wave_sum[w]/N;
    }

    // per-wave p10/p50/p90 across all runs (finished runs count as 0)
    const size_t W = wave_sum.size();
    out.wave_p10.resize(W);
    out.wave_p50.resize(W); 
    out.wave_p90.resize(W);
    
    vector<long> col(N);
    for (size_t w = 0; w < W; ++w) {
        for (int i = 0; i < N; ++i) {
            col[i] = w < run_waves[i].size() ? run_waves[i][w] : 0;
        }
        sort(col.begin(), col.end());
        out.wave_p10[w] = static_cast<double>(col[static_cast<size_t>(llround(0.10 * (N - 1)))]);
        out.wave_p50[w] = static_cast<double>(col[static_cast<size_t>(llround(0.50 * (N - 1)))]);
        out.wave_p90[w] = static_cast<double>(col[static_cast<size_t>(llround(0.90 * (N - 1)))]);
    }

    out.likes = likes/N;  
    out.comments = comments/N;  
    out.shares = shares/N;
    out.saves = saves / N;  
    out.follows = follows/N;
    return out;
}
