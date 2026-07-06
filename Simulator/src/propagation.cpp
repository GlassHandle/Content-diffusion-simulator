#include "propagation.hpp"
#include "engagement.hpp"
#include <cmath>
#include <algorithm>

using namespace std;

namespace {
constexpr int    SAMPLE_N   = 600;    // viewers engaged per wave
constexpr double R_GAIN     = 4.5;    // to convert distribution score reproduction number
constexpr double FLOOR      = 0.86;   // freshness factor of the content
constexpr double BETA0      = 5.0;    // wave-0 targeting the target audience
constexpr double BETA_DECAY = 0.5;    // beta *= this each wave -> toward population avg

constexpr double W_WATCH = 0.35, W_LIKE = 0.15, W_COMMENT = 0.15, W_SHARE = 0.25, W_SAVE = 0.10;

// intent to like is generally more than observed action
constexpr double OBS_LIKE = 1.0, OBS_COMMENT = 0.15, OBS_SHARE = 0.5, OBS_SAVE = 1.0, OBS_FOLLOW = 0.12;

// RPP->reach per post, FLW->followers, MOM->momentum
constexpr double SEED_BASE = 300, SEED_RPP = 40.0, SEED_FLW = 5.0, SEED_MOM = 200.0;
constexpr double SEED_CAP_FRAC = 0.10;
constexpr double FAV_MOM = 0.30;

// mean-one lognormal multiplier: always positive and E[m] = 1 for ANY sigma.
double lognormal_mult(mt19937& rng, double sigma) {
    normal_distribution<double> n(-0.5 * sigma * sigma, sigma);
    return exp(n(rng));
}

struct Mechanics {
    double seed_size, algo_favorability, consistency;
};

// driving mechanics from L2 data
Mechanics derive_mechanics(const Creator& c, long pool) {
    Mechanics m;
    double data_conf = creator_data_confidence(c);
    double reach_per_post = c.monthly_reach / max(1.0, c.posting_freq);
    double aq = 0.25 + 0.75 * c.audience_quality / 100.0;
    double raw = SEED_BASE + SEED_RPP*sqrt(max(0.0,reach_per_post)) + SEED_FLW*sqrt(max(0.0,c.followers))*aq + SEED_MOM*(c.momentum/100.0);
    double cap = SEED_CAP_FRAC * static_cast<double>(pool);

    // for small x tanh(x) ~ x but for large x tanh(x) ~ 1 therefore caps larger creators 
    m.seed_size = cap > 0 ? cap * tanh(raw / cap) : raw;
    m.algo_favorability = 0.6 + 0.6*(c.trust/100.0) + 0.3*(c.niche_authority/100.0) + 0.3*(c.audience_quality/100.0) + FAV_MOM*data_conf*(c.momentum-50.0)/100.0;
    m.consistency = data_conf * (1.0-c.volatility/100.0) + (1.0-data_conf)*0.3;
    return m;
}

// determines how much a persona should affect the current wave while engage detemine the actual engagement
double content_fit(const Persona& p, const Content& c) {
    double in_num = 0, in_den = 0;
    for (int t = 0; t < NTOPICS; ++t) {
        in_num += p.interests[t] * c.topics[t];
        in_den += c.topics[t];
    }
    double interest = in_den>0 ? in_num/in_den : 0.0;

    double af_num = 0, af_den = 0;
    for (int d = 0; d < NDIMS; ++d) {
        af_num += p.affinity[d] * c.dims[d];
        af_den += c.dims[d];
    }
    double affinity = af_den>0 ? af_num / af_den : 0.0;

    return 0.6*interest + 0.4*affinity;
}

double distribution_score(const EngagementResult& e) {
    return W_WATCH*e.watch + W_LIKE*e.like + W_COMMENT*e.comment + W_SHARE*e.share + W_SAVE*e.save;
}
} 

double creator_data_confidence(const Creator& c) {
    return min(1.0, (log1p(c.followers) / 14.0 + log1p(c.monthly_reach) / 17.0) / 2.0);
}

RunResult simulate_once(const SimContext& ctx, mt19937& rng) {
    const auto& P = ctx.personas;
    const long pool = static_cast<long>(P.size());
    const Mechanics mech = derive_mechanics(ctx.creator, pool);

    // variance, more consistency lower variance
    const double sigma = 0.15 + 0.6 * (1.0 - mech.consistency);

    // creates a uniform int distribution of range [0,pool-1]
    uniform_int_distribution<long> pick(0, max<long>(0, pool - 1));

    RunResult res;
    if (pool <= 0) return res;

    const double luck_sigma = 0.30 + 0.25*(1.0-mech.consistency);
    const double luck = lognormal_mult(rng, luck_sigma);

    double wave = mech.seed_size * lognormal_mult(rng, sigma);
    long cumulative = 0;
    double beta = BETA0;

    for (int w = 0; w < ctx.config.max_waves; w++) {
        long shown = llround(wave);
        shown = min<long>(shown, pool-cumulative);          
        if (shown<ctx.config.min_wave) break;              

        // fit-weighted average engagement of this wave's sampled viewers
        double num = 0, den = 0;
        double w_like = 0, w_comment = 0, w_share = 0, w_save = 0, w_follow = 0;
        int n = static_cast<int>(min<long>(SAMPLE_N, shown));
        for (int s=0; s<n; ++s) {
            const Persona& p = P[pick(rng)];
            double f  = content_fit(p, ctx.content);
            EngagementResult e = engage(p, ctx.content, ctx.trend);

            // high fit content has more weight so it dominates
            double wgt = exp(beta * f);
            num += wgt * distribution_score(e);
            den += wgt;
            w_like += wgt * e.like;  
            w_comment += wgt * e.comment;
            w_share += wgt * e.share; 
            w_save += wgt * e.save; 
            w_follow += wgt * e.follow;
        }

        // fit weighted average distribution score
        double rate = den>0 ? num/den : 0.0;

        // converting the intent action to observed action and estimating it for whole wave (multiplying by shown)
        if (den>0) {                   
            res.likes += shown * OBS_LIKE * w_like / den;
            res.comments += shown * OBS_COMMENT * w_comment / den;
            res.shares += shown * OBS_SHARE * w_share / den;
            res.saves += shown * OBS_SAVE * w_save / den;
            res.follows += shown * OBS_FOLLOW * w_follow / den;
        }

        res.wave_sizes.push_back(shown);
        cumulative += shown;
        if (cumulative >= pool) break;

        // R:reproduction number i.e each viewer generates R viewer in the next wave
        double R = R_GAIN*rate*mech.algo_favorability*luck*lognormal_mult(rng, sigma);
        // with each wave freshness decreases exponentially 
        double freshness = pow(FLOOR, w);
        wave = shown * R * freshness;

        // beta decays with each wave i.e earlier wave have higher weights for targeted audience
        beta *= BETA_DECAY;                                    
    }

    res.total_reach = cumulative;
    res.went_viral  = res.total_reach > static_cast<long>(ctx.config.viral_threshold * pool);
    return res;
}
