# CMake generated Testfile for 
# Source directory: /home/runner/work/qtrvsim/qtrvsim/src/cli
# Build directory: /home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/src/cli
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(cli_stalls "/usr/local/bin/cmake" "--build" "." "--target" "cli_test_stalls")
set_tests_properties(cli_stalls PROPERTIES  WORKING_DIRECTORY "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir" _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/cmake/TestingTools.cmake;40;add_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;52;add_cli_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;0;")
add_test(cli_asm_error "/usr/local/bin/cmake" "--build" "." "--target" "cli_test_asm_error")
set_tests_properties(cli_asm_error PROPERTIES  WILL_FAIL "TRUE" WORKING_DIRECTORY "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir" _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/cmake/TestingTools.cmake;40;add_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;60;add_cli_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;0;")
add_test(cli_modifiers "/usr/local/bin/cmake" "--build" "." "--target" "cli_test_modifiers")
set_tests_properties(cli_modifiers PROPERTIES  WORKING_DIRECTORY "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir" _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/cmake/TestingTools.cmake;40;add_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;67;add_cli_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;0;")
add_test(cli_modifiers-pcrel "/usr/local/bin/cmake" "--build" "." "--target" "cli_test_modifiers-pcrel")
set_tests_properties(cli_modifiers-pcrel PROPERTIES  WORKING_DIRECTORY "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir" _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/cmake/TestingTools.cmake;40;add_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;74;add_cli_test;/home/runner/work/qtrvsim/qtrvsim/src/cli/CMakeLists.txt;0;")
