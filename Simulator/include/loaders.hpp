#pragma once
#include "types.hpp"
#include <string>
#include <vector>
using namespace std;

vector<Persona> load_personas(const string& path);  // personas.jsonl 
Content load_content(const string& path);  // data/content/<id>.json 
Trend load_trend(const string& path);  // data/trends/trend_snapshot.json
Creator load_creator (const string& path);  // data/creators/*-creator.json
