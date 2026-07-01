//P2

#pragma once
#include "types.hpp"

// Every field is a probability in [0, 1].
struct EngagementResult {
    double watch = 0, like = 0, comment = 0, share = 0, save = 0, follow = 0;
};

EngagementResult engage(const Persona& p, const Content& c, const Trend& t, const Config& cfg);
