#include "loaders.hpp"
#include "third_party/json.hpp"
#include <fstream>
#include <stdexcept>
#include <unordered_map>

using json = nlohmann::json;

// maps interests and affinities to their index
static unordered_map<string, int> name_index(const char* const* names, int n) {
    unordered_map<string, int> m;
    for (int i=0;i<n;++i){
        m[names[i]] = i;
    }
    return m;
}
static const unordered_map<string, int> DIM_IDX = name_index(DIM_NAMES, NDIMS);
const unordered_map<string, int> TOPIC_IDX = name_index(TOPIC_NAMES, NTOPICS);

static double num(const json& j, const char* key, double def=0.0) {
    auto it = j.find(key);
    return (it != j.end() && it->is_number()) ? it->get<double>() : def;
}

// parses json
static json open_json(const string& path, const char* what) {
    ifstream f(path);
    if (!f){
        throw runtime_error(string("cannot open ")+what+" file: " + path);
    }
    json j;
    f >> j;
    return j;
} 

vector<Persona> load_personas(const string& path) {
    ifstream f(path);
    if (!f){
        throw runtime_error("cannot open personas file: "+path);
    }

    vector<Persona> output;
    output.reserve(51000);
    string line;
    while (getline(f, line)) {
        if (line.find_first_not_of(" \t\r") == string::npos) continue;
        json j = json::parse(line);

        Persona p;
        p.id = j.value("id", "");
        if (j.contains("demographics")) {
            const json& d=j["demographics"];
            p.age = static_cast<int>(num(d, "age"));
            p.age_band = d.value("age_band", "");
            p.sex = d.value("sex", "");
            p.region = d.value("region", "");
        }
        if (j.contains("affinities"))
            for (auto& [k, v]:j["affinities"].items()) {
                auto it=DIM_IDX.find(k);
                if (it != DIM_IDX.end() && v.is_number()){
                    p.affinity[it->second] = v.get<double>();
                }
            }
        if (j.contains("propensities")) {
            const json& pr = j["propensities"];
            p.retention = num(pr, "retention");
            p.like = num(pr, "like");
            p.comment = num(pr, "comment");
            p.share = num(pr, "share");
            p.save = num(pr, "save");
            p.follow = num(pr, "follow");
        }
        p.trend_susceptibility = num(j, "trend_susceptibility");
        p.activity = num(j, "activity", 0.5);
        if (j.contains("interests"))
            for (auto& [k, v] : j["interests"].items()) {
                auto it = TOPIC_IDX.find(k);
                if (it != TOPIC_IDX.end() && v.is_number()){
                    p.interests[it->second] = v.get<double>();
                }
            }
        output.push_back(move(p));
    }
    if (output.empty()){
        throw runtime_error("personas file has no records: " + path);
    }
    return output;
}

Content load_content(const string& path) {
    json j = open_json(path, "content");

    Content c;
    c.content_id = j.value("username", j.value("content_id", ""));
    c.modality = j.value("modality", "");
    if (j.contains("dims"))
        for (auto& [k, v] : j["dims"].items()) {
            auto it = DIM_IDX.find(k);
            if (it != DIM_IDX.end() && v.is_number()) c.dims[it->second] = v.get<double>();
        }
    if (j.contains("composites")) {
        c.shareability = num(j["composites"], "shareability");
        c.saveability  = num(j["composites"], "saveability");
    }
    if (j.contains("topics"))
        for (auto& [k, v] : j["topics"].items()) {
            auto it = TOPIC_IDX.find(k);
            if (it != TOPIC_IDX.end() && v.is_number()) c.topics[it->second] = v.get<double>();
        }
    if (j.contains("entities"))
        for (const json& e : j["entities"]) {
            if (e.is_string()) c.entities.push_back(e.get<string>());
            else if (e.is_object()) {
                for (const char* key : {"label", "name", "entity"})
                    if (e.contains(key) && e[key].is_string()) {
                        c.entities.push_back(e[key].get<string>());
                        break;
                    }
            }
        }
    if (j.contains("tags"))
        for (const json& t : j["tags"])
            if (t.is_string()) c.tags.push_back(t.get<string>());
    return c;
}

Trend load_trend(const string& path) {
    json j = open_json(path, "trend snapshot");

    Trend t;
    if (j.contains("topic_trends"))
        for (auto& [k, v] : j["topic_trends"].items()) {
            auto it = TOPIC_IDX.find(k);
            if (it != TOPIC_IDX.end() && v.is_number()) t.topic_trends[it->second] = v.get<double>();
        }
    if (j.contains("trending_entities"))
        for (const json& e : j["trending_entities"])
            if (e.is_object() && e.contains("label"))
                t.entities.emplace_back(e["label"].get<string>(), num(e, "weight"));
    if (j.contains("tag_trends"))
        for (auto& [name, v] : j["tag_trends"].items())
            if (v.is_number()) t.tag_trends.emplace_back(name, v.get<double>());
    return t;
}

Creator load_creator(const string& path) {
    json j = open_json(path, "creator");

    Creator c;
    if (j.contains("scores")) {
        const json& s = j["scores"];
        c.trust = num(s, "creator_trust_score", 50.0);
        c.momentum = num(s, "creator_momentum_score");
        c.niche_authority = num(s, "niche_authority_score");
        c.audience_quality = num(s, "audience_quality_score", 50.0);
        c.volatility = num(s, "creator_volatility_score");
    }
    if (j.contains("raw_metrics")) {
        // find net mertices from both platforms
        double er_num = 0, fr_num = 0, den = 0;
        for (auto& [platform, m] : j["raw_metrics"].items()) {
            (void)platform;
            if (!m.is_object() || m.empty()) continue;
            double followers = num(m, "followers");
            c.followers += followers;
            c.monthly_reach += num(m, "monthly_reach");
            er_num += num(m, "avg_engagement_rate") * max(followers, 1.0);
            fr_num += num(m, "posting_freq_monthly") * max(followers, 1.0);
            den += max(followers, 1.0);
        }
        if (den > 0) c.avg_engagement_rate = er_num / den;
        if (den > 0 && fr_num > 0) c.posting_freq = fr_num / den; 
    }
    return c;
}
