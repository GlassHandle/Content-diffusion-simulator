// P4

#pragma once
#include "types.hpp"
#include <vector>
using namespace std;

struct SimOutput {
    double expected_reach = 0;
    double reach_p10 = 0, reach_p50 = 0, reach_p90 = 0;
    double viral_probability = 0;
    double confidence = 0;
    vector<double> mean_wave;
};

SimOutput run_montecarlo(const SimContext& ctx);
