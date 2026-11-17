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
# zlib: savestate ZIP reader (formats/shipsave.cpp, t360). System lib, no vendoring.
find_package(ZLIB REQUIRED)
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
  src/formats/gif.cpp
  src/formats/voc.cpp
  src/formats/flic.cpp
  src/formats/fnt.cpp
  src/formats/gamepal.cpp
  src/formats/shp.cpp
  src/formats/shipsave.cpp
  src/game/starstat.cpp
  src/game/mapgen.cpp
  src/game/research.cpp
  src/game/economy.cpp
  src/game/diplomacy.cpp
  src/game/species.cpp
  src/game/campaign.cpp
  src/game/shipsim.cpp
  src/game/observer.cpp
  src/game/campaign_fleet_bridge.cpp
  src/game/aggregate_oracle.cpp
)
# shipsave.cpp inflates savestate ZIPs; PUBLIC so consumers (run_tests) link it.
target_link_libraries(ascend_core PUBLIC ZLIB::ZLIB)

# ---- importer + game ------------------------------------------------------
add_library(ascend_ui STATIC
  src/ui/layout.cpp
  src/ui/boot.cpp
  src/ui/menulaw.cpp
  src/ui/vendortext.cpp
  src/ui/titlepalette.cpp
  src/ui/title.cpp
  src/ui/hudlayout.cpp
  src/ui/mapchrome.cpp
  src/ui/cam3d.cpp
  src/ui/statuslaw.cpp
  src/ui/statusbg.cpp
  src/ui/statuslist.cpp
  src/ui/fleetlist.cpp
  src/ui/planetview.cpp
  src/ui/researchview.cpp
  src/ui/abilitylaw.cpp
  src/ui/speciesmenu.cpp
  src/ui/sysview.cpp
  src/ui/raceintro.cpp
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
  tests/test_campaign_fleet_t365.cpp
  tests/test_diponattack_t204.cpp
  tests/test_invasion_war_t207.cpp
  tests/test_emergency_t201.cpp
  tests/test_demolish_t202b.cpp
  tests/test_freetech_t203.cpp
  tests/test_ui_layout.cpp
  tests/test_boot_t385.cpp
  tests/test_menulaw_t387.cpp
  tests/test_newgame_t393.cpp
  tests/test_poppanel_t263.cpp
  tests/test_hudlayout_t264.cpp
  tests/test_mapchrome_t394.cpp
  tests/test_cam3d_t399.cpp
  tests/test_axis_t416.cpp
  tests/test_rail_t400.cpp
  tests/test_newgame_t401.cpp
  tests/test_statuslaw_t388.cpp
  tests/test_statuslist_t402.cpp
  tests/test_planetview_t406.cpp
  tests/test_statusnav_t405.cpp
  tests/test_statusbg_t417b.cpp
  tests/test_fleetlist_t407.cpp
  tests/test_researchview_t408.cpp
  tests/test_speciesmenu_t409.cpp
  tests/test_sysview_t410.cpp
  tests/test_maplook_t411.cpp
  tests/test_raceintro_t412.cpp
  tests/test_econres_t274.cpp
  tests/test_planetwin_t276.cpp
  tests/test_score_t284.cpp
  tests/test_control_t291.cpp
  tests/test_terrain_t294.cpp
  tests/test_audio.cpp
  tests/test_sound_t395.cpp
  tests/test_sfxpress_t404.cpp
  tests/test_ships.cpp
  tests/test_flic.cpp
  tests/test_gif_t390.cpp
  tests/test_gamepal_t398.cpp
  tests/test_fnt.cpp
  tests/test_shp.cpp
  tests/test_shipsave_t360.cpp
  tests/test_shipsave_t366.cpp
  tests/test_observer_t382.cpp
  tests/test_shipsim_t361.cpp
  tests/test_shipsim_t362.cpp
  tests/test_shipsim_t363.cpp
  tests/test_shipsim_t364.cpp
  tests/test_shipsim_t377.cpp
  tests/test_shipsim_t378.cpp
  tests/test_shipsim_t379.cpp
  tests/test_shipsim_t380.cpp
  tests/test_shipsim_t381.cpp
  tests/test_titletext_t392.cpp
  src/ui/layout.cpp
  src/ui/boot.cpp
  src/ui/menulaw.cpp
  src/ui/hudlayout.cpp
  src/ui/mapchrome.cpp
  src/ui/cam3d.cpp
  src/ui/statuslaw.cpp
  src/ui/statusbg.cpp
  src/ui/statuslist.cpp
  src/ui/planetview.cpp
  src/ui/sysview.cpp
  src/ui/raceintro.cpp
  src/ui/poppanel.cpp
  src/ui/planetwin.cpp
)
target_link_libraries(run_tests PRIVATE ascend_core ascend_ui)
add_test(NAME unit_tests COMMAND run_tests)
