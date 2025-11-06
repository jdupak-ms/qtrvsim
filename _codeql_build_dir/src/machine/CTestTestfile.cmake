# CMake generated Testfile for 
# Source directory: /home/runner/work/qtrvsim/qtrvsim/src/machine
# Build directory: /home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/src/machine
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(alu "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/target/alu_test")
set_tests_properties(alu PROPERTIES  _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;93;add_test;/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;0;")
add_test(registers "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/target/registers_test")
set_tests_properties(registers PROPERTIES  _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;106;add_test;/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;0;")
add_test(memory "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/target/memory_test")
set_tests_properties(memory PROPERTIES  _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;124;add_test;/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;0;")
add_test(cache "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/target/cache_test")
set_tests_properties(cache PROPERTIES  _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;150;add_test;/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;0;")
add_test(instruction "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/target/instruction_test")
set_tests_properties(instruction PROPERTIES  _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;164;add_test;/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;0;")
add_test(program_loader "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/target/program_loader_test")
set_tests_properties(program_loader PROPERTIES  _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;185;add_test;/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;0;")
add_test(core "/home/runner/work/qtrvsim/qtrvsim/_codeql_build_dir/target/core_test")
set_tests_properties(core PROPERTIES  _BACKTRACE_TRIPLES "/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;221;add_test;/home/runner/work/qtrvsim/qtrvsim/src/machine/CMakeLists.txt;0;")
