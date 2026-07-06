#include "engagement.hpp"
#include <algorithm>
#include <cctype>
#include <vector>
using namespace std;

// for personas
static constexpr double G_BASE  = 0.25;  // base value
static constexpr double G_INT   = 0.45;  // interest weight
static constexpr double G_POS   = 0.40;  // positive affinity match weight
static constexpr double G_NEG   = 0.50;  // negative affinity match weight
static constexpr double G_TREND = 0.25;  // trends match weight

static constexpr int D_EDUCATIONAL = 2, D_CONTROVERSY = 4, D_EMOTIONAL = 5, D_PRACTICAL = 7;

static double clamp01(double x){
     return max(0.0, min(1.0, x)); 
}

// breaks string into words
static vector<string> tokenize(const string& s) {
    vector<string> output;
    string curr="";
    for (char ch : s) {
        if (isalnum(static_cast<unsigned char>(ch))) curr += static_cast<char>(tolower(static_cast<unsigned char>(ch)));
        else if (!curr.empty()){
            output.push_back(curr);
            curr.clear();
        }
    }
    if (!curr.empty()) output.push_back(curr);
    return output;
}

// Jaccard similarity between words (|intersection|/|union|)
static double token_jaccard(const vector<string>& a, const vector<string>& b) {
    if (a.empty() || b.empty()) return 0.0;
    int inter = 0;
    for (const string& x : a)
        if (find(b.begin(), b.end(), x) != b.end()) ++inter;
    int uni=static_cast<int>(a.size() + b.size())-inter;
    return uni > 0 ? static_cast<double>(inter)/uni : 0.0;
}

// find best similar trend with threshold Jaccard similarity of 0.5 or either one is a subtring of another
static double best_match_weight(const string& s, const vector<pair<string, double>>& cands) {
    vector<string> st = tokenize(s);
    double best = 0;
    for (const auto& [label, weight] : cands) {
        vector<string> lt = tokenize(label);
        double sim = token_jaccard(st, lt);
        bool contained = !st.empty() && !lt.empty() &&
            (search(st.begin(), st.end(), lt.begin(), lt.end()) != st.end() ||
             search(lt.begin(), lt.end(), st.begin(), st.end()) != lt.end());
        if (sim >= 0.5 || contained) best = max(best, weight);
    }
    return best;
}

double compute_trend_alignment(const Content& c, const Trend& t) {
    constexpr double W_TOPIC = 0.60, W_ENTITY = 0.25, W_TAG = 0.15;

    // weighted average of trendiness
    double num = 0, den = 0;
    for (int i = 0; i<NTOPICS; ++i) {
        num += c.topics[i] * t.topic_trends[i];
        den += c.topics[i];
    }
    double topic = den>0 ? num/den : 0.0;

    // entity alignment
    double entity = 0;
    for (const string& ce : c.entities){
        entity += best_match_weight(ce, t.entities);
    }
    entity = min(1.0, entity);

    // tags alignment
    double tag = 0;
    for (const string& tg : c.tags){
        tag += max(best_match_weight(tg, t.tag_trends), best_match_weight(tg, t.entities));
    }
    tag = min(1.0, tag);

    return clamp01(W_TOPIC * topic + W_ENTITY * entity + W_TAG * tag);
}

EngagementResult engage(const Persona& p, const Content& c, const Trend& t) {
    // normalise dims quality of content to [0,1]
    double qsum=0;
    for (int d = 0; d<NDIMS; ++d){
        qsum += c.dims[d];
    }
    double quality = qsum / (NDIMS * 10.0);

    // for the persona calculate a weighted average affinity to content
    double mnum = 0, mden = 0;
    for (int d = 0; d < NDIMS; ++d) {
        double w = c.dims[d]/10.0;
        mnum += w * p.affinity[d];
        mden += w;
    }
    double match = mden>0 ? mnum/mden : 0.0;

    // for the persona calculate a weighted average interest to content's topics
    double inum = 0, iden = 0;
    for (int i = 0; i < NTOPICS; i++) { 
        inum += c.topics[i] * p.interests[i];
        iden += c.topics[i]; 
    }
    double interest = iden>0 ? inum/iden : 0.0;

    double trend = t.content_alignment * p.trend_susceptibility;

    double gate = G_BASE + G_INT*interest + G_POS*max(0.0, match) + G_NEG*min(0.0, match) + G_TREND*trend;

    // weak content caps engagement
    double pull = clamp01(quality * max(0.0, gate));

    double watch = pull * (0.35 + 0.65 * p.retention) * (0.75 + 0.25 * p.activity);
    double provoke = (c.dims[D_CONTROVERSY] + c.dims[D_EMOTIONAL]) / 20.0;  
    double useful  = (c.dims[D_EDUCATIONAL] + c.dims[D_PRACTICAL]) / 20.0;  

    EngagementResult e;
    e.watch = watch;
    e.like = watch * p.like * (0.55 + 0.45*pull);
    e.comment = watch * p.comment * (0.30 + 0.70*provoke);
    e.share = min(1.0,watch * p.share * (0.15 + 0.85*c.shareability/10.0) * (1.0 + 0.5*trend));
    e.save = watch * p.save * (0.15 + 0.85*c.saveability/10.0) * (0.50+0.50*useful);
    e.follow = watch * p.follow * pull;
    return e;
}
