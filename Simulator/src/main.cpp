// first build the simulator using build.bat
// simulator.exe --content <name> --creator <name> [--runs N] [--seed S] [--data DIR] [--pretty]

#include "loaders.hpp"
#include "engagement.hpp"
#include "propagation.hpp"
#include "montecarlo.hpp"
#include "third_party/json.hpp"
#include <chrono>
#include <cstdio>
#include <filesystem>
#include <iostream>
#include <string>

using json = nlohmann::json;
using clk  = chrono::steady_clock;
namespace fs = std::filesystem;

static double ms_since(clk::time_point t0) {
    return chrono::duration<double, milli>(clk::now() - t0).count();
}

static void usage(const char* argv0) {
    fprintf(stderr,
        "usage: %s --content <name> [--creator <name>]\n"
        "          [--runs N] [--seed S] [--data DIR] [--pretty]\n"
        "  content: username | content file name | path\n"
        "  creator: user id  | creator file name | path\n", argv0);
}

// newest file in dir whose name ends with suffix (timestamped names sort
// lexicographically = chronologically, so max name = latest analysis)
static string newest_matching(const fs::path& dir, const string& suffix) {
    string best;
    error_code ec;
    if (!fs::is_directory(dir, ec)) return best;
    for (const auto& e : fs::directory_iterator(dir, ec)) {
        if (!e.is_regular_file()) continue;
        string fn = e.path().filename().string();
        if (fn.size() >= suffix.size() &&
            fn.compare(fn.size() - suffix.size(), suffix.size(), suffix) == 0 &&
            fn > best) best = fn;
    }
    return best.empty() ? best : (dir / best).string();
}

static string resolve_content(const fs::path& data, const string& name) {
    error_code ec;
    if (fs::is_regular_file(name, ec)) return name;              // direct path
    fs::path root = data / "content";
    if (fs::is_regular_file(root / name, ec)) return (root / name).string();
    if (fs::is_directory(root / name, ec)) {                     // username folder
        string hit = newest_matching(root / name, "-content.json");
        if (!hit.empty()) return hit;
    }
    if (fs::is_directory(root, ec))                              // filename, any user
        for (const auto& user : fs::directory_iterator(root, ec))
            if (user.is_directory() && fs::is_regular_file(user.path() / name, ec))
                return (user.path() / name).string();
    return "";
}

static string resolve_creator(const fs::path& data, const string& name) {
    error_code ec;
    if (fs::is_regular_file(name, ec)) return name;              // direct path
    fs::path root = data / "creators";
    if (fs::is_regular_file(root / name, ec)) return (root / name).string();
    return newest_matching(root, "-" + name + "-creator.json");  // user id
}

int main(int argc, char** argv) {
    string personas_path = "Personas/personas.jsonl";
    string data_dir = "../data";
    string content_name, creator_name;
    Config cfg;
    bool pretty = false;

    for (int i = 1; i < argc; ++i) {
        string a = argv[i];
        auto next = [&]() -> string {
            if (i + 1 >= argc) { usage(argv[0]); exit(2); }
            return argv[++i];
        };
        if (a == "--content") content_name = next();
        else if (a == "--creator") creator_name = next();
        else if (a == "--data") data_dir = next();
        else if (a == "--runs") cfg.runs = stoi(next());
        else if (a == "--seed") cfg.base_seed = static_cast<unsigned>(stoul(next()));
        else if (a == "--pretty") pretty = true;
        else if (a == "--help" || a == "-h") { usage(argv[0]); return 0; }
        else { fprintf(stderr, "unknown arg: %s\n", a.c_str()); usage(argv[0]); return 2; }
    }
    if (content_name.empty()) { usage(argv[0]); return 2; }

    try {
        const fs::path data(data_dir);

        string content_path = resolve_content(data, content_name);
        if (content_path.empty())
            throw runtime_error("content '" + content_name + "' not found under " + (data / "content").string());

        string creator_path;
        if (!creator_name.empty()) {
            creator_path = resolve_creator(data, creator_name);
            if (creator_path.empty())
                throw runtime_error("creator '" + creator_name + "' not found under " + (data / "creators").string());
        }

        auto t0 = clk::now();
        vector<Persona> personas = load_personas(personas_path);
        fprintf(stderr, "[sim] personas: %zu agents (%.0f ms)\n", personas.size(), ms_since(t0));

        Content content = load_content(content_path);
        fprintf(stderr, "[sim] content: %s\n", content_path.c_str());

        // trend + creator are optional: missing -> neutral defaults
        Trend trend;
        try { trend = load_trend((data / "trends" / "trend_snapshot.json").string()); }
        catch (const exception& e) { fprintf(stderr, "[sim] no trend snapshot (%s) — using neutral trend\n", e.what()); }

        Creator creator;
        if (!creator_path.empty()) {
            creator = load_creator(creator_path);
            fprintf(stderr, "[sim] creator: %s\n", creator_path.c_str());
        } else fprintf(stderr, "[sim] no creator given — using default creator mechanics\n");

        trend.content_alignment = compute_trend_alignment(content, trend);
        fprintf(stderr, "[sim] content '%s' (%s): trend_alignment=%.3f\n",
                content.content_id.c_str(), content.modality.c_str(), trend.content_alignment);

        SimContext ctx{personas, content, trend, creator, cfg};
        auto t1 = clk::now();
        SimOutput out = run_montecarlo(ctx);
        fprintf(stderr, "[sim] %d runs in %.0f ms\n", cfg.runs, ms_since(t1));

        json result = {
            {"content_id",        content.content_id},
            {"runs",              cfg.runs},
            {"audience_pool",     personas.size()},
            {"trend_alignment",   trend.content_alignment},
            {"expected_reach",    out.expected_reach},
            {"reach_p10",         out.reach_p10},
            {"reach_p50",         out.reach_p50},
            {"reach_p90",         out.reach_p90},
            {"viral_probability", out.viral_probability},
            {"confidence",        out.confidence},
            {"mean_wave",         out.mean_wave},
            {"wave_p10",          out.wave_p10},
            {"wave_p50",          out.wave_p50},
            {"wave_p90",          out.wave_p90},
            {"engagement", {
                {"likes",    out.likes},
                {"comments", out.comments},
                {"shares",   out.shares},
                {"saves",    out.saves},
                {"follows",  out.follows},
            }},
        };
        cout << (pretty ? result.dump(2) : result.dump()) << endl;
        return 0;
    } catch (const exception& e) {
        fprintf(stderr, "[sim] FATAL: %s\n", e.what());
        return 1;
    }
}
