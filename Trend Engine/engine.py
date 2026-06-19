from Collectors import (YoutubeCollector,RedditCollector,GoogleTrendsCollector)
from Graph import (GraphBuilder,GraphEntityResolver,GraphStore,GraphPruner,GraphTagger,TagNodeBuilder)
from Processors import TrendProcessor

TEXT_BUILDERS = {
    "reddit": lambda item:item.get("title","")+ " . "+ item.get("post_description",""),
    "youtube": lambda item: item.get("title","") + " . "+ item.get("description",""),
    "google-trends": lambda item:item.get("Trend","")+ " , "+ item.get("Trend breakdown","")
}

class TrendEngine:
    def __init__(self):
        self.collectors = {
            "reddit": RedditCollector(),
            "youtube": YoutubeCollector(),
            "google-trends": GoogleTrendsCollector()
        }
        self.processor = TrendProcessor()
        self.store = GraphStore()
        graph = self.store.load()
        self.graph_builder = GraphBuilder(graph)
        self.tagger = GraphTagger()

    def collect(self):
        collected = {}

        reddit = self.collectors["reddit"]
        youtube = self.collectors["youtube"]
        trends = self.collectors["google-trends"]

        reddit_data = reddit.collect(limit=40)
        reddit.save(reddit_data)

        youtube_data = youtube.collect(region="IN",limit=50)
        youtube.save(youtube_data)

        trends_data = trends.collect()
        trends.save(trends_data)

        collected["reddit"] = reddit_data
        collected["youtube"] = youtube_data
        collected["google-trends"] = trends_data

        return collected
    
    def process(self, collected):
        processed = []

        for source, data in collected.items():
            results = self.processor.process_all(
                source,
                data,
                TEXT_BUILDERS[source]
            )
            processed.extend(results)
        return processed
    
    def build_graph(self, processed):
        self.graph_builder.add_all_trends(processed)

        resolver = GraphEntityResolver(self.graph_builder.graph)
        resolver.resolve_all()

        tag_builder = TagNodeBuilder(self.graph_builder.graph)

        self.tagger.tag_graph(self.graph_builder.graph,tag_builder)

    def prune(self):
        pruner = GraphPruner(self.graph_builder.graph)
        pruner.prune_graph()

    def save(self):
        self.store.save(self.graph_builder.graph)

    def run(self):
        collected = self.collect()
        processed = self.process(collected)
        self.build_graph(processed)
        self.prune()
        self.save()
        return self.graph_builder.graph
    
if __name__ == "__main__":
    engine = TrendEngine()
    engine.run()