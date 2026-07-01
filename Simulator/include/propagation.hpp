//P3

#pragma once
#include "types.hpp"
#include <random>
#include <vector>
using namespace std;

struct RunResult {
    long total_reach = 0;
    vector<long> wave_sizes;
    bool went_viral = false;
};

RunResult simulate_once(const SimContext& ctx, mt19937& rng);
