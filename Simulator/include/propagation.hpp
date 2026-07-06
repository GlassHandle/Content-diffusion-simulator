#pragma once
#include "types.hpp"
#include <random>
#include <vector>
using namespace std;

struct RunResult {
    long total_reach = 0;
    vector<long> wave_sizes;
    bool went_viral = false;
    double likes = 0, comments = 0, shares = 0, saves = 0, follows = 0;
};

RunResult simulate_once(const SimContext& ctx, mt19937& rng);
double creator_data_confidence(const Creator& c);
