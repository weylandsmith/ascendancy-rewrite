cmake_minimum_required(VERSION 3.16)
project(ascendancy_rewrite CXX)

# ---------------------------------------------------------------------------
# Evidence rule (docs/PLAN.md rule 1): every constant in this tree cites a
# file under docs/. See src/formats/*.cpp for the format citations.
# ---------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

add_compile_options(-Wall -Wextra -Wno-unused-parameter)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SDL2 REQUIRED sdl2)
pkg_check_modules(SDL2_MIXER REQUIRED SDL2_mixer)

# Project root lets the runtime locate extracted/ and docs/ without an install
# step (the gate builds in-tree and runs headless).
add_compile_definitions(ASCENDANCY_SOURCE_DIR="${CMAKE_SOURCE_DIR}/..")

include_directories(${SDL2_INCLUDE_DIRS} ${SDL2_MIXER_INCLUDE_DIRS} src)

# ---- core: no SDL dependency, so the sim is testable headless -------------
add_library(ascend_core STATIC
  src/formats/cob.cpp
  src/formats/bin_table.cpp
  src/game/starstat.cpp
  src/game/mapgen.cpp
  src/game/research.cpp
  src/game/economy.cpp
  src/game/diplomacy.cpp
  src/game/campaign.cpp
)

# ---- importer + game ------------------------------------------------------
add_executable(ascendancy
  src/main.cpp
)
target_link_libraries(ascendancy PRIVATE ascend_core ${SDL2_LIBRARIES} ${SDL2_MIXER_LIBRARIES})

# ---- tests ----------------------------------------------------------------
enable_testing()
add_executable(run_tests
  tests/main.cpp
  tests/test_cob.cpp
  tests/test_bin_table.cpp
  tests/test_mapgen.cpp
  tests/test_research.cpp
  tests/test_economy.cpp
  tests/test_diplomacy.cpp
  tests/test_campaign.cpp
)
target_link_libraries(run_tests PRIVATE ascend_core)
add_test(NAME unit_tests COMMAND run_tests)
