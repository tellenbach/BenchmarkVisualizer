#include <vector>
#include <benchmark/benchmark.h>

static void BM_VectorPush(benchmark::State& state) {
  std::vector<int> vec;
  for (auto _ : state) {
    for (int i = 0; i < state.range(0); ++i) {
    	vec.push_back(i);
    }
  }

  // Identification of x values
  state.counters["Size"] = state.range(0);

  // Benchmark group
  state.counters["benchmark_visualizer_group"] = 0;
}

static void BM_VectorAccess(benchmark::State& state) {
  std::vector<int> vec(state.range(0));
  for (auto _ : state) {
    for (int i = 0; i < state.range(0); ++i) { 
  		vec[i] = i;
    }
  }

  // Identification of x values
  state.counters["Size"] = state.range(0);

  // Benchmark group
  state.counters["benchmark_visualizer_group"] = 1;
}

BENCHMARK(BM_VectorPush)
	->Arg(10)
	->Arg(100)
	->Arg(1000)
	->Arg(10000);

BENCHMARK(BM_VectorAccess)
	->Arg(10)
	->Arg(100)
	->Arg(1000)
	->Arg(10000);

BENCHMARK_MAIN();
