#pragma once
#include <string>
#include <vector>
#include <array>
#include <utility>
using namespace std;

// personas affinities
constexpr int NDIMS   = 8;
inline constexpr const char* DIM_NAMES[NDIMS] = {
    "humor", "curiosity", "educational", "novelty",
    "controversy", "emotional_intensity", "relatability", "practical_value"
};

// personas interests
constexpr int NTOPICS = 24;
inline constexpr const char* TOPIC_NAMES[NTOPICS] = {
    "comedy", "gaming", "tech", "fitness", "food_cooking", "beauty_fashion",
    "travel", "music", "sports", "education_howto", "news_politics",
    "finance_business", "art_design", "science", "lifestyle_vlog",
    "parenting_family", "pets_animals", "automotive", "diy_crafts",
    "motivation_selfhelp", "relationships", "nature_outdoors", "film_tv",
    "health_wellness"
};


struct Persona {
    string id;
    int age = 0;
    string age_band, sex, region;
    array<double, NDIMS> affinity{};               
    double retention = 0, like = 0, comment = 0, share = 0, save = 0, follow = 0;             
    double trend_susceptibility = 0, activity = 0;
    array<double, NTOPICS> interests{};
};

// from context_engine (+ tags typed by the creator in the upload form)
struct Content {
    string content_id, modality;
    array<double, NDIMS> dims{};
    double shareability = 0, saveability = 0;
    array<double, NTOPICS> topics{};
    vector<string> entities;
    vector<string> tags;      
};

// from trend_engine
struct Trend {
    array<double, NTOPICS> topic_trends{};
    vector<pair<string, double>> entities;
    vector<pair<string, double>> tag_trends;  
    double content_alignment = 0;
};

// from user_engine
struct Creator {
    double trust = 50, momentum = 0, niche_authority = 0, audience_quality = 50, volatility = 0;
    double followers = 0, monthly_reach = 0, avg_engagement_rate = 0;
    double posting_freq = 8.0;  
};

// Simulation Configs
struct Config {
    int runs = 5000;   // Monte Carlo iterations
    int max_waves = 14;
    int min_wave = 20;  // smallest wave size
    double viral_threshold = 0.3;   
    unsigned base_seed = 42;
};

struct SimContext {
    const vector<Persona>& personas;
    const Content& content;
    const Trend& trend;
    const Creator& creator;
    const Config& config;
};
