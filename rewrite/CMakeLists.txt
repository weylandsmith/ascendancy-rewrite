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
# NOTE: SDL2_ttf was dropped 2026-10-05f — UI text now renders from the
# vendor .fnt faces (docs/re/fnt.md, OQ-017 CLOSED), no TTF substitute.

# Project root lets the runtime locate extracted/ and docs/ without an install
# step (the gate builds in-tree and runs headless).
add_compile_definitions(ASCENDANCY_SOURCE_DIR="${CMAKE_SOURCE_DIR}/..")

include_directories(${SDL2_INCLUDE_DIRS} ${SDL2_MIXER_INCLUDE_DIRS} src)

# ---- core: no SDL dependency, so the sim is testable headless -------------
add_library(ascend_core STATIC
  src/formats/cob.cpp
  src/formats/bin_table.cpp
  src/formats/voc.cpp
  src/formats/flic.cpp
  src/formats/fnt.cpp
  src/formats/shp.cpp
  src/game/starstat.cpp
  src/game/mapgen.cpp
  src/game/research.cpp
  src/game/economy.cpp
  src/game/diplomacy.cpp
  src/game/species.cpp
  src/game/campaign.cpp
)

# ---- importer + game ------------------------------------------------------
add_library(ascend_ui STATIC
  src/ui/layout.cpp
  src/ui/hudlayout.cpp
  src/ui/poppanel.cpp
  src/ui/planetwin.cpp
  src/ui/ui.cpp
  src/ui/audio.cpp
)
target_include_directories(ascend_ui PUBLIC src ${SDL2_INCLUDE_DIRS} ${SDL2_MIXER_INCLUDE_DIRS})
target_link_libraries(ascend_ui PUBLIC ascend_core ${SDL2_LIBRARIES} ${SDL2_MIXER_LIBRARIES})

add_executable(ascendancy
  src/main.cpp
)
target_link_libraries(ascendancy PRIVATE ascend_ui)

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
  tests/test_species.cpp
  tests/test_campaign.cpp
  tests/test_diponattack_t204.cpp
  tests/test_invasion_war_t207.cpp
  tests/test_emergency_t201.cpp
  tests/test_demolish_t202b.cpp
  tests/test_freetech_t203.cpp
  tests/test_ui_layout.cpp
  tests/test_poppanel_t263.cpp
  tests/test_hudlayout_t264.cpp
  tests/test_econres_t274.cpp
  tests/test_planetwin_t276.cpp
  tests/test_score_t284.cpp
  tests/test_audio.cpp
  tests/test_ships.cpp
  tests/test_flic.cpp
  tests/test_fnt.cpp
  tests/test_shp.cpp
  src/ui/layout.cpp
  src/ui/hudlayout.cpp
  src/ui/poppanel.cpp
  src/ui/planetwin.cpp
)
target_link_libraries(run_tests PRIVATE ascend_core)
add_test(NAME unit_tests COMMAND run_tests)
